"""Plot the results of an M-LOOP optimisation, for any number of parameters.

One panel per optimisation parameter, showing the cost against that parameter.
Shots taken near the best value of every *other* parameter are highlighted, so
each panel reads as a slice through the optimum rather than a scatter of the
whole search.

This replaces the per-optimisation scripts that used to live in
mloop_plotting/: the panel grid is built from whatever parameters the config
file declares, so switching optimisations only means pointing CONFIG_PATH at a
different config (the same one mloop_multishot.py is using).
"""

import math
import os

import lyse
import matplotlib.pyplot as plt
import numpy as np

import mloop_config

# Path to the config file, as in mloop_multishot.py.  Keep the two in step:
# this script plots the parameters named in whichever config it reads.
# None uses the default mloop_config.toml in this directory.
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'mloop_configs',
                           'mloop_config_zeeman_slower.toml')

# Fraction of each parameter's range counted as "near" its best value.  Widened
# automatically if that leaves too few shots to see, which happens easily once
# there are several parameters.
TOLERANCE = 0.2
MIN_HIGHLIGHTED = 3


def near_best(params, best_vals, ranges, exclude, n_shots):
    """Mask of shots close to the best value of every parameter but `exclude`.

    Returns ``(mask, tolerance)``.  The tolerance is widened until at least
    MIN_HIGHLIGHTED shots qualify, so a panel is never empty just because the
    search moved on in the other parameters.
    """
    others = [name for name in params if name != exclude]
    if not others:
        return np.ones(n_shots, dtype=bool), TOLERANCE

    for tolerance in (TOLERANCE, 2 * TOLERANCE, 3 * TOLERANCE):
        mask = np.ones(n_shots, dtype=bool)
        for name in others:
            mask &= (params[name] - best_vals[name]).abs() < tolerance * ranges[name]
        if mask.sum() >= MIN_HIGHLIGHTED:
            return mask, tolerance
    return mask, tolerance


try:
    df = lyse.data()
    config = mloop_config.get(CONFIG_PATH)
    param_names = list(config['mloop_params'].keys())
    y_col = config['cost_key']
    ylabel = y_col[-1] if isinstance(y_col, tuple) else y_col
    maximize = config.get('maximize', True)

    # Most recent M-LOOP session only, if the sessions are being tracked.
    try:
        gb = df.groupby(('mloop_session', ''))
        mloop_session = list(gb.groups.keys())[-1]
        subdf = gb.get_group(mloop_session)
    except Exception:
        subdf = df
        mloop_session = None

    def get_col(name):
        col = (name, '') if (name, '') in subdf.columns else name
        return subdf[col].astype(float)

    if y_col not in subdf.columns:
        print(f'Cost column {y_col} not found in dataframe.')
        print('Available result columns:',
              [c for c in subdf.columns if c[0] not in ('', 'globals')])
        raise KeyError(y_col)

    y = subdf[y_col].astype(float)
    params = {name: get_col(name) for name in param_names}
    n = len(param_names)

    best_idx = y.idxmax() if maximize else y.idxmin()
    best_vals = {name: float(params[name][best_idx]) for name in param_names}
    best_y = float(y[best_idx])

    ranges = {name: config['mloop_params'][name].max - config['mloop_params'][name].min
              for name in param_names}

    ncols = math.ceil(math.sqrt(n))
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows),
                             squeeze=False)
    axes_flat = axes.flatten()

    fig.suptitle(
        f'M-LOOP session: {mloop_session}   best {ylabel} = {best_y:.3g}\n'
        + '   '.join(f'{name}={best_vals[name]:.3g}' for name in param_names),
        fontsize=9,
    )

    for i, name in enumerate(param_names):
        ax = axes_flat[i]
        x_i = params[name]
        mask, tolerance = near_best(params, best_vals, ranges, name, len(subdf))

        ax.scatter(x_i[~mask], y[~mask], color='lightgray', s=20, zorder=1,
                   label='all shots')
        ax.scatter(x_i[mask], y[mask], color=f'C{i % 10}', s=50, zorder=2,
                   label=f'others within {tolerance:.0%} of best')
        ax.axvline(best_vals[name], color='red', linestyle='--', linewidth=1,
                   label=f'best={best_vals[name]:.3g}')
        ax.set_xlabel(name)
        ax.set_ylabel(ylabel)
        ax.set_title(f'{ylabel} vs {name}')
        ax.legend(fontsize=7)

    for j in range(n, len(axes_flat)):
        axes_flat[j].set_visible(False)

    plt.tight_layout()
    plt.show()

except Exception as e:
    import traceback
    print(f'plot_mloop_results error: {e}')
    traceback.print_exc()
