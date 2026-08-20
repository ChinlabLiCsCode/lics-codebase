import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lyse
import matplotlib.pyplot as plt
import mloop_config
import math
import numpy as np

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'mloop_configs', 'mloop_config_bias_currents.toml')

try:
    df = lyse.data()
    config = mloop_config.get(CONFIG_PATH)
    param_names = list(config['mloop_params'].keys())
    y_col = config['cost_key']
    ylabel = y_col[-1] if isinstance(y_col, tuple) else y_col
    maximize = config.get('maximize', True)

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
        print('Available result columns:', [c for c in subdf.columns if c[0] not in ('', 'globals')])
        raise KeyError(y_col)
    y = subdf[y_col].astype(float)
    n = len(param_names)
    params = {name: get_col(name) for name in param_names}

    best_idx = y.idxmax() if maximize else y.idxmin()
    best_vals = {name: float(params[name][best_idx]) for name in param_names}
    best_y = float(y[best_idx])

    tols = {
        name: 0.2 * (config['mloop_params'][name].max - config['mloop_params'][name].min)
        for name in param_names
    }

    ncols = math.ceil(math.sqrt(n))
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows), squeeze=False)
    axes_flat = axes.flatten()

    fig.suptitle(
        f'M-LOOP session: {mloop_session}   best {ylabel} = {best_y:.3g}\n'
        + '   '.join(f'{name}={best_vals[name]:.3g}' for name in param_names),
        fontsize=9
    )

    for i, name in enumerate(param_names):
        ax = axes_flat[i]
        x_i = params[name]

        near_others = np.ones(len(subdf), dtype=bool)
        for j, other in enumerate(param_names):
            if j != i:
                near_others &= (params[other] - best_vals[other]).abs() < tols[other]

        ax.scatter(x_i[~near_others], y[~near_others], color='lightgray', s=20, zorder=1,
                   label='all shots')
        ax.scatter(x_i[near_others], y[near_others], color=f'C{i}', s=50, zorder=2,
                   label='near optimal')
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
