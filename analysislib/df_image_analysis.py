"""Single-shot absorption analysis with PCA defringing.

The lyse-side equivalent of MATLAB's ``df_view_image``: load the shot's three
frames, build a synthetic light frame from a basis of recent light frames
(masked so the atoms do not pull the fit), turn the ratio into a column
density, fit the integrated profiles, plot, and save the numbers.

Everything configurable lives in PARAMS below; the machinery is in
``analysislib/imaging/``.  Compared with ``absorption_image_analysis.py`` this
routine adds defringing, a view/atom-box crop, and the saturation-corrected OD,
and it fits over the atom box rather than the whole 2048x2048 frame.
"""

import os

import lyse

# lyse puts the routine's own folder on sys.path; notebooks import the package
# by its full path from the repository root.
try:
    from imaging import presets, process, fitting, plotting
    from imaging.defringe import LightFrameCache
except ImportError:                                   # pragma: no cover
    from analysislib.imaging import presets, process, fitting, plotting
    from analysislib.imaging.defringe import LightFrameCache


# ── configuration ─────────────────────────────────────────────────────────
# Presets (view, mask, optics) live in analysislib/imaging/params.py.  Add one
# there when you settle on a new region; override here for a one-off.
PARAMS = presets.CS_H_MOT.replace(
    # 'auto' builds the defringe basis from the last n_reference shots this
    # routine has seen, plus the current one.  Alternatives:
    #   'self'  - use only this shot's light frame (rescaled, no fringe removal)
    #   'none'  - plain atoms/light, i.e. what absorption_image_analysis does
    #   a path  - a set saved with imaging.build_defringe_set(), e.g.
    #             r'D:\LiCs_Exp_Data\defringe_sets\dfset_20260820.npz'
    defringe='auto',
    n_reference=15,
    pca_number=10,
    fit_type='gauss',        # 'gauss' | 'dbl' | 'tf', or a ('x', 'y') pair
    fit_offset=False,        # fit a constant baseline under the profiles
    # acquisition=None       # None picks the first images group in the shot;
                             # set 'absorption1'/'absorption2' when there are
                             # several
)


# ── the shot ──────────────────────────────────────────────────────────────
run = lyse.Run(lyse.path)
shot_path = lyse.path
run_name = os.path.basename(shot_path)

# The reference light frames persist between shots in lyse's analysis
# subprocess, so a scan defringes against the shots that came before it.
cache = None
if PARAMS.defringe == 'auto':
    cache = getattr(lyse.routine_storage, 'light_cache', None)
    if cache is None:
        cache = LightFrameCache(maxlen=PARAMS.n_reference,
                                signature=PARAMS.signature())
        lyse.routine_storage.light_cache = cache

result = process.process_shot(shot_path, PARAMS, cache=cache)
fit = fitting.fit_image(result.nd, PARAMS, od=result.od)

print(f'{run_name}: N={fit.n_count:.3e} atoms, '
      f'sigma_x={fit.x.width:.0f} um, sigma_y={fit.y.width:.0f} um, '
      f'OD_peak={fit.od_peak:.2f}, defringe={result.defringe_mode} '
      f'({result.n_components} components)')

plotting.plot_shot(result, fit, PARAMS, title=run_name)


# ── results ───────────────────────────────────────────────────────────────
# N_int / sigma / x0 keep the names used by absorption_image_analysis.py so
# multishot plots can switch between the two routines.
run.save_result('N_int', fit.n_count)
run.save_result('N_view', fit.n_total)
run.save_result('N_x', fit.x.n_fit)
run.save_result('N_y', fit.y.n_fit)
run.save_result('sigma_x (um)', fit.x.width)
run.save_result('sigma_y (um)', fit.y.width)
run.save_result('x0_x (um)', fit.x.center)
run.save_result('x0_y (um)', fit.y.center)
run.save_result('OD_peak', fit.od_peak)
run.save_result('n_defringe', result.n_components)

if fit.x.separation is not None:
    run.save_result('sep_x (um)', fit.x.separation)
if fit.y.separation is not None:
    run.save_result('sep_y (um)', fit.y.separation)
