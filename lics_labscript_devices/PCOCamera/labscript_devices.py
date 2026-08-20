from labscript import set_passed_properties
from labscript_devices.IMAQdxCamera.labscript_devices import IMAQdxCamera


class PCOCamera(IMAQdxCamera):
    """A PCO camera controlled via the pco Python SDK and triggered with a digital edge.

    Inherits all IMAQdxCamera parameters. serial_number must be passed as a
    decimal integer matching the camera's serial number (printed on the label and
    readable from the PCO Camware software).

    shutter_mode controls the sCMOS readout mode. Valid values:
        'rolling shutter'  (default) — each row starts exposing in sequence
        'global shutter'   — all rows expose simultaneously (no rolling artifact)
        'global reset'     — all rows reset together but read out rolling

    Changing shutter_mode triggers a camera reboot (~3 s) on first use.

    display_mode controls what the BLACS tab shows after a shot. Valid values:
        'live'        (default) — tab behaves as a normal live camera viewer
        'absorption'  — after each shot, the tab computes the optical density
                        (OD) image from that shot's 'dark'/'light'/'atoms'
                        frames (same calculation as
                        analysislib/absorption_image_analysis.py's abs_calc)
                        and displays it in place of the raw camera frames.
                        Requires the shot to have used frametypes 'dark',
                        'light' and 'atoms' under the same exposure name
                        (see Cs_LF_H_Imaging in cs_subsequences.py).

    Typical connection table usage::

        PCOCamera(
            name='pco_panda',
            parent_device=trigger_do,
            connection='port0/line3',
            serial_number=12345,           # decimal serial number from camera label
            orientation='vertical',
            trigger_duration=1e-3,         # 1 ms trigger pulse
            shutter_mode='global shutter', # optional, default 'rolling shutter'
            display_mode='absorption',     # optional, default 'live'
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
        property_names={"connection_table_properties": ["shutter_mode", "display_mode"]}
    )
    def __init__(self, *args, shutter_mode='rolling shutter', display_mode='live', **kwargs):
        super().__init__(*args, **kwargs)
        if display_mode not in ('live', 'absorption'):
            raise ValueError(
                f"display_mode must be 'live' or 'absorption', not {display_mode!r}"
            )
        self.shutter_mode = shutter_mode
        self.display_mode = display_mode
