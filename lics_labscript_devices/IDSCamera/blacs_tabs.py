import ast
import csv
import json
import os
import time
from datetime import datetime

import numpy as np
import pyqtgraph as pg

from qtutils import inmain_decorator
from qtutils.qt import QtCore, QtWidgets

from blacs.tab_base_classes import define_state, MODE_MANUAL
from blacs.device_base_class import DeviceTab
from labscript_utils.ls_zprocess import ZMQServer

import labscript_utils.h5_lock
import h5py
import labscript_utils.properties


MIN_ROI_SIZE_PX = 20


class _LockedPlotWidget(pg.PlotWidget):
    """PlotWidget with all mouse zoom/pan disabled."""
    def wheelEvent(self, ev):
        ev.accept()  # intercept at QGraphicsView level before scene sees it


class _FrameReceiver(ZMQServer):
    """ZMQ REP server that receives raw camera frames from the worker,
    immediately sends b'ok', then calls on_frame on the GUI thread."""

    def __init__(self, on_frame):
        ZMQServer.__init__(self, port=None, dtype='multipart')
        self._on_frame = on_frame

    @inmain_decorator(wait_for_return=True)
    def handler(self, data):
        self.send([b'ok'])
        md = json.loads(data[0])
        image = np.frombuffer(memoryview(data[1]), dtype=md['dtype'])
        image = image.reshape(md['shape'])
        full_scale = md.get('full_scale', 65535)
        self._on_frame(image, full_scale)
        QtWidgets.QApplication.instance().sendPostedEvents()
        return self.NO_RESPONSE


class IDSCameraTab(DeviceTab):
    worker_class = 'lics_labscript_devices.IDSCamera.blacs_workers.IDSCameraWorker'

    # Fixed chrome sizes (px) for axes shared between two linked plots that pyqtgraph
    # wouldn't otherwise force to the same pixel geometry -- see the PCO camera's
    # _AbsorptionDisplay for the full explanation. Without this, e.g. col_plot's own
    # axis labels (which image_plot's hidden axis doesn't have) would eat a different
    # amount of space from each plot's cell, so even with a linked range the two
    # viewports end up different pixel sizes and a given row/column lands at different
    # screen offsets in each -- i.e. the profiles wouldn't visually line up with the image.
    _SHARED_BOTTOM_AXIS_HEIGHT = 30
    _SHARED_LEFT_AXIS_WIDTH = 50

    def initialise_GUI(self):
        self._acquiring = False
        self._levels_initialized = False
        self._last_shape = None
        self._last_roi_rect = None
        self._profile_point = None
        self._last_frame_time = None
        self._fps = 0.0
        self._counts_history = []   # list of (perf_counter, counts)
        self._counts_window_s = 10.0
        self._show_line_cuts = True

        layout = self.get_tab_layout()

        # --- image, with column profile alongside it and row profile below it ---
        # (same pg.GraphicsLayoutWidget + linked-PlotItem + HistogramLUTItem
        # arrangement as the PCO camera's absorption Density panel.)
        self._graphics = pg.GraphicsLayoutWidget()
        self._graphics.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self._graphics.setMinimumHeight(320)
        self._graphics.ci.layout.setContentsMargins(0, 0, 0, 0)

        self._col_plot = self._graphics.addPlot(row=0, col=0)
        self._image_plot = self._graphics.addPlot(row=0, col=1)
        self._hist = pg.HistogramLUTItem()
        self._graphics.addItem(self._hist, row=0, col=2)
        self._row_plot = self._graphics.addPlot(row=1, col=1)

        self._image_item = pg.ImageItem()
        self._image_plot.addItem(self._image_item)
        self._hist.setImageItem(self._image_item)
        self._image_plot.setAspectLocked(True)
        self._image_plot.showGrid(x=False, y=False)
        self._image_plot.setMenuEnabled(False)
        # pg.ImageView (what this used to be) inverts Y by default so row 0 appears at
        # the top, matching normal image-viewer conventions; match that here so the
        # camera view isn't suddenly upside down, and invert col_plot's Y the same way
        # so a given row lands at the same screen position in both (see class docstring).
        self._image_plot.getViewBox().invertY(True)
        self._col_plot.getViewBox().invertY(True)

        # image_plot shares its bottom axis with row_plot's (column position) and its
        # left axis with col_plot's (row position); showing its own duplicate tick
        # labels would be redundant, so hide the text (but keep a fixed height/width
        # matching its shared-axis neighbour).
        axis_bottom = self._image_plot.getAxis('bottom')
        axis_bottom.setStyle(showValues=False)
        axis_bottom.setHeight(self._SHARED_BOTTOM_AXIS_HEIGHT)
        axis_left = self._image_plot.getAxis('left')
        axis_left.setStyle(showValues=False)
        axis_left.setWidth(self._SHARED_LEFT_AXIS_WIDTH)

        self._row_plot.setXLink(self._image_plot)
        self._row_plot.setLabel('bottom', 'column')
        self._row_plot.getAxis('left').setWidth(self._SHARED_LEFT_AXIS_WIDTH)
        self._row_curve = self._row_plot.plot(pen=pg.mkPen('c', width=1))

        self._col_plot.setYLink(self._image_plot)
        self._col_plot.setLabel('left', 'row')
        self._col_plot.getAxis('bottom').setHeight(self._SHARED_BOTTOM_AXIS_HEIGHT)
        self._col_curve = self._col_plot.plot(pen=pg.mkPen('c', width=1))

        row_layout = self._graphics.ci.layout
        row_layout.setRowStretchFactor(0, 5)
        row_layout.setRowStretchFactor(1, 1)
        row_layout.setColumnStretchFactor(0, 1)
        row_layout.setColumnStretchFactor(1, 5)
        row_layout.setColumnStretchFactor(2, 1)

        self.roi = pg.RectROI(
            [50, 50], [200, 200],
            pen=pg.mkPen('g', width=2),
            handlePen=pg.mkPen('g', width=2),
        )
        self.roi.addScaleHandle([1, 1], [0, 0])
        self.roi.addScaleHandle([0, 0], [1, 1])
        self.roi.sigRegionChanged.connect(self._clamp_roi)
        # Restrict ROI to left-button so right-click reaches sigMouseClicked
        self.roi.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self._image_plot.addItem(self.roi)

        self._row_line = pg.InfiniteLine(angle=0, pen=pg.mkPen('y', width=1))
        self._col_line = pg.InfiniteLine(angle=90, pen=pg.mkPen('y', width=1))
        self._row_line.hide()
        self._col_line.hide()
        self._image_plot.addItem(self._row_line)
        self._image_plot.addItem(self._col_line)
        self._image_item.scene().sigMouseClicked.connect(self._on_scene_clicked)

        layout.addWidget(self._graphics, 3)

        # --- below the image: controls on the left, counts history alongside them ---
        bottom_widget = QtWidgets.QWidget()
        bottom_row = QtWidgets.QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_widget.setLayout(bottom_row)

        controls_widget = QtWidgets.QWidget()
        controls_col = QtWidgets.QVBoxLayout()
        controls_col.setContentsMargins(0, 0, 0, 0)
        controls_widget.setLayout(controls_col)
        bottom_row.addWidget(controls_widget, 1)

        btn_widget = QtWidgets.QWidget()
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setContentsMargins(4, 4, 4, 4)
        btn_widget.setLayout(btn_row)
        self._btn_continuous = QtWidgets.QPushButton("Continuous")
        self._btn_stop = QtWidgets.QPushButton("Stop")
        self._btn_snap = QtWidgets.QPushButton("Snap")
        self._label_fps = QtWidgets.QLabel()
        self._btn_stop.hide()
        self._label_fps.hide()
        btn_row.addWidget(self._btn_continuous)
        btn_row.addWidget(self._btn_stop)
        btn_row.addWidget(self._btn_snap)
        btn_row.addWidget(self._label_fps)
        btn_row.addSpacing(16)
        self._chk_line_cuts = QtWidgets.QCheckBox("Show line cuts")
        self._chk_line_cuts.setChecked(True)
        self._chk_line_cuts.toggled.connect(self._on_line_cuts_toggled)
        btn_row.addWidget(self._chk_line_cuts)
        btn_row.addStretch()
        controls_col.addWidget(btn_widget)

        self._btn_continuous.clicked.connect(self._on_continuous_clicked)
        self._btn_stop.clicked.connect(self._on_stop_clicked)
        self._btn_snap.clicked.connect(self._on_snap_clicked)

        # Max fps spinner (controls how fast frames are sent to the tab)
        rate_widget = QtWidgets.QWidget()
        rate_row = QtWidgets.QHBoxLayout()
        rate_row.setContentsMargins(4, 4, 4, 4)
        rate_widget.setLayout(rate_row)
        rate_row.addWidget(QtWidgets.QLabel("Max fps:"))
        self._spin_maxfps = QtWidgets.QDoubleSpinBox()
        self._spin_maxfps.setRange(0.0, 200.0)
        self._spin_maxfps.setValue(10.0)
        self._spin_maxfps.setDecimals(1)
        self._spin_maxfps.setFixedWidth(70)
        rate_row.addWidget(self._spin_maxfps)
        rate_row.addStretch()
        controls_col.addWidget(rate_widget)
        self._spin_maxfps.valueChanged.connect(self._on_maxfps_changed)

        # Exposure slider
        exp_widget = QtWidgets.QWidget()
        exp_row = QtWidgets.QHBoxLayout()
        exp_row.setContentsMargins(4, 4, 4, 4)
        exp_widget.setLayout(exp_row)
        exp_row.addWidget(QtWidgets.QLabel("Exposure:"))
        self._exposure_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        # Range in microseconds — updated in restore_save_data if known;
        # these defaults cover 0.01 ms to 500 ms.
        self._exposure_slider.setMinimum(10)
        self._exposure_slider.setMaximum(500000)
        self._exposure_slider.setValue(10000)   # 10 ms
        exp_row.addWidget(self._exposure_slider)
        self._exposure_label = QtWidgets.QLabel("10.0 ms")
        exp_row.addWidget(self._exposure_label)
        controls_col.addWidget(exp_widget)
        self._exposure_slider.valueChanged.connect(self._on_exposure_changed)

        # Counts-history window slider
        win_widget = QtWidgets.QWidget()
        win_row = QtWidgets.QHBoxLayout()
        win_row.setContentsMargins(4, 4, 4, 4)
        win_widget.setLayout(win_row)
        win_row.addWidget(QtWidgets.QLabel("Window (s):"))
        self._window_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._window_slider.setMinimum(1)
        self._window_slider.setMaximum(120)
        self._window_slider.setValue(10)
        win_row.addWidget(self._window_slider)
        self._window_label = QtWidgets.QLabel("10 s")
        win_row.addWidget(self._window_label)
        controls_col.addWidget(win_widget)
        self._window_slider.valueChanged.connect(self._on_window_changed)

        # Stats readout
        self._stats_label = QtWidgets.QLabel()
        self._stats_label.setStyleSheet("font-family: monospace;")
        self._stats_label.setWordWrap(True)
        controls_col.addWidget(self._stats_label)

        # Reset / Save CSV buttons
        csv_widget = QtWidgets.QWidget()
        csv_row = QtWidgets.QHBoxLayout()
        csv_row.setContentsMargins(4, 4, 4, 4)
        csv_widget.setLayout(csv_row)
        btn_reset = QtWidgets.QPushButton("Reset")
        btn_csv = QtWidgets.QPushButton("Save CSV")
        csv_row.addWidget(btn_reset)
        csv_row.addWidget(btn_csv)
        csv_row.addStretch()
        controls_col.addWidget(csv_widget)
        btn_reset.clicked.connect(self._on_reset_counts)
        btn_csv.clicked.connect(self._on_save_csv)
        controls_col.addStretch()

        # --- counts history plot, alongside the controls above (not below them) ---
        self._counts_plot = _LockedPlotWidget(title="Counts history")
        self._counts_plot.setLabel('bottom', 'seconds ago')
        self._counts_plot.enableAutoRange()
        self._counts_plot.setMouseEnabled(x=False, y=False)
        self._counts_curve = self._counts_plot.plot(pen=pg.mkPen('g', width=1))
        bottom_row.addWidget(self._counts_plot, 1)

        layout.addWidget(bottom_widget, 1)

        # ZMQ server that receives frames from the worker
        self._frame_receiver = _FrameReceiver(self._on_frame)

        self.supports_smart_programming(False)

    def initialise_workers(self):
        table = self.settings['connection_table']
        props = table.find_by_name(self.device_name).properties
        kwargs = {
            'serial_number': props['serial_number'],
            'orientation': props['orientation'],
            'manual_mode_exposure_time_ms': props['manual_mode_exposure_time_ms'],
            'throughput_limit_mbps': props['throughput_limit_mbps'],
            'mock': props['mock'],
            'roi': props.get('roi', None),
            'save_mode': props.get('save_mode', 'images'),
            'image_receiver_port': self._frame_receiver.port,
        }
        self.create_worker('main_worker', self.worker_class, kwargs)
        self.primary_worker = 'main_worker'

    # ------------------------------------------------------------------ #
    # BLACS tab persistence                                                #
    # ------------------------------------------------------------------ #

    def get_save_data(self):
        return {
            'acquiring': self._acquiring,
            'max_fps': self._spin_maxfps.value(),
            'exposure_us': self._exposure_slider.value(),
            'window_s': self._window_slider.value(),
            'colormap': repr(self._hist.gradient.saveState()),
            'roi_geometry': self._roi_geometry(self.roi),
            'show_line_cuts': self._chk_line_cuts.isChecked(),
        }

    def restore_save_data(self, save_data):
        self._spin_maxfps.setValue(save_data.get('max_fps', 10.0))
        self._window_slider.setValue(int(save_data.get('window_s', 10)))
        if 'exposure_us' in save_data:
            self._exposure_slider.setValue(int(save_data['exposure_us']))
        if 'colormap' in save_data:
            try:
                self._hist.gradient.restoreState(
                    ast.literal_eval(save_data['colormap'])
                )
            except Exception:
                pass
        roi_geom = save_data.get('roi_geometry')
        if roi_geom:
            x, y, w, h = roi_geom
            self.roi.setPos((x, y), update=False)
            self.roi.setSize((w, h))
        # Triggers _on_line_cuts_toggled (a no-op if already checked, which is fine
        # since that's the default too).
        self._chk_line_cuts.setChecked(save_data.get('show_line_cuts', True))
        if save_data.get('acquiring', False):
            self._on_continuous_clicked(None)

    @staticmethod
    def _roi_geometry(roi_item):
        """(x, y, w, h) of a draggable RectROI, for save/restore of its exact position
        and size."""
        pos = roi_item.pos()
        size = roi_item.size()
        return (pos.x(), pos.y(), size.x(), size.y())

    # ------------------------------------------------------------------ #
    # ROI helpers                                                          #
    # ------------------------------------------------------------------ #

    def _clamp_roi(self):
        s = self.roi.size()
        nw = max(MIN_ROI_SIZE_PX, s.x())
        nh = max(MIN_ROI_SIZE_PX, s.y())
        if (nw, nh) != (s.x(), s.y()):
            self.roi.setSize([nw, nh])

    def _current_roi_rect(self):
        """Return (col0, row0, w, h) in pixel coords, or None before first frame."""
        if self._last_shape is None:
            return None
        height, width = self._last_shape
        pos = self.roi.pos()
        size = self.roi.size()
        col0 = int(max(0, min(pos.x(), width - 1)))
        row0 = int(max(0, min(pos.y(), height - 1)))
        w = int(max(MIN_ROI_SIZE_PX, min(size.x(), width - col0)))
        h = int(max(MIN_ROI_SIZE_PX, min(size.y(), height - row0)))
        return col0, row0, w, h

    def _on_scene_clicked(self, event):
        """Right-click inside the ROI picks a profile point."""
        if event.button() != QtCore.Qt.RightButton:
            return
        roi_rect = self._current_roi_rect()
        if roi_rect is None:
            return
        vp = self._image_plot.getViewBox().mapSceneToView(event.scenePos())
        col, row = int(vp.x()), int(vp.y())
        col0, row0, w, h = roi_rect
        if col0 <= col < col0 + w and row0 <= row < row0 + h:
            self._profile_point = (col, row)

    # ------------------------------------------------------------------ #
    # Frame handler — called on the GUI thread via _FrameReceiver          #
    # ------------------------------------------------------------------ #

    def _on_frame(self, image, full_scale):
        """Update all UI elements for one received frame."""
        # A stack (e.g. from transition_to_manual) — show the last frame
        if len(image.shape) == 3:
            image = image[-1]

        self._last_shape = image.shape   # (H, W)
        now = time.perf_counter()

        # FPS estimate
        if self._last_frame_time is not None:
            dt = now - self._last_frame_time
            if dt > 0:
                inst = 1.0 / dt
                self._fps = inst if self._fps == 0.0 else 0.1 * inst + 0.9 * self._fps
                self._label_fps.setText(f"{self._fps:.1f} fps")
        self._last_frame_time = now

        # Image display — pyqtgraph wants (W, H) axis order
        first = not self._levels_initialized
        self._image_item.setImage(image.T, autoLevels=False)
        if first:
            self._image_plot.autoRange()
            lo = float(np.percentile(image, 0.1))
            hi = float(np.percentile(image, 99.9))
            self._hist.setLevels(lo, hi)
            self._levels_initialized = True

        # ROI counts
        roi_rect = self._current_roi_rect()
        if roi_rect is None:
            return

        if roi_rect != self._last_roi_rect:
            self._counts_history.clear()
            self._profile_point = None
            self._last_roi_rect = roi_rect

        col0, row0, w, h = roi_rect
        region = image[row0:row0 + h, col0:col0 + w]
        total = int(region.sum())
        self._counts_history.append((now, total))

        # Prune history older than the time window
        cutoff = now - self._counts_window_s
        while self._counts_history and self._counts_history[0][0] < cutoff:
            self._counts_history.pop(0)

        # Row / column profiles. Deliberately not shown as plot titles: row_plot/col_plot
        # are pixel-aligned with image_plot via fixed shared axis chrome (see class
        # docstring) which depends on neither having a title -- image_plot never gets
        # one, so giving row_plot/col_plot one here (even conditionally) would eat extra
        # height/width only from their own cells and throw the alignment off. The picked
        # point is reported in the stats label below instead.
        profile_text = ""
        if self._profile_point is not None:
            px, py = self._profile_point
            if (col0 <= px < col0 + w) and (row0 <= py < row0 + h):
                row_profile = image[py, col0:col0 + w]
                col_profile = image[row0:row0 + h, px]
                self._row_curve.setData(np.arange(col0, col0 + w), row_profile)
                self._col_curve.setData(col_profile, np.arange(row0, row0 + h))
                # Crosshairs are meaningless without the corresponding plots visible.
                if self._show_line_cuts:
                    self._row_line.setPos(py)
                    self._col_line.setPos(px)
                    self._row_line.show()
                    self._col_line.show()
                else:
                    self._row_line.hide()
                    self._col_line.hide()
                profile_text = f"   profile point: ({px}, {py})"
            else:
                self._row_curve.setData([])
                self._col_curve.setData([])
                self._row_line.hide()
                self._col_line.hide()
        else:
            self._row_curve.setData([])
            self._col_curve.setData([])
            self._row_line.hide()
            self._col_line.hide()

        # Stats label
        exp_us = self._exposure_slider.value()
        self._stats_label.setText(
            f"ROI {w}×{h} @ ({col0},{row0})   "
            f"counts={total:,}   mean={region.mean():.1f}   max={int(region.max())}\n"
            f"exposure: {exp_us / 1000:.2f} ms   {self._fps:.1f} fps{profile_text}"
        )

        # Counts history plot
        if len(self._counts_history) >= 2:
            xs = [t - now for t, _ in self._counts_history]
            ys = [v for _, v in self._counts_history]
            self._counts_curve.setData(xs, ys)

    # ------------------------------------------------------------------ #
    # Button / slider handlers                                             #
    # ------------------------------------------------------------------ #

    def _on_continuous_clicked(self, _btn):
        self._btn_snap.setEnabled(False)
        self._btn_continuous.hide()
        self._btn_stop.show()
        self._label_fps.show()
        self._label_fps.setText('? fps')
        self._acquiring = True
        fps = self._spin_maxfps.value()
        dt = 1.0 / fps if fps else 0.0
        self._start_continuous(dt)

    def _on_stop_clicked(self, _btn):
        self._btn_snap.setEnabled(True)
        self._btn_continuous.show()
        self._btn_stop.hide()
        self._label_fps.hide()
        self._acquiring = False
        self._stop_continuous()

    def _on_snap_clicked(self, _btn):
        self._snap()

    def _on_exposure_changed(self, value_us):
        self._exposure_label.setText(f"{value_us / 1000:.2f} ms")
        self._set_exposure(value_us)

    def _on_window_changed(self, value):
        self._counts_window_s = float(value)
        self._window_label.setText(f"{value} s")

    def _on_line_cuts_toggled(self, checked):
        self._show_line_cuts = checked
        row_layout = self._graphics.ci.layout
        axis_bottom = self._image_plot.getAxis('bottom')
        axis_left = self._image_plot.getAxis('left')
        if checked:
            # Just calling .setVisible(True)/stretch factor 1 back on col_plot/row_plot
            # is not enough to make image_plot expand to fill their space when they're
            # hidden -- a hidden-but-still-in-the-layout PlotItem keeps reserving its
            # column/row's minimum size regardless of stretch factor, so it has to be
            # fully removed from the layout (see the 'else' branch). Re-adding it here
            # loses the axis link pyqtgraph set up, so that has to be redone too.
            self._graphics.addItem(self._col_plot, row=0, col=0)
            self._graphics.addItem(self._row_plot, row=1, col=1)
            self._col_plot.setYLink(self._image_plot)
            self._row_plot.setXLink(self._image_plot)
            axis_bottom.setHeight(self._SHARED_BOTTOM_AXIS_HEIGHT)
            axis_left.setWidth(self._SHARED_LEFT_AXIS_WIDTH)
            row_layout.setRowStretchFactor(1, 1)
            row_layout.setColumnStretchFactor(0, 1)
        else:
            self._graphics.removeItem(self._col_plot)
            self._graphics.removeItem(self._row_plot)
            self._row_line.hide()
            self._col_line.hide()
            # image_plot's own bottom/left axis are fixed to the same size as row_plot's/
            # col_plot's (so the three stay pixel-aligned while all shown -- see class
            # docstring); with those hidden there's nothing left to align with, and that
            # fixed reservation is exactly what stopped the image from expanding into
            # their freed space, so shrink it down to (near) nothing too.
            axis_bottom.setHeight(1)
            axis_left.setWidth(1)
            row_layout.setRowStretchFactor(1, 0)
            row_layout.setColumnStretchFactor(0, 0)

    def _on_maxfps_changed(self, fps):
        if self._acquiring:
            self._stop_continuous()
            dt = 1.0 / fps if fps else 0.0
            self._start_continuous(dt)

    def _on_reset_counts(self):
        self._counts_history.clear()
        self._counts_curve.setData([], [])

    def _on_save_csv(self):
        samples = list(self._counts_history)
        if not samples:
            return
        now = time.perf_counter()
        roi_rect = self._current_roi_rect()
        path = os.path.abspath(datetime.now().strftime("ids_counts_%Y%m%d_%H%M%S.csv"))
        with open(path, 'w', newline='') as f:
            if roi_rect:
                f.write(f'# roi: {roi_rect}\n')
            writer = csv.writer(f)
            writer.writerow(['seconds_ago', 'counts'])
            for t, v in samples:
                writer.writerow([f'{now - t:.3f}', v])
        print(f"Saved {len(samples)} samples to {path}")

    # ------------------------------------------------------------------ #
    # BLACS define_state wrappers for worker method calls                  #
    # ------------------------------------------------------------------ #

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _start_continuous(self, dt):
        yield (self.queue_work(self.primary_worker, 'start_continuous', dt))

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _stop_continuous(self):
        yield (self.queue_work(self.primary_worker, 'stop_continuous'))

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _snap(self):
        yield (self.queue_work(self.primary_worker, 'snap'))

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def _set_exposure(self, value_us):
        yield (self.queue_work(self.primary_worker, 'set_exposure', value_us))

    # ------------------------------------------------------------------ #
    # Tab lifecycle                                                        #
    # ------------------------------------------------------------------ #

    def restart(self, *args, **kwargs):
        self._frame_receiver.shutdown()
        return DeviceTab.restart(self, *args, **kwargs)
