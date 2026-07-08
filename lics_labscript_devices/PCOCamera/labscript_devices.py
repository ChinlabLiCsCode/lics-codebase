from labscript_devices.IMAQdxCamera.labscript_devices import IMAQdxCamera


class PCOCamera(IMAQdxCamera):
    """A PCO camera controlled via the pco Python SDK and triggered with a digital edge.

    Inherits all IMAQdxCamera parameters. serial_number must be passed as a
    decimal integer matching the camera's serial number (printed on the label and
    readable from the PCO Camware software).

    Typical connection table usage::

        PCOCamera(
            name='pco_panda',
            parent_device=trigger_do,
            connection='port0/line3',
            serial_number=12345,           # decimal serial number from camera label
            orientation='vertical',
            trigger_duration=1e-3,         # 1 ms trigger pulse
            camera_attributes={
                'trigger_mode': 'external exposure start & software trigger',
                'exposure_time': 0.050,    # seconds
                'pixel_rate': 272250000,   # Hz (max for PCO Panda 4.2)
                'roi': (1, 1, 2048, 2048), # full frame
                'binning': (1, 1),
            },
            manual_mode_camera_attributes={
                'trigger_mode': 'auto sequence',
            },
        )
    """

    description = 'PCO Camera'
