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

Typical use from a lyse single-shot routine is in
``analysislib/df_image_analysis.py``.  From a notebook::

    from analysislib.imaging import presets, process, fitting, plotting

    params = presets.CS_H_MOT
    result = process.process_shot(shot_path, params)
    fit = fitting.fit_image(result.nd, params, od=result.od)
    plotting.plot_shot(result, fit, params, title=shot_path)
"""

from . import params as presets
from .params import ImagingParams
from .defringe import DefringeSet, LightFrameCache, build_defringe_set
from .fitting import ImageFit, TraceFit, fit_image
from .plotting import plot_shot
from .process import (ShotImages, ShotResult, load_light_frame,
                      load_shot_images, nd_calc, od_calc, process_shot,
                      resolve_defringe_set)

__all__ = [
    'ImagingParams', 'presets',
    'DefringeSet', 'LightFrameCache', 'build_defringe_set',
    'ShotImages', 'ShotResult', 'load_shot_images', 'load_light_frame',
    'od_calc', 'nd_calc', 'process_shot', 'resolve_defringe_set',
    'ImageFit', 'TraceFit', 'fit_image',
    'plot_shot',
]
