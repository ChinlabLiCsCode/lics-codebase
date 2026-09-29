"""lyse routine: M-LOOP Cs molasses optimisation, with results plot.

Thin wrapper around mloop_run.py pinned to mloop_config_cs_molasses_optimization.toml.
Only have one M-LOOP routine active in lyse at a time.
"""

import os

from mloop_run import run

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'mloop_configs',
                           'mloop_config_cs_molasses_optimization.toml')

if __name__ == '__main__':
    run(CONFIG_PATH)
