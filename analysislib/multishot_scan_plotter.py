import lyse
import numpy as np
import matplotlib.pyplot as plt

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


def get_column(df, key):
    """Return a Series from df by string name or (routine, result) tuple.

    In lyse's DataFrame, globals are stored as (global_name, '') tuples.
    When key is a plain string, also tries the (key, '') form used for globals.
    Raises KeyError if the column is missing or ambiguous.
    """
    if key in df.columns:
        return df[key]
    if isinstance(key, str):
        # Globals are stored as (name, '') in lyse
        if (key, '') in df.columns:
            return df[(key, '')]
        matches = [c for c in df.columns if (isinstance(c, tuple) and c[-1] == key) or c == key]
        if len(matches) == 1:
            return df[matches[0]]
        if len(matches) > 1:
            raise KeyError(f"Ambiguous key {key!r} — matches {matches}. Use a tuple.")
    raise KeyError(f"Column {key!r} not found in lyse DataFrame.")


def col_label(key):
    """Return a human-readable label for a DataFrame column key.

    Globals are (name, '') tuples so we read index 0; results are
    (routine, name) tuples so we read index -1.
    """
    if isinstance(key, tuple):
        return key[0] if key[-1] == '' else key[-1]
    return key


def find_scanned_globals(df):
    """Return column keys for numeric globals that vary across shots.

    In lyse, globals are stored as (global_name, '') MultiIndex columns.
    Result columns have a non-empty second level (the result name).
    """
    meta = {'filepath', 'sequence_index', 'run number', 'run repeat', 'sequence', 'run'}
    scanned = []
    for col in df.columns:
        # Only consider globals: tuples whose second element is ''
        if not (isinstance(col, tuple) and col[-1] == ''):
            continue
        name = col[0]
        if name in meta:
            continue
        try:
            vals = df[col].dropna()
            if np.issubdtype(vals.dtype, np.number) and vals.nunique() >= 2:
                scanned.append(col)
        except Exception:
            pass
    return scanned


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
        y = get_column(df, rkey).astype(float)
    except (KeyError, TypeError) as e:
        print(f'Skipping result {rkey!r}: {e}')
        for ax in axes[row]:
            ax.set_visible(False)
        continue
    ylabel = col_label(rkey)

    # Uncertainty column: u_<result_name> in the same routine group
    u_key = (rkey[0], 'u_' + rkey[-1]) if isinstance(rkey, tuple) else 'u_' + rkey
    try:
        yerr = get_column(df, u_key).astype(float)
    except (KeyError, TypeError):
        yerr = None

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
