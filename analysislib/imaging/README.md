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
| —                      | `IntensityScale` (`defringe='scale'`)|
| —                      | `portal.view_shot` (notebook access) |
| —                      | `debug.*` (defringe diagnostics)     |

The papers the pipeline follows are in this folder: `Niu.pdf` for the
masked-PCA defringing, `Reinaudi.pdf` for the saturated optical density, and
`Veyron.pdf` for the density dependence of the correction factor α.

## Using it from lyse

Add `analysislib/df_image_analysis.py` as a single-shot routine.  Everything
you would normally change lives in the `PARAMS` block at the top of that file.

## Using it from a notebook

Shots are addressed exactly as in `helperfuncs.live_plot_scan` — year, month,
day, sequence, run number — plus a shot index within the run:

```python
import analysislib.helperfuncs as hf

view = hf.view_shot(2026, 8, 21, 'cs_molasses_healthcheck', 57, shot=12)
view.fit.n_count, view.results()

df = hf.view_scan(2026, 8, 21, 'cs_molasses_healthcheck', 57)   # the whole run
```

`shot` takes a negative index (`-1` for the last) or a filename fragment
(`'rep00007'`).  Any `ImagingParams` field can be overridden inline:

```python
view = hf.view_shot(2026, 8, 21, 'cs_molasses_healthcheck', 57, shot=12,
                    preset='CS_H_IS', n_reference=12, pca_number=3,
                    mask=(100, 700, 50, 1650), fit_type='dbl')
```

`view_shot` returns a `ShotView` holding `result` (frames, A′, OD, column
density), `fit`, `params`, and `figures`.  `view.results()` is the same dict of
numbers the lyse routine saves.

### Where the shots are read from

The sequence folder comes from labconfig's `experiment_shot_storage`, the same
as `helperfuncs._sequence_folder`.  Each machine's paths belong there, so a
notebook says nothing about them and runs unchanged on the control PC and on a
laptop.  The `storage=` argument is for deliberately reading a tree that is
*not* this machine's — an archive, or a copy of another rig's run.

### Choosing the reference shots

`reference=` decides which neighbours make up the basis for a shot:

| value        | meaning                                                    |
| ------------ | ---------------------------------------------------------- |
| `'previous'` | the `n_reference` shots before it — what lyse sees live     |
| `'nearest'`  | the `n_reference` closest either side — better after the fact |
| `'all'`      | every shot in the folder                                    |

`view_shot` defaults to `'previous'` so it reproduces the lyse routine;
`view_scan` defaults to `'nearest'`, since offline there is no reason to
pretend the later shots have not happened yet.

## Tuning the defringing: `debug=True`

```python
view = hf.view_shot(2026, 8, 21, 'cs_molasses_healthcheck', 57, shot=12,
                    n_reference=20, pca_number=20, debug=True)
```

prints the shots that went into the defringe basis, then draws five figures
and prints a verdict on each knob.

```
defringe set: 8 light frames (auto) from .../cs_molasses_healthcheck/2026/08/21/0057
  all named 2026-08-21_0057_cs_molasses_healthcheck_0_*
  [  8] rep00008.h5
  ...
  [ 12] rep00012.h5   <- this shot
  ...
  probe (held out of the basis): [ 16] rep00016.h5
```

The index in brackets is the shot's position in the folder, i.e. what you would
pass as `shot=`.  The probe is the shot the noise scans are measured on: it is
deliberately *not* in the basis, and never the shot being analysed.  The same
list is on the object as `view.reference_names` (and `view.result.reference_paths`
for full paths); `portal.print_reference_set(view)` reprints it.

**`basis`** — Niu's Fig. 3.  The eigenvalue spectrum with the photon-shot-noise
plateau marked, and the components themselves.  Independent shot noise in `n`
reference frames makes `n-1` modes of *equal* variance, so it shows up as a
flat plateau; components above it are real fringes, components in it are noise.
The component images make the same point by eye: fringes, then salt and pepper.

**`defringe`** — the atoms frame, the raw light frame and the synthetic light
frame A′, then the optical density with and without defringing, and a histogram
of the OD over the pixels the fit was allowed to see, whose width is the
residual noise.

Two dotted lines on that histogram answer *is the cloud inside the box?*  The
red one is the median OD in the ring just outside `mask`; the orange one is the
median at the border of the view.  If the ring sits well above the border,
atoms are reaching outside the atom box, the defringe fit is reproducing them,
and `N` will read low — widen `mask`.  If the two agree but both sit above
zero, that offset is not atoms: it is the two exposures receiving different
probe energy, and every mode except `'none'` rescales it away.  The routine
prints whichever of the two it finds.

**`component_scan`** — Niu's Fig. 2(b) against `pca_number`.  A light frame
held *out* of the basis is pushed through the fit; it has no atoms, so
everything left is noise, and the noise inside the atom box — the region the
fit never saw — is the honest figure of merit.  The dashed curve is the
residual over the pixels the fit *did* see: it only ever falls, so the gap
between the two curves is the overfitting.  The right-hand panel shows the
shot's fitted `N` against component count, which is the practical test: once
`N` has stopped moving, the setting is safe.

**`reference_scan`** — the same measurement against `n_reference`, rebuilding
the basis from the `n` frames closest in time at each point.

Both scans report the *cheapest* setting that is within 1 % of the best, not
the raw minimum: these curves are flat-bottomed and a plain `argmin` just picks
whichever wiggle dipped lowest.  They also say when the scan ran out of range
before the noise stopped falling.

**`fringes`** — *did the defringing actually remove fringes?*  The power spectra
of the raw light frame and of both optical densities, over the largest
atom-free window in the view.  The fringe wavevector is found in the light
frame, where the pattern is strongest, and then looked for in the two ODs.

Two numbers per OD.  The **amplitude** is the fringe rms in OD units (Parseval
over the fringe band), which is what to compare against the shot noise.  The
**anisotropy** is power at the fringe wavevector over power at the same spatial
frequency rotated 90°: shot noise is isotropic so it cancels in the ratio, and
`1.0` means no fringe left regardless of the noise level.  The absolute
anisotropy depends on the window size — compare the pair, not the number.

Run 0057, shot 12, with the cloud fully inside the mask:

| mode | N | fringe in OD | anisotropy | OD rms | OD median outside mask |
| --- | --- | --- | --- | --- | --- |
| `'none'`  | 4.92e7 | 0.0018 | 1.25  | 0.184 | **+0.063** |
| `'scale'` | 4.34e7 | 0.0018 | 1.25  | 0.184 | **+0.000** |
| `'self'`  | 4.02e7 | 0.0244 | 72.2  | 0.182 | +0.004 |
| `'auto'`  | 4.30e7 | 0.0049 | 11.1  | 0.151 | −0.003 |

The light frame carries 15% rms fringe contrast and plain `A/L` already
suppresses it to 0.0018 OD, because the atoms and light exposures are only
200 ms apart ([cs_subsequences.py:224](../../apparatus/sequences/cs_sequences/cs_subsequences.py#L224),
[:258](../../apparatus/sequences/cs_sequences/cs_subsequences.py#L258)) while
shots are ~3.3 s apart.  So on this rig the PCA basis is a *worse* fringe
reference than the shot's own light frame, and the check says so.  What `'auto'`
buys instead is broadband: 0.184 → 0.151 rms, from correcting the beam shape.
Both residuals are a few percent of the shot noise, so the choice matters far
less than getting `mask` right.

The pieces are usable on their own:

```python
from analysislib.imaging import debug, portal, presets

paths = portal.shot_paths(2026, 8, 21, 'cs_molasses_healthcheck', 57)
dfset, refs = portal.defringe_set_for(paths, 12, presets.CS_H_MOT,
                                      n_reference=20, reference='nearest')
print(dfset.noise_floor, dfset.n_above_noise)   # suggested pca_number
debug.plot_basis(dfset, presets.CS_H_MOT)
```

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

| value     | meaning                                                              |
| --------- | -------------------------------------------------------------------- |
| `'auto'`  | last `n_reference` shots this routine has seen, plus the current one  |
| `'scale'` | `A' = c·L`: this shot's own light frame times one number. No PCA      |
| `'self'`  | PCA on this shot's light frame alone — a scale *and* an offset        |
| `'none'`  | no defringing at all: plain `atoms / light`                           |
| a path    | a set saved by `build_defringe_set`                                   |

### `'scale'`: the simplest thing that can work

`c = exp(median(log(A/L)))` over the unmasked pixels — by construction the
scale that makes the optical density read **zero where there are no atoms**.
That matters more than it sounds: the two exposures routinely receive a few
percent different probe energy, and on these shots that leaves a `+0.06` OD
pedestal which, integrated over a 700×1750 atom box, inflates `N` by ~13%.

`'scale'` cannot correct a difference in beam *shape*, only the level. What it
never does is damage the fringes — it divides by the shot's own light frame, so
whatever fringe cancellation `A/L` gives you, you keep. Prefer it over `'self'`,
which appends a constant frame to the basis and fits an additive offset: that
offset distorts the fringe contrast of the denominator badly (measured
anisotropy 72 against 1.25 for plain `A/L` on run 0057).

`'auto'` keeps the frames in `lyse.routine_storage`, so the basis grows as a
scan runs and is emptied whenever the view, mask or camera changes.  Restarting
lyse's analysis subprocess empties it too.  From a notebook, `'auto'` instead
pulls the frames straight out of the sequence folder — see *Choosing the
reference shots* above.

`subtract_mean=True` switches to Niu's convention of removing the mean
reference frame before the decomposition.  The default (`False`) reproduces
`defringeset_create.m`, where the leading component ends up being essentially
the mean beam profile and a constant frame is appended to the stack to absorb a
uniform offset.

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

params = presets.CS_H_MOT.replace(defringe='scale')
result = process.process_shot(shot_path, params)
fit = fitting.fit_image(result.nd, params, od=result.od)
plotting.plot_shot(result, fit, params, title=shot_path)
```

## Physics knobs

`I_sat` (counts per pixel) and `alpha` enable the saturation-corrected OD of
`nd_calc.m`; the defaults (`inf`, `(1, 0, 0)`) reduce it to `-log(A/A')`.

`alpha` is `(a0, a1, a2)` in `α = a0 + a1·b + a2·b²`, the correction factor on
the resonant cross section.  With `a1 = a2 = 0` the OD is Reinaudi's
`b = -α·ln(T) + s_c·(1 - T)`; the linear term is Veyron's result that α itself
rises with the optical density (they measure `α = 1.17(9) + 0.255(2)·b` for
σ⁻-polarised Rb, so the values are ours to calibrate, not to copy).
`magnification` is shared with `absorption_image_analysis.py` and was
calibrated on 2026-08-11 from a TOF gravity measurement.
