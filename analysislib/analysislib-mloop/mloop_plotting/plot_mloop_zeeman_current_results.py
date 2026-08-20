import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lyse
import matplotlib.pyplot as plt
import mloop_config
import numpy as np

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'mloop_configs', 'mloop_config_zeeman_currents.toml')

try:
    df = lyse.data()
    config = mloop_config.get(CONFIG_PATH)
    param_names = list(config['mloop_params'].keys())
    y_col = config['cost_key']
    ylabel = y_col[-1] if isinstance(y_col, tuple) else y_col

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

    y = subdf[y_col].astype(float)

    if len(param_names) < 2:
        x = get_col(param_names[0])
        plt.figure()
        plt.scatter(x, y)
        plt.xlabel(param_names[0])
        plt.ylabel(ylabel)
        plt.title(f'M-LOOP session: {mloop_session}')
        plt.show()

    else:
        p1_name, p2_name = param_names[0], param_names[1]
        p1 = get_col(p1_name)
        p2 = get_col(p2_name)

        best_idx = y.idxmax()
        best_p1 = float(p1[best_idx])
        best_p2 = float(p2[best_idx])
        best_y  = float(y[best_idx])

        p1_range = config['mloop_params'][p1_name].max - config['mloop_params'][p1_name].min
        p2_range = config['mloop_params'][p2_name].max - config['mloop_params'][p2_name].min
        tol1 = 0.2 * p1_range
        tol2 = 0.2 * p2_range

        near_p2 = (p2 - best_p2).abs() < tol2
        near_p1 = (p1 - best_p1).abs() < tol1

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        fig.suptitle(f'M-LOOP session: {mloop_session}   '
                     f'best {ylabel} = {best_y:.3g} '
                     f'at {p1_name}={best_p1:.3g}, {p2_name}={best_p2:.3g}')

        ax1.scatter(p1[~near_p2], y[~near_p2], color='lightgray', s=20, zorder=1, label='all shots')
        ax1.scatter(p1[near_p2], y[near_p2], color='C0', s=50, zorder=2,
                    label=f'{p2_name} ≈ {best_p2:.3g} (±{tol2:.2g})')
        ax1.axvline(best_p1, color='red', linestyle='--', linewidth=1, label=f'best = {best_p1:.3g}')
        ax1.set_xlabel(p1_name)
        ax1.set_ylabel(ylabel)
        ax1.set_title(f'{ylabel} vs {p1_name}\nat optimal {p2_name} = {best_p2:.3g}')
        ax1.legend(fontsize=8)

        ax2.scatter(p2[~near_p1], y[~near_p1], color='lightgray', s=20, zorder=1, label='all shots')
        ax2.scatter(p2[near_p1], y[near_p1], color='C1', s=50, zorder=2,
                    label=f'{p1_name} ≈ {best_p1:.3g} (±{tol1:.2g})')
        ax2.axvline(best_p2, color='red', linestyle='--', linewidth=1, label=f'best = {best_p2:.3g}')
        ax2.set_xlabel(p2_name)
        ax2.set_ylabel(ylabel)
        ax2.set_title(f'{ylabel} vs {p2_name}\nat optimal {p1_name} = {best_p1:.3g}')
        ax2.legend(fontsize=8)

        plt.tight_layout()
        plt.show()

except Exception as e:
    import traceback
    print(f'plot_mloop_results error: {e}')
    traceback.print_exc()
