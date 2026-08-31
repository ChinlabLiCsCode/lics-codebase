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


class _AbsorptionCanvas(FigureCanvasQTAgg):
    """Embedded matplotlib panel used in 'absorption' display_mode, in place of the
    pyqtgraph live view: a plain image with a real matplotlib colorbar for Dark/
    Light/Atoms/OD, and for Density, the same x/y integrated-density-profile +
    Gaussian-fit-overlay layout as absorption_image_analysis.py's density panel."""

    def __init__(self):
        self.fig = Figure(constrained_layout=True)
        super().__init__(self.fig)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def show_frame(self, name, image):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        im = ax.imshow(image, origin='lower', extent=_EXTENT_UM, aspect='auto')
        self.fig.colorbar(im, ax=ax)
        ax.set_title(name)
        ax.set_xlabel('x (μm)')
        ax.set_ylabel('y (μm)')
        self.draw_idle()

    def show_density(self, image, x_int, y_int, x_dist, y_dist, N, results):
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

        im = ax_density.imshow(image, origin='lower', extent=_EXTENT_UM, aspect='auto')
        title = "Density (atoms/μm²)"
        if N is not None:
            title += f", N={N:.1e}"
        ax_density.set_title(title)
        self.fig.colorbar(im, cax=ax_cb)
        ax_cb.set_ylabel('Density (atoms/μm²)')
        ax_density.tick_params(labelbottom=False, labelleft=False)

        results = results or {}
        sigma_x = results.get('sigma_x (um)')
        sigma_y = results.get('sigma_y (um)')

        x_int = np.asarray(x_int)
        y_int = np.asarray(y_int)
        ax_x_prof.scatter(span, x_int / conv, s=4, alpha=0.5)
        ax_x_prof.plot(span, x_dist, color='red',
                        label=f'fit σ={sigma_x:.0f} μm' if sigma_x is not None else 'fit')
        ax_x_prof.set_xlabel('x (μm)')
        ax_x_prof.legend(fontsize=8, loc='upper right')

        ax_y_prof.scatter(y_int / conv, span, s=4, alpha=0.5)
        ax_y_prof.plot(y_dist, span, color='red',
                        label=f'fit σ={sigma_y:.0f} μm' if sigma_y is not None else 'fit')
        ax_y_prof.set_ylabel('y (μm)')
        ax_y_prof.xaxis.set_label_position('top')
        ax_y_prof.xaxis.tick_top()
        ax_y_prof.legend(fontsize=8, loc='upper right')

        self.draw_idle()


class _PCOImageReceiver(ImageReceiver):
    """Like ImageReceiver but keeps the histogram x-axis fixed after the first frame
    so the min/max level handles don't visually drift during continuous acquisition.

    Also understands "named frames" messages (sent by PCOCameraWorker in
    'absorption' display_mode): several same-shaped images (Dark/Light/Atoms/OD/
    Density) plus profile/fit data arrive in one message. When mpl_canvas is set,
    these are rendered there (with a real colorbar and, for Density, the x/y
    profile+fit plots) instead of the pyqtgraph view; the tab can switch which
    frame is shown locally via set_selected_frame() without asking the worker
    again."""

    def __init__(self, image_view, label_fps, mpl_canvas=None):
        super().__init__(image_view, label_fps)
        self._frame_callback = None
        self.frames_by_name = {}
        self.profile_data = {}
        self.selected_frame = None
        self.mpl_canvas = mpl_canvas

    def set_selected_frame(self, name):
        """Switch which of the most recently received named frames is displayed."""
        self.selected_frame = name
        if name in self.frames_by_name:
            self._render(name)

    def _render(self, name):
        image = self.frames_by_name[name]
        if self.mpl_canvas is not None:
            if name == 'Density':
                self.mpl_canvas.show_density(image, **self.profile_data)
            else:
                self.mpl_canvas.show_frame(name, image)
        else:
            self._show(image, autolevel=True)
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

        # Read initial ROI/exposure and the display_mode from the connection table HDF5 so
        # the spinboxes start at the values the camera will actually be using, and so we
        # know upfront which display widgets to build.
        roi_w_init, roi_y0_init, roi_h_init = 2048, 1, 2048
        exposure_ms_init = 50.0
        display_mode = 'live'
        try:
            table = self.settings['connection_table']
            ct_props = table.find_by_name(self.device_name).properties
            display_mode = ct_props.get('display_mode', 'live')
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
        self._display_mode = display_mode
        is_absorption = display_mode == 'absorption'

        # In absorption mode, replace the pyqtgraph live view with an embedded matplotlib
        # panel (real colorbar, and x/y profile+fit plots for Density). matplotlib isn't
        # suited to the high update rate of continuous live view, so 'live' mode is left
        # exactly as the base class sets it up.
        self._mpl_canvas = None
        if is_absorption:
            self.image.hide()
            self._mpl_canvas = _AbsorptionCanvas()
            self.ui.horizontalLayout.addWidget(self._mpl_canvas)

            # Hide the Attributes/Snap/Continuous/Stop toolbar column (to the left of the
            # image in blacs_tab.ui). Snap/Continuous only ever update the now-hidden
            # pyqtgraph view, so they'd silently do nothing useful here; Attributes is
            # display-mode-agnostic but is bundled into the same toolbar, so it goes too.
            toolbar_widgets = [
                self.ui.pushButton_attributes,
                self.ui.pushButton_snap,
                self.ui.pushButton_continuous,
                self.ui.pushButton_stop,
                self.ui.doubleSpinBox_maxrate,
                self.ui.toolButton_nomax,
                self.ui.label_fps,
            ]
            for widget in toolbar_widgets:
                # Some of these had setRetainSizeWhenHidden(True) set by the base class
                # (so the layout doesn't jump around during live-mode acquisition toggles);
                # undo that here so the whole column actually collapses to zero width.
                size_policy = widget.sizePolicy()
                if hasattr(size_policy, 'setRetainSizeWhenHidden'):
                    size_policy.setRetainSizeWhenHidden(False)
                    widget.setSizePolicy(size_policy)
                widget.hide()

        # Replace the default ImageReceiver with one that keeps the histogram range fixed
        # (and, in absorption mode, renders into the matplotlib panel). Must happen before
        # initialise_workers() reads self.image_receiver.port.
        self.image_receiver.shutdown()
        self.image_receiver = _PCOImageReceiver(self.image, self.ui.label_fps, mpl_canvas=self._mpl_canvas)

        # --- mode label (own row) ---
        mode_text = "Absorption (last-shot OD/Density, with live fit)" if is_absorption else "Live"
        mode_label = QtWidgets.QLabel(f"Display mode: {mode_text}")
        mode_label.setStyleSheet("font-weight: bold;")
        self.get_tab_layout().addWidget(mode_label)

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

        # --- exposure row (live mode only; absorption shots use exposure_time from the
        # connection table's camera_attributes, not a manually-set live value) ---
        if not is_absorption:
            exposure_widget = QtWidgets.QWidget()
            exp_row = QtWidgets.QHBoxLayout()
            exp_row.setContentsMargins(4, 4, 4, 4)
            exposure_widget.setLayout(exp_row)

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

            self.get_tab_layout().addWidget(exposure_widget)

        # --- frame selector (absorption display_mode only) ---
        # Worker sends Dark/Light/Atoms/OD/Density together in one message each shot;
        # switching the dropdown just re-renders one already locally, no new data needed.
        if is_absorption:
            frame_row = QtWidgets.QWidget()
            frow = QtWidgets.QHBoxLayout()
            frow.setContentsMargins(4, 2, 4, 2)
            frame_row.setLayout(frow)
            frow.addWidget(QtWidgets.QLabel("Show frame:"))
            self._frame_selector = QtWidgets.QComboBox()
            self._frame_selector.addItems(['Dark', 'Light', 'Atoms', 'OD', 'Density'])
            self._frame_selector.setCurrentText('OD')
            self._frame_selector.currentTextChanged.connect(self.image_receiver.set_selected_frame)
            frow.addWidget(self._frame_selector)
            frow.addStretch()
            self.get_tab_layout().addWidget(frame_row)
            self.image_receiver.selected_frame = 'OD'

        # --- photon-count ROI (live mode only; it's a draggable pyqtgraph RectROI drawn
        # on the pyqtgraph live view, which absorption mode replaces with matplotlib) ---
        if not is_absorption:
            count_widget = QtWidgets.QWidget()
            count_row = QtWidgets.QHBoxLayout()
            count_row.setContentsMargins(4, 2, 4, 2)
            count_widget.setLayout(count_row)

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

            self.get_tab_layout().addWidget(count_widget)

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
