import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from labscript_utils.labconfig import LabConfig
from lyse.dataframe_utilities import get_dataframe_from_shots, get_series_from_shot


def _sequence_folder(year, month, day, sequence, number):
    """Return the path to a sequence folder using experiment_shot_storage from labconfig."""
    labconfig = LabConfig()
    storage = labconfig.get('DEFAULT', 'experiment_shot_storage')
    return os.path.join(storage, sequence, f'{year:04d}', f'{month:02d}', f'{day:02d}', f'{number:04d}')


def _find_h5_files(folder):
    h5_files = sorted(glob.glob(os.path.join(folder, '*.h5')))
    if not h5_files:
        raise FileNotFoundError(f'No h5 files found in {folder}')
    return h5_files


def load_shot(year, month, day, sequence, number):
    """Load the first shot from the specified sequence folder.

    Returns a pandas Series containing globals and any saved results.
    """
    folder = _sequence_folder(year, month, day, sequence, number)
    h5_files = _find_h5_files(folder)
    return get_series_from_shot(h5_files[0])


def load_scan(year, month, day, sequence, number):
    """Load all shots from the specified sequence folder as a DataFrame.

    Autodetects all h5 files in the folder, sorted by filename.
    """
    folder = _sequence_folder(year, month, day, sequence, number)
    h5_files = _find_h5_files(folder)
    return get_dataframe_from_shots(h5_files)


# testing:
if __name__ == '__main__':
    shot = load_shot(2026, 8, 10, 'cs_mot_healthcheck', 39)
    print('load_shot keys:', shot.index.tolist())

    scan = load_scan(2026, 8, 10, 'cs_mot_healthcheck', 40)
    print('load_scan shape:', scan.shape)
    print('load_scan columns:', scan.columns.tolist())
