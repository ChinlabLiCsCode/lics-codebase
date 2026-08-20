"""Loading shot frames and turning them into atom density.

Python port of ``MATLAB/imaging/load_img.m``, ``nd_calc.m`` and the processing
half of ``proc_imgs.m``, reading labscript shot files instead of .mat files.

Frame convention: the PCO Panda writes ``atoms``, ``light`` and ``dark`` into
``/images/<camera>/<acquisition>/``.  The dark frame is the per-shot background
(``bginfo = 'self'`` in the MATLAB code), so it is subtracted from both the
atoms and light frames before anything else happens.
"""

from dataclasses import dataclass, field
import os

import h5py
import numpy as np

from .defringe import DefringeSet


@dataclass
class ShotImages:
    """The three raw frames of one shot, cropped to ``params.view``."""

    atoms: np.ndarray
    light: np.ndarray
    dark: np.ndarray
    shot_path: str
    acquisition: str

    @property
    def A(self):
        """Atoms frame, dark subtracted."""
        return self.atoms - self.dark

    @property
    def L(self):
        """Light frame, dark subtracted."""
        return self.light - self.dark


@dataclass
class ShotResult:
    """Everything a single shot produces downstream of the raw frames."""

    images: ShotImages
    A: np.ndarray             # atoms frame, dark subtracted
    L: np.ndarray             # light frame, dark subtracted
    Aprime: np.ndarray        # synthetic light frame for the atoms frame
    od: np.ndarray            # optical density
    nd: np.ndarray            # column density, atoms per pixel
    defringe_set: object = None
    defringe_mode: str = 'none'
    reference_paths: list = field(default_factory=list)

    @property
    def n_components(self):
        return 0 if self.defringe_set is None else self.defringe_set.n_components


# -- loading ---------------------------------------------------------------

def find_acquisition(h5_file, params):
    """Name of the image group to read, autodetecting when unset.

    Sequences name the group after the imaging call (``absorption1``,
    ``absorption2``, ...), so prefer an explicit ``params.acquisition`` when a
    shot contains more than one.
    """
    if params.acquisition is not None:
        return params.acquisition
    group = f'images/{params.camera}'
    if group not in h5_file:
        raise KeyError(f'shot has no {group} group')
    names = sorted(h5_file[group])
    if not names:
        raise KeyError(f'{group} contains no acquisitions')
    return names[0]


def _crop(frame, params):
    """Apply the transpose and view crop, in that order (as in load_img.m)."""
    if params.transpose:
        frame = frame.T
    rows, cols = params.view_slice()
    return np.ascontiguousarray(frame[rows, cols], dtype=float)


def load_frames(shot_path, params, frames=('atoms', 'light', 'dark')):
    """Load named frames of one shot, cropped to ``params.view``.

    Returns a dict keyed by the names in ``frames``.
    """
    names = {'atoms': params.atoms_frame,
             'light': params.light_frame,
             'dark': params.dark_frame}
    out = {}
    with h5py.File(os.fspath(shot_path), 'r') as f:
        acq = find_acquisition(f, params)
        group = f[f'images/{params.camera}/{acq}']
        for key in frames:
            dataset = names[key]
            if dataset not in group:
                raise KeyError(
                    f'{os.path.basename(os.fspath(shot_path))}: no frame '
                    f'{dataset!r} in images/{params.camera}/{acq}')
            out[key] = _crop(group[dataset][:], params)
    out['acquisition'] = acq
    return out


def load_shot_images(shot_path, params):
    """Load all three frames of a shot as a :class:`ShotImages`."""
    data = load_frames(shot_path, params)
    return ShotImages(atoms=data['atoms'], light=data['light'],
                      dark=data['dark'], shot_path=os.fspath(shot_path),
                      acquisition=data['acquisition'])


def load_light_frame(shot_path, params):
    """Load one dark-subtracted light frame: the unit of a defringe set."""
    data = load_frames(shot_path, params, frames=('light', 'dark'))
    return (data['light'] - data['dark']).astype(params.dtype)


# -- density ---------------------------------------------------------------

def od_calc(A, Aprime, params):
    """Optical density of ``A`` against reference ``Aprime``.

    Port of the OD half of ``nd_calc.m``: the saturation-corrected expression
    from Reinaudi et al., extended with the empirical quadratic term.  With the
    defaults (``I_sat = inf``, ``alpha = (1, 0, 0)``) it reduces to the
    familiar ``-log(A/Aprime)``.
    """
    A = np.asarray(A, dtype=float)
    Aprime = np.asarray(Aprime, dtype=float)

    a0, a1, a2 = params.alpha
    with np.errstate(divide='ignore', invalid='ignore'):
        T = np.divide(A, Aprime, out=np.ones_like(A), where=Aprime != 0)
        # A negative transmission is noise, not signal: clamp before the log.
        T = np.where(T > 0, T, np.nan)
        lT = np.log(T)
        sc = Aprime / params.I_sat if np.isfinite(params.I_sat) else np.zeros_like(A)

        if a2 == 0:
            od = (sc - sc * T - a0 * lT) / (1 + a1 * lT)
        else:
            od = (-1 - a1 * lT
                  + np.sqrt(-4 * a2 * lT * (sc * (T - 1) + a0 * lT)
                            + (1 + a1 * lT)**2)) / (2 * a2 * lT)

    od = np.real(od)
    od[~np.isfinite(od)] = 0.0
    return od


def nd_calc(A, Aprime, params):
    """Column density in atoms per pixel.  Port of ``nd_calc.m``."""
    return od_calc(A, Aprime, params) * params.pixel**2 / params.sigma0


# -- defringe set resolution ----------------------------------------------

def resolve_defringe_set(L, params, cache=None):
    """Pick the defringe basis for a shot whose light frame is ``L``.

    ``params.defringe`` selects the mode:

    ``'none'``
        No defringing; the shot's own light frame is the reference.
    ``'self'``
        Basis from this shot's light frame alone, which amounts to rescaling
        it to match the atoms frame outside the mask.
    ``'auto'``
        Basis from ``cache`` (the last ``params.n_reference`` shots) plus this
        shot.  Falls back to ``'self'`` on the first shot.
    a path
        A set saved by :func:`~.defringe.build_defringe_set`.

    Returns ``(defringe_set, mode, reference_paths)``; ``defringe_set`` is
    None for ``'none'``.
    """
    mode = params.defringe

    if mode == 'none':
        return None, 'none', []

    if mode == 'self':
        dfset = DefringeSet.from_stack(L[None, ...], mask=params.mask,
                                       pca_number=params.pca_number,
                                       dtype=params.dtype)
        return dfset, 'self', []

    if mode == 'auto':
        if cache is None or len(cache) == 0:
            stack = L[None, ...]
            paths = []
        else:
            stack = cache.stack()
            paths = cache.paths
        dfset = DefringeSet.from_stack(stack, mask=params.mask,
                                       pca_number=params.pca_number,
                                       sources=paths, dtype=params.dtype)
        return dfset, 'auto', paths

    # Anything else is treated as a path to a saved set.
    dfset = DefringeSet.load(mode)
    if dfset.shape != L.shape:
        raise ValueError(
            f'defringe set {mode} has shape {dfset.shape} but the current '
            f'view gives {L.shape}; rebuild it or fix params.view')
    return dfset, 'file', list(dfset.sources)


# -- the whole pipeline for one shot --------------------------------------

def process_shot(shot_path, params, cache=None, defringe_set=None):
    """Load one shot and produce its density image.

    Port of ``proc_imgs.m`` for a single shot.  Pass ``defringe_set`` to reuse
    a basis, or ``cache`` (a :class:`~.defringe.LightFrameCache`) to let
    ``params.defringe = 'auto'`` build one from recent shots.  The shot's own
    light frame is added to ``cache`` before the basis is built, so it always
    contributes to its own reference.
    """
    images = load_shot_images(shot_path, params)
    A, L = images.A, images.L

    if cache is not None:
        cache.sync(params)
        cache.add(shot_path, L.astype(params.dtype))

    if defringe_set is None:
        defringe_set, mode, refs = resolve_defringe_set(
            L.astype(params.dtype), params, cache=cache)
    else:
        mode, refs = 'given', list(defringe_set.sources)

    Aprime = L if defringe_set is None else defringe_set.apply(A)

    od = od_calc(A, Aprime, params)
    nd = od * params.pixel**2 / params.sigma0

    return ShotResult(images=images, A=A, L=L, Aprime=Aprime, od=od, nd=nd,
                      defringe_set=defringe_set, defringe_mode=mode,
                      reference_paths=refs)
