"""Masked-PCA defringing.

Python port of ``MATLAB/imaging/defringeset_create.m`` and
``MATLAB/imaging/defringe.m`` (originally Colin Parker's code), plus the
bookkeeping needed to use them from lyse: a rolling cache of recent light
frames and on-disk defringe sets.

The idea: a stack of light frames spans a low-dimensional space of fringe
patterns.  Given an atoms frame, fit it with that basis using only the pixels
*outside* the atom region, and the fit extrapolated over the atom region is the
light frame the shot would have had without atoms.  Dividing by that synthetic
frame removes fringes that a plain atoms/light ratio leaves behind.
"""

from collections import OrderedDict
import os

import numpy as np


class DefringeSet:
    """An orthonormal (under the mask weighting) basis of light frames.

    Attributes
    ----------
    vectors : (k, npix) array
        Basis vectors, flattened.  Orthonormal with respect to the weighted
        inner product ``u @ (weights * v)``.
    weights : (npix,) array
        1.0 for pixels included in the fit, 0.0 for pixels inside the atom box.
    shape : tuple
        Image shape the vectors unflatten to.
    """

    def __init__(self, vectors, weights, shape, n_frames=0, sources=()):
        self.vectors = vectors
        self.weights = weights
        self.shape = tuple(shape)
        self.n_frames = int(n_frames)
        self.sources = list(sources)

    # -- construction ------------------------------------------------------
    @classmethod
    def from_stack(cls, stack, mask=None, pca_number=15, sources=(),
                   dtype='float32'):
        """Build a defringe set from a stack of light frames.

        Parameters
        ----------
        stack : (n, ny, nx) array
            Reference light frames, background subtracted.
        mask : (row0, row1, col0, col1) or None
            Atom region to exclude from the fit, in image coordinates.
        pca_number : int
            Maximum number of basis vectors to keep.
        """
        stack = np.asarray(stack, dtype=dtype)
        if stack.ndim == 2:
            stack = stack[None, ...]
        n, ny, nx = stack.shape

        X = np.real(stack).reshape(n, ny * nx).copy()
        X[~np.isfinite(X)] = 0.0
        # A constant frame, as in defringeset_create.m: lets the fit absorb a
        # uniform offset that no light frame happens to carry.
        X = np.vstack([X, np.ones((1, ny * nx), dtype=X.dtype)])

        weights = np.ones(ny * nx, dtype=X.dtype)
        if mask is not None:
            r0, r1, c0, c1 = mask
            w2d = weights.reshape(ny, nx)
            w2d[max(0, r0):r1, max(0, c0):c1] = 0.0

        # Weighted covariance between frames, then keep the leading modes.
        cov = (X * weights) @ X.T
        evals, evecs = np.linalg.eigh(cov)
        order = np.argsort(evals)[::-1]
        evals, evecs = evals[order], evecs[:, order]

        # Drop modes that are numerically zero: unlike MATLAB's eig they would
        # otherwise blow up in the 1/sqrt(eval) normalisation below.
        if evals[0] <= 0:
            raise ValueError('defringe: reference frames carry no signal')
        keep = evals > evals[0] * 1e-12
        k = min(int(pca_number), int(keep.sum()))
        evals, evecs = evals[:k], evecs[:, :k]

        vectors = (evecs / np.sqrt(evals)).T @ X
        return cls(vectors.astype(dtype), weights, (ny, nx), n_frames=n,
                   sources=sources)

    # -- use ---------------------------------------------------------------
    def apply(self, image):
        """Return the best-fit light frame for ``image``.

        The fit uses only unmasked pixels but the result covers the whole
        image, which is exactly what makes it useful over the atoms.
        """
        image = np.asarray(image, dtype=self.vectors.dtype)
        if image.shape != self.shape:
            raise ValueError(
                f'image shape {image.shape} does not match defringe set '
                f'{self.shape}; rebuild the set or fix params.view')
        flat = image.reshape(-1)
        flat = np.where(np.isfinite(flat), flat, 0.0)
        out = self.vectors.T @ (self.vectors @ (self.weights * flat))
        return np.real(out).reshape(self.shape).astype(float)

    @property
    def n_components(self):
        return self.vectors.shape[0]

    def __repr__(self):
        return (f'<DefringeSet {self.n_components} components from '
                f'{self.n_frames} frames, shape {self.shape}>')

    # -- persistence -------------------------------------------------------
    def save(self, path):
        """Save to a .npz file that :meth:`load` can read back."""
        path = os.fspath(path)
        directory = os.path.dirname(os.path.abspath(path))
        if directory:
            os.makedirs(directory, exist_ok=True)
        np.savez_compressed(
            path,
            vectors=self.vectors,
            weights=self.weights,
            shape=np.asarray(self.shape),
            n_frames=self.n_frames,
            sources=np.asarray(self.sources, dtype=object),
        )
        return path

    @classmethod
    def load(cls, path):
        with np.load(os.fspath(path), allow_pickle=True) as data:
            return cls(data['vectors'], data['weights'],
                       tuple(int(n) for n in data['shape']),
                       int(data['n_frames']),
                       [str(s) for s in data['sources']])


class LightFrameCache:
    """The last N reference light frames, keyed by shot path.

    Lives in ``lyse.routine_storage`` so that a single-shot routine can build a
    defringe basis from the shots it has already seen.  Re-adding a shot (a
    re-analysis) replaces its frame instead of duplicating it, and a change of
    view/mask/camera empties the cache.
    """

    def __init__(self, maxlen=20, signature=None):
        self.maxlen = int(maxlen)
        self.signature = signature
        self.frames = OrderedDict()

    def sync(self, params):
        """Drop everything if the frame geometry changed."""
        signature = params.signature()
        if signature != self.signature:
            self.frames.clear()
            self.signature = signature
        self.maxlen = int(params.n_reference)
        self._trim()

    def add(self, shot_path, frame):
        key = os.path.abspath(os.fspath(shot_path))
        self.frames.pop(key, None)
        self.frames[key] = np.asarray(frame)
        self._trim()

    def _trim(self):
        while len(self.frames) > self.maxlen:
            self.frames.popitem(last=False)

    def stack(self):
        """(n, ny, nx) array of cached frames, oldest first."""
        if not self.frames:
            raise ValueError('light frame cache is empty')
        return np.stack(list(self.frames.values()))

    @property
    def paths(self):
        return list(self.frames)

    def __len__(self):
        return len(self.frames)


def build_defringe_set(shot_paths, params, out_path=None):
    """Build (and optionally save) a defringe set from a list of shot files.

    Use this from a notebook to freeze a good set of reference shots::

        from analysislib.imaging import build_defringe_set, presets
        build_defringe_set(sorted(glob(r'D:\\...\\2026\\08\\20\\00*\\*.h5')),
                           presets.CS_H_MOT,
                           'defringe_sets/dfset_20260820.npz')

    Then point a routine at it with ``params.replace(defringe=<path>)``.

    The file holds one float32 plane per component, so it is about
    ``pca_number * ny * nx * 4`` bytes before compression: tens of MB for a
    typical view.  Keep the view no larger than you need.
    """
    from . import process    # imported here to keep the module import light

    frames = [process.load_light_frame(path, params) for path in shot_paths]
    dfset = DefringeSet.from_stack(
        np.stack(frames),
        mask=params.mask,
        pca_number=params.pca_number,
        sources=[os.fspath(p) for p in shot_paths],
        dtype=params.dtype,
    )
    if out_path is not None:
        dfset.save(out_path)
    return dfset
