import numpy as np
import labscript_utils.h5_lock
import h5py
from labscript import Device, set_passed_properties


class IDSCamera(Device):
    """IDS Peak USB3 camera for fluorescence imaging.

    The camera runs continuously (free-running) throughout the experiment.
    Everything captured between the start and end of each shot is saved to the
    HDF5 file. No per-shot sequence instructions are needed — just declare the
    device here.

    ``save_mode`` chooses what gets written, and is the only switch there is::

        'images'  (default)  the full frame stack, as images/…/images
        'counts'             one whole-frame sum per frame, as images/…/counts

    The two are mutually exclusive: a shot has one or the other, never both.
    ``save_mode`` is a connection-table property, so changing it means
    recompiling the connection table *and* restarting the BLACS tab — there is
    no per-shot or GUI control. Note that 'counts' sums whatever the sensor
    delivers; the only way to restrict it to a region is the hardware ``roi``
    crop below. The draggable ROI in the BLACS tab affects the live plot only.

    Typical connection table usage::

        IDSCamera(
            name='ids_fluoro',
            serial_number='XXXXXXXXXX',          # from IDS Cockpit / device label
            orientation='fluorescence',          # subfolder in images/
            manual_mode_exposure_time_ms=10.0,   # live-view exposure (BLACS slider)
            throughput_limit_mbps=200.0,         # USB3 link cap (tune to avoid corruption)
            save_mode='counts',                  # 'images' or 'counts'
            roi=(640, 459, 304, 300),            # sensor crop (x, y, w, h); None = full
        )

    Reading a shot. Note the device name is part of the path — the group is
    images/{device_name}/{orientation}/::

        shot = hf.load_shot(2026, 9, 11, 'cs_molasses_healthcheck', 75)
        counts = shot['counts']       # or 'images', per save_mode
        times  = shot['timestamps']

    ``timestamps`` are seconds from the master pseudoclock start, so frames
    recorded between BLACS programming the shot and the sequence actually
    starting carry negative times. They are real elapsed seconds, while
    time_markers are in labscript time: a wait stops the clock without
    advancing labscript time, so use ``hf.Shot.marker_times()`` to put markers
    on this time base. Shots taken before this convention have no 'time_base'
    attribute on the group and are measured from BLACS programming time.
    """

    description = 'IDS Peak Camera'
    allowed_children = []

    @set_passed_properties(
        property_names={
            'connection_table_properties': [
                'serial_number',
                'orientation',
                'manual_mode_exposure_time_ms',
                'throughput_limit_mbps',
                'mock',
                'roi',
                'save_mode',
            ],
            'device_properties': [],
        }
    )
    def __init__(
        self,
        name,
        parent_device=None,
        connection='',
        serial_number=None,
        manual_mode_exposure_time_ms=10.0,
        throughput_limit_mbps=200.0,
        orientation=None,
        mock=False,
        roi=None,
        save_mode='images',
        **kwargs,
    ):
        Device.__init__(self, name, parent_device, connection, **kwargs)
        self.BLACS_connection = str(serial_number) if serial_number else name
        self.orientation = orientation or name

    def generate_code(self, hdf5_file):
        Device.generate_code(self, hdf5_file)
        # No per-shot instructions; the BLACS worker records all frames autonomously.
        # Still call init_device_group so BLACS can find the device properties group.
        self.init_device_group(hdf5_file)
