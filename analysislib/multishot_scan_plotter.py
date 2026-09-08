import lyse
import numpy as np
import matplotlib.pyplot as plt

# Column lookup lives in helperfuncs so this routine and the notebook helpers
# resolve keys identically -- including the ROUTINE_PRIORITY fallback that lets
# a bare result name find its routine. lyse runs routines with their own folder
# as sys.path[0], notebooks import the package from the repo root.
try:
    from analysislib.helperfuncs import (
        get_column, col_label, find_scanned_globals, _column_with_errors,
    )
except ImportError:
    from helperfuncs import (
        get_column, col_label, find_scanned_globals, _column_with_errors,
    )

# ── Configuration ─────────────────────────────────────────────────────────────
# Results to plot. Each entry is a column key into the lyse DataFrame:
#   - plain string  → matched against the innermost column label
#   - tuple         → ('routine_filename_without_py', 'result_name')
RESULT_KEYS = [
    ('absorption_image_analysis', 'Atom Number'),
    # ('mot_loading_counts_analysis', 'b (s)'),
]

# Globals to use as the x-axis. Leave empty to auto-detect (any numeric global
# that varies across shots in the current sequence).
SCAN_KEYS = []

# How many recent sequences to include (None = all loaded shots).
N_SEQUENCES = None
# ─────────────────────────────────────────────────────────────────────────────


df = lyse.data(n_sequences=N_SEQUENCES)

if df.empty:
    print('No shots in lyse DataFrame.')
    raise SystemExit

scan_keys = SCAN_KEYS if SCAN_KEYS else find_scanned_globals(df)
if not scan_keys:
    print('No varying numeric globals found. Set SCAN_KEYS explicitly.')
    raise SystemExit
if not SCAN_KEYS:
    print(f'Auto-detected scan parameters: {[col_label(k) for k in scan_keys]}')

n_results = len(RESULT_KEYS)
n_scans = len(scan_keys)

fig, axes = plt.subplots(
    n_results, n_scans,
    figsize=(5 * n_scans, 4 * n_results),
    squeeze=False,
)
fig.suptitle('Multi-shot scan results', fontsize=13)

for row, rkey in enumerate(RESULT_KEYS):
    try:
        # also picks up the u_<result_name> column from the same routine
        y, yerr = _column_with_errors(df, rkey)
    except (KeyError, TypeError) as e:
        print(f'Skipping result {rkey!r}: {e}')
        for ax in axes[row]:
            ax.set_visible(False)
        continue
    ylabel = col_label(rkey)

    for col, skey in enumerate(scan_keys):
        ax = axes[row][col]
        try:
            x = get_column(df, skey).astype(float)
        except (KeyError, TypeError) as e:
            print(f'Skipping scan key {skey!r}: {e}')
            ax.set_visible(False)
            continue
        xlabel = col_label(skey)

        valid = x.notna() & y.notna()
        xv, yv = x[valid].values, y[valid].values
        yev = yerr[valid].values if yerr is not None else None

        order = np.argsort(xv)
        ax.errorbar(xv[order], yv[order], yerr=yev[order] if yev is not None else None,
                    fmt='o-', capsize=4, linewidth=1.5)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(f'{ylabel} vs {xlabel}')

plt.tight_layout()
plt.show()
