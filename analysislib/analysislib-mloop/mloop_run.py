"""Run an M-LOOP optimisation and plot its progress from a single lyse routine.

Combines mloop_multishot.py and plot_mloop_results.py so the config path only
has to be set in one place.  On every shot this routine first hands the cost
to M-LOOP (or starts the optimisation on the first shot), then redraws the
cost-vs-parameter panels for the current session.

Use it directly by editing CONFIG_PATH below, or load one of the per-config
wrappers (mloop_run_cs_mot.py, mloop_run_cs_molasses.py, mloop_run_cs_cmot.py) into
lyse instead.  Each lyse routine runs in its own subprocess with its own
routine_storage, so only have ONE M-LOOP routine active at a time -- two active
routines would each start an optimisation and fight over runmanager.
"""

import math
import os

import lyse
import matplotlib.pyplot as plt
import numpy as np

import mloop_config
import mloop_multishot

# Default config when this file itself is loaded as the lyse routine.
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'mloop_configs',
                           'mloop_config_cs_mot_optimization.toml')

# Fraction of each parameter's range counted as "near" its best value; see
# plot_mloop_results.py.
TOLERANCE = 0.2
MIN_HIGHLIGHTED = 3


def optimise(config_path, config):
    """One lyse execution of the mloop_multishot.py routine for config_path."""
    # verify_globals() names mloop_multishot.CONFIG_PATH in its error message.
    mloop_multishot.CONFIG_PATH = config_path
    mloop_multishot.configure_logging(config)
    logger = mloop_multishot.logger

    if not hasattr(lyse.routine_storage, 'queue'):
        logger.info('First execution of lyse routine...')
        from queue import Queue
        logger.debug('Creating queue.')
        lyse.routine_storage.queue = Queue()

    running_config_path = getattr(lyse.routine_storage, 'mloop_config_path', None)
    optimisation_running = (
        hasattr(lyse.routine_storage, 'optimisation')
        and lyse.routine_storage.optimisation.is_alive()
    )

    if optimisation_running and running_config_path != config_path:
        # The live thread keeps the config it was constructed with, so costs
        # would be verified against parameters it never requested.
        message = (
            'Config is {new}, but the optimisation still running was started '
            'with {old}.\nRestart the lyse analysis subprocess for this routine '
            '(right-click it in lyse -> Restart worker process) to start a new '
            'optimisation from the current config.'
        ).format(new=config_path, old=running_config_path)
        logger.error(message)
    elif optimisation_running:
        cost_dict = mloop_multishot.cost_analysis(
            cost_key=config['cost_key'] if not config['mock'] else [],
            maximize=config['maximize'],
            x=list(lyse.routine_storage.params.values())[0] if config['mock'] else None,
        )

        if not cost_dict['bad'] or not config['ignore_bad']:
            if mloop_multishot.check_runmanager(config):
                if mloop_multishot.verify_globals(config):
                    logger.debug('Putting cost in queue.')
                    lyse.routine_storage.queue.put(cost_dict)
                else:
                    logger.debug('NOT putting cost in queue because verify_globals failed.')
            else:
                logger.debug('NOT putting cost in queue because check_runmanager failed.')
        else:
            logger.debug(
                'NOT putting cost in queue because cost was bad and ignore_bad is True.'
            )

    elif mloop_multishot.check_runmanager(config):
        logger.info('(Re)starting optimisation process...')
        import threading
        import mloop_interface

        lyse.routine_storage.mloop_config_path = config_path
        logger.debug('Starting interface thread...')
        lyse.routine_storage.optimisation = threading.Thread(
            target=mloop_interface.main
        )
        lyse.routine_storage.optimisation.daemon = True
        lyse.routine_storage.optimisation.start()
        logger.debug('Interface thread started.')
    else:
        print(
            '\nNot (re)starting optimisation process.',
            'Please address above warnings before trying again.',
        )


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


def plot_results(config):
    """Cost against each optimisation parameter, as in plot_mloop_results.py."""
    df = lyse.data()
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

    ranges = {name: config['mloop_params'][name].max - config['mloop_params'][name].min
              for name in param_names}

    ncols = math.ceil(math.sqrt(n))
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows),
                             squeeze=False)
    axes_flat = axes.flatten()

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
        ax.legend(fontsize=7)

    for j in range(n, len(axes_flat)):
        axes_flat[j].set_visible(False)

    plt.tight_layout()
    plt.show()


def run(config_path):
    """Optimise then plot, both from the config at config_path."""
    config = mloop_config.get(config_path)
    print(f'M-LOOP config: {os.path.basename(config_path)}')

    # Hand the cost to M-LOOP before plotting, so a plotting error can never
    # stall the optimisation.
    optimise(config_path, config)

    try:
        plot_results(config)
    except Exception as e:
        import traceback
        print(f'plot_results error: {e}')
        traceback.print_exc()


if __name__ == '__main__':
    run(CONFIG_PATH)
