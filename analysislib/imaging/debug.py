"""Diagnostics for the masked-PCA defringing.

The two knobs that decide how well defringing works — how many light frames go
into the basis (``n_reference``) and how many principal components are kept
(``pca_number``) — cannot be chosen from first principles.  Niu et al.
(``Niu.pdf``) choose them by looking at two things, and so does this module:

1. **What the components look like.**  The leading components are fringes; the
   trailing ones are white noise.  Keep the fringes, drop the noise.
   :func:`plot_basis` is Niu's Fig. 3.

2. **How much noise survives on a frame with no atoms in it.**  Push a light
   frame that was *held out* of the basis through the defringe fit and take
   ``-log(L / L')``.  There are no atoms, so everything you see is noise, and
   the noise *inside the atom box* — the region the fit never saw — is the
   number that matters.  :func:`plot_component_scan` and
   :func:`plot_reference_scan` are Niu's Fig. 2(b) against each knob.

Unlike :mod:`.plotting`, the axes here are **view pixel coordinates**, not
microns, because the thing you usually do with these figures is go and edit
``params.view`` or ``params.mask``.

Everything is reachable through the ``debug=True`` flag of
:func:`analysislib.imaging.portal.view_shot`, or directly::

    from analysislib.imaging import debug, presets, process
    result = process.process_shot(path, presets.CS_H_MOT.replace(defringe='self'))
    debug.plot_basis(result.defringe_set, presets.CS_H_MOT)
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from .defringe import DefringeSet


# ── the noise figure of merit ─────────────────────────────────────────────

def od_noise(frame, reference, region=None, floor=1e-3):
    """RMS of ``-log(frame / reference)`` over ``region``.

    On an atom-free frame this is pure noise, which is Niu's figure of merit
    for the algorithm.  Deliberately the *plain* optical density rather than
    :func:`~.process.od_calc`: the saturation correction is a monotonic
    rescaling that would only make the number harder to compare with the
    paper.

    ``region`` is ``(row0, row1, col0, col1)`` in view coordinates; None uses
    the whole frame.  Pixels where either image has dropped below ``floor``
    times the reference median are ignored, so dead corners of the beam do not
    dominate the log.
    """
    frame = np.asarray(frame, dtype=float)
    reference = np.asarray(reference, dtype=float)
    if region is not None:
        r0, r1, c0, c1 = region
        frame, reference = frame[r0:r1, c0:c1], reference[r0:r1, c0:c1]

    scale = np.nanmedian(np.abs(reference))
    good = (frame > floor * scale) & (reference > floor * scale)
    if not good.any():
        return np.nan
    with np.errstate(divide='ignore', invalid='ignore'):
        od = -np.log(frame[good] / reference[good])
    od = od[np.isfinite(od)]
    return float(np.std(od)) if od.size else np.nan


def _parsimonious(x, values, tol=0.01):
    """The smallest ``x`` whose ``values`` are within ``tol`` of the minimum.

    These scans are usually flat-bottomed: past the point where the algorithm
    has everything it needs, the curve wanders around inside its own noise and
    a plain ``argmin`` picks whichever wiggle happened to dip lowest.  Taking
    the first point that is as good as the best, to within ``tol`` (1 % by
    default), gives the cheapest setting that buys you the whole improvement.

    Returns ``(best, at_edge)``; ``at_edge`` is True when the true minimum sits
    at the end of the scanned range, which means the range was too short.
    """
    values = np.asarray(values, dtype=float)
    finite = np.isfinite(values)
    if not finite.any():
        return 0, False
    vmin = np.nanmin(values)
    target = vmin + tol * abs(vmin)
    first = int(np.flatnonzero(finite & (values <= target))[0])
    # Only worth extending the range if the choice itself ran into the end:
    # a flat-bottomed curve whose argmin wandered to the last point is still
    # perfectly well resolved by an early, cheap setting.
    return int(x[first]), first == len(values) - 1


def leak_rings(shape, mask, pad=None):
    """Two atom-free test regions: just outside the atom box, and far from it.

    Returns ``(inner, outer)`` boolean masks.  ``inner`` is the ring hugging
    the outside of the atom box, ``outer`` is the border of the view.

    The pair is what makes "are atoms leaking out of the mask?" answerable.
    The border carries whatever uniform offset the shot has — the atoms
    exposure rarely gets exactly the same probe energy as the light exposure,
    which shows up as a constant pedestal in ``-log(A/L)`` everywhere,
    including in corners that certainly hold no atoms.  Subtracting the border
    from the ring leaves only what is actually spatially concentrated around
    the cloud.

    Both are None when the atom box leaves no room for them, which is itself
    the answer: the view is too tight to tell.
    """
    ny, nx = shape
    if mask is None:
        return None, None
    r0, r1, c0, c1 = _fit_region(shape, mask)
    gaps = [r0, ny - r1, c0, nx - c1]
    if min(gaps) < 6:
        return None, None
    if pad is None:
        pad = max(4, min(gaps) // 3)

    inner = np.zeros(shape, dtype=bool)
    inner[max(0, r0 - pad):min(ny, r1 + pad),
          max(0, c0 - pad):min(nx, c1 + pad)] = True
    inner[r0:r1, c0:c1] = False

    outer = np.zeros(shape, dtype=bool)
    outer[:pad, :] = outer[-pad:, :] = True
    outer[:, :pad] = outer[:, -pad:] = True
    outer &= ~inner
    if not outer.any() or not inner.any():
        return None, None
    return inner, outer


def _fit_region(shape, mask):
    """The mask region clipped to ``shape``, or the whole frame if unset."""
    ny, nx = shape
    if mask is None:
        return 0, ny, 0, nx
    r0, r1, c0, c1 = mask
    return max(0, r0), min(ny, r1), max(0, c0), min(nx, c1)


# ── the scans ─────────────────────────────────────────────────────────────

@dataclass
class ComponentScan:
    """Noise against number of principal components kept.

    ``inside`` is the number that matters: the region the fit never saw.  It
    normally falls, bottoms out, and climbs again as the extra components
    start fitting the probe frame's own photon shot noise.  ``outside`` is the
    fit residual and falls monotonically by construction — when the two curves
    part company you are overfitting.
    """

    k: np.ndarray                       # number of components kept
    inside: np.ndarray                  # OD noise inside the atom box
    outside: np.ndarray                 # OD noise over the fitted pixels
    n_atoms: Optional[np.ndarray] = None    # fitted N of the real shot vs k
    baseline: float = np.nan            # OD noise with no defringing at all
    best_k: int = 0                     # cheapest k that is as good as the best
    min_k: int = 0                      # raw argmin, wiggles and all
    at_edge: bool = False               # the minimum ran into the end of the set
    spectrum_k: int = 0                 # what the eigenvalue plateau suggests
    probe_path: str = ''

    def summary(self):
        """One line of advice on ``pca_number``, for the debug printout."""
        best = np.nanmin(self.inside)
        gain = ('' if not np.isfinite(self.baseline)
                else f', {self.baseline / best:.2f}x better than no defringing')
        text = (f'keep {self.best_k} of {self.k[-1]} components '
                f'(noise {best:.4f}{gain})')
        if self.spectrum_k:
            text += f'; the eigenvalue plateau suggests {self.spectrum_k}'
        if self.at_edge:
            text += '; the noise was still falling at the end of the set, '\
                    'so raise pca_number and rerun'
        return text


def scan_components(dfset, probe, mask, reference=None, k_values=None,
                    tol=0.01):
    """Noise against ``pca_number``, on a probe frame held out of the basis.

    Parameters
    ----------
    dfset : :class:`~.defringe.DefringeSet`
    probe : (ny, nx) array
        A dark-subtracted light frame that is **not** in the basis.  It has no
        atoms, so every structure left after defringing is noise.
    mask : region tuple or None
        The atom box, in view coordinates.
    reference : (ny, nx) array or None
        The frame a conventional (non-defringed) analysis would divide by,
        used for the ``baseline`` number.  Typically the probe shot's own
        light frame; None skips the baseline.
    k_values : sequence of int or None
        Component counts to try.  Defaults to every count up to the size of
        the set.
    tol : float
        How much worse than the best a setting may be and still be preferred
        for being smaller.  See :func:`_parsimonious`.
    """
    probe = np.asarray(probe, dtype=float)
    inner = _fit_region(probe.shape, mask)
    outer_weights = dfset.mask_weights > 0

    if k_values is None:
        k_values = np.arange(1, dfset.n_components + 1)
    k_values = np.asarray(k_values, dtype=int)

    inside, outside = [], []
    for k in k_values:
        synthetic = dfset.apply(probe, n_components=k)
        inside.append(od_noise(probe, synthetic, inner))
        # Over the fitted pixels: blank the atom box so it cannot contribute.
        masked = np.where(outer_weights, probe, np.nan)
        outside.append(od_noise(masked, synthetic))

    inside = np.asarray(inside)
    baseline = np.nan if reference is None else od_noise(probe, reference, inner)
    best, at_edge = _parsimonious(k_values, inside, tol)
    raw = int(k_values[int(np.nanargmin(inside))]) if np.isfinite(inside).any() else 0
    return ComponentScan(k=k_values, inside=inside, outside=np.asarray(outside),
                         baseline=baseline, best_k=best, min_k=raw,
                         at_edge=at_edge, spectrum_k=dfset.n_above_noise)


@dataclass
class ReferenceScan:
    """Noise against the number of light frames in the basis."""

    n: np.ndarray
    inside: np.ndarray
    k_used: np.ndarray
    baseline: float = np.nan
    best_n: int = 0                     # cheapest n that is as good as the best
    min_n: int = 0                      # raw argmin
    at_edge: bool = False               # the pool ran out before the noise did

    def summary(self):
        """One line of advice on ``n_reference``, for the debug printout."""
        best = np.nanmin(self.inside)
        text = f'look {self.best_n} shots back (noise {best:.4f})'
        if self.at_edge:
            text += ('; the noise was still falling when the folder ran out, '
                     'so a longer run would defringe better still')
        return text


def scan_references(frames, probe, mask, pca_number=10, n_values=None,
                    reference=None, dtype='float32', subtract_mean=False,
                    tol=0.01):
    """Noise against ``n_reference``, rebuilding the basis at each size.

    ``frames`` is the pool of dark-subtracted light frames, ordered so that
    ``frames[-1]`` is the *closest* to the probe shot in time: the scan takes
    the last ``n`` of them, which is what "look ``n`` shots back in the
    history" means.  ``probe`` must not be in the pool.
    """
    frames = np.asarray(frames, dtype=dtype)
    inner = _fit_region(probe.shape, mask)

    if n_values is None:
        n_values = np.unique(np.clip(
            np.round(np.geomspace(1, len(frames), min(12, len(frames)))),
            1, len(frames)).astype(int))
    n_values = np.asarray(n_values, dtype=int)

    inside, k_used = [], []
    for n in n_values:
        dfset = DefringeSet.from_stack(frames[-n:], mask=mask,
                                       pca_number=pca_number, dtype=dtype,
                                       subtract_mean=subtract_mean)
        inside.append(od_noise(probe, dfset.apply(probe), inner))
        k_used.append(dfset.n_components)

    inside = np.asarray(inside)
    baseline = np.nan if reference is None else od_noise(probe, reference, inner)
    best, at_edge = _parsimonious(n_values, inside, tol)
    raw = int(n_values[int(np.nanargmin(inside))]) if np.isfinite(inside).any() else 0
    return ReferenceScan(n=n_values, inside=inside, k_used=np.asarray(k_used),
                         baseline=baseline, best_n=best, min_n=raw,
                         at_edge=at_edge)


# ── did the fringes actually go? ──────────────────────────────────────────

@dataclass
class FringeCheck:
    """How much of the fringe pattern survives into the optical density.

    Measured as anisotropy: power at the fringe wavevector divided by power at
    the same spatial frequency rotated 90 degrees.  Shot noise is isotropic, so
    it cancels in the ratio and 1.0 means no fringe left, whatever the noise
    level.  Comparing the two optical densities says whether the defringing
    earned its keep on fringes specifically, as opposed to broadband noise.
    """

    period: float = np.nan          # pixels
    angle: float = np.nan           # degrees
    contrast: float = np.nan        # fringe rms / mean, in the raw light frame
    plain: float = np.nan           # anisotropy of -log(A/L)
    defringed: float = np.nan       # anisotropy of -log(A/A')
    plain_od: float = np.nan        # fringe rms in -log(A/L), OD units
    defringed_od: float = np.nan    # fringe rms in -log(A/A'), OD units
    noise_od: float = np.nan        # broadband rms of -log(A/A'), for scale
    box: tuple = ()                 # the atom-free window it was measured in

    def summary(self):
        """The fringe verdict as printed by ``debug=True``, in three lines."""
        if not np.isfinite(self.plain):
            return 'no atom-free window big enough to measure fringes in'
        share = ('' if not np.isfinite(self.noise_od) or not self.noise_od
                 else f', {100 * self.defringed_od / self.noise_od:.1f}% of the '
                      f'{self.noise_od:.3f} broadband noise')
        text = (f'fringes: period {self.period:.0f} px at {self.angle:+.0f} deg, '
                f'{100 * self.contrast:.0f}% rms contrast in the raw light frame\n'
                f'  surviving into the OD: {self.plain_od:.4f} with plain A/L, '
                f'{self.defringed_od:.4f} after defringing{share}\n'
                f'  anisotropy {self.plain:.2f} -> {self.defringed:.2f} '
                f'(1.0 = no fringe left; compare the pair, the absolute value '
                f'depends on the window)')
        if self.defringed > self.plain * 1.3:
            text += ('\n  the PCA fit is leaving MORE fringe than plain A/L would.  '
                     'That happens when the atoms and light exposures are close '
                     'enough in time that their fringes have not moved, while the '
                     'reference shots\' have — try defringe=\'scale\'.')
        return text


def _free_box(shape, mask, min_size=96):
    """The largest atom-free rectangle in the view: one of the four bands.

    A solid rectangle, not the ring :func:`leak_rings` returns, because a
    Fourier transform needs one.  None when the mask leaves nothing big enough.
    """
    ny, nx = shape
    if mask is None:
        return (0, ny, 0, nx)
    r0, r1, c0, c1 = _fit_region(shape, mask)
    bands = [(0, r0, 0, nx), (r1, ny, 0, nx),      # above, below
             (0, ny, 0, c0), (0, ny, c1, nx)]      # left, right
    bands = [b for b in bands
             if b[1] - b[0] >= min_size and b[3] - b[2] >= min_size]
    if not bands:
        return None
    return max(bands, key=lambda b: (b[1] - b[0]) * (b[3] - b[2]))


def _spectrum(image, box):
    """Windowed power spectrum of a box of ``image``, DC at the centre."""
    z = np.asarray(image[box[0]:box[1], box[2]:box[3]], dtype=float)
    z = np.nan_to_num(z - np.nanmean(z))
    window = np.hanning(z.shape[0])[:, None] * np.hanning(z.shape[1])[None, :]
    return np.abs(np.fft.fftshift(np.fft.fft2(z * window)))**2


def _peak_wavevector(power, exclude=8):
    """Index offset of the strongest peak away from DC, or None."""
    cy, cx = np.array(power.shape) // 2
    yy, xx = np.mgrid[0:power.shape[0], 0:power.shape[1]]
    far = (yy - cy)**2 + (xx - cx)**2 > exclude**2
    if not far.any():
        return None
    flat = np.where(far, power, 0)
    if flat.max() <= 0:
        return None
    py, px = np.unravel_index(np.argmax(flat), power.shape)
    return int(py - cy), int(px - cx)


def _disc_power(power, dy, dx, radius=5):
    """Mean power in a disc at ``(dy, dx)`` from DC, and at its conjugate."""
    cy, cx = np.array(power.shape) // 2
    yy, xx = np.mgrid[0:power.shape[0], 0:power.shape[1]]
    disc = (((yy - (cy + dy))**2 + (xx - (cx + dx))**2 <= radius**2) |
            ((yy - (cy - dy))**2 + (xx - (cx - dx))**2 <= radius**2))
    return float(power[disc].mean()) if disc.any() else np.nan


def fringe_amplitude(image, box, dy, dx, radius=5):
    """Rms amplitude of the fringe component of ``image``, in the box's units.

    Parseval on the windowed transform: the mean square of the fringe is the
    power in the band over ``N**2``, corrected for the Hann window's rms.  For
    an optical density this comes back in OD, which is the number to compare
    against the shot noise.
    """
    power = _spectrum(image, box)
    cy, cx = np.array(power.shape) // 2
    yy, xx = np.mgrid[0:power.shape[0], 0:power.shape[1]]
    disc = (((yy - (cy + dy))**2 + (xx - (cx + dx))**2 <= radius**2) |
            ((yy - (cy - dy))**2 + (xx - (cx - dx))**2 <= radius**2))
    return float(np.sqrt(power[disc].sum()) / power.size / (3 / 8))


def fringe_anisotropy(image, box, dy, dx, radius=5):
    """Power at the fringe wavevector over power at the same |k| rotated 90 deg.

    The rotation is done in physical space, so a non-square box is handled
    correctly.  Isotropic noise gives 1.0; a surviving fringe gives more.
    """
    power = _spectrum(image, box)
    ny, nx = box[1] - box[0], box[3] - box[2]
    # (ky, kx) in cycles/pixel is (dy/ny, dx/nx); perpendicular is (-kx, ky).
    ry, rx = -dx * ny / nx, dy * nx / ny
    along = _disc_power(power, dy, dx, radius)
    across = _disc_power(power, int(round(ry)), int(round(rx)), radius)
    if not np.isfinite(across) or across <= 0:
        return np.nan
    return along / across


def check_fringes(result, params, radius=5):
    """Measure fringe survival for one shot.  Returns a :class:`FringeCheck`.

    The fringe wavevector is found in the raw light frame, where the pattern is
    strongest, then looked for in both optical densities.
    """
    A, L, Aprime = result.A, result.L, result.Aprime
    box = _free_box(A.shape, params.mask)
    if box is None:
        return FringeCheck()

    peak = _peak_wavevector(_spectrum(L, box))
    if peak is None:
        return FringeCheck(box=box)
    dy, dx = peak

    ny, nx = box[1] - box[0], box[3] - box[2]
    period = 1.0 / np.hypot(dy / ny, dx / nx)
    angle = np.degrees(np.arctan2(dy / ny, dx / nx))

    # Contrast via Parseval: the share of the light frame's variance sitting
    # in the fringe band, turned back into an rms amplitude.
    patch = np.asarray(L[box[0]:box[1], box[2]:box[3]], dtype=float)
    power = _spectrum(L, box)
    cy, cx = np.array(power.shape) // 2
    yy, xx = np.mgrid[0:power.shape[0], 0:power.shape[1]]
    disc = (((yy - (cy + dy))**2 + (xx - (cx + dx))**2 <= radius**2) |
            ((yy - (cy - dy))**2 + (xx - (cx - dx))**2 <= radius**2))
    # Parseval on the windowed array: mean-square of the fringe component is
    # sum(power in the disc) / N^2.  Dividing by the Hann window's rms (0.612
    # per axis) undoes the attenuation the window applied.
    mean = float(np.nanmean(patch))
    contrast = (fringe_amplitude(L, box, dy, dx, radius) / mean
                if mean else np.nan)

    with np.errstate(divide='ignore', invalid='ignore'):
        od_plain = -np.log(np.clip(A, 1e-9, None) / np.clip(L, 1e-9, None))
        od_df = -np.log(np.clip(A, 1e-9, None) / np.clip(Aprime, 1e-9, None))

    # Robust: the free box can reach into unilluminated edges of the view,
    # where the log blows up and a plain std would be meaningless.
    patch_df = od_df[box[0]:box[1], box[2]:box[3]]
    finite = patch_df[np.isfinite(patch_df)]
    noise = (1.4826 * float(np.median(np.abs(finite - np.median(finite))))
             if finite.size else np.nan)
    return FringeCheck(
        period=period, angle=angle, contrast=float(contrast),
        plain=fringe_anisotropy(od_plain, box, dy, dx, radius),
        defringed=fringe_anisotropy(od_df, box, dy, dx, radius),
        plain_od=fringe_amplitude(od_plain, box, dy, dx, radius),
        defringed_od=fringe_amplitude(od_df, box, dy, dx, radius),
        noise_od=noise,
        box=box)


def plot_fringe_check(result, params, check=None, figsize=(13, 4.2),
                      show=True, title=''):
    """The power spectra behind :func:`check_fringes`, side by side.

    The bright spots off the centre are the fringe.  They are unmissable in the
    light frame; how much of them is left in the two optical densities is the
    whole question.
    """
    check = check_fringes(result, params) if check is None else check
    if not check.box:
        print(check.summary())
        return None
    box = check.box
    A, L, Aprime = result.A, result.L, result.Aprime
    with np.errstate(divide='ignore', invalid='ignore'):
        od_plain = -np.log(np.clip(A, 1e-9, None) / np.clip(L, 1e-9, None))
        od_df = -np.log(np.clip(A, 1e-9, None) / np.clip(Aprime, 1e-9, None))

    panels = [('raw light frame L', L, f'{100 * check.contrast:.0f}% contrast'),
              ('OD, no defringe: $-\\log(A/L)$', od_plain,
               f'anisotropy {check.plain:.2f}, {check.plain_od:.4f} OD'),
              ("OD, defringed: $-\\log(A/A\')$", od_df,
               f'anisotropy {check.defringed:.2f}, {check.defringed_od:.4f} OD')]

    fig, axes = plt.subplots(1, 3, figsize=figsize, constrained_layout=True)
    for ax, (label, image, note) in zip(axes, panels):
        power = _spectrum(image, box)
        cy, cx = np.array(power.shape) // 2
        half = min(60, cy, cx)
        crop = power[cy - half:cy + half, cx - half:cx + half]
        ax.imshow(np.log10(crop + crop.max() * 1e-12), cmap='magma',
                  origin='lower', extent=[-half, half, -half, half])
        ax.plot(0, 0, '+', color='cyan', ms=6)
        ax.set_title(f'{label}\n{note}' if note else label, fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])

    heading = (f'fringe survival — period {check.period:.0f} px at '
               f'{check.angle:+.0f} deg; 1.0 = no fringe left')
    fig.suptitle(f'{title}\n{heading}' if title else heading, fontsize=10)
    if show:
        plt.show()
    return fig


# ── the figures ───────────────────────────────────────────────────────────

def _outline(ax, mask, **kwargs):
    """Draw the atom box in view pixel coordinates."""
    if mask is None:
        return
    r0, r1, c0, c1 = mask
    style = dict(fill=False, edgecolor='white', linewidth=0.8,
                 linestyle='--', alpha=0.8)
    style.update(kwargs)
    ax.add_patch(Rectangle((c0, r0), c1 - c0, r1 - r0, **style))


def _symmetric(image, percentile=99.5):
    """A colour limit that centres zero and ignores the outlying few pixels."""
    finite = image[np.isfinite(image)]
    if not finite.size:
        return 1.0
    return float(np.percentile(np.abs(finite), percentile)) or 1.0


def plot_basis(dfset, params=None, n_show=8, coefficients=None,
               figsize=None, width=14, show=True, title=''):
    """Niu Fig. 3: the eigenvalue spectrum and the components themselves.

    Read it the way the paper does.  The leading components are the smooth
    beam profile and then clean fringes; somewhere down the list they stop
    looking like fringes and turn into salt and pepper.  That crossover is
    where ``pca_number`` belongs, and the dotted line on the spectrum finds it
    for you: independent photon shot noise in the reference frames produces a
    flat plateau of equal eigenvalues, so every component sitting *in* the
    plateau is noise and every component *above* it is signal.

    The dashed box is the atom mask.  Components whose fringes carry on across
    it are the ones doing useful work, since that is the region the fit has to
    extrapolate into.

    ``coefficients`` (from ``result.coefficients``) overlays how strongly this
    particular shot actually used each component.

    ``figsize`` defaults to whatever keeps the component panels at their true
    aspect ratio, which for a wide view means a tall figure; pass ``width`` to
    scale the whole thing instead.
    """
    mask = None if params is None else params.mask
    n_show = int(min(n_show, dfset.n_components))
    n_cols = 2 if n_show > 1 else 1
    n_rows = int(np.ceil(n_show / n_cols))

    ny, nx = dfset.shape
    spectrum_height = 3.2
    panel_height = (width / n_cols) * ny / nx
    if figsize is None:
        figsize = (width, spectrum_height + n_rows * (panel_height + 0.35))

    fig = plt.figure(constrained_layout=True, figsize=figsize)
    gs = fig.add_gridspec(2, 1, height_ratios=[spectrum_height,
                                               figsize[1] - spectrum_height])

    # top: the spectrum, kept vs discarded, against the shot-noise plateau
    gs_top = gs[0].subgridspec(1, 2 if coefficients is not None else 1)
    ax = fig.add_subplot(gs_top[0])
    spectrum = np.asarray(dfset.spectrum, dtype=float)
    positive = spectrum > 0
    index = np.arange(1, spectrum.size + 1)
    ax.semilogy(index[positive], spectrum[positive], 'o-', ms=4, lw=1,
                color='0.6', label='discarded')
    kept = index <= dfset.n_components
    ax.semilogy(index[positive & kept], spectrum[positive & kept], 'o-', ms=5,
                lw=1.5, color='tab:blue', label=f'kept ({dfset.n_components})')

    floor = dfset.noise_floor
    if np.isfinite(floor):
        ax.axhline(floor, color='tab:orange', ls=':', lw=1.5,
                   label=f'shot-noise plateau')
        suggested = dfset.n_above_noise
        ax.axvline(suggested + 0.5, color='tab:green', lw=1.2,
                   label=f'{suggested} above the plateau')
    ax.set_xlabel('component index $j$')
    ax.set_ylabel('eigenvalue of $v_j$')
    ax.set_title(f'PCA spectrum, {dfset.n_frames} reference frames', fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which='both')

    if coefficients is not None:
        axc = fig.add_subplot(gs_top[1])
        coefficients = np.abs(np.asarray(coefficients, dtype=float))
        axc.semilogy(np.arange(1, coefficients.size + 1), coefficients, 'o-',
                     ms=4, color='tab:purple')
        axc.set_xlabel('component index $j$')
        axc.set_ylabel(r'$|x_j|$')
        axc.set_title("how strongly this shot's atoms frame used each component",
                      fontsize=10)
        axc.grid(alpha=0.3, which='both')

    # bottom: the components as images, big enough to tell fringes from noise
    gs_bottom = gs[1].subgridspec(n_rows, n_cols, hspace=0.06, wspace=0.04)
    for j in range(n_show):
        axj = fig.add_subplot(gs_bottom[j // n_cols, j % n_cols])
        image = dfset.component(j)
        limit = _symmetric(image)
        axj.imshow(image, cmap='RdBu_r', vmin=-limit, vmax=limit,
                   origin='lower', interpolation='nearest')
        _outline(axj, mask, edgecolor='k')
        note = ''
        if np.isfinite(floor) and j < spectrum.size:
            note = ' — noise' if j >= dfset.n_above_noise else ' — signal'
        axj.set_title(f'$P_{{{j + 1}}}$  ($\\lambda$={dfset.eigenvalues[j]:.2e}){note}',
                      fontsize=8)
        axj.set_xticks([])
        axj.set_yticks([])

    heading = f'defringe basis — {dfset!r}'
    fig.suptitle(f'{title}\n{heading}' if title else heading, fontsize=10)
    if show:
        plt.show()
    return fig


def plot_defringe(result, params, figsize=(14, 7), show=True, title=''):
    """What the defringing actually did to this shot.

    Top row: the atoms frame, the raw light frame, and the synthetic light
    frame the basis fitted.  Bottom row: the two candidate optical densities
    side by side on a shared colour scale — ``-log(A/L)`` as a plain
    atoms/light analysis would compute it, and ``-log(A/A')`` after defringing
    — plus the histogram of both over the pixels the fit was allowed to see.

    The histogram's **width** is the residual noise.  Its two dotted markers
    answer a different question — is the cloud inside the box?  Red is the
    median optical density in the ring just outside ``params.mask``, orange the
    median at the border of the view.  A ring well above the border means atoms
    are reaching outside the atom box, where the defringe fit will try to
    reproduce them, dragging the synthetic light frame down over the cloud so
    that ``N`` reads low; widen ``params.mask``, and ``params.view`` with it.
    The two agreeing but both sitting above zero is a different thing entirely:
    the two exposures received different probe energy, which every mode except
    ``'none'`` rescales away.  :func:`_report_leak` prints whichever it finds.
    """
    mask = params.mask
    A, L, Aprime = result.A, result.L, result.Aprime
    outside = result.defringe_set.mask_weights > 0 if result.defringe_set is not None \
        else np.ones(A.shape, dtype=bool)

    with np.errstate(divide='ignore', invalid='ignore'):
        od_plain = -np.log(np.where(L > 0, A / np.where(L > 0, L, 1), np.nan))
        od_df = -np.log(np.where(Aprime > 0, A / np.where(Aprime > 0, Aprime, 1),
                                 np.nan))

    fig, axes = plt.subplots(2, 3, figsize=figsize, constrained_layout=True)

    for ax, image, label in zip(axes[0],
                                [A, L, Aprime],
                                ['A  (atoms − dark)', "L  (light − dark)",
                                 "A'  (synthetic light)"]):
        handle = ax.imshow(image, origin='lower')
        _outline(ax, mask)
        ax.set_title(label, fontsize=9)
        fig.colorbar(handle, ax=ax, location='bottom', shrink=0.8)
        ax.set_xticks([])
        ax.set_yticks([])

    limit = _symmetric(od_df[np.isfinite(od_df)], 99)
    for ax, image, label in zip(axes[1][:2],
                                [od_plain, od_df],
                                ['OD, no defringe: $-\\log(A/L)$',
                                 "OD, defringed: $-\\log(A/A')$"]):
        handle = ax.imshow(image, origin='lower', cmap='viridis',
                           vmin=-limit, vmax=limit)
        _outline(ax, mask)
        ax.set_title(label, fontsize=9)
        fig.colorbar(handle, ax=ax, location='bottom', shrink=0.8)
        ax.set_xticks([])
        ax.set_yticks([])

    # OD over the pixels the fit was allowed to see: width is the noise,
    # centre is the check that no atoms got out of the box.
    ax = axes[1][2]
    bins = np.linspace(-limit, limit, 120)
    for image, label, colour in ((od_plain, 'no defringe', 'tab:gray'),
                                 (od_df, 'defringed', 'tab:blue')):
        values = image[outside]
        values = values[np.isfinite(values)]
        if not values.size:
            continue
        ax.hist(values, bins=bins, histtype='step', density=True, color=colour,
                label=f'{label}  $\\sigma$={values.std():.4f}')
    ax.axvline(0, color='k', lw=0.8, alpha=0.5)
    ax.set_xlabel('OD outside the atom box')
    ax.set_ylabel('density')
    ax.set_title('residual noise over the fitted pixels', fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    _report_leak(od_plain, params, A.shape, ax)

    heading = (f'defringe: {result.defringe_mode}, '
               f'{result.n_components} components from '
               f'{len(result.reference_paths) or 1} frames')
    fig.suptitle(f'{title}\n{heading}' if title else heading, fontsize=10)
    if show:
        plt.show()
    return fig


def _report_leak(od_plain, params, shape, ax=None):
    """Say whether the cloud is spilling out of ``params.mask``.

    Compares the ring just outside the atom box with the border of the view.
    A ring well above the border means atoms the mask does not cover, which
    the defringe fit will try to reproduce — it drags the synthetic light
    frame down over the cloud and ``N`` reads low.  A ring level with the
    border means the mask is doing its job, whatever the border itself sits
    at: a common offset is the two exposures' probe energies differing, and
    the fit rescales that away.
    """
    inner, outer = leak_rings(shape, params.mask)
    if inner is None:
        print('the atom box leaves no border to compare against, so whether '
              'atoms reach outside params.mask cannot be judged from this '
              'shot: widen params.view.')
        return np.nan, np.nan

    ring = float(np.nanmedian(od_plain[inner]))
    border = float(np.nanmedian(od_plain[outer]))
    if ax is not None:
        ax.axvline(border, color='tab:orange', ls=':', lw=1.2)
        ax.axvline(ring, color='tab:red', ls=':', lw=1.2)
        ax.legend(fontsize=8, title=f'ring {ring:+.3f} / border {border:+.3f}',
                  title_fontsize=7)

    if ring - border > 0.05:
        print(f'warning: OD just outside params.mask is {ring:+.3f} against '
              f'{border:+.3f} at the edge of the view, so the cloud reaches '
              f'{ring - border:+.3f} beyond the atom box.  The defringe fit '
              f'will absorb those atoms and N will read low — widen '
              f'params.mask, and params.view with it if the box already '
              f'fills it.')
    elif abs(border) > 0.02:
        print(f'params.mask covers the cloud (ring {ring:+.3f} vs border '
              f'{border:+.3f}).  The {border:+.3f} pedestal across the whole '
              f'frame is the two exposures receiving different probe energy, '
              f'not atoms — any mode other than {chr(39)}none{chr(39)} rescales it away, '
              f'which is why {chr(39)}none{chr(39)} reads the highest N on these shots.')
    return ring, border


def plot_component_scan(scan, pca_number=None, figsize=(11, 4.5), show=True,
                        title=''):
    """Niu Fig. 2(b) against component count: where to set ``pca_number``.

    The solid curve is the noise the algorithm leaves *inside* the atom box on
    a held-out light frame — the region the fit never saw, so this is an
    honest test.  Its minimum is the best ``pca_number``.  The dashed curve is
    the residual over the pixels the fit *did* see; it only ever falls, so the
    gap between the two curves is the overfitting.
    """
    fig, axes = plt.subplots(1, 2 if scan.n_atoms is not None else 1,
                             figsize=figsize, constrained_layout=True,
                             squeeze=False)
    ax = axes[0, 0]
    ax.plot(scan.k, scan.inside, 'o-', color='tab:blue', ms=4,
            label='inside atom box (held out)')
    ax.plot(scan.k, scan.outside, 's--', color='tab:gray', ms=3,
            label='outside atom box (fitted)')
    if np.isfinite(scan.baseline):
        ax.axhline(scan.baseline, color='tab:red', ls=':',
                   label=f'no defringing ({scan.baseline:.4f})')
    if scan.best_k:
        ax.axvline(scan.best_k, color='tab:green', lw=1,
                   label=f'best = {scan.best_k}')
    if pca_number is not None:
        ax.axvline(pca_number, color='k', lw=1, ls='-.',
                   label=f'params.pca_number = {pca_number}')
    ax.set_xlabel('principal components kept')
    ax.set_ylabel('residual OD noise (rms)')
    ax.set_yscale('log')
    ax.set_title('noise on a held-out light frame', fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which='both')

    if scan.n_atoms is not None:
        ax = axes[0, 1]
        ax.plot(scan.k, scan.n_atoms, 'o-', color='tab:purple', ms=4)
        if pca_number is not None:
            ax.axvline(pca_number, color='k', lw=1, ls='-.')
        ax.set_xlabel('principal components kept')
        ax.set_ylabel('fitted N')
        ax.set_title('atom number of this shot vs component count', fontsize=10)
        ax.grid(alpha=0.3)

    if title:
        fig.suptitle(title, fontsize=10)
    if show:
        plt.show()
    return fig


def plot_reference_scan(scan, n_reference=None, figsize=(6, 4.5), show=True,
                        title=''):
    """Niu Fig. 2(b) against reference count: how far back to look.

    Each point rebuilds the basis from the ``n`` light frames closest in time
    to the probe shot and measures the noise left inside the atom box.  Too
    few frames and the basis cannot span the shot's fringes; too many and it
    is dominated by frames describing fringes that have since drifted away.
    """
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    ax.plot(scan.n, scan.inside, 'o-', color='tab:blue', ms=4)
    if np.isfinite(scan.baseline):
        ax.axhline(scan.baseline, color='tab:red', ls=':',
                   label=f'no defringing ({scan.baseline:.4f})')
    if scan.best_n:
        ax.axvline(scan.best_n, color='tab:green', lw=1,
                   label=f'best = {scan.best_n}')
    if n_reference is not None:
        ax.axvline(n_reference, color='k', lw=1, ls='-.',
                   label=f'params.n_reference = {n_reference}')
    ax.set_xlabel('reference light frames in the basis')
    ax.set_ylabel('residual OD noise inside the atom box')
    ax.set_yscale('log')
    ax.set_title(title or 'noise vs reference-set size', fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which='both')
    if show:
        plt.show()
    return fig
