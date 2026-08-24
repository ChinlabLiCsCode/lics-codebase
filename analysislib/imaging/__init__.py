"""Absorption imaging pipeline: a Python port of MATLAB/imaging.

The MATLAB folder builds a density image out of a shot in four steps, and so
does this package:

===========================  ==================================
MATLAB                       here
===========================  ==================================
``build_params.m``           :mod:`.params` (``ImagingParams``, presets)
``load_img.m``               :func:`.process.load_shot_images`
``defringeset_create.m``     :meth:`.defringe.DefringeSet.from_stack`
``defringe.m``               :meth:`.defringe.DefringeSet.apply`
``nd_calc.m``                :func:`.process.nd_calc`
``proc_imgs.m``              :func:`.process.process_shot`
``scan_fit1Dflex.m``         :func:`.fitting.fit_image`
``df_view_image``            :func:`.plotting.plot_shot`
===========================  ==================================

Two things have no MATLAB counterpart: :mod:`.portal`, which addresses a shot
the way ``helperfuncs.live_plot_scan`` addresses a scan, and :mod:`.debug`,
which plots the principal components and scans the two defringe knobs.

From a notebook, the short way::

    import analysislib.helperfuncs as hf

    view = hf.view_shot(2026, 8, 21, 'cs_molasses_healthcheck', 57, shot=12)
    view = hf.view_shot(2026, 8, 21, 'cs_molasses_healthcheck', 57, shot=12,
                        n_reference=8, pca_number=6, debug=True)

and the long way, when you want to hold the pieces yourself::

    from analysislib.imaging import presets, process, fitting, plotting

    params = presets.CS_H_MOT
    result = process.process_shot(shot_path, params)
    fit = fitting.fit_image(result.nd, params, od=result.od)
    plotting.plot_shot(result, fit, params, title=shot_path)
"""

from . import debug
from . import params as presets
from . import portal
from .params import ImagingParams
from .defringe import (DefringeSet, IntensityScale, LightFrameCache,
                       build_defringe_set)
from .debug import (ComponentScan, FringeCheck, ReferenceScan, check_fringes,
                    fringe_anisotropy, od_noise, plot_basis,
                    plot_component_scan, plot_defringe, plot_fringe_check,
                    plot_reference_scan, scan_components, scan_references)
from .fitting import ImageFit, TraceFit, fit_image
from .plotting import plot_shot
from .portal import (ShotView, print_reference_set, sequence_folder,
                     shot_paths, view_scan, view_shot)
from .process import (ShotImages, ShotResult, load_light_frame,
                      load_shot_images, nd_calc, od_calc, process_shot,
                      resolve_defringe_set)

__all__ = [
    'ImagingParams', 'presets',
    'DefringeSet', 'IntensityScale', 'LightFrameCache', 'build_defringe_set',
    'ShotImages', 'ShotResult', 'load_shot_images', 'load_light_frame',
    'od_calc', 'nd_calc', 'process_shot', 'resolve_defringe_set',
    'ImageFit', 'TraceFit', 'fit_image',
    'plot_shot',
    'portal', 'ShotView', 'view_shot', 'view_scan', 'sequence_folder',
    'shot_paths', 'print_reference_set',
    'debug', 'ComponentScan', 'ReferenceScan', 'FringeCheck', 'od_noise',
    'check_fringes', 'fringe_anisotropy', 'plot_basis', 'plot_defringe',
    'plot_component_scan', 'plot_reference_scan', 'plot_fringe_check',
    'scan_components', 'scan_references',
]
