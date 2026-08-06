import sys
import threading
import time

import numpy as np
import zmq

import labscript_utils.h5_lock
import h5py

from blacs.tab_base_classes import Worker
from labscript_utils.ls_zprocess import Context
from labscript_utils.shared_drive import path_to_local


class IDSCameraWorker(Worker):
    """BLACS worker for IDS Peak USB3 cameras.

    The camera runs continuously at all times. In manual mode, frames are
    forwarded to the BLACS tab for display (throttled by start_continuous's dt
    argument). In buffered mode, every frame is recorded; at the end of the
    shot, the full stack is written to the HDF5 file under
    images/{orientation}/.
    """

    def init(self):
        self._setup_ids_imports()
        if self.mock:
            self._init_mock()
            return

        self.ids_peak.Library.Initialize()
        self._open_camera()
        self._configure_camera()
        self._open_datastream()

        # Grab one frame before the loop to learn the sensor's bit depth.
        self._datastream_start()
        _raw, bits = self._grab_raw()
        self.full_scale = (1 << bits) - 1
        self._datastream_stop()

        self._init_shared_state()
        self._datastream_start()
        self._start_acq_thread()

    # ------------------------------------------------------------------ #
    # IDS SDK imports                                                      #
    # ------------------------------------------------------------------ #

    def _setup_ids_imports(self):
        from ids_peak import ids_peak
        from ids_peak import ids_peak_ipl_extension
        from ids_peak_ipl import ids_peak_ipl
        self.ids_peak = ids_peak
        self.ids_ipl_ext = ids_peak_ipl_extension
        self.ids_ipl = ids_peak_ipl
        self._unpacked_by_bits = {
            8:  ids_peak_ipl.PixelFormatName_Mono8,
            10: ids_peak_ipl.PixelFormatName_Mono10,
            12: ids_peak_ipl.PixelFormatName_Mono12,
        }

    # ------------------------------------------------------------------ #
    # Mock mode                                                            #
    # ------------------------------------------------------------------ #

    def _init_mock(self):
        print("IDSCameraWorker: starting as mock device")
        self.full_scale = 4095
        self._init_shared_state()
        self._start_acq_thread(mock=True)

    def _mock_acquire_loop(self):
        rng = np.random.default_rng(42)
        h, w = 512, 512
        yy, xx = np.mgrid[:h, :w]
        base = (
            self.full_scale
            * 0.3
            * np.exp(-((xx - w // 2) ** 2 + (yy - h // 2) ** 2) / (2 * (w / 8) ** 2))
        ).astype(np.uint16)
        frame_period = 0.05
        while self._running:
            raw = np.clip(base + rng.integers(0, 80, base.shape), 0, self.full_scale).astype(np.uint16)
            self._process_frame(raw)
            time.sleep(frame_period)

    # ------------------------------------------------------------------ #
    # Camera open / configure                                              #
    # ------------------------------------------------------------------ #

    def _open_camera(self):
        dm = self.ids_peak.DeviceManager.Instance()
        dm.Update()
        descs = dm.Devices()
        if not descs:
            raise RuntimeError("No IDS Peak device found. Is the camera connected?")
        target = str(self.serial_number) if self.serial_number else None
        self.device = None
        for desc in descs:
            if target is None or str(desc.SerialNumber()) == target:
                self.device = desc.OpenDevice(self.ids_peak.DeviceAccessType_Control)
                break
        if self.device is None:
            serials = [str(d.SerialNumber()) for d in descs]
            raise RuntimeError(
                f"IDS camera serial {self.serial_number!r} not found. "
                f"Available serials: {serials}"
            )
        node_maps = self.device.RemoteDevice().NodeMaps()
        if not node_maps:
            raise RuntimeError(
                "Camera opened but has no node maps -- it may be in a wedged "
                "state. Try unplugging and replugging the USB3 cable."
            )
        self.nodemap = node_maps[0]

    def _configure_camera(self):
        """One-time setup: disable auto functions, apply throughput/frame-rate
        limits, set initial exposure. Run before acquisition starts."""
        try:
            self.nodemap.FindNode("TLParamsLocked").SetValue(0)
        except self.ids_peak.Exception:
            pass
        for node_name in ("ExposureAuto", "GainAuto"):
            try:
                self.nodemap.FindNode(node_name).SetCurrentEntry("Off")
            except self.ids_peak.Exception:
                pass
        # USB3 throughput cap
        try:
            self.nodemap.FindNode("DeviceLinkThroughputLimitMode").SetCurrentEntry("On")
            n = self.nodemap.FindNode("DeviceLinkThroughputLimit")
            target = int(self.throughput_limit_mbps * 1e6)
            target = max(int(n.Minimum()), min(int(n.Maximum()), target))
            n.SetValue(target)
        except self.ids_peak.Exception:
            pass
        # Apply ROI before raising frame rate (ROI affects max fps)
        if self.roi is not None:
            self._set_roi(*self.roi)
        else:
            self._set_roi_full()
        # Maximise frame rate (ceiling re-raised after each exposure change)
        self._raise_frame_rate()
        # Initial exposure
        self.exposure_node = self.nodemap.FindNode("ExposureTime")
        us = self.manual_mode_exposure_time_ms * 1000.0
        us = max(self.exposure_node.Minimum(), min(self.exposure_node.Maximum(), us))
        self.exposure_node.SetValue(us)
        self.converter = self.ids_ipl.ImageConverter()

    def _set_roi_full(self):
        """Reset the camera to full-sensor ROI."""
        try:
            ox = self.nodemap.FindNode("OffsetX")
            oy = self.nodemap.FindNode("OffsetY")
            wn = self.nodemap.FindNode("Width")
            hn = self.nodemap.FindNode("Height")
            ox.SetValue(int(ox.Minimum()))
            oy.SetValue(int(oy.Minimum()))
            wn.SetValue(int(wn.Maximum()))
            hn.SetValue(int(hn.Maximum()))
        except self.ids_peak.Exception as e:
            print(f"IDSCameraWorker: could not reset ROI: {e}")

    def _set_roi(self, x, y, w, h):
        """Set camera ROI (x, y, w, h) in pixels. Offsets and size are snapped
        to the camera's valid increments."""
        def snap(node, value):
            mn, mx, inc = int(node.Minimum()), int(node.Maximum()), int(node.Increment())
            value = max(mn, min(mx, value))
            return mn + round((value - mn) / inc) * inc

        try:
            ox = self.nodemap.FindNode("OffsetX")
            oy = self.nodemap.FindNode("OffsetY")
            wn = self.nodemap.FindNode("Width")
            hn = self.nodemap.FindNode("Height")
            # Reset offsets so the full sensor is addressable for width/height
            ox.SetValue(int(ox.Minimum()))
            oy.SetValue(int(oy.Minimum()))
            wn.SetValue(snap(wn, w))
            hn.SetValue(snap(hn, h))
            ox.SetValue(snap(ox, x))
            oy.SetValue(snap(oy, y))
        except self.ids_peak.Exception as e:
            print(f"IDSCameraWorker: could not set ROI: {e}")

    def _raise_frame_rate(self):
        try:
            self.nodemap.FindNode("AcquisitionFrameRateEnable").SetValue(False)
            return
        except self.ids_peak.Exception:
            pass
        try:
            n = self.nodemap.FindNode("AcquisitionFrameRate")
            n.SetValue(n.Maximum())
        except self.ids_peak.Exception:
            pass

    # ------------------------------------------------------------------ #
    # Datastream helpers                                                   #
    # ------------------------------------------------------------------ #

    def _open_datastream(self):
        self.datastream = self.device.DataStreams()[0].OpenDataStream()

    def _datastream_start(self):
        payload = self.nodemap.FindNode("PayloadSize").Value()
        n = max(self.datastream.NumBuffersAnnouncedMinRequired(), 4)
        for _ in range(n):
            b = self.datastream.AllocAndAnnounceBuffer(payload)
            self.datastream.QueueBuffer(b)
        self.nodemap.FindNode("TLParamsLocked").SetValue(1)
        self.datastream.StartAcquisition()
        self.nodemap.FindNode("AcquisitionStart").Execute()
        self.nodemap.FindNode("AcquisitionStart").WaitUntilDone()

    def _datastream_stop(self):
        try:
            self.nodemap.FindNode("AcquisitionStop").Execute()
            self.nodemap.FindNode("AcquisitionStop").WaitUntilDone()
        except self.ids_peak.Exception:
            pass
        self.datastream.StopAcquisition(self.ids_peak.AcquisitionStopMode_Default)
        self.datastream.Flush(self.ids_peak.DataStreamFlushMode_DiscardAll)
        for b in self.datastream.AnnouncedBuffers():
            self.datastream.RevokeBuffer(b)
        try:
            self.nodemap.FindNode("TLParamsLocked").SetValue(0)
        except self.ids_peak.Exception:
            pass

    def _grab_raw(self, timeout_ms=2000):
        """Return (raw_uint_array, bit_depth) for one frame."""
        buf = self.datastream.WaitForFinishedBuffer(timeout_ms)
        ipl = self.ids_ipl_ext.BufferToImage(buf)
        pf = ipl.PixelFormat()
        bits = pf.NumSignificantBitsPerChannel()
        if pf.IsPacked():
            if bits not in self._unpacked_by_bits:
                raise RuntimeError(f"No unpacked format mapping for {bits}-bit source")
            ipl = self.converter.Convert(
                ipl, self.ids_ipl.PixelFormat(self._unpacked_by_bits[bits])
            )
        raw = ipl.get_numpy().copy()
        self.datastream.QueueBuffer(buf)
        return raw, bits

    # ------------------------------------------------------------------ #
    # Shared state and acquisition thread                                  #
    # ------------------------------------------------------------------ #

    def _init_shared_state(self):
        # ZMQ socket for sending frames to the BLACS tab
        self._image_socket = Context().socket(zmq.REQ)
        self._image_socket.connect(
            f'tcp://{self.parent_host}:{self.image_receiver_port}'
        )
        self._socket_lock = threading.Lock()

        # Manual-mode continuous display state
        self._continuous = False
        self._continuous_dt = None   # None = not running; 0.0 = unlimited fps
        self._last_send_time = 0.0

        # Snap: set this event to capture the next frame and send it to tab
        self._snap_event = threading.Event()
        self._snap_frame = None

        # Buffered-mode recording state
        self._recording = False
        self._record_t0 = 0.0
        self._record_lock = threading.Lock()
        self._record_buffer = []   # [(elapsed_s, raw_array), ...]
        self.h5_filepath = None
        self._running = True

    def _start_acq_thread(self, mock=False):
        target = self._mock_acquire_loop if mock else self._acquire_loop
        self._acq_thread = threading.Thread(target=target, daemon=True)
        self._acq_thread.start()

    # ------------------------------------------------------------------ #
    # Acquisition loop (real hardware)                                     #
    # ------------------------------------------------------------------ #

    def _acquire_loop(self):
        while self._running:
            try:
                raw, _bits = self._grab_raw(timeout_ms=500)
            except Exception:
                time.sleep(0.05)
                continue
            self._process_frame(raw)

    def _process_frame(self, raw):
        now = time.perf_counter()

        # Snap request: deliver the next frame to snap() then clear
        if self._snap_event.is_set():
            self._snap_frame = raw
            self._snap_event.clear()

        # Buffered recording: collect frames or per-frame counts with timestamps
        if self._recording:
            elapsed = now - self._record_t0
            value = int(raw.sum()) if self.save_mode == 'counts' else raw
            with self._record_lock:
                self._record_buffer.append((elapsed, value))

        # Continuous display: throttled forwarding to BLACS tab
        if self._continuous:
            if (now - self._last_send_time) >= self._continuous_dt:
                if self._socket_lock.acquire(blocking=False):
                    try:
                        self._send_image(raw)
                    except Exception:
                        pass
                    finally:
                        self._socket_lock.release()
                self._last_send_time = now

    # ------------------------------------------------------------------ #
    # ZMQ image sender                                                     #
    # ------------------------------------------------------------------ #

    def _send_image(self, image):
        """Send one frame to the tab's ZMQ server. Caller must hold
        _socket_lock. Blocks until the tab acknowledges with b'ok'."""
        metadata = {'dtype': str(image.dtype), 'shape': list(image.shape),
                    'full_scale': self.full_scale}
        self._image_socket.send_json(metadata, zmq.SNDMORE)
        self._image_socket.send(image, copy=False)
        resp = self._image_socket.recv()
        assert resp == b'ok', resp

    # ------------------------------------------------------------------ #
    # Methods called by the BLACS tab                                      #
    # ------------------------------------------------------------------ #

    def start_continuous(self, dt):
        """Begin forwarding frames to the tab at the given minimum interval (s).
        dt=0 means send as fast as the tab can consume them."""
        self._continuous_dt = dt if dt else 0.0
        self._continuous = True

    def stop_continuous(self, pause=False):
        """Stop forwarding frames to the tab. If pause=True, remember dt so
        that continuous mode can be resumed after a buffered shot."""
        self._continuous = False
        if not pause:
            self._continuous_dt = None

    def snap(self):
        """Capture the next frame from the acquire loop and send it to the tab."""
        self._snap_frame = None
        self._snap_event.set()
        deadline = time.perf_counter() + 5.0
        while self._snap_frame is None and time.perf_counter() < deadline:
            time.sleep(0.01)
        if self._snap_frame is not None:
            with self._socket_lock:
                try:
                    self._send_image(self._snap_frame)
                except Exception:
                    pass

    def set_exposure(self, value_us):
        """Set exposure time (microseconds). Clamps to camera limits and
        re-raises the frame-rate ceiling, which depends on exposure time."""
        if self.mock:
            return
        lo, hi = self.exposure_node.Minimum(), self.exposure_node.Maximum()
        self.exposure_node.SetValue(max(lo, min(hi, float(value_us))))
        self._raise_frame_rate()

    def get_exposure(self):
        """Return the current exposure time in microseconds."""
        if self.mock:
            return self.manual_mode_exposure_time_ms * 1000.0
        return float(self.exposure_node.Value())

    # ------------------------------------------------------------------ #
    # BLACS buffered-mode lifecycle                                        #
    # ------------------------------------------------------------------ #

    def transition_to_buffered(self, device_name, h5_filepath, initial_values, fresh):
        if getattr(self, 'is_remote', False):
            h5_filepath = path_to_local(h5_filepath)

        with self._record_lock:
            self._record_buffer = []
        self._record_t0 = time.perf_counter()
        self._recording = True
        self.h5_filepath = h5_filepath
        return {}

    def transition_to_manual(self):
        self._recording = False

        with self._record_lock:
            buf = list(self._record_buffer)
            self._record_buffer = []

        if buf and self.h5_filepath:
            self._save_images_to_h5(buf, self.h5_filepath)
            # Send a representative frame to the tab for display
            _t, last_frame = buf[-1]
            with self._socket_lock:
                try:
                    self._send_image(last_frame)
                except Exception:
                    pass

        self.h5_filepath = None

        # Resume continuous display if it was running before the shot
        if self._continuous_dt is not None:
            self.start_continuous(self._continuous_dt)

        return True

    def abort_buffered(self):
        self._recording = False
        with self._record_lock:
            self._record_buffer = []
        self.h5_filepath = None
        if self._continuous_dt is not None:
            self.start_continuous(self._continuous_dt)
        return True

    def abort_transition_to_buffered(self):
        return self.abort_buffered()

    # ------------------------------------------------------------------ #
    # HDF5 output                                                          #
    # ------------------------------------------------------------------ #

    def _save_images_to_h5(self, buf, h5_filepath):
        orientation = getattr(self, 'orientation', None) or self.device_name
        timestamps = np.array([t for t, _ in buf])

        print(f"Saving {len(buf)} IDS frames ({self.save_mode}) to {h5_filepath} "
              f"under images/{self.device_name}/{orientation}/")
        with h5py.File(h5_filepath, 'r+') as f:
            grp = f.require_group(f'images/{self.device_name}/{orientation}')
            grp.attrs['camera'] = self.device_name
            grp.attrs['failed_shot'] = False
            grp.create_dataset('timestamps', data=timestamps)

            if self.save_mode == 'counts':
                counts = np.array([c for _, c in buf], dtype=np.int64)
                grp.create_dataset('counts', data=counts)
            else:
                frames = np.stack([img for _, img in buf])   # (N, H, W)
                chunk = (1,) + frames.shape[1:]
                dset = grp.create_dataset(
                    'images', data=frames, dtype='uint16',
                    compression='gzip', compression_opts=1, chunks=chunk,
                )
                dset.attrs['CLASS'] = np.bytes_('IMAGE')
                dset.attrs['IMAGE_VERSION'] = np.bytes_('1.2')
                dset.attrs['IMAGE_SUBCLASS'] = np.bytes_('IMAGE_GRAYSCALE')
                dset.attrs['IMAGE_WHITE_IS_ZERO'] = np.uint8(0)

    # ------------------------------------------------------------------ #
    # Shutdown                                                             #
    # ------------------------------------------------------------------ #

    def program_manual(self, values):
        return {}

    def shutdown(self):
        self._running = False
        if hasattr(self, '_acq_thread'):
            self._acq_thread.join(timeout=3.0)
        if not self.mock:
            try:
                self._datastream_stop()
            except Exception:
                pass
            self.ids_peak.Library.Close()
