"""Rolling-shutter timing for the pco.panda 4.2 bi/bi UV camera.

The camera is rolling-shutter only (see the shutter_mode docstring in
labscript_devices.py) -- there is no camera setting that makes the whole sensor
expose simultaneously in a short time on its own. Each row's exposure window is
staggered from the next by a fixed LINE_TIME_S, so the earliest a row can start is
determined by its position, not by how short the configured exposure_time is. A
2048-line full-frame sweep takes ~25 ms regardless of whether exposure_time is 10us
or 5s, because that's how long the readout electronics take to sequentially cycle
through every row -- see chapter 6 ("Rolling Shutter") of the camera's user manual,
particularly the "Rolling Shutter General Timing Diagram" and the worked example on
p.13 (100us exposure / 12.136us line time -> 8 simultaneously-exposed lines).

The standard way to get a short, effectively-global-shutter-like exposure on rolling-
shutter hardware: set exposure_time comfortably longer than the full-ROI readout time
(sensor_readout_time_s below), so there's a window during which every row is
simultaneously mid-exposure (the manual's "Show common time of All Lines"), and pulse
the *imaging light itself* (e.g. an AOM-gated probe beam, controlled independently of
the camera) for a short duration timed to land inside that window -- see
common_exposure_window_s(). The camera's own exposure_time then just needs to safely
bracket the light pulse; it does not have to equal the desired "effective shutter
speed" the atoms see, since that comes from the light gating, not the camera.

Do not try to shorten the rolling-shutter sweep itself for a full-height ROI to
compete with the light-pulse duration -- getting the *whole-frame* sweep under, say,
100us requires an ROI only ~8 lines tall (100us / LINE_TIME_S), which isn't useful for
imaging an extended atom cloud. If you only need a *portion* of the frame, a shorter
ROI directly buys a shorter/no-common-window-needed sweep -- see
sensor_readout_time_s() to check what a given ROI height costs.

The pco SDK also exposes set_cmos_line_timing()/set_cmos_line_exposure_delay() (see
PCO_Camera.cam.sdk in blacs_workers.py), which may allow further low-level tuning --
deliberately not used here without the actual PCO SDK manual (not the camera user
manual bundled in this folder) to confirm their semantics: this camera has already
had one firmware-level setting (shutter_mode='global shutter') silently rejected and
left the USB connection wedged, needing a physical power-cycle to recover, so unverified
low-level SDK calls are avoided by default (see [[pco-camera-integration]] memory). The
SDK's get_image_timing() call *is* safe to use for direct verification, though -- it's
read-only and returns the camera's own measured frame/exposure/trigger timing; see
its docstring in the installed pco package for the exact fields it returns.
"""

# Fixed line time for this camera -- NOT independently adjustable via any documented
# camera_attributes setting (pixel_rate is fixed to a single value for this USB
# variant, and no other timing knob is exposed by IMAQdxCamera/PCO_Camera's
# ATTRIBUTE_NAMES). From the "Rolling Shutter General Timing Diagram" table, ch. 6 of
# the camera's user manual (bundled in this folder as
# "pco.panda 4.2 bi and bi UV User Manual.pdf").
LINE_TIME_S = 12.174e-6   # pco.panda 4.2 bi / bi UV (the variant covered by that manual)
LINE_TIME_S_BASE_MODEL = 12.136e-6  # plain pco.panda 4.2, in case that's ever swapped in

# Per the manual: "Jitter tjit <= 1 line time" -- the trigger-to-exposure-start
# uncertainty, already well under 100us with no configuration needed.
JITTER_S_MAX = LINE_TIME_S


def _roi_height_px(roi):
    """roi is (x0, y0, x1, y1), 1-indexed inclusive pixel coordinates (matching
    PCO_Camera's convention in blacs_workers.py / cam.sdk.get_roi())."""
    _, y0, _, y1 = roi
    return y1 - y0 + 1


def sensor_readout_time_s(roi, binning=(1, 1)):
    """Time for the rolling-shutter sweep to cross the full height of roi: (number of
    readout lines - 1) * LINE_TIME_S -- i.e. the delay between the first line's
    exposure start and the last line's exposure start.

    binning's vertical factor is assumed to proportionally reduce the number of
    *readout* lines (on-chip analog binning combines physical rows before readout,
    which is the normal design for this class of sCMOS sensor) -- this isn't spelled
    out explicitly in the camera's user manual, so treat this as a reasonable estimate
    to confirm empirically (e.g. via get_image_timing(), see module docstring) before
    relying on it for tight timing margins."""
    height_px = _roi_height_px(roi)
    v_binning = binning[1]
    n_lines = max(1, -(-height_px // v_binning))  # ceil division
    return (n_lines - 1) * LINE_TIME_S


def common_exposure_window_s(exposure_time_s, roi, binning=(1, 1)):
    """(window_start_s, window_end_s), relative to the camera's exposure trigger, of
    the period during which *every* row in roi is simultaneously mid-exposure -- the
    only time a brief external light pulse illuminates the whole ROI at once rather
    than just whatever band of rows happens to be exposing at that instant.

    Returns None if exposure_time_s doesn't exceed the ROI's sensor_readout_time_s (no
    such window exists at all -- see the module docstring for what to do instead:
    lengthen exposure_time_s or shrink roi's height).

    Callers should leave real margin from both ends of the returned window (not just
    the bare JITTER_S_MAX) before picking an actual pulse time, to comfortably absorb
    trigger jitter and any small drift in actual vs. nominal timing."""
    readout_s = sensor_readout_time_s(roi, binning)
    if exposure_time_s <= readout_s:
        return None
    return (readout_s, exposure_time_s)
