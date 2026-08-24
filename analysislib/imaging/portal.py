"""Easy access to the defringed absorption analysis, from a notebook.

``analysislib/df_image_analysis.py`` is a lyse single-shot routine: it runs
against ``lyse.path`` at import time, so it cannot be called.  This module is
the callable half of it, addressed exactly the way
``helperfuncs.live_plot_scan`` addresses a scan::

    view_shot(year, month, day, sequence, number, shot=0, ...)

so a daily notebook can go straight from "shot 12 of run 57 looked odd" to the
picture, without touching lyse.

    import analysislib.helperfuncs as hf
    view = hf.view_shot(2026, 8, 21, 'cs_molasses_healthcheck', 57, shot=12)
    print(view.fit.n_count)

Add ``debug=True`` for the defringing diagnostics: the principal components
that were kept, what the fit did to this shot, and the two knob scans that say
where ``pca_number`` and ``n_reference`` should sit.  See :mod:`.debug`.

Where the shots live
--------------------
The sequence folder is resolved from labconfig's ``experiment_shot_storage``,
the same as ``helperfuncs._sequence_folder``: that is where each machine's
paths belong, so a notebook says nothing about them and works everywhere.  The
per-call ``storage=`` argument is for reading somewhere that is not the
machine's shot tree at all — an archive, a copy of someone else's run.
"""

from collections import OrderedDict
from dataclasses import dataclass, field
import glob
import os
from typing import List, Optional

import numpy as np

from . import fitting, params as presets, plotting, process
from .defringe import DefringeSet

#: How many light frames to hold in memory between calls.  Each one costs
#: ``ny * nx * 4`` bytes: about 5 MB for the standard CS_H_MOT view.
FRAME_CACHE_SIZE = 96

_frame_cache = OrderedDict()


# ── locating shots ────────────────────────────────────────────────────────

def shot_storage(storage=None):
    """Root of the shot tree: the ``storage`` argument, else labconfig.

    Machine-specific paths live in labconfig, not in notebooks, so leave
    ``storage`` alone unless you are deliberately reading a tree that is not
    this machine's — an archive, or a copy of another rig's run.
    """
    if storage is not None:
        return os.fspath(storage)
    from labscript_utils.labconfig import LabConfig
    return LabConfig().get('DEFAULT', 'experiment_shot_storage')


def sequence_folder(year, month, day, sequence, number, storage=None):
    """``<storage>/<sequence>/<year>/<month>/<day>/<number>``.

    The same layout ``helperfuncs._sequence_folder`` uses, which is
    runmanager's ``output_folder_format``.
    """
    return os.path.join(shot_storage(storage), sequence,
                        f'{year:04d}', f'{month:02d}', f'{day:02d}',
                        f'{number:04d}')


def shot_paths(year, month, day, sequence, number, storage=None):
    """Every h5 file in a sequence folder, sorted by name (so, by shot index)."""
    folder = sequence_folder(year, month, day, sequence, number, storage)
    paths = sorted(glob.glob(os.path.join(folder, '*.h5')))
    if not paths:
        raise FileNotFoundError(f'No h5 files found in {folder}')
    return paths


def _resolve_shot(paths, shot):
    """Index of ``shot`` within ``paths``: an int index or a filename fragment."""
    if isinstance(shot, (int, np.integer)):
        try:
            return range(len(paths))[int(shot)]      # supports shot=-1
        except IndexError:
            raise IndexError(
                f'shot {shot} out of range: the folder holds {len(paths)} '
                f'shots (0..{len(paths) - 1})') from None
    matches = [i for i, p in enumerate(paths) if str(shot) in os.path.basename(p)]
    if not matches:
        raise FileNotFoundError(f'no shot matching {shot!r} in the folder')
    return matches[0]


# ── reference light frames ────────────────────────────────────────────────

def cached_light_frame(path, params):
    """``process.load_light_frame`` memoised on (path, frame geometry).

    ``view_scan`` over N shots would otherwise reload the same reference
    frames N times over, which on a network share dominates the runtime.
    """
    key = (os.path.abspath(os.fspath(path)), params.signature())
    frame = _frame_cache.pop(key, None)
    if frame is None:
        frame = process.load_light_frame(path, params)
    _frame_cache[key] = frame
    while len(_frame_cache) > FRAME_CACHE_SIZE:
        _frame_cache.popitem(last=False)
    return frame


def clear_frame_cache():
    """Forget the memoised light frames (after editing files on disk)."""
    _frame_cache.clear()


def reference_indices(paths, index, n_reference=None, reference='previous',
                      include_self=True):
    """Which shots of ``paths`` go into the defringe basis for shot ``index``.

    ``n_reference`` is how far back to look; None means the whole folder.

    ``reference``
        ``'previous'``  the ``n_reference`` shots immediately before this one,
                        which is what the lyse routine's rolling cache sees.
                        Falls forward when there are not enough earlier shots,
                        so shot 0 is still usable.
        ``'nearest'``   the ``n_reference`` shots closest in index, before or
                        after.  Better offline, where the fringes drift in both
                        directions around the shot of interest.
        ``'all'``       every shot in the folder.

    The shot's own light frame is included unless ``include_self=False``; it
    is by construction the frame most like the one being reconstructed.
    """
    n_total = len(paths)
    if reference == 'all' or n_reference is None:
        chosen = list(range(n_total))
    elif reference == 'previous':
        n = int(n_reference)
        start = max(0, index - n + 1) if include_self else max(0, index - n)
        chosen = list(range(start, index + (1 if include_self else 0)))
        # Not enough history (early in the run): take what follows instead.
        wanted = n if include_self else n
        if len(chosen) < wanted:
            extra = [i for i in range(index + 1, n_total)][:wanted - len(chosen)]
            chosen = sorted(chosen + extra)
    elif reference == 'nearest':
        order = sorted(range(n_total), key=lambda i: (abs(i - index), i))
        if not include_self:
            order = [i for i in order if i != index]
        chosen = sorted(order[:int(n_reference)])
    else:
        raise ValueError(f"unknown reference mode {reference!r}; choose from "
                         "'previous', 'nearest', 'all'")

    if include_self and index not in chosen:
        chosen = sorted(set(chosen) | {index})
    if not include_self:
        chosen = [i for i in chosen if i != index]
    return chosen


def defringe_set_for(paths, index, params, n_reference=None,
                     reference='previous', include_self=True):
    """Build the defringe basis for one shot out of its neighbours in the run.

    Returns ``(defringe_set, reference_paths)``.
    """
    chosen = reference_indices(paths, index, n_reference, reference,
                               include_self)
    frames = [cached_light_frame(paths[i], params) for i in chosen]
    dfset = DefringeSet.from_stack(
        np.stack(frames), mask=params.mask, pca_number=params.pca_number,
        sources=[paths[i] for i in chosen], dtype=params.dtype,
        subtract_mean=params.subtract_mean)
    return dfset, [paths[i] for i in chosen]


# ── the view ──────────────────────────────────────────────────────────────

@dataclass
class ShotView:
    """What :func:`view_shot` gives back."""

    result: process.ShotResult
    fit: fitting.ImageFit
    params: presets.ImagingParams
    path: str
    index: int
    paths: List[str] = field(default_factory=list)
    figures: dict = field(default_factory=dict)
    component_scan: Optional[object] = None
    reference_scan: Optional[object] = None
    fringe_check: Optional[object] = None

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def reference_names(self):
        """Basenames of the shots whose light frames make up the basis."""
        return [os.path.basename(p) for p in self.result.reference_paths]

    def results(self):
        """The numbers ``df_image_analysis.py`` saves, as a dict."""
        fit = self.fit
        out = {'N_int': fit.n_count, 'N_view': fit.n_total,
               'N_x': fit.x.n_fit, 'N_y': fit.y.n_fit,
               'sigma_x (um)': fit.x.width, 'sigma_y (um)': fit.y.width,
               'x0_x (um)': fit.x.center, 'x0_y (um)': fit.y.center,
               'OD_peak': fit.od_peak, 'n_defringe': self.result.n_components}
        if fit.x.separation is not None:
            out['sep_x (um)'] = fit.x.separation
        if fit.y.separation is not None:
            out['sep_y (um)'] = fit.y.separation
        return out

    def __repr__(self):
        return (f'<ShotView {self.name}: N={self.fit.n_count:.3e}, '
                f'sigma=({self.fit.x.width:.0f}, {self.fit.y.width:.0f}) um, '
                f'{self.result.n_components} components>')


def _build_params(preset, overrides):
    """Resolve the preset (name, instance or None) and apply field overrides."""
    if preset is None:
        base = presets.DEFAULT
    elif isinstance(preset, str):
        try:
            base = getattr(presets, preset)
        except AttributeError:
            raise ValueError(
                f'unknown preset {preset!r}; params.py defines '
                f'{[n for n in dir(presets) if n.isupper()]}') from None
    else:
        base = preset
    overrides = {k: v for k, v in overrides.items() if v is not None}
    return base.replace(**overrides) if overrides else base


def view_shot(year, month, day, sequence, number, shot=0, *,
              preset=None, n_reference=None, pca_number=None, defringe=None,
              reference='previous', include_self=True, plot=True, debug=False,
              storage=None, title=None, **overrides):
    """Load, defringe, fit and plot one shot, addressed like ``live_plot_scan``.

    Parameters
    ----------
    year, month, day, sequence, number
        The sequence folder, exactly as in ``helperfuncs.live_plot_scan``.
    shot : int or str
        Index into the folder's sorted h5 files (negative counts from the
        end), or a fragment of the filename such as ``'rep00007'``.
    preset : str or ImagingParams or None
        A preset from :mod:`.params` by name (``'CS_H_MOT'``, ``'CS_H_IS'``,
        ``'CS_H_FULL'``), or an :class:`~.params.ImagingParams`.  Defaults to
        ``params.DEFAULT``.
    n_reference : int or None
        **How far back to look** when pulling the defringe set out of the
        folder.  None uses ``params.n_reference``; pass ``0`` or set
        ``reference='all'`` to use every shot in the folder.
    pca_number : int or None
        **How many principal components to keep.**  None uses
        ``params.pca_number``.
    defringe : str or None
        Override ``params.defringe``.  ``'auto'`` (the default) builds the
        basis from this folder's shots; ``'scale'``, ``'self'``, ``'none'``
        and a path to a saved set behave as in the lyse routine.  ``'scale'``
        is worth trying whenever the fringe check says the PCA fit is leaving
        more fringe than a plain ``A/L`` would.
    reference : {'previous', 'nearest', 'all'}
        Which neighbours make up the basis — see :func:`reference_indices`.
        ``'previous'`` reproduces what the lyse routine sees live;
        ``'nearest'`` is usually better after the fact.
    include_self : bool
        Put this shot's own light frame in the basis.  True matches the lyse
        routine.
    plot : bool
        Draw the ``df_view_image`` figure.
    debug : bool
        Also draw the defringing diagnostics: the kept principal components
        and the spectrum, a before/after of the fit, and the noise-vs-knob
        scans that say where ``pca_number`` and ``n_reference`` belong.
        Costs one extra pass over the basis per component, so it is a few
        seconds rather than instant.
    storage : str or None
        Read a shot tree other than this machine's; see :func:`shot_storage`.
        Normally left alone — labconfig says where the shots are.
    **overrides
        Any other :class:`~.params.ImagingParams` field: ``view=``, ``mask=``,
        ``fit_type=``, ``alpha=``, ``I_sat=``, ``subtract_mean=`` ...

    Returns
    -------
    :class:`ShotView`
    """
    params = _build_params(preset, dict(overrides, n_reference=n_reference,
                                        pca_number=pca_number,
                                        defringe=defringe))

    paths = shot_paths(year, month, day, sequence, number, storage)
    index = _resolve_shot(paths, shot)
    path = paths[index]

    n_ref = None if reference == 'all' or not params.n_reference \
        else params.n_reference

    dfset, refs = (None, [])
    if params.defringe == 'auto':
        dfset, refs = defringe_set_for(paths, index, params, n_ref, reference,
                                       include_self)

    result = process.process_shot(path, params, defringe_set=dfset)
    if dfset is not None:
        result.defringe_mode = 'auto'
        result.reference_paths = refs
    fit = fitting.fit_image(result.nd, params, od=result.od)

    view = ShotView(result=result, fit=fit, params=params, path=path,
                    index=index, paths=paths)
    label = title if title is not None else os.path.basename(path)

    if plot:
        view.figures['shot'] = plotting.plot_shot(result, fit, params,
                                                  title=label)
    if debug:
        _add_debug(view, label, reference, include_self)
    return view


def print_reference_set(view, probe_index=None, max_listed=40):
    """List the shots whose light frames make up this shot's defringe basis.

    Marks the shot under analysis and, when the diagnostics have picked one,
    the held-out probe shot the noise is measured on.  The shots' shared
    filename prefix is printed once rather than on every line.
    """
    paths = list(view.result.reference_paths)
    mode = view.result.defringe_mode
    if not paths:
        note = {'scale': "this shot's own light frame times one scale factor",
                'self': "this shot's own light frame, PCA'd with a constant",
                'none': 'no defringing',
                }.get(mode, 'no reference shots recorded')
        print(f'defringe set: {mode} — {note}')
        return

    names = [os.path.basename(p) for p in paths]
    prefix = os.path.commonprefix(names)
    prefix = prefix[:prefix.rfind('_') + 1] if '_' in prefix else ''
    index_of = {os.path.abspath(p): i for i, p in enumerate(view.paths)}

    folder = os.path.dirname(paths[0])
    print(f'defringe set: {len(paths)} light frames ({mode}) from {folder}')
    if prefix:
        print(f'  all named {prefix}*')

    def _strip(name):
        return name[len(prefix):] if prefix and name.startswith(prefix) else name

    def line(path, name):
        i = index_of.get(os.path.abspath(path))
        tag = ''
        if os.path.abspath(path) == os.path.abspath(view.path):
            tag = '   <- this shot'
        shown = _strip(name)
        return f'  [{i:3d}] {shown}{tag}' if i is not None else f'  [  ?] {shown}{tag}'

    if len(paths) <= max_listed:
        rows = range(len(paths))
    else:
        head, tail = max_listed // 2, max_listed - max_listed // 2
        rows = list(range(head)) + [None] + list(range(len(paths) - tail, len(paths)))
    for r in rows:
        if r is None:
            print(f'  ...  ({len(paths) - max_listed} more)')
        else:
            print(line(paths[r], names[r]))

    if probe_index is not None:
        probe = view.paths[probe_index]
        print(f'  probe (held out of the basis): [{probe_index:3d}] '
              f'{_strip(os.path.basename(probe))}')


def _add_debug(view, label, reference, include_self):
    """Attach the defringing diagnostics to a :class:`ShotView`."""
    from . import debug as dbg

    params, result = view.params, view.result
    probe_index = _probe_index(view, include_self)
    print_reference_set(view, probe_index)
    print()

    view.figures['defringe'] = dbg.plot_defringe(result, params, title=label)

    if result.defringe_set is None:
        print("defringe='none': nothing to diagnose beyond the frames above")
        return

    view.fringe_check = dbg.check_fringes(result, params)
    view.figures['fringes'] = dbg.plot_fringe_check(result, params,
                                                    check=view.fringe_check,
                                                    title=label)
    print(view.fringe_check.summary())
    print()

    if not getattr(result.defringe_set, 'pca', True):
        print(f'defringe={params.defringe!r}: {result.defringe_set!r} — one '
              f'scale factor, no basis, so there is no spectrum to plot and '
              f'neither pca_number nor n_reference does anything.')
        return

    view.figures['basis'] = dbg.plot_basis(result.defringe_set, params,
                                           coefficients=result.coefficients,
                                           title=label)

    if probe_index is None:
        print('every shot in the folder is in the basis, so there is no '
              'held-out frame to measure the noise on: pass include_self=False '
              'or a smaller n_reference to enable the knob scans.')
        return

    probe = cached_light_frame(view.paths[probe_index], params)
    reference_frame = result.L

    scan = dbg.scan_components(result.defringe_set, probe, params.mask,
                               reference=reference_frame)
    scan.probe_path = view.paths[probe_index]
    scan.n_atoms = _atoms_vs_components(view, scan.k)
    view.component_scan = scan
    view.figures['component_scan'] = dbg.plot_component_scan(
        scan, pca_number=params.pca_number,
        title=f'{label}\nprobe: {os.path.basename(scan.probe_path)}')
    print(f'pca_number={params.pca_number}: {scan.summary()}')

    pool = [i for i in range(len(view.paths)) if i != probe_index]
    # Ordered so the last entry is the closest in time to the probe shot,
    # which is what "look n shots back" has to mean for the scan to be honest.
    pool.sort(key=lambda i: -abs(i - probe_index))
    frames = [cached_light_frame(view.paths[i], params) for i in pool]
    rscan = dbg.scan_references(frames, probe, params.mask,
                                pca_number=params.pca_number,
                                reference=reference_frame,
                                dtype=params.dtype,
                                subtract_mean=params.subtract_mean)
    view.reference_scan = rscan
    view.figures['reference_scan'] = dbg.plot_reference_scan(
        rscan, n_reference=params.n_reference,
        title=f'noise vs reference-set size (pca_number={params.pca_number})')
    print(f'n_reference={params.n_reference}: {rscan.summary()}')


def _probe_index(view, include_self):
    """A shot whose light frame is *not* in the basis, for the noise scans.

    The shot under analysis is excluded whatever the mode says.  In ``'auto'``
    its light frame is normally in the basis anyway; in ``'self'`` the basis
    *is* its light frame, so using it as the probe would reconstruct it
    perfectly and report zero noise at every setting.
    """
    used = {os.path.abspath(p) for p in view.result.reference_paths}
    used.add(os.path.abspath(view.path))
    candidates = [i for i, p in enumerate(view.paths)
                  if os.path.abspath(p) not in used]
    if not candidates:
        return None
    # Closest to the shot under study: its fringes are the most comparable.
    return min(candidates, key=lambda i: abs(i - view.index))


def _atoms_vs_components(view, k_values):
    """Fitted atom number of this shot as the basis is truncated.

    The practical companion to the noise scan: ``pca_number`` is safe once N
    has stopped moving with it.
    """
    params, result = view.params, view.result
    numbers = []
    for k in k_values:
        synthetic = result.defringe_set.apply(result.A, n_components=int(k))
        nd = process.nd_calc(result.A, synthetic, params)
        numbers.append(fitting.fit_image(nd, params).n_count)
    return np.asarray(numbers, dtype=float)


def view_scan(year, month, day, sequence, number, shots=None, *,
              preset=None, n_reference=None, pca_number=None, defringe=None,
              reference='nearest', include_self=True, plot=False,
              storage=None, **overrides):
    """Run :func:`view_shot` over a whole sequence folder.

    Returns a :class:`pandas.DataFrame` of the same numbers
    ``df_image_analysis.py`` saves, indexed by shot filename — the offline
    equivalent of letting lyse chew through the run.  ``shots`` selects a
    subset (indices or filename fragments); None does all of them.

    Note the different default: ``reference='nearest'``, because offline there
    is no reason to pretend the later shots have not happened yet.
    """
    import pandas as pd

    paths = shot_paths(year, month, day, sequence, number, storage)
    if shots is None:
        indices = list(range(len(paths)))
    else:
        indices = [_resolve_shot(paths, s) for s in shots]

    rows, names = [], []
    for i in indices:
        view = view_shot(year, month, day, sequence, number, shot=i,
                         preset=preset, n_reference=n_reference,
                         pca_number=pca_number, defringe=defringe,
                         reference=reference, include_self=include_self,
                         plot=plot, storage=storage, **overrides)
        rows.append(view.results())
        names.append(view.name)
    return pd.DataFrame(rows, index=names)
