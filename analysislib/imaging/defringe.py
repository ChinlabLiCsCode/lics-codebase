"""Masked-PCA defringing.

Python port of ``MATLAB/imaging/defringeset_create.m`` and
``MATLAB/imaging/defringe.m`` (originally Colin Parker's code), plus the
bookkeeping needed to use them from lyse: a rolling cache of recent light
frames and on-disk defringe sets.

The idea (Ockeloen 2010; Niu 2018, ``Niu.pdf`` in this folder): a stack of
light frames spans a low-dimensional space of fringe patterns.  Given an atoms
frame, fit it with that basis using only the pixels *outside* the atom region,
and the fit extrapolated over the atom region is the light frame the shot would
have had without atoms.  Dividing by that synthetic frame removes fringes that
a plain atoms/light ratio leaves behind.

Two knobs decide how well it works, and both are worth scanning with
:mod:`analysislib.imaging.debug`:

``n_reference``
    How many light frames go into the basis.  More frames span more of the
    fringe space, but frames from too long ago describe fringes the current
    shot no longer has.
``pca_number``
    How many principal components are kept.  Niu's Fig. 3 is the criterion:
    keep components while they still look like fringes, drop them once they
    look like white noise.  Keeping too many overfits the shot's own photon
    shot noise into the reference frame, which *adds* noise instead of
    removing it — the effect is strongest when the reference set is small.
"""

from collections import OrderedDict
import os

import numpy as np


class DefringeSet:
    """An orthonormal (under the mask weighting) basis of light frames.

    Attributes
    ----------
    vectors : (k, npix) array
        Basis vectors, flattened, ordered by decreasing eigenvalue.
        Orthonormal with respect to the weighted inner product
        ``u @ (weights * v)``.
    weights : (npix,) array
        1.0 for pixels included in the fit, 0.0 for pixels inside the atom box.
    shape : tuple
        Image shape the vectors unflatten to.
    eigenvalues : (k,) array
        Eigenvalue of each kept component: the variance the component carries
        over the fitted (unmasked) pixels.
    spectrum : (m,) array
        The *full* eigenvalue spectrum before truncation, so a debug plot can
        show what was thrown away as well as what was kept.
    mean : (npix,) array or None
        Mean reference frame, subtracted before the fit and added back after,
        when the set was built with ``subtract_mean=True`` (Niu's convention).
    """

    def __init__(self, vectors, weights, shape, n_frames=0, sources=(),
                 eigenvalues=None, spectrum=None, mean=None):
        self.vectors = vectors
        self.weights = weights
        self.shape = tuple(shape)
        self.n_frames = int(n_frames)
        self.sources = list(sources)
        self.eigenvalues = (np.zeros(len(vectors)) if eigenvalues is None
                            else np.asarray(eigenvalues))
        self.spectrum = (self.eigenvalues if spectrum is None
                         else np.asarray(spectrum))
        self.mean = None if mean is None else np.asarray(mean)

    # -- construction ------------------------------------------------------
    @classmethod
    def from_stack(cls, stack, mask=None, pca_number=15, sources=(),
                   dtype='float32', subtract_mean=False):
        """Build a defringe set from a stack of light frames.

        Parameters
        ----------
        stack : (n, ny, nx) array
            Reference light frames, background subtracted.
        mask : (row0, row1, col0, col1) or None
            Atom region to exclude from the fit, in image coordinates.
        pca_number : int
            Maximum number of basis vectors to keep.
        subtract_mean : bool
            Subtract the mean reference frame before the decomposition, as in
            Niu et al.  The default (False) reproduces
            ``defringeset_create.m``, where the first component ends up being
            essentially the mean beam profile.
        """
        stack = np.asarray(stack, dtype=dtype)
        if stack.ndim == 2:
            stack = stack[None, ...]
        n, ny, nx = stack.shape

        X = np.real(stack).reshape(n, ny * nx).copy()
        X[~np.isfinite(X)] = 0.0

        mean = None
        if subtract_mean:
            mean = X.mean(axis=0)
            X = X - mean

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
        spectrum = evals.copy()

        # Drop modes that are numerically zero: unlike MATLAB's eig they would
        # otherwise blow up in the 1/sqrt(eval) normalisation below.
        if evals[0] <= 0:
            raise ValueError('defringe: reference frames carry no signal')
        keep = evals > evals[0] * 1e-12
        k = min(int(pca_number), int(keep.sum()))
        evals, evecs = evals[:k], evecs[:, :k]

        vectors = (evecs / np.sqrt(evals)).T @ X
        return cls(vectors.astype(dtype), weights, (ny, nx), n_frames=n,
                   sources=sources, eigenvalues=evals, spectrum=spectrum,
                   mean=None if mean is None else mean.astype(dtype))

    # -- use ---------------------------------------------------------------
    def coefficients(self, image):
        """Expansion coefficients of ``image`` on the basis.

        ``x_j = v_j . W . image`` (Niu's step 2).  Because the basis is
        orthonormal under the mask weighting, these are the weighted
        least-squares fit coefficients, and ``|x_j|`` falling to a noise floor
        is the sign that component ``j`` and beyond are no longer describing
        real fringes.
        """
        flat = self._flatten(image)
        return np.asarray(self.vectors @ (self.weights * flat), dtype=float)

    def apply(self, image, n_components=None, return_coefficients=False):
        """Return the best-fit light frame for ``image``.

        The fit uses only unmasked pixels but the result covers the whole
        image, which is exactly what makes it useful over the atoms.

        Parameters
        ----------
        n_components : int or None
            Truncate the basis to its leading ``n_components`` vectors.  None
            (the default) uses the whole set.  Components are ordered by
            decreasing eigenvalue, so truncation is just a row slice — which is
            what makes scanning over component count cheap.
        return_coefficients : bool
            Also return the (untruncated) expansion coefficients.
        """
        flat = self._flatten(image)
        vectors = self.vectors
        if n_components is not None:
            vectors = vectors[:int(n_components)]

        coeffs = vectors @ (self.weights * flat)
        out = np.real(vectors.T @ coeffs).reshape(self.shape).astype(float)
        if self.mean is not None:
            out = out + np.real(self.mean).reshape(self.shape)
        if return_coefficients:
            return out, np.asarray(coeffs, dtype=float)
        return out

    def component(self, index):
        """Principal component ``index`` as a 2D image, for plotting."""
        return np.real(self.vectors[int(index)]).reshape(self.shape)

    def _flatten(self, image):
        image = np.asarray(image, dtype=self.vectors.dtype)
        if image.shape != self.shape:
            raise ValueError(
                f'image shape {image.shape} does not match defringe set '
                f'{self.shape}; rebuild the set or fix params.view')
        flat = image.reshape(-1)
        flat = np.where(np.isfinite(flat), flat, 0.0)
        if self.mean is not None:
            flat = flat - self.mean
        return flat

    @property
    def n_components(self):
        return self.vectors.shape[0]

    @property
    def noise_floor(self):
        """Eigenvalue of the photon-shot-noise plateau, or nan if too small.

        Independent shot noise in ``n`` reference frames contributes ``n-1``
        modes of *equal* variance, so it shows up as a flat plateau at the
        bottom of the spectrum.  Components standing above the plateau carry
        real fringe structure; components inside it carry nothing but the
        reference frames' own noise, and fitting them to a shot just copies
        that noise into the synthetic light frame.  The plateau is therefore
        where ``pca_number`` belongs.
        """
        spectrum = np.asarray(self.spectrum, dtype=float)
        spectrum = spectrum[spectrum > 0]
        if spectrum.size < 4:
            return np.nan
        return float(np.median(spectrum[spectrum.size // 2:]))

    @property
    def n_above_noise(self):
        """How many components stand clear of the shot-noise plateau.

        The suggested ``pca_number``.  Real fringe modes sit above the
        plateau and the plateau is flat, so the boundary between them shows up
        as the largest step down in the spectrum: keep everything above the
        biggest gap.

        The very first component is exempt from the search.  With the
        uncentred PCA of ``defringeset_create.m`` it is the mean beam profile,
        orders of magnitude larger than anything else, and it would otherwise
        win the gap outright and hide the fringes behind it.  A set built with
        ``subtract_mean=True`` has no such component and none is skipped.

        It is a heuristic, and a spectrum with no clean gap has no honest
        answer: treat it as the starting point for
        :func:`~.debug.plot_component_scan`, not as the last word.
        """
        spectrum = np.asarray(self.spectrum, dtype=float)
        floor = self.noise_floor
        if not np.isfinite(floor) or floor <= 0:
            return self.n_components
        # Drop the numerically-null tail: those modes were never in the basis.
        spectrum = spectrum[spectrum > 0.5 * floor]
        first = 1 if self.mean is None else 0
        if spectrum.size <= first + 1:
            return max(1, min(self.n_components, spectrum.size))
        ratios = spectrum[first:-1] / spectrum[first + 1:]
        best = int(np.argmax(ratios))
        if ratios[best] < 1.2:          # no gap worth the name: beam only
            return max(1, min(self.n_components, first))
        return min(self.n_components, first + best + 1)

    @property
    def mask_weights(self):
        """The fit weights as a 2D image: 0 inside the atom box, 1 outside."""
        return np.asarray(self.weights).reshape(self.shape)

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
            eigenvalues=self.eigenvalues,
            spectrum=self.spectrum,
            # np.load cannot round-trip a None, so store an empty array.
            mean=np.asarray([] if self.mean is None else self.mean),
        )
        return path

    @classmethod
    def load(cls, path):
        with np.load(os.fspath(path), allow_pickle=True) as data:
            mean = data['mean'] if 'mean' in data else np.asarray([])
            return cls(data['vectors'], data['weights'],
                       tuple(int(n) for n in data['shape']),
                       int(data['n_frames']),
                       [str(s) for s in data['sources']],
                       eigenvalues=data['eigenvalues'] if 'eigenvalues' in data else None,
                       spectrum=data['spectrum'] if 'spectrum' in data else None,
                       mean=None if mean.size == 0 else mean)


class IntensityScale:
    """``A' = c * L``: this shot's own light frame, rescaled.  No PCA.

    The simplest thing that can work, and on a rig where the atoms and light
    exposures are close enough together that their fringes have not moved, it
    removes fringes *better* than a PCA basis built from other shots — the
    shot's own light frame is the best fringe reference it will ever have.
    What it cannot do is correct a difference in beam *shape*; it only fixes
    the overall level.

    ``c`` is ``exp(median(log(A/L)))`` over the unmasked pixels, which is by
    construction the scale that makes the optical density read zero where
    there are no atoms.  That matters more than it sounds: the two exposures
    routinely receive a few percent different probe energy, and a 0.04 OD
    pedestal left over a 700x1750 atom box integrates into a large spurious
    atom number.

    Quacks like a :class:`DefringeSet` where the pipeline needs it to, but
    ``pca`` is False, so the diagnostics know there is no basis to inspect.
    """

    pca = False

    def __init__(self, light, mask=None, dtype='float32'):
        self.light = np.asarray(light, dtype=dtype)
        self.shape = self.light.shape
        weights = np.ones(self.shape, dtype=self.light.dtype)
        if mask is not None:
            r0, r1, c0, c1 = mask
            weights[max(0, r0):r1, max(0, c0):c1] = 0.0
        self.weights = weights.reshape(-1)
        self.n_frames = 1
        self.sources = []
        self.eigenvalues = np.array([1.0])
        self.spectrum = np.array([1.0])
        self.mean = None
        self.scale = np.nan

    def factor(self, image):
        """The scale ``c`` relating ``image`` to the light frame."""
        image = np.asarray(image, dtype=float)
        light = np.asarray(self.light, dtype=float)
        good = (self.mask_weights > 0) & (image > 0) & (light > 0)
        if not good.any():
            return 1.0
        return float(np.exp(np.median(np.log(image[good] / light[good]))))

    def apply(self, image, n_components=None, return_coefficients=False):
        """``c * L`` for this ``image``.  ``n_components`` is accepted and
        ignored: there is only ever the one component.

        Records the factor on ``self.scale`` so the repr and the diagnostics
        can report what it settled on.
        """
        if image.shape != self.shape:
            raise ValueError(
                f'image shape {image.shape} does not match light frame '
                f'{self.shape}')
        self.scale = self.factor(image)
        out = self.scale * np.asarray(self.light, dtype=float)
        if return_coefficients:
            return out, np.array([self.scale])
        return out

    def coefficients(self, image):
        return np.array([self.factor(image)])

    @property
    def n_components(self):
        return 1

    @property
    def noise_floor(self):
        return np.nan

    @property
    def n_above_noise(self):
        return 1

    @property
    def mask_weights(self):
        return np.asarray(self.weights).reshape(self.shape)

    def component(self, index):
        return np.asarray(self.light, dtype=float)

    def __repr__(self):
        scale = '' if not np.isfinite(self.scale) else f', c={self.scale:.4f}'
        return f'<IntensityScale on this shot\'s own light frame{scale}>'


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


def build_defringe_set(shot_paths, params, out_path=None, pca_number=None,
                       subtract_mean=False):
    """Build (and optionally save) a defringe set from a list of shot files.

    Use this from a notebook to freeze a good set of reference shots::

        from analysislib.imaging import build_defringe_set, presets
        build_defringe_set(sorted(glob(r'D:\\...\\2026\\08\\20\\00*\\*.h5')),
                           presets.CS_H_MOT,
                           'defringe_sets/dfset_20260820.npz')

    Then point a routine at it with ``params.replace(defringe=<path>)``.

    ``pca_number`` defaults to ``params.pca_number``.  The file holds one
    float32 plane per component, so it is about ``pca_number * ny * nx * 4``
    bytes before compression: tens of MB for a typical view.  Keep the view no
    larger than you need.
    """
    from . import process    # imported here to keep the module import light

    frames = [process.load_light_frame(path, params) for path in shot_paths]
    dfset = DefringeSet.from_stack(
        np.stack(frames),
        mask=params.mask,
        pca_number=params.pca_number if pca_number is None else pca_number,
        sources=[os.fspath(p) for p in shot_paths],
        dtype=params.dtype,
        subtract_mean=subtract_mean,
    )
    if out_path is not None:
        dfset.save(out_path)
    return dfset
