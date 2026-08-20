"""1D fits of a density image.

Python port of ``MATLAB/imaging/scan_fit1Dflex.m``: integrate the density image
over the atom box along each axis, fit the resulting trace, and report physical
numbers.  Fit types are ``'gauss'``, ``'dbl'`` (two Gaussians a fixed
separation apart) and ``'tf'`` (Thomas-Fermi).

Traces are in atoms per pixel; positions and widths come back in microns and
fitted atom numbers in atoms.
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy.ndimage import uniform_filter
from scipy.optimize import curve_fit


# -- models ----------------------------------------------------------------

def gauss1d(x, amp, sigma, x0):
    return amp * np.exp(-(x - x0)**2 / (2 * sigma**2))


def dbl_gauss1d(x, amp, sigma, x0, sep):
    return amp * (np.exp(-(x - x0 - sep / 2)**2 / (2 * sigma**2))
                  + np.exp(-(x - x0 + sep / 2)**2 / (2 * sigma**2)))


def thomas_fermi1d(x, amp, r_tf, x0):
    arg = 1 - ((x - x0) / r_tf)**2
    return amp * np.clip(arg, 0, None)**2


@dataclass
class TraceFit:
    """Fit of one integrated trace."""

    axis: str                       # 'x' or 'y'
    fit_type: str
    index: np.ndarray               # pixel index along the axis, within the view
    position: np.ndarray            # full-frame position in microns
    trace: np.ndarray               # atoms per pixel
    fit_trace: np.ndarray           # atoms per pixel
    popt: dict                      # fit parameters, pixel units
    center: float = np.nan          # full-frame position, microns
    width: float = np.nan           # sigma, or r_TF for 'tf', in microns
    amplitude: float = np.nan       # atoms per pixel
    offset: float = 0.0             # atoms per pixel
    n_fit: float = np.nan           # atoms under the fitted profile
    separation: Optional[float] = None   # microns, 'dbl' only
    success: bool = False


@dataclass
class ImageFit:
    """The pair of trace fits plus the straight sums over the atom box."""

    x: TraceFit
    y: TraceFit
    n_count: float                  # atoms summed over the mask
    n_total: float                  # atoms summed over the whole view
    od_peak: float                  # peak of the smoothed OD inside the box
    mask: tuple = field(default=None)


def _moments(inside, low, high, base):
    """Centre and rms width of the trace inside the box, as fit start values.

    Falls back to the middle of the box and a tenth of its width when the
    trace carries no positive signal.
    """
    span = high - low
    weights = np.clip(inside - base, 0, None)
    total = weights.sum()
    if not np.isfinite(total) or total <= 0:
        return (low + high) / 2, span / 10
    index = np.arange(inside.size, dtype=float) + low
    centre = float((index * weights).sum() / total)
    variance = float(((index - centre)**2 * weights).sum() / total)
    width = float(np.clip(np.sqrt(max(variance, 0.0)), 1.0, span))
    return float(np.clip(centre, low, high)), width


def _fit_trace(trace, fit_type, centre_bounds, params, axis, offset=0.0):
    """Fit one trace.  ``centre_bounds`` bounds the centre to the atom box.

    ``offset`` is the full-frame index of the first pixel of the view; it is
    added to reported positions but not to the fit itself.
    """
    trace = np.asarray(trace, dtype=float)
    index = np.arange(trace.size, dtype=float)
    low, high = centre_bounds
    low = float(np.clip(low, 0, trace.size - 1))
    high = float(np.clip(high, low + 1, trace.size))
    inside = trace[int(low):int(high)]
    peak = float(inside.max()) if inside.size else float(trace.max())
    span = high - low
    fit_offset = bool(params.fit_offset)
    base = float(np.median(trace)) if fit_offset else 0.0

    # Start from the moments of the trace inside the box.  A guess of
    # span/10 (as in scan_fit1Dflex.m) costs a lot of iterations on the wide,
    # flat-topped clouds this camera sees, and sometimes fails outright.
    centre, width = _moments(inside, low, high, base)

    if fit_type == 'gauss':
        model, names = gauss1d, ['amp', 'sigma', 'x0']
        p0 = [max(peak - base, 1e-12), width, centre]
        lower, upper = [0, 0, low], [np.inf, span, high]
    elif fit_type == 'dbl':
        model, names = dbl_gauss1d, ['amp', 'sigma', 'x0', 'sep']
        p0 = [max(peak - base, 1e-12), width / 2, centre, width]
        lower, upper = [0, 0, low, 0], [np.inf, span, high, span]
    elif fit_type == 'tf':
        model, names = thomas_fermi1d, ['amp', 'rTF', 'x0']
        p0 = [max(peak - base, 1e-12), 2 * width, centre]
        lower, upper = [0, 0, low], [np.inf, span, high]
    else:
        raise ValueError(f"unknown fit type {fit_type!r}; "
                         "choose from 'gauss', 'dbl', 'tf'")

    if fit_offset:
        base_model = model

        def model(x, *args):
            return base_model(x, *args[:-1]) + args[-1]

        names = names + ['B']
        p0 = p0 + [base]
        lower = lower + [-np.inf]
        upper = upper + [np.inf]

    result = TraceFit(axis=axis, fit_type=fit_type, index=index,
                      position=(index + offset) * params.pixel_um, trace=trace,
                      fit_trace=np.full_like(trace, np.nan), popt={})
    try:
        popt, _ = curve_fit(model, index, trace, p0=p0,
                            bounds=(lower, upper), maxfev=5000)
    except Exception as exc:                      # a bad shot must not stop lyse
        print(f'{axis} fit ({fit_type}) failed: {exc}')
        return result

    popt = dict(zip(names, popt))
    result.popt = popt
    result.fit_trace = model(index, *[popt[n] for n in names])
    result.success = True
    result.amplitude = popt['amp']
    result.offset = popt.get('B', 0.0)
    result.center = (popt['x0'] + offset) * params.pixel_um

    # Atom numbers are integrals of the fitted profile, offset excluded: the
    # constant term is background, not atoms.
    if fit_type == 'gauss':
        result.width = abs(popt['sigma']) * params.pixel_um
        result.n_fit = np.sqrt(2 * np.pi) * popt['amp'] * abs(popt['sigma'])
    elif fit_type == 'dbl':
        result.width = abs(popt['sigma']) * params.pixel_um
        result.n_fit = 2 * np.sqrt(2 * np.pi) * popt['amp'] * abs(popt['sigma'])
        result.separation = abs(popt['sep']) * params.pixel_um
    else:
        result.width = abs(popt['rTF']) * params.pixel_um
        result.n_fit = popt['amp'] * abs(popt['rTF']) * 16 / 15

    return result


def fit_image(nd, params, od=None):
    """Fit the x and y traces of a density image.

    ``nd`` is in atoms per pixel.  The x trace sums the rows inside the atom
    box and runs over columns; the y trace sums the columns inside the box and
    runs over rows, matching ``scan_fit1Dflex.m``.  Centres come back as
    full-frame positions in microns, so they stay comparable when the view
    changes.
    """
    nd = np.asarray(nd, dtype=float)
    r0, r1, c0, c1 = params.mask_region(nd.shape)

    x_trace = nd[r0:r1, :].sum(axis=0)
    y_trace = nd[:, c0:c1].sum(axis=1)

    row_origin, col_origin = params.view_origin
    x_fit_type, y_fit_type = params.fit_types
    x_fit = _fit_trace(x_trace, x_fit_type, (c0, c1), params, 'x', col_origin)
    y_fit = _fit_trace(y_trace, y_fit_type, (r0, r1), params, 'y', row_origin)

    n_count = float(nd[r0:r1, c0:c1].sum())
    n_total = float(nd.sum())
    if od is None:
        od_peak = np.nan
    else:
        # Smooth before taking the peak, otherwise od_peak just reports the
        # worst pixel of shot noise.
        od_peak = float(np.nanmax(uniform_filter(od, 5)[r0:r1, c0:c1]))

    return ImageFit(x=x_fit, y=y_fit, n_count=n_count, n_total=n_total,
                    od_peak=od_peak, mask=(r0, r1, c0, c1))
