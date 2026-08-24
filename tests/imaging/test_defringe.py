"""The parts of the defringing that can be checked without a shot file.

Synthetic light frames: a smooth beam profile, one or two sinusoidal fringe
patterns whose amplitudes vary shot to shot, and photon shot noise.  That is
the situation the algorithm is designed for, so a basis built from such a stack
should recover the fringes, report a shot-noise plateau below them, and
reconstruct a held-out frame better than a neighbouring frame does.
"""

import numpy as np
import pytest

from analysislib.imaging import portal
from analysislib.imaging.debug import (_parsimonious, od_noise,
                                       scan_components, scan_references)
from analysislib.imaging.defringe import DefringeSet, LightFrameCache
from analysislib.imaging.params import ImagingParams

NY, NX = 40, 60
MASK = (12, 28, 18, 42)
COUNTS = 400.0


def make_frames(n, n_fringes=2, seed=0, noise=True):
    """A stack of light frames: beam profile + drifting fringes + shot noise."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:NY, 0:NX]
    beam = COUNTS * np.exp(-((x - NX / 2)**2 / (2 * (NX / 1.5)**2)
                             + (y - NY / 2)**2 / (2 * (NY / 1.5)**2)))
    patterns = [np.sin(2 * np.pi * (x + 2 * y) / 11),
                np.cos(2 * np.pi * (x - y) / 7)][:n_fringes]

    frames = []
    for _ in range(n):
        frame = beam.copy()
        for pattern in patterns:
            frame = frame + 0.15 * COUNTS * rng.normal() * pattern
        if noise:
            frame = rng.poisson(np.clip(frame, 0, None)).astype(float)
        frames.append(frame)
    return np.asarray(frames, dtype='float32')


# ── the basis itself ──────────────────────────────────────────────────────

def test_basis_is_orthonormal_under_the_mask_weighting():
    """The property ``apply`` relies on: the fit is a projection, not a solve."""
    dfset = DefringeSet.from_stack(make_frames(8), mask=MASK, pca_number=6,
                                   dtype='float64')
    gram = dfset.vectors @ (dfset.weights * dfset.vectors).T
    assert np.allclose(gram, np.eye(dfset.n_components), atol=1e-10)


def test_float32_orthonormality_is_good_enough_to_use():
    """float32 is the working dtype; it costs a few parts in 10^3, no more."""
    dfset = DefringeSet.from_stack(make_frames(8), mask=MASK, pca_number=6)
    gram = dfset.vectors @ (dfset.weights * dfset.vectors).T
    assert np.allclose(gram, np.eye(dfset.n_components), atol=5e-3)


def test_masked_pixels_carry_no_weight():
    dfset = DefringeSet.from_stack(make_frames(6), mask=MASK, pca_number=4)
    r0, r1, c0, c1 = MASK
    assert dfset.mask_weights[r0:r1, c0:c1].max() == 0
    # and every pixel outside the box does count
    outside = dfset.mask_weights.copy()
    outside[r0:r1, c0:c1] = 1
    assert outside.min() == 1


def test_pca_number_caps_the_basis():
    frames = make_frames(10)
    assert DefringeSet.from_stack(frames, mask=MASK, pca_number=3).n_components == 3
    # never more components than the stack (plus the constant frame) can span
    assert DefringeSet.from_stack(frames, mask=MASK, pca_number=99).n_components <= 11


def test_apply_truncates_to_n_components():
    dfset = DefringeSet.from_stack(make_frames(8), mask=MASK, pca_number=6)
    probe = make_frames(1, seed=99)[0]
    full = dfset.apply(probe)
    assert np.allclose(dfset.apply(probe, n_components=dfset.n_components), full)
    # a truncated fit is a different, worse fit
    assert not np.allclose(dfset.apply(probe, n_components=1), full)


def test_apply_rejects_a_mismatched_view():
    dfset = DefringeSet.from_stack(make_frames(4), mask=MASK, pca_number=3)
    with pytest.raises(ValueError, match='does not match defringe set'):
        dfset.apply(np.zeros((NY + 1, NX)))


def test_coefficients_agree_with_the_reconstruction():
    dfset = DefringeSet.from_stack(make_frames(8), mask=MASK, pca_number=5)
    probe = make_frames(1, seed=7)[0]
    synthetic, coefficients = dfset.apply(probe, return_coefficients=True)
    assert np.allclose(coefficients, dfset.coefficients(probe), rtol=1e-4)
    rebuilt = (coefficients @ dfset.vectors).reshape(dfset.shape)
    assert np.allclose(rebuilt, synthetic, rtol=1e-4, atol=1e-4)


def test_defringing_beats_a_neighbouring_light_frame():
    """The point of the exercise: a fitted reference beats a raw one."""
    frames = make_frames(16, seed=1)
    probe = make_frames(1, seed=1234)[0]
    dfset = DefringeSet.from_stack(frames, mask=MASK, pca_number=4)
    assert od_noise(probe, dfset.apply(probe), MASK) < \
        od_noise(probe, frames[-1], MASK)


def test_subtract_mean_round_trips_and_still_fits():
    frames = make_frames(10, seed=3)
    probe = make_frames(1, seed=55)[0]
    plain = DefringeSet.from_stack(frames, mask=MASK, pca_number=4)
    centred = DefringeSet.from_stack(frames, mask=MASK, pca_number=4,
                                     subtract_mean=True)
    assert centred.mean is not None and plain.mean is None
    # both are legitimate fits of the same frame, to within the noise
    assert od_noise(probe, centred.apply(probe), MASK) < \
        od_noise(probe, frames[-1], MASK)


def test_save_and_load_round_trip(tmp_path):
    dfset = DefringeSet.from_stack(make_frames(6), mask=MASK, pca_number=4,
                                   sources=['a.h5', 'b.h5'])
    probe = make_frames(1, seed=11)[0]
    loaded = DefringeSet.load(dfset.save(tmp_path / 'set.npz'))
    assert loaded.n_components == dfset.n_components
    assert loaded.sources == ['a.h5', 'b.h5']
    assert np.allclose(loaded.eigenvalues, dfset.eigenvalues)
    assert np.allclose(loaded.apply(probe), dfset.apply(probe))


# ── the shot-noise plateau ────────────────────────────────────────────────

def test_noise_floor_finds_the_shot_noise_plateau():
    """Two fringe patterns in the frames, so two components should stand out."""
    dfset = DefringeSet.from_stack(make_frames(20, n_fringes=2, seed=5),
                                   mask=MASK, pca_number=18)
    assert np.isfinite(dfset.noise_floor)
    # beam profile + the two fringe patterns
    assert dfset.n_above_noise == 3
    assert dfset.eigenvalues[2] > 2 * dfset.noise_floor
    assert dfset.eigenvalues[-1] < 2 * dfset.noise_floor


def test_noise_floor_tracks_the_number_of_fringe_patterns():
    one = DefringeSet.from_stack(make_frames(20, n_fringes=1, seed=6),
                                 mask=MASK, pca_number=18)
    assert one.n_above_noise == 2          # beam profile + one fringe


def test_noise_free_frames_have_no_plateau_to_speak_of():
    dfset = DefringeSet.from_stack(make_frames(12, seed=8, noise=False),
                                   mask=MASK, pca_number=10)
    # with no shot noise the trailing eigenvalues collapse, so everything
    # real stands above them
    assert dfset.n_above_noise <= 3


# ── choosing the knobs ────────────────────────────────────────────────────

def test_parsimonious_prefers_the_cheapest_equally_good_setting():
    x = np.arange(1, 7)
    values = np.array([1.0, 0.5, 0.499, 0.498, 0.4979, 0.4978])
    best, at_edge = _parsimonious(x, values, tol=0.01)
    assert best == 2            # not 6, even though 6 is the raw minimum
    assert at_edge is False


def test_parsimonious_flags_a_range_that_was_too_short():
    x = np.arange(1, 5)
    best, at_edge = _parsimonious(x, np.array([4.0, 3.0, 2.0, 1.0]), tol=0.01)
    assert best == 4 and at_edge is True


def test_component_scan_stops_at_the_plateau():
    frames = make_frames(20, n_fringes=2, seed=9)
    probe = make_frames(1, seed=4321)[0]
    dfset = DefringeSet.from_stack(frames, mask=MASK, pca_number=12)
    scan = scan_components(dfset, probe, MASK, reference=frames[-1])
    assert scan.baseline > np.nanmin(scan.inside)      # defringing helps
    assert scan.best_k <= scan.spectrum_k + 2          # agrees with the spectrum
    assert scan.k[-1] == dfset.n_components


def test_reference_scan_improves_with_more_frames():
    frames = make_frames(24, seed=10)
    probe = make_frames(1, seed=999)[0]
    scan = scan_references(frames, probe, MASK, pca_number=4,
                           n_values=[2, 4, 8, 16, 24], reference=frames[-1])
    assert scan.inside[0] > scan.inside[-1]
    assert scan.baseline > np.nanmin(scan.inside)


def test_od_noise_ignores_the_dead_corners_of_a_beam():
    frame = np.full((NY, NX), 100.0)
    reference = frame.copy()
    frame[0, 0] = reference[0, 0] = 0.0       # a dead pixel, not a fluctuation
    assert od_noise(frame, reference) == pytest.approx(0.0, abs=1e-12)


# ── picking reference shots out of a run ──────────────────────────────────

PATHS = [f'shot_{i:02d}.h5' for i in range(10)]


def test_previous_looks_backwards_and_includes_the_shot_itself():
    assert portal.reference_indices(PATHS, 6, 3, 'previous') == [4, 5, 6]


def test_previous_falls_forward_when_the_run_has_only_just_started():
    assert portal.reference_indices(PATHS, 0, 3, 'previous') == [0, 1, 2]
    assert portal.reference_indices(PATHS, 1, 3, 'previous') == [0, 1, 2]


def test_nearest_straddles_the_shot():
    assert portal.reference_indices(PATHS, 5, 5, 'nearest') == [3, 4, 5, 6, 7]


def test_all_takes_the_whole_folder_whatever_n_reference_says():
    assert portal.reference_indices(PATHS, 5, 2, 'all') == list(range(10))
    assert portal.reference_indices(PATHS, 5, None, 'previous') == list(range(10))


def test_include_self_false_leaves_the_shot_out():
    chosen = portal.reference_indices(PATHS, 6, 3, 'previous', include_self=False)
    assert 6 not in chosen and len(chosen) == 3
    chosen = portal.reference_indices(PATHS, 6, 4, 'nearest', include_self=False)
    assert 6 not in chosen and len(chosen) == 4


def test_unknown_reference_mode_is_rejected():
    with pytest.raises(ValueError, match='unknown reference mode'):
        portal.reference_indices(PATHS, 1, 3, 'sideways')


def test_resolve_shot_accepts_an_index_or_a_name_fragment():
    assert portal._resolve_shot(PATHS, 3) == 3
    assert portal._resolve_shot(PATHS, -1) == 9
    assert portal._resolve_shot(PATHS, 'shot_07') == 7
    with pytest.raises(IndexError, match='out of range'):
        portal._resolve_shot(PATHS, 99)
    with pytest.raises(FileNotFoundError, match='no shot matching'):
        portal._resolve_shot(PATHS, 'nope')


# ── the lyse-side rolling cache ───────────────────────────────────────────

def test_cache_keeps_the_last_n_and_forgets_a_changed_view():
    params = ImagingParams(view=(0, NY, 0, NX), mask=MASK, n_reference=3)
    cache = LightFrameCache(maxlen=3, signature=params.signature())
    for i, frame in enumerate(make_frames(5)):
        cache.sync(params)
        cache.add(f'shot_{i}.h5', frame)
    assert len(cache) == 3
    assert cache.stack().shape == (3, NY, NX)
    assert cache.paths[-1].endswith('shot_4.h5')

    cache.sync(params.replace(view=(0, NY - 1, 0, NX)))
    assert len(cache) == 0


def test_cache_replaces_rather_than_duplicates_a_reanalysed_shot():
    cache = LightFrameCache(maxlen=5)
    frames = make_frames(2)
    cache.add('a.h5', frames[0])
    cache.add('a.h5', frames[1])
    assert len(cache) == 1
    assert np.allclose(cache.stack()[0], frames[1])


# ── listing the reference set ─────────────────────────────────────────────

class _FakeResult:
    def __init__(self, reference_paths, defringe_mode):
        self.reference_paths = list(reference_paths)
        self.defringe_mode = defringe_mode


class _FakeView:
    """Just enough of a ShotView for print_reference_set and _probe_index."""

    def __init__(self, paths, chosen, index, mode='auto'):
        self.paths = list(paths)
        self.path = paths[index]
        self.index = index
        self.result = _FakeResult([paths[i] for i in chosen], mode)


def _folder(n, tmp_path):
    return [str(tmp_path / f'2026-08-21_0057_run_{i:02d}.h5') for i in range(n)]


def test_reference_set_listing_marks_the_shot_and_the_probe(tmp_path, capsys):
    paths = _folder(8, tmp_path)
    view = _FakeView(paths, chosen=[2, 3, 4, 5], index=4)
    portal.print_reference_set(view, probe_index=7)
    out = capsys.readouterr().out

    assert '4 light frames (auto)' in out
    assert out.count('<- this shot') == 1
    # the shared prefix is printed once, so the rows carry only what differs
    assert 'all named 2026-08-21_0057_run_*' in out
    for i in (2, 3, 4, 5):
        assert f'[  {i}] {i:02d}.h5' in out
    assert '00.h5' not in out and '06.h5' not in out
    assert 'probe (held out of the basis): [  7] 07.h5' in out


def test_reference_set_listing_prints_the_shared_prefix_once(tmp_path, capsys):
    view = _FakeView(_folder(5, tmp_path), chosen=[0, 1, 2], index=1)
    portal.print_reference_set(view)
    out = capsys.readouterr().out
    # once in the "all named" line, once in the folder path of the header
    assert out.count('2026-08-21_0057_run_') == 1
    assert 'probe' not in out                           # none was given


def test_reference_set_listing_explains_the_basis_free_modes(tmp_path, capsys):
    for mode, expected in (('self', 'own light frame'), ('none', 'no defringing')):
        view = _FakeView(_folder(3, tmp_path), chosen=[], index=0, mode=mode)
        portal.print_reference_set(view, probe_index=None)
        assert expected in capsys.readouterr().out


def test_reference_set_listing_elides_a_very_long_set(tmp_path, capsys):
    paths = _folder(60, tmp_path)
    view = _FakeView(paths, chosen=list(range(60)), index=0)
    portal.print_reference_set(view, max_listed=10)
    out = capsys.readouterr().out
    assert '(50 more)' in out
    assert out.count('.h5') <= 12                      # header lines aside


def test_the_shot_itself_is_never_the_held_out_probe(tmp_path):
    """Otherwise 'self' mode reconstructs its own probe and reports zero noise."""
    paths = _folder(6, tmp_path)
    view = _FakeView(paths, chosen=[], index=3, mode='self')
    assert portal._probe_index(view, include_self=True) != 3

    view = _FakeView(paths, chosen=[1, 2, 3], index=3)
    probe = portal._probe_index(view, include_self=True)
    assert probe not in (1, 2, 3)


def test_no_probe_when_the_whole_folder_is_in_the_basis(tmp_path):
    paths = _folder(4, tmp_path)
    view = _FakeView(paths, chosen=[0, 1, 2, 3], index=1)
    assert portal._probe_index(view, include_self=True) is None


# ── A' = c*L, the no-PCA mode ─────────────────────────────────────────────

from analysislib.imaging.defringe import IntensityScale


def test_intensity_scale_is_the_light_frame_times_one_number():
    frames = make_frames(1, seed=20)
    L = frames[0]
    scale = IntensityScale(L, mask=MASK)
    A = 0.87 * L                              # a pure intensity difference
    out = scale.apply(A)
    assert np.allclose(out / L, out[0, 0] / L[0, 0], rtol=1e-5)   # one factor
    assert scale.factor(A) == pytest.approx(0.87, rel=1e-6)


def test_intensity_scale_zeroes_the_od_outside_the_atom_box():
    """The whole point: no atoms outside the box means OD reads zero there."""
    rng = np.random.default_rng(21)
    L = make_frames(1, seed=21)[0].astype(float)
    A = 0.93 * L
    r0, r1, c0, c1 = MASK
    A[r0:r1, c0:c1] *= np.exp(-0.8)           # atoms, strictly inside the box

    scale = IntensityScale(L, mask=MASK)
    od = -np.log(A / scale.apply(A))
    outside = scale.mask_weights > 0
    assert np.median(od[outside]) == pytest.approx(0.0, abs=1e-6)
    assert np.median(od[r0:r1, c0:c1]) == pytest.approx(0.8, abs=0.02)


def test_intensity_scale_does_not_pretend_to_be_a_pca_basis():
    scale = IntensityScale(make_frames(1)[0], mask=MASK)
    assert scale.pca is False
    assert scale.n_components == 1
    assert not np.isfinite(scale.noise_floor)
    assert scale.coefficients(make_frames(1, seed=2)[0]).shape == (1,)
    with pytest.raises(ValueError, match='does not match'):
        scale.apply(np.zeros((NY + 1, NX)))


def test_scale_mode_is_reachable_through_params():
    from analysislib.imaging import process
    params = ImagingParams(view=(0, NY, 0, NX), mask=MASK, defringe='scale')
    dfset, mode, refs = process.resolve_defringe_set(make_frames(1)[0], params)
    assert mode == 'scale' and refs == [] and isinstance(dfset, IntensityScale)


# ── the fringe survival check ─────────────────────────────────────────────

from analysislib.imaging import debug as dbg

FY, FX = 300, 300
FMASK = (100, 200, 100, 200)


def _fringed(amplitude, phase=0.0, period=20.0, mean=500.0, seed=None):
    """A flat beam carrying one sinusoidal fringe of known rms contrast.

    ``seed`` adds photon shot noise.  Without it the frames are noise-free,
    which is useful for calibrating an amplitude but not for anisotropy: a
    perfectly flat optical density has an empty spectrum, and the ratio of two
    empty bands is meaningless rather than 1.0.
    """
    y, x = np.mgrid[0:FY, 0:FX]
    pattern = np.cos(2 * np.pi * (x + 0.6 * y) / period + phase)
    frame = mean * (1 + amplitude * np.sqrt(2) * pattern)
    if seed is not None:
        frame = np.random.default_rng(seed).poisson(frame).astype(float)
    return frame


def test_free_box_finds_the_biggest_atom_free_band():
    box = dbg._free_box((FY, FX), FMASK)
    assert box is not None
    r0, r1, c0, c1 = box
    # it must not overlap the atom box
    assert r1 <= FMASK[0] or r0 >= FMASK[1] or c1 <= FMASK[2] or c0 >= FMASK[3]
    assert (r1 - r0) >= 96 and (c1 - c0) >= 96


def test_free_box_gives_up_when_the_mask_fills_the_view():
    assert dbg._free_box((120, 120), (5, 115, 5, 115)) is None


def test_fringe_amplitude_recovers_a_known_modulation():
    box = (0, 100, 0, 300)
    a = 0.05                                   # rms contrast
    img = _fringed(a)
    peak = dbg._peak_wavevector(dbg._spectrum(img, box))
    assert peak is not None
    recovered = dbg.fringe_amplitude(img, box, *peak) / 500.0
    assert recovered == pytest.approx(a, rel=0.15)


def test_anisotropy_is_about_one_when_the_fringes_divide_out():
    """A and L carrying the same fringe: the ratio keeps none of it."""
    box = (0, 100, 0, 300)
    L = _fringed(0.10, seed=1)
    A = np.random.default_rng(2).poisson(0.9 * L).astype(float)
    peak = dbg._peak_wavevector(dbg._spectrum(L, box))
    assert dbg.fringe_anisotropy(-np.log(A / L), box, *peak) < 3


def test_anisotropy_rises_when_the_fringe_has_moved():
    """A and L whose fringes are out of phase: the ratio keeps one."""
    box = (0, 100, 0, 300)
    L = _fringed(0.10, seed=1)
    A = 0.9 * _fringed(0.10, phase=0.9, seed=3)
    peak = dbg._peak_wavevector(dbg._spectrum(L, box))
    assert dbg.fringe_anisotropy(-np.log(A / L), box, *peak) > 50


def test_check_fringes_prefers_the_reference_whose_fringes_match():
    """The comparison the check exists to make, on data with a known answer."""
    from analysislib.imaging.process import ShotImages, ShotResult

    L = _fringed(0.10, seed=1)                     # this shot's light frame
    A = np.random.default_rng(2).poisson(0.9 * L).astype(float)   # same fringe
    drifted = _fringed(0.10, phase=1.2, seed=4)    # a reference that has moved

    params = ImagingParams(view=(0, FY, 0, FX), mask=FMASK)
    images = ShotImages(A, L, np.zeros_like(L), 'shot.h5', 'absorption1')

    good = ShotResult(images=images, A=A, L=L, Aprime=0.9 * L,
                      od=None, nd=None)
    bad = ShotResult(images=images, A=A, L=L, Aprime=0.9 * drifted,
                     od=None, nd=None)

    ok, moved = dbg.check_fringes(good, params), dbg.check_fringes(bad, params)
    assert ok.period == pytest.approx(20.0, rel=0.15)
    assert ok.contrast == pytest.approx(0.10, rel=0.2)
    assert ok.plain == pytest.approx(moved.plain, rel=1e-6)   # same A/L both
    assert ok.defringed < 5 < moved.defringed
    assert moved.defringed_od > 5 * ok.defringed_od
    assert 'MORE fringe than plain' in moved.summary()
    assert 'MORE fringe than plain' not in ok.summary()
