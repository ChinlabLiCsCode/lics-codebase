# Absorption imaging pipeline

Python port of `MATLAB/imaging`, wired into lyse.  It turns a shot's
atoms/light/dark frames into a column-density image, using a masked-PCA
defringe basis built from other shots' light frames, then fits and plots it.

| MATLAB                 | here                                |
| ---------------------- | ----------------------------------- |
| `build_params.m`       | `params.ImagingParams`, presets      |
| `load_params.m`        | presets in `params.py` (edit in git) |
| `load_img.m`           | `process.load_shot_images`           |
| `defringeset_create.m` | `DefringeSet.from_stack`             |
| `defringe.m`           | `DefringeSet.apply`                  |
| `nd_calc.m`            | `process.nd_calc` / `process.od_calc`|
| `proc_imgs.m`          | `process.process_shot`               |
| `scan_fit1Dflex.m`     | `fitting.fit_image`                  |
| `df_view_image`        | `plotting.plot_shot`                 |

## Using it from lyse

Add `analysislib/df_image_analysis.py` as a single-shot routine.  Everything
you would normally change lives in the `PARAMS` block at the top of that file.

## Regions

`view` and `mask` are `(row_start, row_stop, col_start, col_stop)` with
half-open (python slice) bounds.

* `view` crops the full sensor frame; everything downstream works inside it.
  Keep it tight — the defringe basis costs `pca_number * ny * nx * 4` bytes,
  and the cached reference frames cost `n_reference * ny * nx * 4`.
* `mask` is the **atom box**, in view coordinates.  Pixels inside it are
  excluded from the defringe fit (so the atoms cannot pull the synthetic light
  frame down) and are the integration window for the 1D fits.

Fitted centres and plot axes are reported in *full-frame* microns, so they stay
comparable when the view changes.

## Choosing the defringe reference

`params.defringe` picks where the basis comes from:

| value    | meaning                                                             |
| -------- | ------------------------------------------------------------------- |
| `'auto'` | last `n_reference` shots this routine has seen, plus the current one |
| `'self'` | only this shot's light frame (a rescaling, no fringe removal)        |
| `'none'` | no defringing at all: plain `atoms / light`                          |
| a path   | a set saved by `build_defringe_set`                                  |

`'auto'` keeps the frames in `lyse.routine_storage`, so the basis grows as a
scan runs and is emptied whenever the view, mask or camera changes.  Restarting
lyse's analysis subprocess empties it too.

To freeze a known-good set instead, from a notebook:

```python
from glob import glob
from analysislib.imaging import build_defringe_set, presets

shots = sorted(glob(r'D:\LiCs_Exp_Data\Experiments\...\2026\08\20\00*\*.h5'))
build_defringe_set(shots, presets.CS_H_MOT,
                   r'D:\LiCs_Exp_Data\defringe_sets\dfset_20260820.npz')
```

then set `defringe=r'D:\...\dfset_20260820.npz'` in the routine.  Pick shots
with the same imaging light and no atoms (or atoms well inside the mask).

## Processing one shot outside lyse

```python
from analysislib.imaging import presets, process, fitting, plotting

params = presets.CS_H_MOT.replace(defringe='self')
result = process.process_shot(shot_path, params)
fit = fitting.fit_image(result.nd, params, od=result.od)
plotting.plot_shot(result, fit, params, title=shot_path)
```

## Physics knobs

`I_sat` (counts per pixel) and `alpha` enable the saturation-corrected OD of
`nd_calc.m`; the defaults (`inf`, `(1, 0, 0)`) reduce it to `-log(A/A')`.
`magnification` is shared with `absorption_image_analysis.py` and was
calibrated on 2026-08-11 from a TOF gravity measurement.
