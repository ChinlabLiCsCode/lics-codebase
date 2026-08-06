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

        layout = self.get_tab_layout()

        # Root: horizontal split — image view left, dashboard right
        outer = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout(outer)
        hbox.setContentsMargins(0, 0, 0, 0)

        # --- Left: image view with ROI and crosshair ---
        self.image_view = pg.ImageView()
        self.image_view.ui.roiBtn.hide()
        self.image_view.ui.menuBtn.hide()
        self.image_view.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        hbox.addWidget(self.image_view, stretch=3)

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
        self.image_view.getView().setMenuEnabled(False)
        self.image_view.getView().addItem(self.roi)

        self._row_line = pg.InfiniteLine(angle=0, pen=pg.mkPen('y', width=1))
        self._col_line = pg.InfiniteLine(angle=90, pen=pg.mkPen('y', width=1))
        self._row_line.hide()
        self._col_line.hide()
        self.image_view.getView().addItem(self._row_line)
        self.image_view.getView().addItem(self._col_line)
        self.image_view.getImageItem().scene().sigMouseClicked.connect(
            self._on_scene_clicked
        )

        # --- Right: dashboard ---
        dash = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(dash)
        vbox.setContentsMargins(4, 4, 4, 4)

        # Control buttons row
        btn_row = QtWidgets.QHBoxLayout()
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
        btn_row.addStretch()
        vbox.addLayout(btn_row)

        self._btn_continuous.clicked.connect(self._on_continuous_clicked)
        self._btn_stop.clicked.connect(self._on_stop_clicked)
        self._btn_snap.clicked.connect(self._on_snap_clicked)

        # Max fps spinner (controls how fast frames are sent to the tab)
        rate_row = QtWidgets.QHBoxLayout()
        rate_row.addWidget(QtWidgets.QLabel("Max fps:"))
        self._spin_maxfps = QtWidgets.QDoubleSpinBox()
        self._spin_maxfps.setRange(0.0, 200.0)
        self._spin_maxfps.setValue(10.0)
        self._spin_maxfps.setDecimals(1)
        self._spin_maxfps.setFixedWidth(70)
        rate_row.addWidget(self._spin_maxfps)
        rate_row.addStretch()
        vbox.addLayout(rate_row)
        self._spin_maxfps.valueChanged.connect(self._on_maxfps_changed)

        # Stats readout
        self._stats_label = QtWidgets.QLabel()
        self._stats_label.setStyleSheet("font-family: monospace;")
        self._stats_label.setWordWrap(True)
        vbox.addWidget(self._stats_label)

        # Exposure slider
        exp_row = QtWidgets.QHBoxLayout()
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
        vbox.addLayout(exp_row)
        self._exposure_slider.valueChanged.connect(self._on_exposure_changed)

        # Counts-history window slider
        win_row = QtWidgets.QHBoxLayout()
        win_row.addWidget(QtWidgets.QLabel("Window (s):"))
        self._window_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._window_slider.setMinimum(1)
        self._window_slider.setMaximum(120)
        self._window_slider.setValue(10)
        win_row.addWidget(self._window_slider)
        self._window_label = QtWidgets.QLabel("10 s")
        win_row.addWidget(self._window_label)
        vbox.addLayout(win_row)
        self._window_slider.valueChanged.connect(self._on_window_changed)

        # Counts history plot — _LockedPlotWidget blocks zoom/pan
        self._counts_plot = _LockedPlotWidget(title="Counts history")
        self._counts_plot.setLabel('bottom', 'seconds ago')
        self._counts_plot.enableAutoRange()
        self._counts_plot.setMouseEnabled(x=False, y=False)
        self._counts_curve = self._counts_plot.plot(pen=pg.mkPen('g', width=1))
        vbox.addWidget(self._counts_plot, stretch=1)

        # Reset / Save CSV buttons
        csv_row = QtWidgets.QHBoxLayout()
        btn_reset = QtWidgets.QPushButton("Reset")
        btn_csv = QtWidgets.QPushButton("Save CSV")
        csv_row.addWidget(btn_reset)
        csv_row.addWidget(btn_csv)
        csv_row.addStretch()
        vbox.addLayout(csv_row)
        btn_reset.clicked.connect(self._on_reset_counts)
        btn_csv.clicked.connect(self._on_save_csv)

        # Row / column profile plots
        self._row_plot = _LockedPlotWidget(title="Row profile")
        self._row_plot.setMouseEnabled(x=False, y=False)
        self._row_curve = self._row_plot.plot(pen=pg.mkPen('c', width=1))
        vbox.addWidget(self._row_plot, stretch=1)

        self._col_plot = _LockedPlotWidget(title="Column profile")
        self._col_plot.setMouseEnabled(x=False, y=False)
        self._col_curve = self._col_plot.plot(pen=pg.mkPen('c', width=1))
        vbox.addWidget(self._col_plot, stretch=1)

        hbox.addWidget(dash, stretch=2)
        layout.addWidget(outer)

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
            'colormap': repr(self.image_view.ui.histogram.gradient.saveState()),
        }

    def restore_save_data(self, save_data):
        self._spin_maxfps.setValue(save_data.get('max_fps', 10.0))
        self._window_slider.setValue(int(save_data.get('window_s', 10)))
        if 'exposure_us' in save_data:
            self._exposure_slider.setValue(int(save_data['exposure_us']))
        if 'colormap' in save_data:
            try:
                self.image_view.ui.histogram.gradient.restoreState(
                    ast.literal_eval(save_data['colormap'])
                )
            except Exception:
                pass
        if save_data.get('acquiring', False):
            self._on_continuous_clicked(None)

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
        vp = self.image_view.getView().mapSceneToView(event.scenePos())
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
        self.image_view.setImage(
            image.T,
            autoLevels=False,
            autoRange=first,
            autoHistogramRange=first,
        )
        if first:
            lo = float(np.percentile(image, 0.1))
            hi = float(np.percentile(image, 99.9))
            self.image_view.setLevels(lo, hi)
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

        # Stats label
        exp_us = self._exposure_slider.value()
        self._stats_label.setText(
            f"ROI {w}×{h} @ ({col0},{row0})   "
            f"counts={total:,}   mean={region.mean():.1f}   max={int(region.max())}\n"
            f"exposure: {exp_us / 1000:.2f} ms   {self._fps:.1f} fps"
        )

        # Counts history plot
        if len(self._counts_history) >= 2:
            xs = [t - now for t, _ in self._counts_history]
            ys = [v for _, v in self._counts_history]
            self._counts_curve.setData(xs, ys)

        # Row / column profiles
        if self._profile_point is not None:
            px, py = self._profile_point
            if (col0 <= px < col0 + w) and (row0 <= py < row0 + h):
                row_profile = image[py, col0:col0 + w]
                col_profile = image[row0:row0 + h, px]
                self._row_curve.setData(row_profile)
                self._col_curve.setData(col_profile)
                self._row_plot.setTitle(f"Row profile (y={py})")
                self._col_plot.setTitle(f"Column profile (x={px})")
                self._row_line.setPos(py)
                self._col_line.setPos(px)
                self._row_line.show()
                self._col_line.show()
                return
        self._row_curve.setData([])
        self._col_curve.setData([])
        self._row_plot.setTitle("Row profile")
        self._col_plot.setTitle("Column profile")
        self._row_line.hide()
        self._col_line.hide()

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
