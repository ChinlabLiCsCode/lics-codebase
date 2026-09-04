from labscript import set_passed_properties
from labscript_devices.IMAQdxCamera.labscript_devices import IMAQdxCamera


class PCOCamera(IMAQdxCamera):
    """A PCO camera controlled via the pco Python SDK and triggered with a digital edge.

    Inherits all IMAQdxCamera parameters. serial_number must be passed as a
    decimal integer matching the camera's serial number (printed on the label and
    readable from the PCO Camware software).

    shutter_mode controls the sCMOS readout mode. The pco SDK accepts several string
    values here ('rolling shutter', 'global shutter', 'global reset', ...) as a generic
    enum shared across PCO's whole camera line, but the pco.panda 4.2 bi/bi UV hardware
    is **rolling-shutter only** — confirmed by the camera's own user manual (zero
    mentions of 'global shutter'/'global reset' anywhere in it; its datasheet lists
    "Shutter mode: Rolling Shutter" with no alternative) and by direct experience: an
    earlier attempt to set shutter_mode='global shutter' on this exact camera was
    rejected by the firmware ("Value is out of range") and left the USB connection
    wedged, needing a physical power-cycle to recover. Leave this at the default;
    see rolling_shutter_timing.py for how to work correctly *with* the rolling shutter
    (e.g. for a short external light pulse to expose the whole frame at once) instead.

    Changing shutter_mode triggers a camera reboot (~3 s) on first use.

    The BLACS tab's display mode ('Live' camera viewer vs. 'Absorption', which
    computes and shows the OD/density image from each shot's 'dark'/'light'/
    'atoms' frames — same calculation as
    analysislib/absorption_image_analysis.py's abs_calc) is switched live from
    a dropdown in the tab itself, not configured here — see PCOCameraTab.

    Typical connection table usage::

        PCOCamera(
            name='pco_panda',
            parent_device=trigger_do,
            connection='port0/line3',
            serial_number=12345,           # decimal serial number from camera label
            orientation='vertical',
            trigger_duration=1e-3,         # 1 ms trigger pulse
            # shutter_mode left at its default ('rolling shutter') -- see the class
            # docstring above; other values are not supported by this hardware.
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

    @set_passed_properties(
        property_names={"connection_table_properties": ["shutter_mode"]}
    )
    def __init__(self, *args, shutter_mode='rolling shutter', **kwargs):
        super().__init__(*args, **kwargs)
        self.shutter_mode = shutter_mode
