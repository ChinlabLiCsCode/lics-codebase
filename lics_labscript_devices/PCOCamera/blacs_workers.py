import sys
import time

from labscript_devices.IMAQdxCamera.blacs_workers import IMAQdxCameraWorker


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

    def get_camera(self):
        if self.mock:
            from labscript_devices.IMAQdxCamera.blacs_workers import MockCamera
            return MockCamera()
        return self.interface_class(self.serial_number, shutter_mode=self.shutter_mode)

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
