"""
Local path configuration for the lics Python codebase.

Copy this file to the repo root as `local_paths.py` and fill in the paths
for your machine. `local_paths.py` is gitignored (machine-specific).

Usage:
    from local_paths import local_path
    seq_file = local_path('lvseqread', year=2024, month=9, day=4, num=423)
    dump_file = local_path('lvseqdump', year=2024, month=9, day=4, num=423)
    img_file  = local_path('H', year=2024, month=9, day=4, num=1)
    param_dir = local_path('loadparams')
"""

# ---------------------------------------------------------------------------
# Path templates — callables take (year, month, day, num) keyword args;
# plain strings are returned as-is (no formatting needed).
# ---------------------------------------------------------------------------

_PATHS = {

    # Sequence file read path (mirrors localpath('lvseqread') in MATLAB)
    'lvseqread': lambda year, month, day, num: (
        f'//DESKTOP-L5NCGH6/Experimentalcontroll/ExpControl{year}/timingsettings/'
        f'{year}{month:02d}{day:02d}/{year}{month:02d}{day:02d}{num:04d}'
    ),

    # Sequence dump output path (mirrors localpath('lvseqdump') in MATLAB)
    'lvseqdump': lambda year, month, day, num: (
        f'/path/to/seq_dumps/{year}{month:02d}{day:02d}/'
        f'{year}{month:02d}{day:02d}{num:04d}_dump.txt'
    ),

    # Labscript conversion output path
    'lvconvert': lambda year, month, day, num: (
        f'/path/to/seq_converts/{year}{month:02d}{day:02d}/'
        f'{year}{month:02d}{day:02d}{num:04d}_convert.py'
    ),

    # Horizontal camera image path (mirrors localpath('H') in MATLAB)
    'H': lambda year, month, day, num: (
        f'/Users/your_username/Library/CloudStorage/Box-Box/CHIN_LICS/NAS_Data_Backup/'
        f'Data/{year:04d}{month:02d}{day:02d}/{year:04d}{month:02d}{day:02d}_{num}.mat'
    ),

    # Vertical camera image path (mirrors localpath('V') in MATLAB)
    'V': lambda year, month, day, num: (
        f'/Users/your_username/Library/CloudStorage/Box-Box/CHIN_LICS/NAS_Data_Backup/'
        f'V_Images/Data/{year:04d}/{month:02d}/'
        f'{year:04d}{month:02d}{day:02d}/{year:04d}{month:02d}{day:02d}_{num}.mat'
    ),

    # Param log folder for loading (mirrors localpath('loadparams') in MATLAB)
    'loadparams': '/Users/your_username/Library/CloudStorage/Box-Box/CHIN_LICS/NAS_Data_Backup/paramlogs',

    # Param save folder — set to None on non-lab machines to prevent remote writes
    # (mirrors the error in localpath('saveparams') on mac in MATLAB)
    'saveparams': None,
}


def local_path(path_type, year=None, month=None, day=None, num=None):
    """Return the configured local path for path_type, formatted with any provided args.

    Parameters
    ----------
    path_type : str
        One of: 'lvseqread', 'lvseqdump', 'H', 'V', 'loadparams', 'saveparams'
    year, month, day, num : int, optional
        Components used to format templated paths.

    Returns
    -------
    str
    """
    if path_type not in _PATHS:
        raise KeyError(f"Unknown path type '{path_type}'. Add it to local_paths.py.")
    entry = _PATHS[path_type]
    if entry is None:
        raise NotImplementedError(
            f"local_path('{path_type}') is not configured on this machine. "
            "Set it in local_paths.py if needed."
        )
    if callable(entry):
        return entry(year=year, month=month, day=day, num=num)
    return entry
