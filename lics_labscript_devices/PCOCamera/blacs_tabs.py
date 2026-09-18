import json
import numpy as np
from time import perf_counter

import h5py
import labscript_utils.properties
import pyqtgraph as pg

from qtutils import inmain_decorator
from qtutils.qt import QtCore, QtWidgets

from blacs.tab_base_classes import define_state, MODE_MANUAL
from labscript_devices.IMAQdxCamera.blacs_tabs import IMAQdxCameraTab, ImageReceiver, exp_av
from lics_labscript_devices.PCOCamera.absorption_analysis import CONV_UM_PER_PIX

# Colorbar limits are stored per group rather than per frame -- Light and Atoms share
# units (raw camera counts) and are typically compared at the same scale.
_COLORBAR_GROUPS = ['Dark', 'Light/Atoms', 'OD', 'Density']


def _colorbar_group(frame_name):
    return 'Light/Atoms' if frame_name in ('Light', 'Atoms') else frame_name


def _style_colorbar_like_matplotlib(hist_item, hist_widget=None):
    """Narrow the LUT viewbox and load a colored gradient preset (pyqtgraph's own default
    is a plain black-to-white 'grey' one), so a pg.HistogramLUTItem reads closer to
    matplotlib's standard colorbar -- a colored gradient bar with tick labels -- instead
    of pyqtgraph's plain default grey one, while keeping its usual data-histogram trace
    (showing the pixel-value distribution) alongside it. Stays fully interactive (levels
    still draggable) and pyqtgraph-native throughout (no matplotlib resize lag). Applied
    to every PCO view that has a colorbar: self.image's built-in one (Live/Dark/Light/
    Atoms/OD, since they all share that one pg.ImageView) and the Density panel's own.

    Called again, unconditionally, after restore_save_data() -- a previously-*persisted*
    gradient (e.g. 'grey', saved back before this default existed) would otherwise win
    over this one, since restore runs after the initial call in initialise_GUI."""
    hist_item.vb.setMaximumWidth(30)
    hist_item.vb.setMinimumWidth(20)
    if hist_widget is not None:
        hist_widget.setMinimumWidth(60)
    hist_item.gradient.loadPreset('viridis')
    # The gradient itself has its own triangular tick handles (one per colour stop -- 5
    # for viridis) for interactively editing the colour map; not needed, since the map is
    # fixed to viridis. The level-region's own drag-handle markers (on the two thin lines)
    # are left alone -- those are the actual level-dragging affordance and are wanted.
    hist_item.gradient.showTicks(False)


class _AbsorptionDisplay:
    """Renders 'absorption' display_mode frames using pyqtgraph throughout, so the UI
    stays fast and responsive when resized (unlike matplotlib) and keeps the familiar
    draggable histogram/LUT colorbar.

    Dark/Light/Atoms/OD are shown by reusing the tab's existing pg.ImageView -- the same
    widget 'live' mode uses -- which already has a fast-updating image and a draggable
    histogram colorbar built in, so there's nothing extra to build for those.

    Density needs linked x/y integrated-density-profile + Gaussian-fit-overlay plots
    alongside the image (the pyqtgraph equivalent of absorption_image_analysis.py's
    density panel), which pg.ImageView alone doesn't provide, so it gets its own
    pg.GraphicsLayoutWidget with a HistogramLUTItem colorbar of its own."""

    # Fixed chrome sizes (px) for axes shared between two plots that are linked but not
    # otherwise forced to the same pixel geometry by pyqtgraph. Without this, yprof_plot's
    # bottom axis labels (which density_plot's hidden bottom axis doesn't have) would eat
    # a different amount of space from their own plot's cell, so even with a linked Y
    # range the two viewports end up different pixel heights -- the same data position
    # then lands at different pixel offsets in each, i.e. they don't visually line up.
    _SHARED_BOTTOM_AXIS_HEIGHT = 30
    _SHARED_LEFT_AXIS_WIDTH = 50

    # Fit results shown in the table below the plots, in display order. Matches the
    # attributes PCOCameraWorker attaches to the saved 'density' image dataset (a
    # sibling of dark/light/atoms) and logs under 'results/live_image_analysis', so
    # what's on screen matches what's in the shot file (and the lyse dataframe).
    _RESULT_COLUMNS = [
        ('N', '{:.3e}'), ('N_x', '{:.3e}'), ('N_y', '{:.3e}'),
        ('sigma_x (um)', '{:.1f}'), ('sigma_y (um)', '{:.1f}'),
        ('x0_x (um)', '{:.1f}'), ('x0_y (um)', '{:.1f}'),
    ]

    def __init__(self, image_view):
        self.image_view = image_view  # tab's pg.ImageView; reused for non-Density frames
        # True while show_frame()/show_density() are programmatically setting levels
        # (Auto mode's auto-computed levels, or applying a stored manual Min/Max), so the
        # tab's sigLevelsChanged handler can tell that apart from an actual user drag on
        # the colorbar (pyqtgraph fires the same signal for both).
        self.suppress_level_signal = False
        # Force 1:1 aspect ratio (equal x/y scale) so images are never stretched/squished
        # to fill the panel -- applies to Dark/Light/Atoms/OD (self.image_view) and Live
        # mode alike, since they all share this same view.
        self.image_view.getView().setAspectLocked(True)

        self.density_widget = pg.GraphicsLayoutWidget()

        self.yprof_plot = self.density_widget.addPlot(row=0, col=0)
        self.density_plot = self.density_widget.addPlot(row=0, col=1)
        self.density_hist = pg.HistogramLUTItem()
        _style_colorbar_like_matplotlib(self.density_hist)
        self.density_widget.addItem(self.density_hist, row=0, col=2)
        self.xprof_plot = self.density_widget.addPlot(row=1, col=1)

        self.density_img = pg.ImageItem()
        self.density_plot.addItem(self.density_img)
        self.density_hist.setImageItem(self.density_img)
        self.density_plot.showGrid(x=False, y=False)
        # 1:1 aspect ratio for the density image too; xprof_plot/yprof_plot are 1D
        # profiles (value vs. position) so aspect-locking them wouldn't make sense.
        self.density_plot.setAspectLocked(True)
        # density_plot shares its bottom axis with xprof_plot's (position, μm) and its
        # left axis with yprof_plot's (position, μm); showing its own duplicate tick
        # labels would be redundant, so hide the text (but keep the axis line/ticks and
        # -- crucially -- a fixed height/width matching its shared-axis neighbour).
        axis_bottom = self.density_plot.getAxis('bottom')
        axis_bottom.setStyle(showValues=False)
        axis_bottom.setHeight(self._SHARED_BOTTOM_AXIS_HEIGHT)
        axis_left = self.density_plot.getAxis('left')
        axis_left.setStyle(showValues=False)
        axis_left.setWidth(self._SHARED_LEFT_AXIS_WIDTH)

        self.xprof_plot.setXLink(self.density_plot)
        self.xprof_plot.setLabel('bottom', 'x (μm)')
        self.xprof_plot.getAxis('left').setWidth(self._SHARED_LEFT_AXIS_WIDTH)
        self.xprof_scatter = pg.ScatterPlotItem(size=4, pen=None, brush=pg.mkBrush(100, 100, 255, 150))
        self.xprof_plot.addItem(self.xprof_scatter)
        self.xprof_fit = self.xprof_plot.plot(pen=pg.mkPen('r', width=2))

        self.yprof_plot.setYLink(self.density_plot)
        self.yprof_plot.setLabel('left', 'y (μm)')
        self.yprof_plot.getAxis('bottom').setHeight(self._SHARED_BOTTOM_AXIS_HEIGHT)
        self.yprof_scatter = pg.ScatterPlotItem(size=4, pen=None, brush=pg.mkBrush(100, 100, 255, 150))
        self.yprof_plot.addItem(self.yprof_scatter)
        self.yprof_fit = self.yprof_plot.plot(pen=pg.mkPen('r', width=2))

        layout = self.density_widget.ci.layout
        layout.setRowStretchFactor(0, 5)
        layout.setRowStretchFactor(1, 1)
        layout.setColumnStretchFactor(0, 1)
        layout.setColumnStretchFactor(1, 5)
        layout.setColumnStretchFactor(2, 1)

        # Fit-results table -- vertical (one row per result), since it's placed by the
        # tab as a narrow sidebar next to its other controls rather than as its own
        # full-width row (see PCOCameraTab.initialise_GUI). Built here, alongside the
        # plots it summarizes, but not part of density_widget/container -- the tab shows/
        # hides it separately, in step with density_widget.
        self.results_table = QtWidgets.QTableWidget(len(self._RESULT_COLUMNS), 1)
        self.results_table.setVerticalHeaderLabels([name for name, _ in self._RESULT_COLUMNS])
        self.results_table.horizontalHeader().hide()
        self.results_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.results_table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.results_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        # Wide enough for the widest value this table ever shows -- the '{:.3e}' columns
        # (N/N_x/N_y), e.g. '-1.234e+05' -- with a couple of px to spare. A previous fixed
        # width of 130px here was too narrow for this data column *on top of* the row-
        # label column ('sigma_x (um)' etc.), so values were being truncated internally
        # (e.g. '4.224e+05' rendering as just '4.224').
        self.results_table.setColumnWidth(0, 72)
        for row in range(len(self._RESULT_COLUMNS)):
            item = QtWidgets.QTableWidgetItem('—')
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.results_table.setItem(row, 0, item)
        # QTableWidget defaults to an Expanding vertical size policy, so without this it
        # stretches to match whatever height its layout neighbour (the taller controls
        # column) ends up with, leaving a lot of blank space below the 7 actual rows.
        self.results_table.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        table_height = 2 * self.results_table.frameWidth()
        for row in range(self.results_table.rowCount()):
            table_height += self.results_table.rowHeight(row)
        self.results_table.setFixedHeight(table_height)
        # Width from the *actual* row-label column width (auto-sized to fit labels like
        # 'sigma_x (um)' via ResizeToContents above) plus the data column width just set,
        # rather than a guessed total that can either clip values or waste space.
        # verticalHeader().width() doesn't reflect its ResizeToContents-computed size
        # until the table has actually been laid out/shown at least once -- sizeHint()
        # gives the right content-based value immediately, before that first show.
        table_width = (
            2 * self.results_table.frameWidth()
            + self.results_table.verticalHeader().sizeHint().width()
            + self.results_table.columnWidth(0)
        )
        self.results_table.setFixedWidth(table_width)
        self.results_table.hide()

        # container is what the tab shows/hides and adds to its layout; there's nothing
        # else to wrap it with now that results_table lives elsewhere.
        self.container = self.density_widget
        self.container.hide()

        self._placeholder = pg.TextItem("Waiting for next shot…", color='gray', anchor=(0.5, 0.5))
        self._placeholder.hide()
        self.image_view.getView().addItem(self._placeholder)

    def show_placeholder(self, text="Waiting for next shot…"):
        self.container.hide()
        self.results_table.hide()
        self.image_view.show()
        self.image_view.clear()
        self._placeholder.setText(text)
        self._placeholder.show()

    def show_frame(self, name, image, vmin=None, vmax=None):
        self._placeholder.hide()
        self.container.hide()
        self.results_table.hide()  # only meaningful for Density; see show_density()
        self.image_view.show()
        first = self.image_view.image is None
        # setImage() re-sets the histogram's level region every time regardless of
        # autoLevels (see HistogramLUTItem.imageChanged()), which fires sigLevelsChanged
        # -- suppress the tab's handler for it here, so a programmatic level change isn't
        # mistaken for the user dragging the colorbar.
        self.suppress_level_signal = True
        try:
            if vmin is not None and vmax is not None:
                self.image_view.setImage(
                    image.swapaxes(-1, -2), autoRange=first, autoLevels=False, levels=(vmin, vmax)
                )
            else:
                self.image_view.setImage(image.swapaxes(-1, -2), autoRange=first, autoLevels=True)
        finally:
            self.suppress_level_signal = False

    def show_density(self, image, x_int, y_int, x_dist, y_dist, N, results,
                      span_x=None, span_y=None, vmin=None, vmax=None):
        self._placeholder.hide()
        self.image_view.hide()
        self.container.show()
        self.results_table.show()

        conv = CONV_UM_PER_PIX
        h, w = image.shape
        # span_x/span_y come from the worker's full_analysis() call and are sized to
        # match the actual (possibly Save-ROI-cropped) image, not necessarily the full
        # 2048x2048 sensor; fall back to computing them here only if not provided (e.g.
        # a caller invoking show_density() directly).
        if span_x is None:
            span_x = np.linspace(0, w * conv, w)
        if span_y is None:
            span_y = np.linspace(0, h * conv, h)
        # setImage()/setLevels() fire sigLevelsChanged regardless of whether this is a
        # programmatic level change or a user drag -- suppress_level_signal (see
        # show_frame()) distinguishes the two for the tab's drag handler.
        self.suppress_level_signal = True
        try:
            self.density_img.setImage(image.swapaxes(-1, -2), autoLevels=False)
            self.density_img.setRect(QtCore.QRectF(0, 0, w * conv, h * conv))
            if vmin is not None and vmax is not None:
                lo, hi = vmin, vmax
            else:
                lo, hi = float(np.nanmin(image)), float(np.nanmax(image))
                if lo == hi:
                    hi = lo + 1.0
            self.density_hist.setLevels(lo, hi)
        finally:
            self.suppress_level_signal = False

        results = results or {}
        for row, (key, fmt) in enumerate(self._RESULT_COLUMNS):
            value = results.get(key)
            # NaN (not just None) means "no value" here too -- full_analysis() reports
            # every fit-derived result as NaN when called with fit=False (Fits
            # unchecked in the tab), rather than omitting the keys.
            is_missing = value is None or (isinstance(value, float) and np.isnan(value))
            self.results_table.item(row, 0).setText('—' if is_missing else fmt.format(value))

        x_int = np.asarray(x_int)
        y_int = np.asarray(y_int)
        self.xprof_scatter.setData(span_x, x_int / conv)
        self.xprof_fit.setData(span_x, x_dist)
        self.yprof_scatter.setData(y_int / conv, span_y)
        self.yprof_fit.setData(y_dist, span_y)


class _PCOImageReceiver(ImageReceiver):
    """Like ImageReceiver but keeps the histogram x-axis fixed after the first frame
    so the min/max level handles don't visually drift during continuous acquisition.

    Also understands "named frames" messages (sent by PCOCameraWorker whenever its
    display_mode is 'absorption'): several same-shaped images (Dark/Light/Atoms/OD/
    Density) plus profile/fit data arrive in one message, and are rendered via
    `display` (an _AbsorptionDisplay). Which branch is used is decided purely by
    whether a given message carries frame_names, so this doesn't need to know the tab's
    current display_mode selection; the tab can switch which frame is shown locally via
    set_selected_frame() without asking the worker again."""

    def __init__(self, image_view, label_fps, display=None, colorbar_limits=None):
        super().__init__(image_view, label_fps)
        self._frame_callback = None
        self.frames_by_name = {}
        self.profile_data = {}
        self.selected_frame = None
        self.display = display
        # Shared dict (same object the tab's colorbar controls mutate), keyed by
        # _colorbar_group() name, e.g. {'auto': False, 'vmin': 0.0, 'vmax': 1.0}.
        self.colorbar_limits = colorbar_limits if colorbar_limits is not None else {}

    def set_selected_frame(self, name):
        """Switch which of the most recently received named frames is displayed."""
        self.selected_frame = name
        if name in self.frames_by_name:
            self._render(name)

    def _render(self, name):
        image = self.frames_by_name[name]
        limits = self.colorbar_limits.get(_colorbar_group(name))
        if limits and not limits.get('auto', True):
            vmin, vmax = limits['vmin'], limits['vmax']
        else:
            vmin = vmax = None
        if name == 'Density':
            self.display.show_density(image, vmin=vmin, vmax=vmax, **self.profile_data)
        else:
            self.display.show_frame(name, image, vmin=vmin, vmax=vmax)
        if self._frame_callback is not None:
            try:
                self._frame_callback()
            except Exception:
                pass

    def _show(self, image, autolevel):
        first = self.image_view.image is None
        self.image_view.setImage(
            image.swapaxes(-1, -2),
            autoRange=first,
            autoLevels=autolevel,
            autoHistogramRange=autolevel,
        )

    @inmain_decorator(wait_for_return=True)
    def handler(self, data):
        self.send([b'ok'])
        md = json.loads(data[0])
        image = np.frombuffer(memoryview(data[1]), dtype=md['dtype'])
        image = image.reshape(md['shape'])
        this_frame_time = perf_counter()
        if self.last_frame_time is not None:
            dt = this_frame_time - self.last_frame_time
            if self.frame_rate is not None:
                self.frame_rate = exp_av(self.frame_rate, 1 / dt, dt, 1.0)
            else:
                self.frame_rate = 1 / dt
        self.last_frame_time = this_frame_time
        if self.frame_rate is not None:
            self.label_fps.setText(f"{self.frame_rate:.01f} fps")

        frame_names = md.get('frame_names')
        if frame_names:
            # Absorption-mode message: Dark/Light/Atoms/OD/Density + profile/fit data.
            self.frames_by_name = {name: image[i] for i, name in enumerate(frame_names)}
            self.profile_data = {
                'x_int': md.get('x_int'),
                'y_int': md.get('y_int'),
                'x_dist': md.get('x_dist'),
                'y_dist': md.get('y_dist'),
                'span_x': md.get('span_x'),
                'span_y': md.get('span_y'),
                'N': md.get('N'),
                'results': md.get('results'),
            }
            name = self.selected_frame if self.selected_frame in self.frames_by_name else frame_names[0]
            self.selected_frame = name
            self._render(name)
        else:
            self.frames_by_name = {}
            if len(image.shape) == 3 and image.shape[0] == 1:
                image = image.reshape(image.shape[1:])
            self._show(image, autolevel=self.image_view.image is None)
            if self._frame_callback is not None:
                try:
                    self._frame_callback()
                except Exception:
                    pass

        QtWidgets.QApplication.instance().sendPostedEvents()
        return self.NO_RESPONSE


class PCOCameraTab(IMAQdxCameraTab):
    worker_class = 'lics_labscript_devices.PCOCamera.blacs_workers.PCOCameraWorker'

    def initialise_GUI(self):
        super().initialise_GUI()

        # self.image is shared by Live/Dark/Light/Atoms/OD, so this one call styles the
        # colorbar for all of them at once; Density's own colorbar is styled where it's
        # built, in _AbsorptionDisplay.__init__.
        _style_colorbar_like_matplotlib(self.image.ui.histogram.item, self.image.ui.histogram)

        # Read initial exposure from the connection table HDF5 so the spinbox starts at
        # the value the camera will actually be using. display_mode is no longer a
        # connection table property -- it's switched live from the dropdown below and
        # defaults to 'live' (persisted across BLACS restarts via get/restore_save_data).
        exposure_ms_init = 50.0
        try:
            table = self.settings['connection_table']
            ct_props = table.find_by_name(self.device_name).properties
            with h5py.File(table.filepath, 'r') as f:
                dev_props = labscript_utils.properties.get(f, self.device_name, 'device_properties')
            attrs = {**dev_props.get('camera_attributes', {}),
                     **ct_props.get('manual_mode_camera_attributes', {})}
            if 'exposure_time' in attrs:
                exposure_ms_init = attrs['exposure_time'] * 1000.0
        except Exception:
            pass

        # Renders 'absorption' display_mode frames. Dark/Light/Atoms/OD reuse self.image
        # (the fast pg.ImageView with its draggable histogram colorbar, same widget 'live'
        # mode uses); Density gets its own linked-profile-plots widget, added alongside.
        self._absorption_display = _AbsorptionDisplay(self.image)
        self.ui.horizontalLayout.addWidget(self._absorption_display.container)

        # Colorbar limits, stored per group (Dark / Light+Atoms / OD / Density) so each
        # remembers its own manual min/max independently of which frame is shown.
        self._colorbar_limits = {
            group: {'auto': True, 'vmin': 0.0, 'vmax': 1.0} for group in _COLORBAR_GROUPS
        }

        # Replace the default ImageReceiver with one that keeps the histogram range fixed
        # and can render absorption-mode frames. Must happen before initialise_workers()
        # reads self.image_receiver.port.
        self.image_receiver.shutdown()
        self.image_receiver = _PCOImageReceiver(
            self.image, self.ui.label_fps,
            display=self._absorption_display, colorbar_limits=self._colorbar_limits,
        )

        # The Attributes/Snap/Continuous/Stop toolbar column (left of the image in
        # blacs_tab.ui) only does anything useful in 'live' mode -- Snap/Continuous write
        # single raw frames into self.image, which would clobber whatever absorption
        # frame is currently shown there. Some of these widgets have
        # setRetainSizeWhenHidden(True) set by the base class (to stop the layout jumping
        # around during live-mode acquisition toggles); undo that so the whole column
        # actually collapses to zero width when hidden in absorption mode.
        self._toolbar_widgets = [
            self.ui.pushButton_attributes,
            self.ui.pushButton_snap,
            self.ui.pushButton_continuous,
            self.ui.pushButton_stop,
            self.ui.doubleSpinBox_maxrate,
            self.ui.toolButton_nomax,
            self.ui.label_fps,
        ]
        for widget in self._toolbar_widgets:
            size_policy = widget.sizePolicy()
            if hasattr(size_policy, 'setRetainSizeWhenHidden'):
                size_policy.setRetainSizeWhenHidden(False)
                widget.setSizePolicy(size_policy)

        # All the narrow control rows below go into this column, which sits to the left
        # of the (Density-only) results table rather than each row spanning the tab's
        # full width with the table as its own row underneath -- saves vertical space.
        controls_widget = QtWidgets.QWidget()
        controls_col = QtWidgets.QVBoxLayout()
        controls_col.setContentsMargins(4, 4, 4, 4)
        controls_col.setSpacing(6)
        controls_widget.setLayout(controls_col)

        def _row(*row_widgets):
            """A single control row: the given widgets laid out left to right, packed
            tightly together, with the rest of the row's horizontal space left as
            passive trailing blank (via addStretch()) rather than distributed *between*
            widgets -- every row in this column is built this way so they all pack the
            same way and line up left-aligned underneath each other."""
            row_widget = QtWidgets.QWidget()
            row = QtWidgets.QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)
            row_widget.setLayout(row)
            for w in row_widgets:
                row.addWidget(w)
            row.addStretch()
            controls_col.addWidget(row_widget)
            return row_widget

        # --- display-mode switcher ---
        self._mode_selector = QtWidgets.QComboBox()
        self._mode_selector.addItems(['Live', 'Absorption'])
        self._mode_selector.setToolTip(
            "Live: normal live camera viewer.\n"
            "Absorption: after each shot, compute and show the OD/Density image from "
            "that shot's dark/light/atoms frames, with live x/y profile fits."
        )
        self._mode_selector.currentTextChanged.connect(self._on_display_mode_selected)
        _row(QtWidgets.QLabel("Display mode:"), self._mode_selector)

        # --- exposure (hidden in absorption mode; those shots use exposure_time from
        # the connection table's camera_attributes, not a manually-set live value) ---
        self._exposure_spinbox = QtWidgets.QDoubleSpinBox()
        self._exposure_spinbox.setRange(0.001, 10000.0)
        self._exposure_spinbox.setDecimals(3)
        self._exposure_spinbox.setValue(exposure_ms_init)
        self._exposure_spinbox.setFixedWidth(90)
        btn_exp = QtWidgets.QPushButton("Apply Exposure")
        btn_exp.clicked.connect(self._on_apply_exposure)
        self._exposure_widget = _row(
            QtWidgets.QLabel("Exposure (ms):"), self._exposure_spinbox, btn_exp
        )

        # --- frame selector + species (shown in absorption mode only) ---
        # Worker sends Dark/Light/Atoms/OD/Density together in one message each shot;
        # switching the dropdown just re-renders one already locally, no new data needed.
        self._frame_selector = QtWidgets.QComboBox()
        self._frame_selector.addItems(['Dark', 'Light', 'Atoms', 'OD', 'Density'])
        self._frame_selector.setCurrentText('OD')
        self._frame_selector.currentTextChanged.connect(self._on_frame_selected)
        self._species_selector = QtWidgets.QComboBox()
        self._species_selector.addItems(['Cs', 'Li'])
        self._species_selector.setToolTip(
            "Atomic species used to compute the resonant cross section for Density/atom-"
            "number results. Doesn't affect the OD image. Switching this instantly "
            "redisplays the last shot with the new species."
        )
        self._species_selector.currentTextChanged.connect(self._on_species_selected)
        self._chk_fits = QtWidgets.QCheckBox("Fits")
        self._chk_fits.setChecked(True)
        self._chk_fits.setToolTip(
            "Gaussian curve fitting (cloud size, position, atom number) -- the slowest "
            "part of computing the absorption display. Turn off for faster live "
            "display between shots when fit results aren't needed every time; N_int, "
            "the OD image, and Density are unaffected and still update either way."
        )
        self._chk_fits.toggled.connect(self._on_fit_enabled_toggled)
        self._frame_row = _row(
            QtWidgets.QLabel("Show frame:"), self._frame_selector,
            QtWidgets.QLabel("Species:"), self._species_selector,
            self._chk_fits,
        )
        self.image_receiver.selected_frame = 'OD'

        # --- colorbar limits (shown in absorption mode only) ---
        # Stored per group (Dark / Light+Atoms / OD / Density); switching Show-frame above
        # loads that frame's group's own remembered limits into these controls. The
        # underlying pg histogram/LUT widgets can also be dragged directly as usual.
        self._cb_auto = QtWidgets.QCheckBox("Auto")
        self._cb_auto.setChecked(True)
        self._cb_auto.toggled.connect(self._on_colorbar_limits_changed)
        self._cb_min = QtWidgets.QDoubleSpinBox()
        self._cb_min.setRange(-1e9, 1e9)
        self._cb_min.setDecimals(4)
        self._cb_min.setFixedWidth(100)
        self._cb_min.valueChanged.connect(self._on_colorbar_limits_changed)
        self._cb_max = QtWidgets.QDoubleSpinBox()
        self._cb_max.setRange(-1e9, 1e9)
        self._cb_max.setDecimals(4)
        self._cb_max.setValue(1.0)
        self._cb_max.setFixedWidth(100)
        self._cb_max.valueChanged.connect(self._on_colorbar_limits_changed)
        self._colorbar_row = _row(
            QtWidgets.QLabel("Colorbar:"), self._cb_auto,
            QtWidgets.QLabel("Min"), self._cb_min,
            QtWidgets.QLabel("Max"), self._cb_max,
        )
        self._sync_colorbar_controls('OD')

        # Dragging either colorbar's levels directly should update the Min/Max spinboxes
        # to match (and switch Auto off, since a drag is a manual choice) instead of just
        # silently drifting out of sync with what the spinboxes display. density_hist is
        # pinned to always mean the 'Density' group explicitly (it's a dedicated widget,
        # never used for anything else) -- see _on_histogram_dragged for why this matters.
        self.image.ui.histogram.item.sigLevelsChanged.connect(
            lambda: self._on_histogram_dragged(self.image.ui.histogram.item)
        )
        self._absorption_display.density_hist.sigLevelsChanged.connect(
            lambda: self._on_histogram_dragged(self._absorption_display.density_hist, group='Density')
        )

        # --- Save ROI + Defringe ROI ---
        # Draggable/resizable rectangles on self.image, each with an editable x0/y0/x1/y1
        # spinbox row that stays in sync with the drag box in both directions. Save ROI:
        # images are cropped down to this region before being saved to the shot file (see
        # PCOCameraWorker._crop_saved_images_and_record_rois). Defringe ROI: recorded as
        # metadata only, for a future fringe-removal algorithm to use as its background
        # reference region. Both are pushed to the worker on drag release/spinbox edit
        # (not every intermediate drag frame) and recorded on every shot regardless of
        # display_mode.
        self._chk_show_rois = QtWidgets.QCheckBox("Show Save/Defringe ROI boxes on image")
        self._chk_show_rois.setChecked(True)
        self._chk_show_rois.toggled.connect(self._on_show_rois_toggled)
        _row(self._chk_show_rois)

        save_roi_widget, self._save_roi_boxes = self._build_roi_spinbox_row("Save ROI:")
        controls_col.addWidget(save_roi_widget)

        defringe_roi_widget, self._defringe_roi_boxes = self._build_roi_spinbox_row("Defringe ROI:")
        controls_col.addWidget(defringe_roi_widget)

        # Rows above are all natural-height widgets with no vertical stretch of their
        # own; without an explicit trailing stretch here, controls_widget's *own* height
        # (set below by however tall controls_col's addWidget() calls above ended up)
        # is fine on its own -- but placing controls_widget in bottom_row below still
        # needs AlignTop (see there) or it stretches to match the table's height and
        # this addStretch() would otherwise be needed to keep the rows from spreading
        # out to fill that stretched height. Belt and braces: keep both.
        controls_col.addStretch()

        # Save ROI: green, defaults to a large central region (most of the sensor).
        self._save_roi = pg.RectROI(
            [124, 124], [1800, 1800],
            pen=pg.mkPen('g', width=2),
            handlePen=pg.mkPen('g', width=2),
        )
        for handle in ([1, 1], [0, 0], [1, 0], [0, 1]):
            self._save_roi.addScaleHandle(handle, [1 - handle[0], 1 - handle[1]])
        self.image.addItem(self._save_roi)
        self._save_roi.sigRegionChanged.connect(self._on_save_roi_dragged)
        self._save_roi.sigRegionChangeFinished.connect(self._push_save_roi)
        for box in self._save_roi_boxes.values():
            box.valueChanged.connect(self._on_save_roi_box_edited)

        # Defringe ROI: orange, defaults to a small corner region away from where the
        # atom cloud usually is, as a plausible starting "no atoms" reference patch.
        self._defringe_roi = pg.RectROI(
            [50, 50], [250, 250],
            pen=pg.mkPen(255, 165, 0, width=2),
            handlePen=pg.mkPen(255, 165, 0, width=2),
        )
        for handle in ([1, 1], [0, 0], [1, 0], [0, 1]):
            self._defringe_roi.addScaleHandle(handle, [1 - handle[0], 1 - handle[1]])
        self.image.addItem(self._defringe_roi)
        self._defringe_roi.sigRegionChanged.connect(self._on_defringe_roi_dragged)
        self._defringe_roi.sigRegionChangeFinished.connect(self._push_defringe_roi)
        for box in self._defringe_roi_boxes.values():
            box.valueChanged.connect(self._on_defringe_roi_box_edited)

        self._sync_roi_boxes(self._save_roi, self._save_roi_boxes)
        self._sync_roi_boxes(self._defringe_roi, self._defringe_roi_boxes)

        # controls_widget (all the rows built above) alongside the Density fit-results
        # table -- the table sits to the right instead of adding its own full-width row.
        bottom_row_widget = QtWidgets.QWidget()
        bottom_row = QtWidgets.QHBoxLayout()
        # A bit of right padding so the table (pinned to the right edge below) doesn't
        # sit flush against the panel's actual edge.
        bottom_row.setContentsMargins(0, 0, 8, 0)
        bottom_row.setSpacing(10)
        bottom_row_widget.setLayout(bottom_row)
        # Stretch factor 0 *and* AlignTop on both -- neither should expand to fill
        # whatever's left (giving controls_widget a stretch factor here, as a previous
        # version of this did, was exactly what caused it to claim leftover width/height
        # from the row without its own content growing to fill it, leaving that space
        # stranded as a visible gap around its rows instead of doing anything useful).
        bottom_row.addWidget(controls_widget, 0, QtCore.Qt.AlignTop)
        # The stretch goes *between* controls and the table -- pushes the table to the
        # right edge of the available panel width (with the padding above) rather than
        # sitting immediately next to controls_widget with a fixed gap.
        bottom_row.addStretch()
        bottom_row.addWidget(self._absorption_display.results_table, 0, QtCore.Qt.AlignTop)

        # If the BLACS window/dock is narrower than controls_widget's own minimum width
        # (mainly set by the Save/Defringe ROI spinbox rows) plus the table, there's
        # nothing left to shrink -- without this wrapper that overflow used to render past
        # the tab's right edge, invisibly, rather than being reachable at all. A horizontal
        # scroll area makes that overflow reachable via scrollbar instead of just lost.
        # setWidgetResizable(True) means it still simply fills the available width with no
        # scrollbar at all whenever there's enough room, which is the common case.
        bottom_scroll = QtWidgets.QScrollArea()
        bottom_scroll.setWidget(bottom_row_widget)
        bottom_scroll.setWidgetResizable(True)
        bottom_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        bottom_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        bottom_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        bottom_scroll.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        bottom_scroll.setFixedHeight(bottom_row_widget.sizeHint().height())
        self.get_tab_layout().addWidget(bottom_scroll)

        # Apply the default ('live') visibility state; restore_save_data() (called after
        # the worker exists) may switch this to the last-used mode and push it to the
        # worker.
        self._display_mode = 'live'
        self._apply_display_mode('live')

    def get_save_data(self):
        data = super().get_save_data()
        data['pco_display_mode'] = self._display_mode
        data['pco_species'] = self._species_selector.currentText()
        data['pco_fit_enabled'] = self._chk_fits.isChecked()
        data['pco_frame_selector'] = self._frame_selector.currentText()
        # A *copy*, not a live reference -- BLACS's front_panel_settings collects this
        # dict via get_save_data() and only actually repr()s/writes it to disk in a
        # later, separate call (with a real gap between them, e.g. a blocking "save
        # broken tab data?" dialog on exit). If a new shot re-renders Density in that
        # window and self._colorbar_limits gets mutated in place, a live reference here
        # would let the on-disk save silently drift from whatever was actually showing
        # when the user triggered the save.
        data['pco_colorbar_limits'] = {group: dict(limits) for group, limits in self._colorbar_limits.items()}
        data['pco_save_roi_geometry'] = self._roi_geometry(self._save_roi)
        data['pco_defringe_roi_geometry'] = self._roi_geometry(self._defringe_roi)
        data['pco_show_rois'] = self._chk_show_rois.isChecked()
        # Exposure spinbox value (not necessarily applied to the camera -- that requires
        # clicking Apply -- just what was showing, so a restored tab looks the same as
        # when it was saved). super().get_save_data() already covers self.image's own
        # colormap; the density panel's histogram is separate.
        data['pco_exposure_ms'] = self._exposure_spinbox.value()
        return data

    def restore_save_data(self, save_data):
        super().restore_save_data(save_data)

        saved_limits = save_data.get('pco_colorbar_limits')
        if saved_limits:
            for group in _COLORBAR_GROUPS:
                if group in saved_limits:
                    self._colorbar_limits[group] = saved_limits[group]

        frame_name = save_data.get('pco_frame_selector', 'OD')
        if frame_name in ('Dark', 'Light', 'Atoms', 'OD', 'Density'):
            # Triggers _on_frame_selected, which syncs the colorbar controls to the
            # restored limits above.
            self._frame_selector.setCurrentText(frame_name)
        else:
            self._sync_colorbar_controls(self._frame_selector.currentText())

        species = save_data.get('pco_species', 'Cs')
        # Triggers _on_species_selected -> pushes to the worker (a no-op if already 'Cs',
        # which is fine since the worker also starts with species='Cs').
        self._species_selector.setCurrentText(species)

        # Triggers _on_fit_enabled_toggled (a no-op if already checked, which is fine
        # since the worker also starts with fit_enabled=True).
        self._chk_fits.setChecked(save_data.get('pco_fit_enabled', True))

        # Triggers _on_show_rois_toggled (a no-op if already checked, which is fine since
        # that's the default too).
        self._chk_show_rois.setChecked(save_data.get('pco_show_rois', True))

        # Restore Save/Defringe ROI geometry if we have it, then push to the worker
        # unconditionally -- even on a first-ever run with no saved geometry, the worker
        # should still get the boxes' default positions, so save_roi/defringe_roi are
        # always recorded from the very first shot rather than only after a manual drag.
        save_roi_geom = save_data.get('pco_save_roi_geometry')
        if save_roi_geom:
            x, y, w, h = save_roi_geom
            self._save_roi.setPos((x, y), update=False)
            self._save_roi.setSize((w, h))
        self._sync_roi_boxes(self._save_roi, self._save_roi_boxes)
        self._push_save_roi()

        defringe_roi_geom = save_data.get('pco_defringe_roi_geometry')
        if defringe_roi_geom:
            x, y, w, h = defringe_roi_geom
            self._defringe_roi.setPos((x, y), update=False)
            self._defringe_roi.setSize((w, h))
        self._sync_roi_boxes(self._defringe_roi, self._defringe_roi_boxes)
        self._push_defringe_roi()

        if 'pco_exposure_ms' in save_data:
            self._exposure_spinbox.setValue(save_data['pco_exposure_ms'])

        # super().restore_save_data() above just restored self.image's gradient from
        # whatever was persisted (possibly the plain black-to-white 'grey' preset, saved
        # back before this default existed) -- reassert the colored default over that.
        _style_colorbar_like_matplotlib(self.image.ui.histogram.item, self.image.ui.histogram)
        _style_colorbar_like_matplotlib(self._absorption_display.density_hist)

        mode = save_data.get('pco_display_mode', 'live')
        text = 'Absorption' if mode == 'absorption' else 'Live'
        # Triggers _on_display_mode_selected via the combo box's signal (a no-op if the
        # mode is already 'live', which is fine since the worker also starts in 'live').
        self._mode_selector.setCurrentText(text)

    def _on_display_mode_selected(self, text):
        mode = 'absorption' if text == 'Absorption' else 'live'
        self._apply_display_mode(mode)
        self._push_display_mode(mode)

    def _on_frame_selected(self, name):
        self.image_receiver.set_selected_frame(name)
        self._sync_colorbar_controls(name)

    def _sync_colorbar_controls(self, frame_name):
        """Load the given frame's group's remembered colorbar limits into the Auto/Min/
        Max controls, without re-triggering _on_colorbar_limits_changed."""
        group = _colorbar_group(frame_name)
        limits = self._colorbar_limits.setdefault(group, {'auto': True, 'vmin': 0.0, 'vmax': 1.0})
        for widget in (self._cb_auto, self._cb_min, self._cb_max):
            widget.blockSignals(True)
        self._cb_auto.setChecked(limits['auto'])
        self._cb_min.setValue(limits['vmin'])
        self._cb_max.setValue(limits['vmax'])
        for widget in (self._cb_auto, self._cb_min, self._cb_max):
            widget.blockSignals(False)
        self._cb_min.setEnabled(not limits['auto'])
        self._cb_max.setEnabled(not limits['auto'])

    def _on_colorbar_limits_changed(self, *_args):
        self._cb_min.setEnabled(not self._cb_auto.isChecked())
        self._cb_max.setEnabled(not self._cb_auto.isChecked())
        group = _colorbar_group(self._frame_selector.currentText())
        self._colorbar_limits[group] = {
            'auto': self._cb_auto.isChecked(),
            'vmin': self._cb_min.value(),
            'vmax': self._cb_max.value(),
        }
        name = self.image_receiver.selected_frame
        if name in self.image_receiver.frames_by_name:
            self.image_receiver._render(name)

    def _on_histogram_dragged(self, hist_item, group=None):
        """Fires on every levels change, including our own programmatic ones (auto-level
        on a new frame, applying a stored manual Min/Max) -- _AbsorptionDisplay sets
        suppress_level_signal around those, so anything that gets here (with that guard
        not already having returned) is meant to be an actual user drag on the colorbar.

        group is passed explicitly by density_hist's connection (always 'Density', since
        that's a dedicated widget never used for anything else). For self.image's shared
        histogram (Dark/Light/Atoms/OD all reuse it), the group instead has to come from
        whichever frame is currently selected -- but self.image is never legitimately
        showing Density (that's density_hist's job, and self.image is hidden while
        Density is shown), so a signal reaching here with group=None and a *currently*
        Density-selected frame is a stale one, most likely a still-in-flight level change
        from whatever frame self.image was previously displaying, racing against a since-
        completed switch of the frame selector to Density. Misattributing that leftover
        signal to the Density group is exactly what caused Density's colorbar range to
        silently pick up Atoms/Light's or OD's numbers instead of its own -- so drop it
        rather than writing it to the wrong group's stored limits."""
        if self._display_mode != 'absorption' or self._absorption_display.suppress_level_signal:
            return
        if group is None:
            name = self.image_receiver.selected_frame
            if not name:
                return
            group = _colorbar_group(name)
            if group == 'Density':
                return
        lo, hi = hist_item.getLevels()
        self._colorbar_limits[group] = {'auto': False, 'vmin': lo, 'vmax': hi}
        if group == _colorbar_group(self._frame_selector.currentText()):
            self._sync_colorbar_controls(self._frame_selector.currentText())

    def _on_species_selected(self, species):
        self._push_species(species)

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _push_species(self, species):
        yield self.queue_work(self.primary_worker, 'set_species', species)

    def _on_fit_enabled_toggled(self, enabled):
        self._push_fit_enabled(enabled)

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _push_fit_enabled(self, enabled):
        yield self.queue_work(self.primary_worker, 'set_fit_enabled', enabled)

    def _apply_display_mode(self, mode):
        """Toggle which widgets are visible for the given mode. Purely a GUI-thread
        visibility update; see _push_display_mode() for telling the worker."""
        is_absorption = mode == 'absorption'
        self._display_mode = mode

        self._exposure_widget.setVisible(not is_absorption)
        self._frame_row.setVisible(is_absorption)
        self._colorbar_row.setVisible(is_absorption)
        for widget in self._toolbar_widgets:
            widget.setVisible(not is_absorption)

        if is_absorption:
            name = self.image_receiver.selected_frame
            if name in self.image_receiver.frames_by_name:
                # Re-show the last-received frame if we have one (e.g. switching back
                # from Live without a new shot in between); otherwise the panel would
                # otherwise just be blank until the next shot arrives, which looks broken.
                self.image_receiver._render(name)
            else:
                self._absorption_display.show_placeholder()
        else:
            self._absorption_display.container.hide()
            self._absorption_display.results_table.hide()
            self.image.show()

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _push_display_mode(self, mode):
        yield self.queue_work(self.primary_worker, 'set_display_mode', mode)

    def _roi_pixel_bounds(self, roi_item):
        """(x0, y0, x1, y1) pixel bounds of a draggable RectROI, clamped to the actual
        displayed image size (falling back to the full 2048x2048 sensor if nothing has
        been displayed yet)."""
        pos = roi_item.pos()
        size = roi_item.size()
        max_w, max_h = 2048, 2048
        if self.image.image is not None:
            # image is stored as (W, H) due to swapaxes (see _show()/show_frame()).
            max_w, max_h = self.image.image.shape[0], self.image.image.shape[1]
        x0 = max(0, int(round(pos.x())))
        y0 = max(0, int(round(pos.y())))
        x1 = min(max_w, x0 + max(1, int(round(size.x()))))
        y1 = min(max_h, y0 + max(1, int(round(size.y()))))
        return x0, y0, x1, y1

    @staticmethod
    def _roi_geometry(roi_item):
        """(x, y, w, h) of a draggable RectROI, for save/restore of its exact position
        and size (as opposed to _roi_pixel_bounds(), which is clamped/rounded for
        sending to the worker)."""
        pos = roi_item.pos()
        size = roi_item.size()
        return (pos.x(), pos.y(), size.x(), size.y())

    @staticmethod
    def _build_roi_spinbox_row(label_text):
        """A labelled row of 4 editable pixel-bound spinboxes (x0, y0, x1, y1) for a
        Save/Defringe ROI. Returns (row_widget, {'x0': spinbox, ...})."""
        widget = QtWidgets.QWidget()
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(4, 2, 4, 2)
        row.setSpacing(6)
        widget.setLayout(row)
        row.addWidget(QtWidgets.QLabel(label_text))
        boxes = {}
        for key in ('x0', 'y0', 'x1', 'y1'):
            row.addWidget(QtWidgets.QLabel(key))
            box = QtWidgets.QSpinBox()
            box.setRange(0, 2048)
            box.setFixedWidth(55)
            row.addWidget(box)
            boxes[key] = box
        row.addStretch()
        return widget, boxes

    def _sync_roi_boxes(self, roi_item, boxes):
        """Load roi_item's current pixel bounds into its spinboxes, without
        re-triggering the box-edited handler (which would otherwise fight back)."""
        x0, y0, x1, y1 = self._roi_pixel_bounds(roi_item)
        for key, value in zip(('x0', 'y0', 'x1', 'y1'), (x0, y0, x1, y1)):
            boxes[key].blockSignals(True)
            boxes[key].setValue(value)
            boxes[key].blockSignals(False)

    @staticmethod
    def _apply_roi_boxes(roi_item, boxes):
        """Move/resize roi_item to match its spinboxes, without re-triggering the
        drag-sync handler (which would otherwise just redundantly re-read the same
        values back, but more importantly would fire before x1/y1 are both applied)."""
        x0, y0 = boxes['x0'].value(), boxes['y0'].value()
        x1 = max(boxes['x1'].value(), x0 + 1)
        y1 = max(boxes['y1'].value(), y0 + 1)
        roi_item.blockSignals(True)
        roi_item.setPos((x0, y0))
        roi_item.setSize((x1 - x0, y1 - y0))
        roi_item.blockSignals(False)

    def _on_show_rois_toggled(self, checked):
        self._save_roi.setVisible(checked)
        self._defringe_roi.setVisible(checked)

    def _on_save_roi_dragged(self, *_):
        self._sync_roi_boxes(self._save_roi, self._save_roi_boxes)

    def _on_defringe_roi_dragged(self, *_):
        self._sync_roi_boxes(self._defringe_roi, self._defringe_roi_boxes)

    def _on_save_roi_box_edited(self, *_):
        self._apply_roi_boxes(self._save_roi, self._save_roi_boxes)
        self._push_save_roi()

    def _on_defringe_roi_box_edited(self, *_):
        self._apply_roi_boxes(self._defringe_roi, self._defringe_roi_boxes)
        self._push_defringe_roi()

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _push_save_roi(self, *_):
        roi = self._roi_pixel_bounds(self._save_roi)
        yield self.queue_work(self.primary_worker, 'set_save_roi', roi)

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _push_defringe_roi(self, *_):
        roi = self._roi_pixel_bounds(self._defringe_roi)
        yield self.queue_work(self.primary_worker, 'set_defringe_roi', roi)

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _on_apply_exposure(self, checked):
        exposure_s = self._exposure_spinbox.value() / 1000.0
        yield self.queue_work(self.primary_worker, 'set_manual_attribute', 'exposure_time', exposure_s)
