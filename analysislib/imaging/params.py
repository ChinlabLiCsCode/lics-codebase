"""Imaging parameters for the absorption imaging pipeline.

Python port of ``MATLAB/imaging/build_params.m``: a parameter bundle that
describes where the frames live in the shot file, how to crop them, and the
physics needed to turn counts into atoms.  Named presets at the bottom of this
module play the role of ``paramsCH_IS``, ``paramsCH_MOT`` and friends.

Region conventions
------------------
``view`` and ``mask`` are both ``(row_start, row_stop, col_start, col_stop)``
tuples with half-open (python slice) bounds.

* ``view`` crops the full sensor frame.  Everything downstream works in view
  coordinates.
* ``mask`` is the *atom region*, given in view coordinates.  As in
  ``defringeset_create.m`` it is excluded from the defringe fit (the synthetic
  light frame is fitted only to pixels outside it) and, as in
  ``scan_fit1Dflex.m``, it sets the integration window and the centre bounds
  for the 1D fits.
"""

from dataclasses import dataclass, replace
from typing import Optional, Sequence, Tuple, Union

import numpy as np

Region = Tuple[int, int, int, int]


@dataclass(frozen=True)
class ImagingParams:
    """Everything needed to turn a shot file into an atom-density image."""

    # ── where the frames live in the shot file ────────────────────────────
    camera: str = 'pco_panda'
    acquisition: Optional[str] = None       # None → autodetect (absorption1, …)
    atoms_frame: str = 'atoms'
    light_frame: str = 'light'
    dark_frame: str = 'dark'

    # ── geometry ──────────────────────────────────────────────────────────
    view: Optional[Region] = None           # crop of the full frame
    mask: Optional[Region] = None           # atom box, in view coordinates
    transpose: bool = False                 # swap rows/cols after loading

    # ── physics ───────────────────────────────────────────────────────────
    atom: str = 'Cs'
    wavelength: float = 852.34727582e-9     # m, Cs D2
    sensor_pixel: float = 6.5e-6            # m, physical pixel pitch
    magnification: float = 1.2823           # calibrated 2026-08-11 (TOF gravity)
    I_sat: float = np.inf                   # counts per pixel; inf → no sat. corr.
    alpha: Tuple[float, float, float] = (1.0, 0.0, 0.0)   # OD correction terms

    # ── defringing ────────────────────────────────────────────────────────
    defringe: str = 'auto'                  # 'none' | 'self' | 'auto' | <path>
    pca_number: int = 10                    # basis vectors kept
    n_reference: int = 15                   # rolling cache depth for 'auto'
    dtype: str = 'float32'                  # working dtype for the big arrays

    # ── fitting ───────────────────────────────────────────────────────────
    fit_type: Union[str, Sequence[str]] = 'gauss'   # 'gauss' | 'dbl' | 'tf'
    fit_offset: bool = False                # fit a constant baseline as well

    # ── derived quantities ────────────────────────────────────────────────
    @property
    def pixel(self) -> float:
        """Object-plane size of one pixel, in metres."""
        return self.sensor_pixel / self.magnification

    @property
    def pixel_um(self) -> float:
        """Object-plane size of one pixel, in microns."""
        return self.pixel * 1e6

    @property
    def sigma0(self) -> float:
        """Resonant cross section 3λ²/2π, in m²."""
        return 3 * self.wavelength**2 / (2 * np.pi)

    @property
    def fit_types(self) -> Tuple[str, str]:
        """Fit type for the (x, y) traces, as in scan_fit1Dflex.m."""
        if isinstance(self.fit_type, str):
            return self.fit_type, self.fit_type
        x_fit, y_fit = self.fit_type
        return x_fit, y_fit

    # ── helpers ───────────────────────────────────────────────────────────
    def replace(self, **kwargs) -> 'ImagingParams':
        """Return a copy with the given fields overridden."""
        return replace(self, **kwargs)

    @property
    def view_origin(self) -> Tuple[int, int]:
        """(row, column) of the top-left view pixel in the full frame.

        Fitted centres and plot axes are reported in full-frame coordinates so
        that a change of view does not move the cloud.
        """
        if self.view is None:
            return 0, 0
        return self.view[0], self.view[2]

    def view_slice(self) -> Tuple[slice, slice]:
        """Slices that crop a full frame down to ``view``."""
        if self.view is None:
            return slice(None), slice(None)
        r0, r1, c0, c1 = self.view
        return slice(r0, r1), slice(c0, c1)

    def mask_region(self, shape) -> Region:
        """The atom box clipped to ``shape``; the whole image if unset."""
        ny, nx = shape
        if self.mask is None:
            return 0, ny, 0, nx
        r0, r1, c0, c1 = self.mask
        return (max(0, r0), min(ny, r1), max(0, c0), min(nx, c1))

    def mask_slice(self, shape) -> Tuple[slice, slice]:
        r0, r1, c0, c1 = self.mask_region(shape)
        return slice(r0, r1), slice(c0, c1)

    def signature(self) -> tuple:
        """Identity of the frame geometry, for cache invalidation.

        Two sets of parameters sharing a signature produce light frames of the
        same shape describing the same pixels, so a defringe basis built under
        one is valid under the other.
        """
        return (self.camera, self.acquisition, self.light_frame, self.dark_frame,
                self.view, self.mask, self.transpose, self.dtype)


# ── presets ───────────────────────────────────────────────────────────────
# The build_params.m analogue.  Add a preset when you settle on a new region
# rather than editing values in a routine.

#: Full sensor, no crop.  Correct but memory-hungry: a defringe basis over the
#: whole 2048 x 2048 frame costs ~270 MB for 16 reference frames.  Use it to
#: find a cloud, then crop with .replace(view=...).
CS_H_FULL = ImagingParams()

#: Cs MOT / molasses on the horizontal PCO Panda.  View and mask were set from
#: the 2026-08-20 healthcheck shots: the cloud is elongated along x, spanning
#: full-frame rows 750-1100 and columns 250-1550, centred near row 913.
CS_H_MOT = ImagingParams(
    view=(550, 1350, 50, 1750),
    mask=(150, 600, 150, 1550),
    fit_type='gauss',
)

#: Same optics, tighter box for the dense core of the cloud (in situ, or after
#: a short time of flight).
CS_H_IS = CS_H_MOT.replace(
    view=(700, 1150, 150, 1100),
    mask=(100, 350, 150, 750),
)

#: Default used by the lyse routine.
DEFAULT = CS_H_MOT
