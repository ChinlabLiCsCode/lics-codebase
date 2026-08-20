import json
import numpy as np
from time import perf_counter

import h5py
import labscript_utils.properties
import pyqtgraph as pg

from qtutils import inmain_decorator
from qtutils.qt import QtWidgets

from blacs.tab_base_classes import define_state, MODE_MANUAL
from labscript_devices.IMAQdxCamera.blacs_tabs import IMAQdxCameraTab, ImageReceiver, exp_av


class _PCOImageReceiver(ImageReceiver):
    """Like ImageReceiver but keeps the histogram x-axis fixed after the first frame
    so the min/max level handles don't visually drift during continuous acquisition."""

    def __init__(self, image_view, label_fps):
        super().__init__(image_view, label_fps)
        self._frame_callback = None

    @inmain_decorator(wait_for_return=True)
    def handler(self, data):
        self.send([b'ok'])
        md = json.loads(data[0])
        image = np.frombuffer(memoryview(data[1]), dtype=md['dtype'])
        image = image.reshape(md['shape'])
        if len(image.shape) == 3 and image.shape[0] == 1:
            image = image.reshape(image.shape[1:])
        this_frame_time = perf_counter()
        if self.last_frame_time is not None:
            dt = this_frame_time - self.last_frame_time
            if self.frame_rate is not None:
                self.frame_rate = exp_av(self.frame_rate, 1 / dt, dt, 1.0)
            else:
                self.frame_rate = 1 / dt
        self.last_frame_time = this_frame_time
        first = self.image_view.image is None
        self.image_view.setImage(
            image.swapaxes(-1, -2),
            autoRange=first,
            autoLevels=first,
            autoHistogramRange=first,
        )
        if self.frame_rate is not None:
            self.label_fps.setText(f"{self.frame_rate:.01f} fps")
        QtWidgets.QApplication.instance().sendPostedEvents()
        if self._frame_callback is not None:
            try:
                self._frame_callback()
            except Exception:
                pass
        return self.NO_RESPONSE


class PCOCameraTab(IMAQdxCameraTab):
    worker_class = 'lics_labscript_devices.PCOCamera.blacs_workers.PCOCameraWorker'

    def initialise_GUI(self):
        super().initialise_GUI()

        # Replace the default ImageReceiver with one that keeps the histogram range fixed.
        # Must happen before initialise_workers() reads self.image_receiver.port.
        self.image_receiver.shutdown()
        self.image_receiver = _PCOImageReceiver(self.image, self.ui.label_fps)

        # Read initial ROI and exposure from the connection table HDF5 so the spinboxes
        # start at the values the camera will actually be using.
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

        # --- build controls row ---
        # The PCO Panda reads out from both edges of the sensor simultaneously so the
        # horizontal ROI is always centred (x0 + x1 = 2049, width multiple of 8).
        # The vertical ROI is unconstrained: set y0 and height freely.
        controls = QtWidgets.QWidget()
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(4, 4, 4, 4)
        controls.setLayout(row)

        mode_text = "Absorption (last-shot OD)" if display_mode == 'absorption' else "Live"
        mode_label = QtWidgets.QLabel(f"Display mode: {mode_text}")
        mode_label.setStyleSheet("font-weight: bold;")
        row.addWidget(mode_label)
        row.addSpacing(16)

        row.addWidget(QtWidgets.QLabel("ROI:"))

        row.addWidget(QtWidgets.QLabel("W (x centred)"))
        self._roi_w = QtWidgets.QSpinBox()
        self._roi_w.setRange(64, 2048)
        self._roi_w.setSingleStep(8)
        self._roi_w.setValue(max(64, (roi_w_init // 8) * 8))
        self._roi_w.setFixedWidth(65)
        row.addWidget(self._roi_w)

        row.addWidget(QtWidgets.QLabel("y0"))
        self._roi_y0 = QtWidgets.QSpinBox()
        self._roi_y0.setRange(1, 2047)
        self._roi_y0.setValue(roi_y0_init)
        self._roi_y0.setFixedWidth(55)
        row.addWidget(self._roi_y0)

        row.addWidget(QtWidgets.QLabel("H"))
        self._roi_h = QtWidgets.QSpinBox()
        self._roi_h.setRange(1, 2048)
        self._roi_h.setValue(roi_h_init)
        self._roi_h.setFixedWidth(55)
        row.addWidget(self._roi_h)

        self._roi_coords_label = QtWidgets.QLabel()
        row.addWidget(self._roi_coords_label)

        btn_roi = QtWidgets.QPushButton("Apply ROI")
        btn_roi.clicked.connect(self._on_apply_roi)
        row.addWidget(btn_roi)

        row.addSpacing(16)

        # Exposure spinbox
        row.addWidget(QtWidgets.QLabel("Exposure (ms):"))
        self._exposure_spinbox = QtWidgets.QDoubleSpinBox()
        self._exposure_spinbox.setRange(0.001, 10000.0)
        self._exposure_spinbox.setDecimals(3)
        self._exposure_spinbox.setValue(exposure_ms_init)
        self._exposure_spinbox.setFixedWidth(90)
        row.addWidget(self._exposure_spinbox)

        btn_exp = QtWidgets.QPushButton("Apply Exposure")
        btn_exp.clicked.connect(self._on_apply_exposure)
        row.addWidget(btn_exp)

        row.addStretch()

        self._roi_w.valueChanged.connect(self._update_roi_label)
        self._roi_y0.valueChanged.connect(self._clamp_roi_h)
        self._roi_y0.valueChanged.connect(self._update_roi_label)
        self._roi_h.valueChanged.connect(self._update_roi_label)
        self._update_roi_label()

        self.get_tab_layout().addWidget(controls)

        # --- photon-count ROI ---
        # A draggable/resizable rectangle drawn on the live image.
        # Drag to move, drag handles to resize. Count updates on every move.
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
