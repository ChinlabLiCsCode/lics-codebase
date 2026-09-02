import json
import numpy as np
from time import perf_counter

import h5py
import labscript_utils.properties
import pyqtgraph as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from qtutils import inmain_decorator
from qtutils.qt import QtWidgets

from blacs.tab_base_classes import define_state, MODE_MANUAL
from labscript_devices.IMAQdxCamera.blacs_tabs import IMAQdxCameraTab, ImageReceiver, exp_av
from lics_labscript_devices.PCOCamera.absorption_analysis import (
    CONV_UM_PER_PIX, SPAN_UM, SENSOR_PIXELS,
)

# Physical extent (microns) of a full-sensor frame, matching absorption_image_analysis.py's
# plots. Used for the axes of the matplotlib absorption-mode display.
_EXTENT_UM = [0, SENSOR_PIXELS * CONV_UM_PER_PIX, 0, SENSOR_PIXELS * CONV_UM_PER_PIX]

# Colorbar limits are stored per group rather than per frame -- Light and Atoms share
# units (raw camera counts) and are typically compared at the same scale.
_COLORBAR_GROUPS = ['Dark', 'Light/Atoms', 'OD', 'Density']


def _colorbar_group(frame_name):
    return 'Light/Atoms' if frame_name in ('Light', 'Atoms') else frame_name


class _AbsorptionCanvas(FigureCanvasQTAgg):
    """Embedded matplotlib panel used in 'absorption' display_mode, in place of the
    pyqtgraph live view: a plain image with a real matplotlib colorbar for Dark/
    Light/Atoms/OD, and for Density, the same x/y integrated-density-profile +
    Gaussian-fit-overlay layout as absorption_image_analysis.py's density panel.

    The panel width is fully flexible (Expanding size policy, small minimum size), and
    every colorbar is placed in its own gridspec column at a fixed proportion of the
    figure width, so it stays anchored to the right edge and fully visible at any
    panel size rather than being computed relative to a fixed-size axes."""

    def __init__(self):
        self.fig = Figure(constrained_layout=True)
        super().__init__(self.fig)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setMinimumSize(150, 150)

    def show_placeholder(self, text="Waiting for next shot…"):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.axis('off')
        ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=12, color='gray',
                 transform=ax.transAxes)
        self.draw_idle()

    def show_frame(self, name, image, vmin=None, vmax=None):
        self.fig.clear()
        gs = self.fig.add_gridspec(1, 2, width_ratios=[20, 1], wspace=0.05)
        ax = self.fig.add_subplot(gs[0, 0])
        ax_cb = self.fig.add_subplot(gs[0, 1])
        im = ax.imshow(image, origin='lower', extent=_EXTENT_UM, aspect='auto', vmin=vmin, vmax=vmax)
        self.fig.colorbar(im, cax=ax_cb)
        ax.set_title(name)
        ax.set_xlabel('x (μm)')
        ax.set_ylabel('y (μm)')
        self.draw_idle()

    def show_density(self, image, x_int, y_int, x_dist, y_dist, N, results, vmin=None, vmax=None):
        self.fig.clear()
        conv = CONV_UM_PER_PIX
        span = SPAN_UM

        gs = self.fig.add_gridspec(
            2, 3, height_ratios=[5, 1], width_ratios=[1, 8, 0.2], hspace=0.04, wspace=0.04
        )
        ax_density = self.fig.add_subplot(gs[0, 1])
        ax_y_prof = self.fig.add_subplot(gs[0, 0], sharey=ax_density)
        ax_cb = self.fig.add_subplot(gs[0, 2])
        ax_x_prof = self.fig.add_subplot(gs[1, 1], sharex=ax_density)

        im = ax_density.imshow(image, origin='lower', extent=_EXTENT_UM, aspect='auto', vmin=vmin, vmax=vmax)
        title = "Density (atoms/μm²)"
        if N is not None:
            title += f", N={N:.1e}"
        ax_density.set_title(title)
        self.fig.colorbar(im, cax=ax_cb)
        ax_cb.set_ylabel('Density (atoms/μm²)')
        ax_density.tick_params(labelbottom=False, labelleft=False)

        x_int = np.asarray(x_int)
        y_int = np.asarray(y_int)
        ax_x_prof.scatter(span, x_int / conv, s=4, alpha=0.5)
        ax_x_prof.plot(span, x_dist, color='red')
        ax_x_prof.set_xlabel('x (μm)')

        ax_y_prof.scatter(y_int / conv, span, s=4, alpha=0.5)
        ax_y_prof.plot(y_dist, span, color='red')
        ax_y_prof.set_ylabel('y (μm)')
        ax_y_prof.xaxis.set_label_position('top')
        ax_y_prof.xaxis.tick_top()

        self.draw_idle()


class _PCOImageReceiver(ImageReceiver):
    """Like ImageReceiver but keeps the histogram x-axis fixed after the first frame
    so the min/max level handles don't visually drift during continuous acquisition.

    Also understands "named frames" messages (sent by PCOCameraWorker whenever its
    display_mode is 'absorption'): several same-shaped images (Dark/Light/Atoms/OD/
    Density) plus profile/fit data arrive in one message, and are rendered into
    mpl_canvas (with a real colorbar and, for Density, the x/y profile+fit plots)
    instead of the pyqtgraph view. Which branch is used is decided purely by whether a
    given message carries frame_names, so this doesn't need to know the tab's current
    display_mode selection; the tab can switch which frame is shown locally via
    set_selected_frame() without asking the worker again."""

    def __init__(self, image_view, label_fps, mpl_canvas=None, colorbar_limits=None):
        super().__init__(image_view, label_fps)
        self._frame_callback = None
        self.frames_by_name = {}
        self.profile_data = {}
        self.selected_frame = None
        self.mpl_canvas = mpl_canvas
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
            self.mpl_canvas.show_density(image, vmin=vmin, vmax=vmax, **self.profile_data)
        else:
            self.mpl_canvas.show_frame(name, image, vmin=vmin, vmax=vmax)
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

        # Read initial ROI/exposure from the connection table HDF5 so the spinboxes start
        # at the values the camera will actually be using. display_mode is no longer a
        # connection table property -- it's switched live from the dropdown below and
        # defaults to 'live' (persisted across BLACS restarts via get/restore_save_data).
        roi_w_init, roi_y0_init, roi_h_init = 2048, 1, 2048
        exposure_ms_init = 50.0
        try:
            table = self.settings['connection_table']
            ct_props = table.find_by_name(self.device_name).properties
            with h5py.File(table.filepath, 'r') as f:
                dev_props = labscript_utils.properties.get(f, self.device_name, 'device_properties')
            attrs = {**dev_props.get('camera_attributes', {}),
                     **ct_props.get('manual_mode_camera_attributes', {})}
            if 'roi' in attrs:
                x0, y0, x1, y1 = attrs['roi']
                roi_w_init  = x1 - x0 + 1
                roi_y0_init = y0
                roi_h_init  = y1 - y0 + 1
            if 'exposure_time' in attrs:
                exposure_ms_init = attrs['exposure_time'] * 1000.0
        except Exception:
            pass

        # Embedded matplotlib panel (real colorbar, x/y profile+fit plots for Density),
        # shown in place of the pyqtgraph live view while display_mode is 'absorption'.
        # matplotlib isn't suited to the high update rate of continuous live view, so both
        # widgets always exist and _apply_display_mode() toggles which one is visible.
        self._mpl_canvas = _AbsorptionCanvas()
        self.ui.horizontalLayout.addWidget(self._mpl_canvas)

        # Colorbar limits, stored per group (Dark / Light+Atoms / OD / Density) so each
        # remembers its own manual min/max independently of which frame is shown.
        self._colorbar_limits = {
            group: {'auto': True, 'vmin': 0.0, 'vmax': 1.0} for group in _COLORBAR_GROUPS
        }

        # Replace the default ImageReceiver with one that keeps the histogram range fixed
        # and can render into the matplotlib panel. Must happen before initialise_workers()
        # reads self.image_receiver.port.
        self.image_receiver.shutdown()
        self.image_receiver = _PCOImageReceiver(
            self.image, self.ui.label_fps,
            mpl_canvas=self._mpl_canvas, colorbar_limits=self._colorbar_limits,
        )

        # The Attributes/Snap/Continuous/Stop toolbar column (left of the image in
        # blacs_tab.ui) only does anything useful in 'live' mode -- Snap/Continuous only
        # ever update the pyqtgraph view. Some of these widgets have
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

        # --- display-mode switcher (own row) ---
        mode_widget = QtWidgets.QWidget()
        mode_row = QtWidgets.QHBoxLayout()
        mode_row.setContentsMargins(4, 4, 4, 4)
        mode_widget.setLayout(mode_row)
        mode_row.addWidget(QtWidgets.QLabel("Display mode:"))
        self._mode_selector = QtWidgets.QComboBox()
        self._mode_selector.addItems(['Live', 'Absorption'])
        self._mode_selector.setToolTip(
            "Live: normal live camera viewer.\n"
            "Absorption: after each shot, compute and show the OD/Density image from "
            "that shot's dark/light/atoms frames, with live x/y profile fits."
        )
        self._mode_selector.currentTextChanged.connect(self._on_display_mode_selected)
        mode_row.addWidget(self._mode_selector)
        mode_row.addStretch()
        self.get_tab_layout().addWidget(mode_widget)

        # --- ROI row ---
        # The PCO Panda reads out from both edges of the sensor simultaneously so the
        # horizontal ROI is always centred (x0 + x1 = 2049, width multiple of 8).
        # The vertical ROI is unconstrained: set y0 and height freely.
        roi_widget = QtWidgets.QWidget()
        roi_row = QtWidgets.QHBoxLayout()
        roi_row.setContentsMargins(4, 4, 4, 4)
        roi_widget.setLayout(roi_row)

        roi_row.addWidget(QtWidgets.QLabel("ROI:"))

        roi_row.addWidget(QtWidgets.QLabel("W (x centred)"))
        self._roi_w = QtWidgets.QSpinBox()
        self._roi_w.setRange(64, 2048)
        self._roi_w.setSingleStep(8)
        self._roi_w.setValue(max(64, (roi_w_init // 8) * 8))
        self._roi_w.setFixedWidth(65)
        roi_row.addWidget(self._roi_w)

        roi_row.addWidget(QtWidgets.QLabel("y0"))
        self._roi_y0 = QtWidgets.QSpinBox()
        self._roi_y0.setRange(1, 2047)
        self._roi_y0.setValue(roi_y0_init)
        self._roi_y0.setFixedWidth(55)
        roi_row.addWidget(self._roi_y0)

        roi_row.addWidget(QtWidgets.QLabel("H"))
        self._roi_h = QtWidgets.QSpinBox()
        self._roi_h.setRange(1, 2048)
        self._roi_h.setValue(roi_h_init)
        self._roi_h.setFixedWidth(55)
        roi_row.addWidget(self._roi_h)

        self._roi_coords_label = QtWidgets.QLabel()
        roi_row.addWidget(self._roi_coords_label)

        btn_roi = QtWidgets.QPushButton("Apply ROI")
        btn_roi.clicked.connect(self._on_apply_roi)
        roi_row.addWidget(btn_roi)

        roi_row.addStretch()

        self._roi_w.valueChanged.connect(self._update_roi_label)
        self._roi_y0.valueChanged.connect(self._clamp_roi_h)
        self._roi_y0.valueChanged.connect(self._update_roi_label)
        self._roi_h.valueChanged.connect(self._update_roi_label)
        self._update_roi_label()

        self.get_tab_layout().addWidget(roi_widget)

        # --- exposure row (hidden in absorption mode; those shots use exposure_time from
        # the connection table's camera_attributes, not a manually-set live value) ---
        self._exposure_widget = QtWidgets.QWidget()
        exp_row = QtWidgets.QHBoxLayout()
        exp_row.setContentsMargins(4, 4, 4, 4)
        self._exposure_widget.setLayout(exp_row)

        exp_row.addWidget(QtWidgets.QLabel("Exposure (ms):"))
        self._exposure_spinbox = QtWidgets.QDoubleSpinBox()
        self._exposure_spinbox.setRange(0.001, 10000.0)
        self._exposure_spinbox.setDecimals(3)
        self._exposure_spinbox.setValue(exposure_ms_init)
        self._exposure_spinbox.setFixedWidth(90)
        exp_row.addWidget(self._exposure_spinbox)

        btn_exp = QtWidgets.QPushButton("Apply Exposure")
        btn_exp.clicked.connect(self._on_apply_exposure)
        exp_row.addWidget(btn_exp)

        exp_row.addStretch()

        self.get_tab_layout().addWidget(self._exposure_widget)

        # --- frame selector + species (shown in absorption mode only) ---
        # Worker sends Dark/Light/Atoms/OD/Density together in one message each shot;
        # switching the dropdown just re-renders one already locally, no new data needed.
        self._frame_row = QtWidgets.QWidget()
        frow = QtWidgets.QHBoxLayout()
        frow.setContentsMargins(4, 2, 4, 2)
        self._frame_row.setLayout(frow)
        frow.addWidget(QtWidgets.QLabel("Show frame:"))
        self._frame_selector = QtWidgets.QComboBox()
        self._frame_selector.addItems(['Dark', 'Light', 'Atoms', 'OD', 'Density'])
        self._frame_selector.setCurrentText('OD')
        self._frame_selector.currentTextChanged.connect(self._on_frame_selected)
        frow.addWidget(self._frame_selector)

        frow.addSpacing(16)
        frow.addWidget(QtWidgets.QLabel("Species:"))
        self._species_selector = QtWidgets.QComboBox()
        self._species_selector.addItems(['Cs', 'Li'])
        self._species_selector.setToolTip(
            "Atomic species used to compute the resonant cross section for Density/atom-"
            "number results. Doesn't affect the OD image. Switching this instantly "
            "redisplays the last shot with the new species."
        )
        self._species_selector.currentTextChanged.connect(self._on_species_selected)
        frow.addWidget(self._species_selector)

        frow.addStretch()
        self.get_tab_layout().addWidget(self._frame_row)
        self.image_receiver.selected_frame = 'OD'

        # --- colorbar limits (shown in absorption mode only) ---
        # Stored per group (Dark / Light+Atoms / OD / Density); switching Show-frame above
        # loads that frame's group's own remembered limits into these controls.
        self._colorbar_row = QtWidgets.QWidget()
        cb_row = QtWidgets.QHBoxLayout()
        cb_row.setContentsMargins(4, 2, 4, 2)
        self._colorbar_row.setLayout(cb_row)
        cb_row.addWidget(QtWidgets.QLabel("Colorbar:"))
        self._cb_auto = QtWidgets.QCheckBox("Auto")
        self._cb_auto.setChecked(True)
        self._cb_auto.toggled.connect(self._on_colorbar_limits_changed)
        cb_row.addWidget(self._cb_auto)
        cb_row.addWidget(QtWidgets.QLabel("Min"))
        self._cb_min = QtWidgets.QDoubleSpinBox()
        self._cb_min.setRange(-1e9, 1e9)
        self._cb_min.setDecimals(4)
        self._cb_min.setFixedWidth(100)
        self._cb_min.valueChanged.connect(self._on_colorbar_limits_changed)
        cb_row.addWidget(self._cb_min)
        cb_row.addWidget(QtWidgets.QLabel("Max"))
        self._cb_max = QtWidgets.QDoubleSpinBox()
        self._cb_max.setRange(-1e9, 1e9)
        self._cb_max.setDecimals(4)
        self._cb_max.setValue(1.0)
        self._cb_max.setFixedWidth(100)
        self._cb_max.valueChanged.connect(self._on_colorbar_limits_changed)
        cb_row.addWidget(self._cb_max)
        cb_row.addStretch()
        self.get_tab_layout().addWidget(self._colorbar_row)
        self._sync_colorbar_controls('OD')

        # --- photon-count ROI (shown in live mode only; it's a draggable pyqtgraph
        # RectROI drawn on the pyqtgraph live view, which absorption mode replaces with
        # the matplotlib panel) ---
        self._count_widget = QtWidgets.QWidget()
        count_row = QtWidgets.QHBoxLayout()
        count_row.setContentsMargins(4, 2, 4, 2)
        self._count_widget.setLayout(count_row)

        count_row.addWidget(QtWidgets.QLabel("Selection counts:"))
        self._photon_count_label = QtWidgets.QLabel("—")
        self._photon_count_label.setMinimumWidth(120)
        count_row.addWidget(self._photon_count_label)

        count_row.addSpacing(16)
        count_row.addWidget(QtWidgets.QLabel("ROI pixels:"))
        self._photon_roi_size_label = QtWidgets.QLabel("—")
        count_row.addWidget(self._photon_roi_size_label)

        count_row.addSpacing(16)
        count_row.addWidget(QtWidgets.QLabel("coords:"))
        self._photon_roi_coords_label = QtWidgets.QLabel("—")
        self._photon_roi_coords_label.setMinimumWidth(220)
        count_row.addWidget(self._photon_roi_coords_label)

        count_row.addStretch()

        self.get_tab_layout().addWidget(self._count_widget)

        # Place the RectROI centred on a 2048×2048 sensor; 200×200 default size.
        # The image is stored transposed (swapaxes) so x/y in scene coords map
        # to col/row of the original sensor array.
        self._photon_roi = pg.RectROI(
            [924, 924], [200, 200],
            pen=pg.mkPen('r', width=2),
            handlePen=pg.mkPen('r', width=2),
        )
        self._photon_roi.addScaleHandle([1, 1], [0, 0])
        self._photon_roi.addScaleHandle([0, 0], [1, 1])
        self._photon_roi.addScaleHandle([1, 0], [0, 1])
        self._photon_roi.addScaleHandle([0, 1], [1, 0])
        self.image.addItem(self._photon_roi)
        self._photon_roi.sigRegionChanged.connect(self._update_photon_count)
        self.image_receiver._frame_callback = self._update_photon_count

        # Apply the default ('live') visibility state; restore_save_data() (called after
        # the worker exists) may switch this to the last-used mode and push it to the
        # worker.
        self._display_mode = 'live'
        self._apply_display_mode('live')

    def get_save_data(self):
        data = super().get_save_data()
        data['pco_display_mode'] = self._display_mode
        data['pco_species'] = self._species_selector.currentText()
        data['pco_frame_selector'] = self._frame_selector.currentText()
        data['pco_colorbar_limits'] = self._colorbar_limits
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

    def _on_species_selected(self, species):
        self._push_species(species)

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _push_species(self, species):
        yield self.queue_work(self.primary_worker, 'set_species', species)

    def _apply_display_mode(self, mode):
        """Toggle which widgets are visible for the given mode. Purely a GUI-thread
        visibility update; see _push_display_mode() for telling the worker."""
        is_absorption = mode == 'absorption'
        self._display_mode = mode

        self.image.setVisible(not is_absorption)
        self._mpl_canvas.setVisible(is_absorption)
        self._exposure_widget.setVisible(not is_absorption)
        self._frame_row.setVisible(is_absorption)
        self._colorbar_row.setVisible(is_absorption)
        self._count_widget.setVisible(not is_absorption)
        self._photon_roi.setVisible(not is_absorption)
        for widget in self._toolbar_widgets:
            widget.setVisible(not is_absorption)

        if is_absorption:
            # Re-show the last-received frame if we have one (e.g. switching back from
            # Live without a new shot in between); otherwise the panel would otherwise
            # just be blank until the next shot arrives, which looks broken.
            name = self.image_receiver.selected_frame
            if name in self.image_receiver.frames_by_name:
                self.image_receiver._render(name)
            else:
                self._mpl_canvas.show_placeholder()

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _push_display_mode(self, mode):
        yield self.queue_work(self.primary_worker, 'set_display_mode', mode)

    @staticmethod
    def _compute_roi(w, y0, h, sensor_w=2048):
        """Horizontal ROI is always centred (PCO Panda hardware constraint).
        Vertical ROI is free."""
        x0 = sensor_w // 2 + 1 - w // 2
        x1 = sensor_w // 2 + w // 2
        y1 = y0 + h - 1
        return (x0, y0, x1, y1)

    def _update_roi_label(self):
        roi = self._compute_roi(self._roi_w.value(), self._roi_y0.value(), self._roi_h.value())
        self._roi_coords_label.setText(f"→ ({roi[0]},{roi[1]},{roi[2]},{roi[3]})")

    def _clamp_roi_h(self):
        self._roi_h.setMaximum(2048 - self._roi_y0.value() + 1)

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _on_apply_roi(self, checked):
        roi = self._compute_roi(self._roi_w.value(), self._roi_y0.value(), self._roi_h.value())
        yield self.queue_work(self.primary_worker, 'set_manual_attribute', 'roi', roi)
        self.image.clear()  # next frame auto-ranges to new image dimensions

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _on_apply_exposure(self, checked):
        exposure_s = self._exposure_spinbox.value() / 1000.0
        yield self.queue_work(self.primary_worker, 'set_manual_attribute', 'exposure_time', exposure_s)

    def _update_photon_count(self, _=None):
        if self.image.image is None:
            return
        pos = self._photon_roi.pos()
        size = self._photon_roi.size()
        # image is stored as (W, H) due to swapaxes, so axis 0 = x, axis 1 = y
        img = self.image.image
        x0 = max(0, int(round(pos.x())))
        y0 = max(0, int(round(pos.y())))
        x1 = min(img.shape[0], x0 + max(1, int(round(size.x()))))
        y1 = min(img.shape[1], y0 + max(1, int(round(size.y()))))
        roi_data = img[x0:x1, y0:y1]
        total = float(np.sum(roi_data))
        self._photon_count_label.setText(f"{total:,.0f}")
        self._photon_roi_size_label.setText(f"{x1-x0} × {y1-y0}")
        self._photon_roi_coords_label.setText(f"x:[{x0}, {x1}]  y:[{y0}, {y1}]")
