import sys
import time

import numpy as np
import labscript_utils.h5_lock
import h5py
import zmq
from labscript_utils.properties import set_attributes

from labscript_devices.IMAQdxCamera.blacs_workers import IMAQdxCameraWorker
from lics_labscript_devices.PCOCamera.absorption_analysis import full_analysis


class PCO_Camera:
    """Hardware interface for PCO cameras using the pco Python SDK.

    Exposes camera settings as named attributes consumed by IMAQdxCameraWorker's
    smart-programming mechanism. Supported attribute names:

        trigger_mode  str   'auto sequence' | 'external exposure start & software trigger'
        exposure_time float seconds
        pixel_rate    int   Hz, e.g. 272250000 for PCO Panda 4.2 fast scan
        roi           tuple (x0, y0, x1, y1), 1-indexed pixel coordinates
        binning       tuple (h_binning, v_binning)
    """

    ATTRIBUTE_NAMES = ['trigger_mode', 'exposure_time', 'roi', 'binning']

    def __init__(self, serial_number, shutter_mode='rolling shutter'):
        import pco
        self._serial_number = serial_number
        self.cam = pco.Camera(serial=serial_number)
        self._abort_acquisition = False
        self.exception_on_failed_shot = True
        self._img_index = 0
        self._continuous = False

        if shutter_mode is not None:
            try:
                current_mode = self.cam.sdk.get_shutter_mode().get('shutter_mode')
            except Exception:
                current_mode = None
            if current_mode != shutter_mode:
                print(
                    f"PCO_Camera: changing shutter mode '{current_mode}' → '{shutter_mode}'"
                    " (camera will reboot, ~3 s)..."
                )
                try:
                    self.cam.sdk.set_shutter_mode(shutter_mode)
                except Exception as e:
                    print(f"PCO_Camera: warning — could not set shutter mode: {e}")
                else:
                    print("PCO_Camera: waiting for camera reboot...")
                    time.sleep(3)
                    self.cam = pco.Camera(serial=serial_number)
                    print("PCO_Camera: camera ready after shutter mode change.")

    # --- Attribute interface (called by IMAQdxCameraWorker) ---

    def set_attributes(self, attr_dict):
        for name, value in attr_dict.items():
            self.set_attribute(name, value)

    def set_attribute(self, name, value):
        if name == 'trigger_mode':
            self.cam.sdk.set_trigger_mode(value)
            # SMA #1 must be explicitly enabled to accept the external trigger signal.
            # In 'auto sequence' mode, disable it so the camera ignores SMA #1.
            if value == 'auto sequence':
                self.cam.configureHWIO_1_exposureTrigger(on=False, edgePolarity='rising edge')
            else:
                self.cam.configureHWIO_1_exposureTrigger(on=True, edgePolarity='rising edge')
        elif name == 'exposure_time':
            # cam.exposure_time is a high-level property that accepts seconds
            self.cam.exposure_time = value
        elif name == 'pixel_rate':
            self.cam.sdk.set_pixel_rate(int(value))
        elif name == 'roi':
            x0, y0, x1, y1 = value
            self.cam.sdk.set_roi(int(x0), int(y0), int(x1), int(y1))
        elif name == 'binning':
            x_bin, y_bin = value
            self.cam.sdk.set_binning(int(x_bin), int(y_bin))
        else:
            raise ValueError(f"Unknown PCO camera attribute: {name!r}")

    def get_attribute(self, name):
        if name == 'trigger_mode':
            return self.cam.sdk.get_trigger_mode()['trigger mode']
        elif name == 'exposure_time':
            # cam.exposure_time is a high-level property that returns seconds
            return self.cam.exposure_time
        elif name == 'pixel_rate':
            return self.cam.sdk.get_pixel_rate()['pixel rate']
        elif name == 'roi':
            r = self.cam.sdk.get_roi()
            return (r['x0'], r['y0'], r['x1'], r['y1'])
        elif name == 'binning':
            b = self.cam.sdk.get_binning()
            return (b['binning x'], b['binning y'])
        else:
            raise ValueError(f"Unknown PCO camera attribute: {name!r}")

    def get_attribute_names(self, visibility_level=None):
        return list(self.ATTRIBUTE_NAMES)

    # --- Acquisition interface (called by IMAQdxCameraWorker) ---

    def snap(self):
        """Acquire one frame in free-running (auto sequence) mode."""
        self.cam.record(number_of_images=1, mode='sequence non blocking')
        self.cam.wait_for_first_image()
        image, _ = self.cam.image(image_index=0)
        self.cam.stop()
        return image.copy()

    def configure_acquisition(self, continuous=True, bufferCount=5):
        self._img_index = 0
        self._continuous = continuous
        # Stop any active recording before re-arming.  Three levels of cleanup:
        # 1. cam.stop() → PCO_RecorderStopRecord: works when the recorder handle
        #    is still live (intra-session tab crash where stop_acquisition was
        #    never called).  No-op when the handle is null.
        # 2. set_recording_state('off'): stops the firmware directly, covers the
        #    cross-session case where a new pco.Camera was opened after a full
        #    BLACS restart but the hardware was still recording.
        # 3. reset_lib() → PCO_RecorderResetLib: clears residual DLL state.
        try:
            self.cam.stop()
        except Exception:
            pass
        try:
            self.cam.sdk.set_recording_state('off')
        except Exception:
            pass
        try:
            self.cam.rec.reset_lib()
        except Exception:
            pass
        if continuous:
            # Force auto sequence (free-running) mode so live view always
            # works regardless of what trigger mode the firmware was left in
            # (e.g. after a crash mid-shot in external exposure control mode).
            self.cam.sdk.set_trigger_mode('auto sequence')
            self.cam.configureHWIO_1_exposureTrigger(on=False, edgePolarity='rising edge')
            self.cam.record(number_of_images=bufferCount, mode='ring buffer')
        else:
            self.cam.record(number_of_images=bufferCount, mode='sequence non blocking')

    def grab(self, waitForNextBuffer=True, timeout=30.0):
        """Return the next image from the camera buffer.

        In continuous (ring buffer) mode the camera is free-running and we wait for
        a new frame. In sequence mode we poll the segment image count so that each
        external trigger is matched to exactly one image_number slot.
        """
        if waitForNextBuffer:
            if self._continuous:
                self.cam.wait_for_new_image(delay=False, timeout=timeout)
            else:
                target = self._img_index
                deadline = time.perf_counter() + timeout
                while True:
                    if self.cam.recorded_image_count > target:
                        break
                    if time.perf_counter() > deadline:
                        raise TimeoutError(
                            f"Timed out waiting for PCO image {target + 1}"
                        )
                    time.sleep(0.005)

        if self._continuous:
            image, _ = self.cam.image(image_index=0xFFFFFFFF)  # PCO_RECORDER_LATEST_IMAGE
        else:
            image, _ = self.cam.image(image_index=self._img_index)
            self._img_index += 1
        return image.copy()

    def grab_multiple(self, n_images, images, waitForNextBuffer=True):
        print(f"Attempting to grab {n_images} images.")
        for i in range(n_images):
            while True:
                if self._abort_acquisition:
                    print("Abort during acquisition.")
                    self._abort_acquisition = False
                    return
                try:
                    images.append(self.grab(waitForNextBuffer))
                    print(f"Got image {i + 1} of {n_images}.")
                    break
                except TimeoutError as e:
                    if self.exception_on_failed_shot:
                        raise
                    print(str(e), file=sys.stderr)
                    return
        print(f"Got {len(images)} of {n_images} images.")

    def stop_acquisition(self):
        self.cam.stop()

    def abort_acquisition(self):
        self._abort_acquisition = True

    def close(self):
        self.cam.close()


class PCOCameraWorker(IMAQdxCameraWorker):
    """BLACS worker for PCO cameras. Uses PCO_Camera as the hardware interface."""

    interface_class = PCO_Camera

    def init(self):
        # display_mode, species, save_roi and defringe_roi are runtime-only settings (see
        # PCOCameraTab's switchers/draggable ROIs), not connection table properties:
        # they're changed live from the tab, and reset to their defaults on every worker
        # (re)start.
        self.display_mode = 'live'
        self.species = 'Cs'
        # Gaussian curve fitting (scipy.optimize.curve_fit, x2 per shot) is the
        # slowest part of the absorption pipeline by far -- defaults on, but the tab's
        # Fits checkbox can disable it for faster live display between shots where
        # fit results aren't needed every time.
        self.fit_enabled = True
        # (x0, y0, x1, y1) pixel bounds, or None for "not configured yet" (no cropping,
        # nothing recorded). Set live from the tab's draggable ROI boxes.
        self.save_roi = None
        self.defringe_roi = None
        # (dark, light, atoms) from the most recently computed absorption shot, so
        # set_species() can instantly redisplay with the new species without waiting for
        # another shot.
        self._last_absorption_frames = None
        super().init()

    def get_camera(self):
        if self.mock:
            from labscript_devices.IMAQdxCamera.blacs_workers import MockCamera
            return MockCamera()
        return self.interface_class(self.serial_number, shutter_mode=self.shutter_mode)

    def set_display_mode(self, mode):
        if mode not in ('live', 'absorption'):
            raise ValueError(f"display_mode must be 'live' or 'absorption', not {mode!r}")
        self.display_mode = mode
        if mode == 'absorption' and self.continuous_thread is not None:
            # Continuous live-view acquisition is pointless while the absorption panel
            # is shown, and leaving it running would race with our own image_socket use
            # in transition_to_manual() below (see the comment there). Fully stop it
            # (not just pause) so it won't auto-resume around future shots either.
            self.stop_continuous()

    def set_species(self, species):
        if species not in ('Cs', 'Li'):
            raise ValueError(f"species must be 'Cs' or 'Li', not {species!r}")
        self.species = species
        if self._last_absorption_frames is not None:
            # Instantly redisplay the last shot's frames with the new species, rather
            # than waiting for another shot. Species only affects the resonant cross
            # section (Density/atom-number results), not the OD image, but it's simplest
            # to just recompute everything. Deliberately does NOT rewrite
            # 'results/live_image_analysis' in the shot's h5 file -- that log reflects
            # what the shot actually used, and shouldn't be retroactively changed by a
            # later species toggle done purely for redisplay.
            dark, light, atoms = self._last_absorption_frames
            analysis = full_analysis(dark, light, atoms, species=self.species, fit=self.fit_enabled)
            self._send_absorption_analysis(dark, light, atoms, analysis)

    def set_fit_enabled(self, enabled):
        self.fit_enabled = bool(enabled)
        if self._last_absorption_frames is not None:
            # Instantly redisplay, same rationale as set_species() above.
            dark, light, atoms = self._last_absorption_frames
            analysis = full_analysis(dark, light, atoms, species=self.species, fit=self.fit_enabled)
            self._send_absorption_analysis(dark, light, atoms, analysis)

    def set_save_roi(self, roi):
        """roi is (x0, y0, x1, y1) pixel bounds (half-open: x1/y1 exclusive), in the
        coordinate system of the acquired image, or None to stop cropping/recording."""
        self.save_roi = tuple(int(v) for v in roi) if roi is not None else None

    def set_defringe_roi(self, roi):
        """Same coordinate convention as set_save_roi(). Recorded as metadata only --
        no defringing algorithm is implemented (yet); this just reserves the region for
        one to use later."""
        self.defringe_roi = tuple(int(v) for v in roi) if roi is not None else None

    def transition_to_manual(self):
        # Base class clears self.h5_filepath before returning, so capture it first.
        h5_filepath = self.h5_filepath
        result = super().transition_to_manual()
        if h5_filepath is not None:
            try:
                self._crop_saved_images_and_record_rois(h5_filepath)
            except Exception as e:
                print(f"PCOCameraWorker: failed to crop saved images / record ROIs: {e}", file=sys.stderr)
        if self.display_mode == 'absorption' and h5_filepath is not None:
            # super().transition_to_manual() may have just resumed continuous
            # acquisition (if it was running before the shot and not stopped by
            # set_display_mode above), which uses self.image_socket from a background
            # thread. zmq REQ sockets aren't thread-safe and enforce strict alternating
            # send/recv, so using it concurrently from here raises ZMQError:
            # "Operation cannot be accomplished in current state". Pause it around our
            # own use of the socket to avoid that race.
            was_continuous = self.continuous_thread is not None
            if was_continuous:
                self.stop_continuous(pause=True)
            try:
                self._compute_and_send_absorption_display(h5_filepath)
            except Exception as e:
                print(f"PCOCameraWorker: failed to compute absorption image: {e}", file=sys.stderr)
            finally:
                if was_continuous:
                    self.start_continuous(self.continuous_dt)
        return result

    def _crop_saved_images_and_record_rois(self, h5_filepath):
        """Crop every image transition_to_manual() just saved down to save_roi (if set),
        and record save_roi/defringe_roi as metadata on the image group -- regardless of
        display_mode, and regardless of whether a crop was actually needed, so the ROIs
        configured at shot time are always recoverable from the shot file. Runs before
        the absorption display/analysis below, so that (if display_mode is 'absorption')
        it operates on the already-cropped images, same as anyone re-reading the shot
        file afterwards would see."""
        if self.save_roi is None and self.defringe_roi is None:
            return
        image_path = 'images/' + (self.orientation or self.device_name)
        with h5py.File(h5_filepath, 'r+') as f:
            image_group = f.get(image_path)
            if image_group is None:
                return

            roi_attrs = {}
            if self.save_roi is not None:
                roi_attrs['save_roi'] = self.save_roi
            if self.defringe_roi is not None:
                roi_attrs['defringe_roi'] = self.defringe_roi
            set_attributes(image_group, roi_attrs)

            if self.save_roi is None:
                return
            x0, y0, x1, y1 = self.save_roi
            for key in list(image_group.keys()):
                exposure_group = image_group[key]
                if not isinstance(exposure_group, h5py.Group):
                    continue
                for frametype in list(exposure_group.keys()):
                    dset = exposure_group[frametype]
                    # (H, W) for a single frame, or (N, H, W) if this (name, frametype)
                    # pair had multiple exposures in the same shot.
                    h, w = dset.shape[-2:]
                    cx0, cy0 = max(0, x0), max(0, y0)
                    cx1, cy1 = min(w, x1), min(h, y1)
                    if cx1 <= cx0 or cy1 <= cy0:
                        continue  # ROI doesn't overlap this image; leave it alone
                    if (cx0, cy0, cx1, cy1) == (0, 0, w, h):
                        continue  # ROI covers the whole image already; nothing to trim
                    cropped = dset[..., cy0:cy1, cx0:cx1]
                    attrs = dict(dset.attrs)
                    del exposure_group[frametype]
                    new_dset = exposure_group.create_dataset(
                        frametype, data=cropped, dtype='uint16', compression='gzip'
                    )
                    for attr_key, attr_val in attrs.items():
                        new_dset.attrs[attr_key] = attr_val

    def _compute_and_send_absorption_display(self, h5_filepath):
        """Read back the most recently acquired exposure's dark/light/atoms frames
        from the shot file, run the shared absorption analysis (same calculation as
        analysislib/absorption_image_analysis.py), log the fit results under
        'results/live_image_analysis' (the same HDF5 location lyse's own
        run.save_result() writes to, so these show up as ordinary columns in the lyse
        dataframe without needing a separate analysis script to run), and send
        Dark/Light/Atoms/OD/Density to the BLACS tab in place of the raw camera frames
        that transition_to_manual() already sent, so the tab's frame selector can switch
        between them."""
        image_path = 'images/' + (self.orientation or self.device_name)
        with h5py.File(h5_filepath, 'r+') as f:
            exposures = f['devices'][self.device_name]['EXPOSURES'][:]
            if not len(exposures):
                return
            exposures.sort(order='t')
            name = exposures[-1]['name']
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            group = f.get(image_path)
            if group is None or name not in group:
                return
            frame_group = group[name]
            if not all(ft in frame_group for ft in ('dark', 'light', 'atoms')):
                return

            def last_frame(dset):
                data = dset[()]
                return data[-1] if data.ndim == 3 else data

            dark = last_frame(frame_group['dark']).astype(float)
            light = last_frame(frame_group['light']).astype(float)
            atoms = last_frame(frame_group['atoms']).astype(float)

            analysis = full_analysis(dark, light, atoms, species=self.species, fit=self.fit_enabled)

            # 'results/<name>' is exactly the HDF5 location lyse's own Run.save_result()
            # writes to (results/<analysis script's basename>/<result name>) -- writing
            # here directly means these appear as ordinary lyse dataframe columns
            # (('live_image_analysis', 'N_x'), etc.) without lyse needing to run a
            # separate analysis script against the shot. A plain top-level group (what
            # this used to be) is invisible to lyse's dataframe builder, which only walks
            # 'results' and 'images' (see lyse/dataframe_utilities.py).
            results_group = f.require_group('results/live_image_analysis')
            set_attributes(results_group, analysis['results'])

            # Persist the density image itself (previously only sent transiently to the
            # tab for display, never saved), as a sibling of dark/light/atoms under this
            # exposure so it shows up in the lyse dataframe the same way those do
            # (('pco_panda', 'absorption1', 'density', 'N_x'), etc.), with the cloud-size
            # fit results attached directly to it as attributes too, so a later analysis
            # script can load the image and its fit numbers together without recomputing
            # anything.
            if 'density' in frame_group:
                del frame_group['density']
            density_dset = frame_group.create_dataset(
                'density', data=analysis['density'].astype('float32'), compression='gzip'
            )
            density_dset.attrs['CLASS'] = np.bytes_('IMAGE')
            density_dset.attrs['IMAGE_VERSION'] = np.bytes_('1.2')
            density_dset.attrs['IMAGE_SUBCLASS'] = np.bytes_('IMAGE_GRAYSCALE')
            density_dset.attrs['IMAGE_WHITE_IS_ZERO'] = np.uint8(0)
            density_dset.attrs['species'] = self.species
            fit_result_keys = (
                'N_x', 'N_y', 'N',
                'sigma_x (um)', 'sigma_y (um)',
                'x0_x (um)', 'x0_y (um)',
            )
            set_attributes(
                density_dset,
                {k: analysis['results'][k] for k in fit_result_keys},
            )

        self._last_absorption_frames = (dark, light, atoms)
        self._send_absorption_analysis(dark, light, atoms, analysis)

    def _send_absorption_analysis(self, dark, light, atoms, analysis):
        """Send Dark/Light/Atoms/OD/Density plus profile/fit data to the BLACS tab, so
        its frame selector can switch between them without asking the worker again."""
        frames = {
            'Dark': dark,
            'Light': light,
            'Atoms': atoms,
            'OD': analysis['log_image'],
            'Density': analysis['density'],
        }
        # x/y integrated-density profiles + Gaussian fit curves, and the geometric-mean
        # atom number N, so the tab can draw the same live fit-overlay plots as
        # absorption_image_analysis.py's density panel, without recomputing anything.
        profile = {
            'x_int': analysis['x_int'].tolist(),
            'y_int': analysis['y_int'].tolist(),
            'x_dist': analysis['x_dist'].tolist(),
            'y_dist': analysis['y_dist'].tolist(),
            # Sized to match the actual (possibly Save-ROI-cropped) image, not
            # necessarily the full 2048x2048 sensor -- see full_analysis().
            'span_x': analysis['span_x'].tolist(),
            'span_y': analysis['span_y'].tolist(),
            'N': float(analysis['N']),
            'results': {k: float(v) for k, v in analysis['results'].items()},
        }
        self._send_named_frames_to_parent(frames, extra=profile)

    def _send_named_frames_to_parent(self, frames, extra=None):
        """Send several same-shaped named 2D frames (e.g. Dark/Light/Atoms/OD/Density)
        to the BLACS tab in one message, so it can switch between them locally without
        asking the worker again. `extra` is merged into the JSON metadata (e.g. profile
        fit data) alongside the binary image stack."""
        names = list(frames.keys())
        stacked = np.stack([np.asarray(frames[n], dtype=float) for n in names])
        metadata = dict(dtype=str(stacked.dtype), shape=stacked.shape, frame_names=names)
        if extra:
            metadata.update(extra)
        self.image_socket.send_json(metadata, zmq.SNDMORE)
        self.image_socket.send(stacked, copy=False)
        response = self.image_socket.recv()
        assert response == b'ok', response

    def set_manual_attribute(self, name, value):
        """Set a camera attribute from the BLACS tab during manual mode.
        Pauses and resumes continuous acquisition around the attribute change.
        If arming fails with the new value, reverts to the previous value."""
        was_continuous = self.continuous_thread is not None
        if was_continuous:
            self.stop_continuous(pause=True)
        previous_value = self.smart_cache.get(name)
        self.camera.set_attribute(name, value)
        self.smart_cache[name] = value
        if was_continuous:
            try:
                self.start_continuous(self.continuous_dt)
            except Exception:
                # Camera refused to arm (e.g. invalid ROI). Revert and restart.
                if previous_value is not None:
                    self.camera.set_attribute(name, previous_value)
                    self.smart_cache[name] = previous_value
                    self.start_continuous(self.continuous_dt)
                raise
