import numpy as np
import labscript_utils.h5_lock
import h5py
from labscript import Device, set_passed_properties


class IDSCamera(Device):
    """IDS Peak USB3 camera for fluorescence imaging.

    The camera runs continuously (free-running) throughout the experiment.
    All frames captured between the start and end of each shot are saved to
    the HDF5 file as a stack under images/{orientation}/. No per-shot
    sequence instructions are needed — just declare the device here.

    Typical connection table usage::

        IDSCamera(
            name='ids_fluoro',
            serial_number='XXXXXXXXXX',          # from IDS Cockpit / device label
            orientation='fluorescence',          # subfolder in images/
            manual_mode_exposure_time_ms=10.0,   # live-view exposure (BLACS slider)
            throughput_limit_mbps=200.0,         # USB3 link cap (tune to avoid corruption)
        )

    Accessing images in lyse::

        f = open_hdf5_file(run)                  # run is a pandas Series with h5 path
        images = f['images/fluorescence/images'][:]   # shape (N, H, W), uint16
        times  = f['images/fluorescence/timestamps'][:] # seconds from shot start
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
