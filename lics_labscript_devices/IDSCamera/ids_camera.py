"""
PyQt5/pyqtgraph live viewer for an IDS peak (USB3) camera -- a rewrite of
ids_camera.py's OpenCV/HighGUI UI. OpenCV's cv2.imshow/HighGUI only gives you
an image and integer trackbars; everything else in ids_camera.py (buttons,
histogram, draggable levels, zoom/pan, non-overlapping panels) had to be
hand-drawn and hand-hit-tested. pyqtgraph provides widgets for most of that
directly:
    - pg.ImageView:  image display + a built-in histogram with a draggable
                     black/white "levels" region, plus native scroll-zoom
                     and drag-pan on both the image and the histogram.
    - pg.RectROI:    draggable/resizable region-of-interest box with real
                     handles, instead of hand-rolled corner hit-testing.
    - pg.PlotWidget: proper axes/zoom/pan for the counts-history and
                     per-pixel-profile plots.

Known gap: pyqtgraph's stock histogram plots linear frequency, not the
log-scaled bars ids_camera.py ended up needing (a single dominant peak,
e.g. background, flattens smaller ones on a linear axis). Reaching into
ImageView's internals to force log bars would trade one fragility for
another, so this ships with the default for now.

Setup:
    pip install ids_peak ids_peak_ipl PyQt5 pyqtgraph numpy

Controls:
    drag the ROI box / its corner handle - move/resize the region of interest
                                            (clamped to a minimum size)
    right-click inside the ROI  - pick a pixel; plots per-pixel counts along
                                  its row and column (cleared when the ROI
                                  changes)
    "Reset" button              - clears the counts-history plot
    "Save CSV" button           - writes the counts history to a timestamped
                                  CSV in the working directory
    histogram (left of the image) - drag the shaded region's edges to set
                                  black/white display levels; scroll to zoom,
                                  drag to pan (built into pyqtgraph)
    exposure slider              - live-adjusts real sensor exposure time
"""

import csv
import math
import os
import sys
import time
from collections import deque
from datetime import datetime

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

from ids_peak import ids_peak
from ids_peak import ids_peak_ipl_extension
from ids_peak_ipl import ids_peak_ipl

# ---------------------------------------------------------------------------
# Camera control and data-model code below is unchanged from ids_camera.py --
# none of it is UI-framework-specific.
# ---------------------------------------------------------------------------

# Packed IDS formats (e.g. Mono10g40IDS, Mono12g24IDS) can't be read
# directly as a numpy array; map their bit depth to the unpacked
# equivalent to convert to first.
_UNPACKED_MONO_BY_BITS = {
    8: ids_peak_ipl.PixelFormatName_Mono8,
    10: ids_peak_ipl.PixelFormatName_Mono10,
    12: ids_peak_ipl.PixelFormatName_Mono12,
}

MIN_ROI_SIZE_PX = 20  # an ROI resized smaller than this is clamped back up
COUNTS_HISTORY_WINDOW_S = 10.0  # default; adjustable live via the dial in the UI
COUNTS_HISTORY_WINDOW_MIN_S = 1.0
COUNTS_HISTORY_WINDOW_MAX_S = 120.0

# USB3 link throughput limit, in MB/s. Too low caps the achievable frame
# rate; too high exceeds what this camera's cable/port can sustain and
# corrupts frames (dark bands/grain). Find a safe value by editing this,
# rerunning, and checking the image -- raise it until corruption appears,
# then back off. None leaves the camera's current (persisted) value
# untouched. Applied once before streaming starts -- this node isn't
# writable while acquisition is running.
THROUGHPUT_LIMIT_MBPS = 200.0


def clamp(value, lo, hi):
    """Restricts `value` to the closed range [lo, hi]."""
    return max(lo, min(hi, value))


def open_first_device():
    """Finds the first IDS peak camera on the system and opens it with
    full (Control) access. Prints the access status first as a diagnostic:
    if something else already has the camera open (e.g. IDS Cockpit),
    that's visible here before the OpenDevice() call fails."""
    device_manager = ids_peak.DeviceManager.Instance()
    device_manager.Update()
    descriptors = device_manager.Devices()
    if len(descriptors) == 0:
        raise RuntimeError("No IDS peak device found. Is the camera connected and not open in Cockpit?")
    descriptor = descriptors[0]
    print(f"Device access status: {ids_peak.DeviceAccessStatusEnumEntryToString(descriptor.AccessStatus())}")
    return descriptor.OpenDevice(ids_peak.DeviceAccessType_Control)


def raise_frame_rate_to_max(nodemap, verbose=False):
    """Raises AcquisitionFrameRate to its current ceiling. That ceiling
    depends on ExposureTime (and throughput), so this must be re-run after
    every exposure change too -- otherwise the cap stays pinned to whatever
    ceiling applied at the time of the last call, and lowering exposure
    later won't actually unlock a higher frame rate."""
    try:
        rate_enable_node = nodemap.FindNode("AcquisitionFrameRateEnable")
        if verbose:
            print(f"AcquisitionFrameRateEnable: {rate_enable_node.Value()}")
        rate_enable_node.SetValue(False)
        return
    except ids_peak.Exception as exc:
        if verbose:
            print(f"AcquisitionFrameRateEnable not adjustable: {exc}")

    try:
        rate_node = nodemap.FindNode("AcquisitionFrameRate")
        if verbose:
            print(f"AcquisitionFrameRate: {rate_node.Value()} (max {rate_node.Maximum()})")
        rate_node.SetValue(rate_node.Maximum())
    except ids_peak.Exception as exc2:
        if verbose:
            print(f"AcquisitionFrameRate not adjustable: {exc2}")


def apply_throughput_limit(nodemap, limit_mbps):
    """Sets DeviceLinkThroughputLimit once, before streaming starts (the
    node isn't writable while acquisition is running). Too high a value
    exceeds what the USB3 link/cable can sustain and corrupts frames."""
    try:
        nodemap.FindNode("DeviceLinkThroughputLimitMode").SetCurrentEntry("On")
    except ids_peak.Exception as exc:
        print(f"DeviceLinkThroughputLimitMode not adjustable: {exc}")

    limit_node = nodemap.FindNode("DeviceLinkThroughputLimit")
    print(f"DeviceLinkThroughputLimit: {limit_node.Value()} (range {limit_node.Minimum()}-{limit_node.Maximum()})")

    if limit_mbps is not None:
        # Valid values must land exactly on Minimum + k*Increment.
        target_bps = limit_mbps * 1_000_000
        steps = round((target_bps - limit_node.Minimum()) / limit_node.Increment())
        target_bps = clamp(limit_node.Minimum() + steps * limit_node.Increment(),
                            limit_node.Minimum(), limit_node.Maximum())
        limit_node.SetValue(int(target_bps))
        print(f"DeviceLinkThroughputLimit set to {int(target_bps)} ({target_bps / 1e6:.1f} MB/s)")

    return limit_node


def configure_nodemap(nodemap, exposure_ms):
    """One-time camera setup, run before acquisition starts: clears a
    possibly-stuck parameter lock, disables auto-exposure/auto-gain (we
    drive exposure manually from the UI), applies the configured
    throughput limit and frame-rate ceiling, and sets the initial exposure
    time. Returns the ExposureTime and DeviceLinkThroughputLimit nodes so
    the caller can read/adjust them later."""
    # A previous abnormal exit can leave TLParamsLocked=1 on the device
    # itself (our cleanup only clears it via stop_acquisition(), which
    # never runs if the crash happened before acquisition started). Clear
    # it unconditionally so a stuck lock from an earlier crash doesn't
    # block writes to nodes like DeviceLinkThroughputLimit here.
    try:
        nodemap.FindNode("TLParamsLocked").SetValue(0)
    except ids_peak.Exception:
        pass

    try:
        nodemap.FindNode("ExposureAuto").SetCurrentEntry("Off")
    except ids_peak.Exception:
        pass
    try:
        nodemap.FindNode("GainAuto").SetCurrentEntry("Off")
    except ids_peak.Exception:
        pass

    # Must run before raise_frame_rate_to_max(): the achievable
    # AcquisitionFrameRate ceiling is itself constrained by the current
    # throughput limit, so raising throughput first means the frame-rate
    # cap gets lifted to the new (higher) ceiling instead of the old one.
    throughput_node = apply_throughput_limit(nodemap, THROUGHPUT_LIMIT_MBPS)
    raise_frame_rate_to_max(nodemap, verbose=True)

    exposure_node = nodemap.FindNode("ExposureTime")
    exposure_node.SetValue(clamp(exposure_ms * 1000.0, exposure_node.Minimum(), exposure_node.Maximum()))
    return exposure_node, throughput_node


def open_datastream(device):
    """Opens the GenTL stream module. Call once per session -- closing and
    reopening it repeatedly (e.g. to apply a setting that requires
    acquisition to be stopped) is unreliable on this SDK/driver. Use
    stop_acquisition()/start_acquisition() on the same DataStream instead."""
    return device.DataStreams()[0].OpenDataStream()


def start_acquisition(datastream, nodemap):
    """Allocates and queues the DataStream's buffers, locks the streaming
    parameters (resolution/pixel format can't change while they're
    locked), then starts acquisition on both the host (DataStream) and
    the camera itself (the AcquisitionStart command)."""
    payload_size = nodemap.FindNode("PayloadSize").Value()
    buffer_count = max(datastream.NumBuffersAnnouncedMinRequired(), 4)
    for _ in range(buffer_count):
        buffer = datastream.AllocAndAnnounceBuffer(payload_size)
        datastream.QueueBuffer(buffer)

    nodemap.FindNode("TLParamsLocked").SetValue(1)
    datastream.StartAcquisition()
    nodemap.FindNode("AcquisitionStart").Execute()
    nodemap.FindNode("AcquisitionStart").WaitUntilDone()


def stop_acquisition(nodemap, datastream):
    """Reverses start_acquisition(): stops the camera and the DataStream,
    releases the queued buffers, and unlocks the streaming parameters."""
    try:
        nodemap.FindNode("AcquisitionStop").Execute()
        nodemap.FindNode("AcquisitionStop").WaitUntilDone()
    except ids_peak.Exception:
        pass
    datastream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)
    datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)
    for buffer in datastream.AnnouncedBuffers():
        datastream.RevokeBuffer(buffer)
    try:
        nodemap.FindNode("TLParamsLocked").SetValue(0)
    except ids_peak.Exception:
        pass


def grab_raw_frame(datastream, converter, timeout_ms=2000):
    """Returns (raw, bits): raw is a native-bit-depth numpy array (for
    counts), bits is the sensor's significant bit depth (used to size the
    initial display levels)."""
    buffer = datastream.WaitForFinishedBuffer(timeout_ms)
    ipl_image = ids_peak_ipl_extension.BufferToImage(buffer)
    pixel_format = ipl_image.PixelFormat()
    bits = pixel_format.NumSignificantBitsPerChannel()
    if pixel_format.IsPacked():
        if bits not in _UNPACKED_MONO_BY_BITS:
            raise RuntimeError(f"No unpacked pixel format mapping for a {bits}-bit source format")
        # converter reuses pooled buffers across frames; ConvertTo would
        # allocate fresh memory every call and was the main frame-rate cost.
        ipl_image = converter.Convert(ipl_image, ids_peak_ipl.PixelFormat(_UNPACKED_MONO_BY_BITS[bits]))
    raw = ipl_image.get_numpy().copy()
    datastream.QueueBuffer(buffer)
    return raw, bits


class CountsHistory:
    """Rolling window of (timestamp, counts) samples for the live counts
    plot, pruned to the last `window_s` seconds. Time-based rather than a
    fixed sample count since fps varies a lot as exposure changes."""

    def __init__(self, window_s):
        self.window_s = window_s  # mutable at any time -- add() re-reads it every call
        self._samples = deque()

    def add(self, value):
        """Appends one (now, value) sample, then drops everything older
        than window_s seconds from the left of the deque."""
        now = time.perf_counter()
        self._samples.append((now, value))
        cutoff = now - self.window_s
        while self._samples and self._samples[0][0] < cutoff:
            self._samples.popleft()

    def values(self):
        """Just the counts, oldest first, with timestamps stripped."""
        return [v for _, v in self._samples]

    def samples(self):
        """The raw (timestamp, counts) pairs, oldest first -- used for the
        CSV export and for plotting against real elapsed time."""
        return list(self._samples)

    def clear(self):
        self._samples.clear()


def save_counts_csv(history, roi_rect):
    """Writes the current counts history to a timestamped CSV in the
    working directory: one row per sample, oldest first, with
    seconds_ago measured back from the moment of saving."""
    samples = history.samples()
    if not samples:
        print("No counts data to save yet.")
        return None

    now = time.perf_counter()
    path = os.path.abspath(datetime.now().strftime("counts_%Y%m%d_%H%M%S.csv"))
    roi_desc = f"{roi_rect[0]},{roi_rect[1]},{roi_rect[2]},{roi_rect[3]}" if roi_rect is not None else "full frame"

    with open(path, "w", newline="") as f:
        f.write(f"# roi: {roi_desc}\n")
        writer = csv.writer(f)
        writer.writerow(["seconds_ago", "counts"])
        for t, v in samples:
            writer.writerow([f"{now - t:.3f}", v])

    print(f"Saved {len(samples)} samples to {path}")
    return path


def percentile_range(raw, full_scale, low_pct=0.1, high_pct=99.9):
    """Returns a (lo, hi) value range covering [low_pct, high_pct] of raw's
    pixel value distribution. A plain min()/max() range is driven entirely
    by the single most extreme pixel -- one hot/dead pixel or a small
    saturated cluster can force it to span nearly the whole sensor range
    even though the real signal sits in a narrow band. Computed from a
    histogram's cumulative distribution (fast, vectorized) rather than
    sorting the full array. Used once at startup to seed sensible initial
    display levels."""
    counts, edges = np.histogram(raw, bins=full_scale + 1, range=(0, full_scale))
    cumulative = np.cumsum(counts)
    total = cumulative[-1]
    if total == 0:
        return 0.0, float(full_scale)
    lo_idx = np.searchsorted(cumulative, total * low_pct / 100.0)
    hi_idx = np.searchsorted(cumulative, total * high_pct / 100.0)
    lo = float(edges[lo_idx])
    hi = float(edges[min(hi_idx + 1, len(edges) - 1)])
    if hi <= lo:
        hi = lo + 1.0
    return lo, hi


def round_up_to_2sf(value):
    """Rounds `value` up (ceiling, not nearest) to 2 significant figures,
    e.g. 5,432,891 -> 5,500,000. Keeps the counts plot's y-axis maximum
    from jittering on tiny frame-to-frame fluctuations while guaranteeing
    it's never smaller than the actual data max (which would clip the
    plotted line)."""
    if value <= 0:
        return 1
    magnitude = 10 ** (math.floor(math.log10(value)) - 1)
    return int(math.ceil(value / magnitude) * magnitude)


# ---------------------------------------------------------------------------
# Acquisition thread -- WaitForFinishedBuffer() blocks for however long the
# current frame period is (which can be seconds at long exposures), so
# grabbing frames on the GUI thread would freeze the whole window. This
# thread just blocks on the SDK call and emits each frame via a Qt signal,
# which Qt automatically delivers to the main thread as a queued call.
#
# Queued signals aren't coalesced -- if the GUI thread takes longer to
# redraw the image + plots than the camera's frame period (easy at short
# exposure / high fps), frames queue up faster than they're consumed and
# the display falls further and further behind real time, which is
# exactly what makes live alignment tuning feel laggy/delayed. _gui_ready
# gates emission to one frame in flight at a time; anything captured while
# the GUI is still busy is dropped rather than queued, so the display
# always tracks the *latest* state instead of a growing backlog.
# ---------------------------------------------------------------------------

class AcquisitionThread(QtCore.QThread):
    frame_ready = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(str)

    def __init__(self, datastream, converter):
        super().__init__()
        self.datastream = datastream
        self.converter = converter
        self._running = True
        self._gui_ready = True

    def run(self):
        while self._running:
            try:
                raw, _bits = grab_raw_frame(self.datastream, self.converter)
            except ids_peak.Exception as exc:
                self.error.emit(str(exc))
                time.sleep(0.05)
                continue
            if self._gui_ready:
                self._gui_ready = False
                self.frame_ready.emit(raw)

    def mark_gui_ready(self):
        """Called by MainWindow once it's finished handling a frame, to
        allow the next one through."""
        self._gui_ready = True

    def stop(self):
        """Signals run() to exit and blocks until it does (with a timeout
        so a wedged camera call can't hang shutdown forever)."""
        self._running = False
        self.wait(2000)


class MainWindow(QtWidgets.QMainWindow):
    """The whole UI: camera view + ROI on the left, dashboard (exposure/
    window controls, stats, counts-history and profile plots) on the
    right. Owns the AcquisitionThread and does all the per-frame widget
    updates in on_frame()."""

    def __init__(self, nodemap, exposure_node, throughput_node, datastream, converter, full_scale):
        super().__init__()
        self.setWindowTitle("IDS camera live view")

        self.nodemap = nodemap
        self.exposure_node = exposure_node
        self.throughput_node = throughput_node
        self.full_scale = full_scale  # sensor's max representable pixel value (2**bits - 1)

        self.counts_history = CountsHistory(COUNTS_HISTORY_WINDOW_S)
        self.profile_point = None  # (col, row) in raw-array coords, or None if nothing picked
        self.last_roi_rect = None  # previous frame's ROI rect, to detect ROI changes
        self._last_shape = None  # (height, width) of the most recent frame
        self._levels_initialized = False  # have we seeded the histogram's black/white levels yet?
        self.fps = 0.0
        self.prev_time = time.perf_counter()

        self._build_ui()

        # Frames arrive via this signal, delivered on the GUI thread even
        # though they're captured on acq_thread (Qt queues cross-thread
        # signal/slot connections automatically).
        self.acq_thread = AcquisitionThread(datastream, converter)
        self.acq_thread.frame_ready.connect(self.on_frame)
        self.acq_thread.error.connect(lambda msg: print(f"Acquisition error: {msg}"))
        self.acq_thread.start()

    def _build_ui(self):
        """Builds the whole widget tree: image view + ROI + crosshair on
        the left, dashboard (stats, sliders, buttons, plots) on the
        right."""
        central = QtWidgets.QWidget()
        root = QtWidgets.QHBoxLayout(central)

        # --- Left: camera view ---
        self.image_view = pg.ImageView()
        self.image_view.ui.roiBtn.hide()  # ImageView's own 1D-profile ROI tool; we have our own 2D ROI
        self.image_view.ui.menuBtn.hide()
        root.addWidget(self.image_view, stretch=3)

        self.roi = pg.RectROI([50, 50], [150, 150], pen=pg.mkPen('g', width=2))
        self.roi.addScaleHandle([1, 1], [0, 0])
        self.roi.addScaleHandle([0, 0], [1, 1])
        self.roi.sigRegionChanged.connect(self._clamp_roi_size)
        # Right-click-inside-the-ROI is our profile-pick gesture, but ROI
        # items (and the ViewBox) claim right-click by default for their
        # own context menus -- that swallows the click before our
        # scene-level handler below ever sees it. Restrict the ROI to left
        # button only and disable the ViewBox menu so right-clicks fall
        # through to sigMouseClicked instead.
        self.roi.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.image_view.getView().setMenuEnabled(False)
        self.image_view.getView().addItem(self.roi)

        # Crosshair marking the picked profile pixel's row/column, drawn
        # directly on the camera image (angle=0 -> horizontal, angle=90 ->
        # vertical); hidden until a point is picked.
        self.row_line = pg.InfiniteLine(angle=0, pen=pg.mkPen('y', width=1))
        self.col_line = pg.InfiniteLine(angle=90, pen=pg.mkPen('y', width=1))
        self.row_line.hide()
        self.col_line.hide()
        self.image_view.getView().addItem(self.row_line)
        self.image_view.getView().addItem(self.col_line)

        self.image_view.getImageItem().scene().sigMouseClicked.connect(self.on_scene_clicked)

        # --- Right: dashboard ---
        dashboard = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(dashboard)

        # Live text readout: ROI counts/mean/max/dims, exposure, throughput
        # limit, fps -- refreshed every frame in on_frame().
        self.stats_label = QtWidgets.QLabel()
        self.stats_label.setStyleSheet("font-family: monospace;")
        self.stats_label.setWordWrap(True)
        vbox.addWidget(self.stats_label)

        # Real sensor exposure time, in microseconds (the node's native
        # unit) -- a plain integer slider is fine here since exposure
        # ranges always span far more than 1us, unlike some of the
        # coarser-grained trackbars in the old OpenCV version.
        exp_row = QtWidgets.QHBoxLayout()
        exp_row.addWidget(QtWidgets.QLabel("Exposure:"))
        self.exposure_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.exposure_slider.setMinimum(int(self.exposure_node.Minimum()))
        self.exposure_slider.setMaximum(int(self.exposure_node.Maximum()))
        self.exposure_slider.setValue(int(self.exposure_node.Value()))
        self.exposure_slider.valueChanged.connect(self.on_exposure_changed)
        exp_row.addWidget(self.exposure_slider)
        vbox.addLayout(exp_row)

        # How far back the counts-history plot below looks, in seconds.
        self.window_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        window_row = QtWidgets.QHBoxLayout()
        window_row.addWidget(QtWidgets.QLabel("Window (s):"))
        self.window_slider.setMinimum(int(COUNTS_HISTORY_WINDOW_MIN_S))
        self.window_slider.setMaximum(int(COUNTS_HISTORY_WINDOW_MAX_S))
        self.window_slider.setValue(int(COUNTS_HISTORY_WINDOW_S))
        self.window_slider.valueChanged.connect(self.on_window_changed)
        window_row.addWidget(self.window_slider)
        self.window_label = QtWidgets.QLabel(f"{COUNTS_HISTORY_WINDOW_S:.0f}s")
        window_row.addWidget(self.window_label)
        vbox.addLayout(window_row)

        # ROI (or full-frame) total counts over time -- the "loading
        # curve" plot. X-axis left to auto-fit (see on_frame()); Y-axis is
        # pinned each frame to keep some headroom above the current max.
        self.counts_plot = pg.PlotWidget(title=f"Counts history (last {COUNTS_HISTORY_WINDOW_S:.0f}s)")
        self.counts_plot.setLabel('bottom', 'seconds ago')
        self.counts_plot.enableAutoRange(axis='x')
        self.counts_curve = self.counts_plot.plot(pen=pg.mkPen('g', width=1))
        vbox.addWidget(self.counts_plot, stretch=2)

        btn_row = QtWidgets.QHBoxLayout()
        reset_btn = QtWidgets.QPushButton("Reset")
        reset_btn.clicked.connect(self.counts_history.clear)
        save_btn = QtWidgets.QPushButton("Save CSV")
        save_btn.clicked.connect(self.on_save_csv)
        btn_row.addWidget(reset_btn)
        btn_row.addWidget(save_btn)
        vbox.addLayout(btn_row)

        # Per-pixel counts along the picked profile point's row/column
        # (see on_scene_clicked() and the crosshair above); empty until a
        # point is picked.
        self.row_profile_plot = pg.PlotWidget(title="Row profile")
        self.row_profile_curve = self.row_profile_plot.plot(pen=pg.mkPen('c', width=1))
        vbox.addWidget(self.row_profile_plot, stretch=1)

        self.col_profile_plot = pg.PlotWidget(title="Column profile")
        self.col_profile_curve = self.col_profile_plot.plot(pen=pg.mkPen('c', width=1))
        vbox.addWidget(self.col_profile_plot, stretch=1)

        root.addWidget(dashboard, stretch=2)

        self.setCentralWidget(central)
        self.resize(1400, 800)

    def _clamp_roi_size(self):
        """Connected to the ROI's sigRegionChanged -- if a resize drags it
        below the minimum, push it back up immediately rather than letting
        it shrink to a degenerate size."""
        size = self.roi.size()
        w, h = size.x(), size.y()
        new_w, new_h = max(MIN_ROI_SIZE_PX, w), max(MIN_ROI_SIZE_PX, h)
        if (new_w, new_h) != (w, h):
            self.roi.setSize([new_w, new_h])

    def _current_roi_rect(self):
        """Returns (col0, row0, w, h) in raw-array coordinates, clamped to
        the last displayed frame's bounds, or None if no frame yet."""
        if self._last_shape is None:
            return None
        height, width = self._last_shape
        pos = self.roi.pos()
        size = self.roi.size()
        col0 = int(clamp(pos.x(), 0, width))
        row0 = int(clamp(pos.y(), 0, height))
        w = int(clamp(size.x(), MIN_ROI_SIZE_PX, width - col0))
        h = int(clamp(size.y(), MIN_ROI_SIZE_PX, height - row0))
        return col0, row0, w, h

    def on_scene_clicked(self, event):
        """Right-click-inside-the-ROI profile-pick gesture. Left clicks
        (draw/move/resize the ROI) are handled entirely by pg.RectROI
        itself and never reach here."""
        if event.button() != QtCore.Qt.RightButton:
            return
        roi_rect = self._current_roi_rect()
        if roi_rect is None:
            return
        view_pos = self.image_view.getView().mapSceneToView(event.scenePos())
        col, row = int(view_pos.x()), int(view_pos.y())
        col0, row0, w, h = roi_rect
        if col0 <= col < col0 + w and row0 <= row < row0 + h:
            self.profile_point = (col, row)

    def on_exposure_changed(self, value_us):
        """Exposure slider callback: pushes the new value to the camera
        and re-raises the frame-rate ceiling, which depends on exposure
        (see raise_frame_rate_to_max())."""
        value_us = clamp(float(value_us), self.exposure_node.Minimum(), self.exposure_node.Maximum())
        self.exposure_node.SetValue(value_us)
        raise_frame_rate_to_max(self.nodemap)

    def on_save_csv(self):
        save_counts_csv(self.counts_history, self._current_roi_rect())

    def on_window_changed(self, value):
        """Window-length slider callback: CountsHistory.add() re-reads
        window_s on every call, so just updating the attribute here is
        enough to take effect immediately."""
        self.counts_history.window_s = float(value)
        self.window_label.setText(f"{value}s")
        self.counts_plot.setTitle(f"Counts history (last {value}s)")

    def on_frame(self, raw):
        """The main per-frame update: runs once for every frame the
        acquisition thread delivers. Updates the fps estimate, the image
        display, the ROI stats/label, the counts-history plot, and the
        row/column profile plots (if a point is picked), in that order.

        try/finally: mark_gui_ready() must always run, even if something
        below raises, or a single bad frame would permanently stall the
        acquisition thread (see AcquisitionThread -- it never emits again
        once _gui_ready is False)."""
        try:
            now = time.perf_counter()
            dt = now - self.prev_time
            self.prev_time = now
            if dt > 0:
                instant_fps = 1.0 / dt
                self.fps = instant_fps if self.fps == 0.0 else (0.9 * self.fps + 0.1 * instant_fps)

            self._last_shape = raw.shape  # (height, width)

            # pyqtgraph's image axes are (x, y); raw is (row, col) = (y, x), so
            # transpose. autoLevels/autoRange False so the user's dragged levels
            # and zoom/pan aren't reset every frame; autoHistogramRange only on
            # the very first frame for a sensible initial view (see module
            # docstring re: not fighting a manual histogram zoom every frame).
            first_frame = not self._levels_initialized
            self.image_view.setImage(raw.T, autoLevels=False, autoRange=first_frame,
                                      autoHistogramRange=first_frame)
            if first_frame:
                self.image_view.setLevels(*percentile_range(raw, self.full_scale))
                self._levels_initialized = True

            roi_rect = self._current_roi_rect()
            if roi_rect != self.last_roi_rect:
                self.counts_history.clear()
                self.profile_point = None
                self.last_roi_rect = roi_rect

            col0, row0, w, h = roi_rect
            region = raw[row0:row0 + h, col0:col0 + w]
            total_counts = int(region.sum())
            roi_desc = (f"ROI counts: {total_counts}  mean: {region.mean():.1f}  max: {region.max()}  "
                        f"dims: {w}x{h} @ ({col0},{row0})")

            self.counts_history.add(total_counts)

            self.stats_label.setText(
                f"{roi_desc}\n"
                f"exposure: {self.exposure_node.Value() / 1000.0:.2f} ms   "
                f"throughput limit: {self.throughput_node.Value() / 1e6:.1f} MB/s   "
                f"{self.fps:.1f} fps"
            )

            # Plot against actual elapsed time, not sample index -- fps
            # varies a lot with exposure, so a fixed number of samples
            # doesn't correspond to a fixed time span. Let the x-axis
            # auto-fit to whatever's actually been collected so far
            # (capped at COUNTS_HISTORY_WINDOW_S by CountsHistory's own
            # pruning) rather than pinning it to a fixed [-60, 0] window --
            # a fixed window leaves most of the plot empty right after a
            # reset, whereas auto-fitting stretches whatever recent data
            # exists across the full plot width, making small/recent
            # changes much easier to see.
            history_samples = self.counts_history.samples()
            if len(history_samples) >= 2:
                xs = [t - now for t, _ in history_samples]
                values = [v for _, v in history_samples]
                self.counts_curve.setData(xs, values)
                self.counts_plot.setYRange(0, round_up_to_2sf(max(values) * 1.5))

            if self.profile_point is not None:
                px, py = self.profile_point
                row_profile = raw[py, col0:col0 + w]
                col_profile = raw[row0:row0 + h, px]
                self.row_profile_curve.setData(row_profile)
                self.col_profile_curve.setData(col_profile)
                self.row_profile_plot.setTitle(f"Row profile (y={py})")
                self.col_profile_plot.setTitle(f"Column profile (x={px})")
                self.row_line.setPos(py)
                self.col_line.setPos(px)
                self.row_line.show()
                self.col_line.show()
            else:
                self.row_profile_curve.setData([])
                self.col_profile_curve.setData([])
                self.row_profile_plot.setTitle("Row profile")
                self.col_profile_plot.setTitle("Column profile")
                self.row_line.hide()
                self.col_line.hide()
        finally:
            self.acq_thread.mark_gui_ready()

    def closeEvent(self, event):
        """Qt calls this when the window is closing; stop the acquisition
        thread first so it isn't left running against a datastream that
        main() is about to tear down."""
        self.acq_thread.stop()
        super().closeEvent(event)


def main():
    # Library.Initialize()/Close() bracket the whole SDK session; the try
    # below owns device/datastream/window so the finally block can clean
    # up whichever of them actually got created, regardless of where
    # startup failed.
    ids_peak.Library.Initialize()
    app = QtWidgets.QApplication(sys.argv)

    device = None
    datastream = None
    window = None
    exit_code = 1
    try:
        device = open_first_device()
        node_maps = device.RemoteDevice().NodeMaps()
        if len(node_maps) == 0:
            raise RuntimeError(
                "Device opened but has no node maps -- its GenICam description "
                "didn't load. This usually means the camera/driver is in a wedged "
                "state (e.g. after an abnormal exit). Try: closing any other "
                "process/Cockpit instance holding the camera, unplugging and "
                "replugging the USB3 cable, then retrying."
            )
        nodemap = node_maps[0]
        # Initial exposure of 10ms is just a starting point -- the UI
        # slider takes over from here.
        exposure_node, throughput_node = configure_nodemap(nodemap, 10.0)
        datastream = open_datastream(device)
        start_acquisition(datastream, nodemap)
        converter = ids_peak_ipl.ImageConverter()

        # One synchronous grab before the GUI/acquisition thread exist, just
        # to learn the sensor's bit depth (full_scale) for seeding the
        # histogram's initial levels.
        seed_raw, bits = grab_raw_frame(datastream, converter)
        full_scale = (1 << bits) - 1

        window = MainWindow(nodemap, exposure_node, throughput_node, datastream, converter, full_scale)
        window.show()
        exit_code = app.exec_()  # blocks until the window is closed
    finally:
        # Tear down in reverse order of creation, tolerating any of these
        # having failed to get created in the first place.
        if window is not None:
            window.acq_thread.stop()
        if device is not None and datastream is not None:
            try:
                stop_acquisition(device.RemoteDevice().NodeMaps()[0], datastream)
            except Exception:
                pass
        ids_peak.Library.Close()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
