"""Tests for labview_sequence/labview.py"""
import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from labview_sequence.labview import (
    LabviewSeq,
    seq_read,
    seq_write,
    seq_sort,
    seq_dump,
    seq_quickdump,
    seq_quickreport,
    seq_clear_disabled,
    seq_block_write,
    channel_report,
    var_lookup,
    get_channels_by_name,
    get_channel_by_no,
)


# ---------------------------------------------------------------------------
# var_lookup
# ---------------------------------------------------------------------------

class TestVarLookup:
    def test_direct_value_returned_unchanged(self):
        """Values <= 65499.6 pass through directly."""
        ramp_params = {'cur_val': np.array([1.0, 2.0, 3.0])}
        assert var_lookup(ramp_params, 42.0) == 42.0

    def test_variable_reference_resolved(self):
        """Values > 65499.6 are treated as variable indices (offset by 65500)."""
        ramp_params = {'cur_val': np.array([10.0, 20.0, 30.0])}
        # index 0 -> cur_val[0] = 10.0
        assert var_lookup(ramp_params, 65500.0) == 10.0
        # index 2 -> cur_val[2] = 30.0
        assert var_lookup(ramp_params, 65502.0) == 30.0

    def test_boundary_value(self):
        """65499.6 is the exact boundary — should be returned directly."""
        ramp_params = {'cur_val': np.array([99.0])}
        assert var_lookup(ramp_params, 65499.6) == 65499.6


# ---------------------------------------------------------------------------
# seq_read — ground truth from MATLAB R2024b on 202409040423
# ---------------------------------------------------------------------------

SEQ_FILE = os.path.join(
    os.path.dirname(__file__), '..', '..', 'labview_sequence', '202409040423'
)


@pytest.mark.skipif(not os.path.exists(SEQ_FILE), reason="202409040423 not present")
class TestSeqRead:
    @pytest.fixture(autouse=True)
    def load(self):
        self.seq = seq_read(SEQ_FILE)

    def test_version_and_timing(self):
        assert self.seq.version == 4
        assert self.seq.timing == 100

    def test_primary_analog_shape(self):
        assert self.seq.primary_analog['dims'][0] == 24

    def test_primary_analog_first_channel(self):
        assert self.seq.primary_analog['name'][0] == '3.0_N_V_AH'
        np.testing.assert_almost_equal(self.seq.primary_analog['ival'][0], 0.18829346, decimal=6)

    def test_digital_shape(self):
        assert self.seq.digital['dims'][0] == 62

    def test_secondary_analog_shape(self):
        assert self.seq.secondary_analog['dims'][0] == 40

    def test_proc_details_shape(self):
        assert list(self.seq.proc_details['dims']) == [39, 72]

    def test_procedures_shape_and_names(self):
        assert self.seq.procedures['dims'][0] == 39
        assert self.seq.procedures['name'][0] == 'Cs_MOT_Loading'
        assert self.seq.procedures['name'][1] == 'Cs_Molasses_Cooling'
        assert self.seq.procedures['name'][2] == 'Cs_H_Imaging'

    def test_procedures_time(self):
        np.testing.assert_array_almost_equal(
            self.seq.procedures['time'][:5], [11700, 15495, 65501, 15500, 15600]
        )

    def test_ramp_params_num(self):
        assert self.seq.ramp_params['num'] == 13

    def test_ramp_params_cur_val(self):
        np.testing.assert_array_almost_equal(
            self.seq.ramp_params['cur_val'][:5],
            [29700.5, 29700.0, 29810.0, 4.4003, 1300.0],
            decimal=3,
        )

    def test_ramp_params_ramp_every_all_ones(self):
        # All 13 ramp_every values should be 1
        np.testing.assert_array_equal(self.seq.ramp_params['ramp_every'], np.ones(13))

    def test_ramp_params_next_ramp_all_zeros(self):
        # All 13 next_ramp values should be 0
        np.testing.assert_array_equal(self.seq.ramp_params['next_ramp'], np.zeros(13))

    def test_always_ramp(self):
        assert self.seq.always_ramp is True

    def test_never_ramp(self):
        assert self.seq.never_ramp is False


# ---------------------------------------------------------------------------
# seq_write round-trip (uses same file)
# ---------------------------------------------------------------------------

MATLAB_BIN = '/Applications/MATLAB_R2024b.app/bin/matlab'
MATLAB_AVAILABLE = os.path.exists(MATLAB_BIN)


@pytest.mark.skipif(not os.path.exists(SEQ_FILE), reason="202409040423 not present")
class TestSeqWrite:
    def test_python_round_trip(self, tmp_path):
        """Python write then Python read: all key fields survive intact."""
        seq = seq_read(SEQ_FILE)
        out_file = str(tmp_path / "out_seq")
        seq_write(seq, out_file)
        seq2 = seq_read(out_file)
        assert seq.version == seq2.version
        assert seq.timing == seq2.timing
        np.testing.assert_array_equal(seq.primary_analog['name'], seq2.primary_analog['name'])
        np.testing.assert_array_almost_equal(seq.primary_analog['ival'], seq2.primary_analog['ival'])
        np.testing.assert_array_equal(seq.proc_details['time'], seq2.proc_details['time'])
        np.testing.assert_array_equal(seq.proc_details['channel_no'], seq2.proc_details['channel_no'])
        np.testing.assert_array_equal(seq.ramp_params['ramp_every'], seq2.ramp_params['ramp_every'])
        np.testing.assert_array_equal(seq.ramp_params['next_ramp'], seq2.ramp_params['next_ramp'])

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_matlab_reads_python_written_file(self, tmp_path):
        """MATLAB lv_seq_read on a Python-written file must match MATLAB read of the original."""
        import subprocess
        out_file = str(tmp_path / "py_written")
        seq_write(seq_read(SEQ_FILE), out_file)

        script = (
            "cd('/Users/henry/Documents/MATLAB/lics-codebase'); addpath(genpath('.'));"
            f"orig = lv_seq_read('labview_sequence/202409040423');"
            f"py = lv_seq_read('{out_file}');"
            "ok = true;"
            "fields = {'version','timing','always_ramp','never_ramp'};"
            "for i = 1:numel(fields); f = fields{i};"
            "  if orig.(f) ~= py.(f); fprintf('MISMATCH %s\\n', f); ok=false; end; end;"
            "grps = {'primary_analog','digital','secondary_analog'};"
            "for g = 1:numel(grps); nm = grps{g};"
            "  if ~isequal(orig.(nm).ival, py.(nm).ival); fprintf('MISMATCH %s.ival\\n',nm); ok=false; end;"
            "  if ~isequal(orig.(nm).name, py.(nm).name); fprintf('MISMATCH %s.name\\n',nm); ok=false; end;"
            "end;"
            "pd_fields = {'time','voltage','channel_no','enabled','ramp_res'};"
            "for i = 1:numel(pd_fields); f = pd_fields{i};"
            "  if ~isequal(orig.proc_details.(f), py.proc_details.(f)); fprintf('MISMATCH proc_details.%s\\n',f); ok=false; end; end;"
            "if ~isequal(orig.procedures.name, py.procedures.name); fprintf('MISMATCH procedures.name\\n'); ok=false; end;"
            "if ~isequal(orig.procedures.time, py.procedures.time); fprintf('MISMATCH procedures.time\\n'); ok=false; end;"
            "rfields = {'num','cur_val','start_val','end_val','incr_val','ramp_every','next_ramp'};"
            "for i = 1:numel(rfields); f = rfields{i};"
            "  if ~isequal(orig.ramp_params.(f), py.ramp_params.(f)); fprintf('MISMATCH ramp_params.%s\\n',f); ok=false; end; end;"
            "if ok; fprintf('ALL FIELDS MATCH\\n'); end"
        )
        result = subprocess.run(
            [MATLAB_BIN, '-nodisplay', '-nosplash', '-batch', script],
            capture_output=True, text=True, timeout=120,
        )
        output = result.stdout + result.stderr
        assert 'MISMATCH' not in output, f"MATLAB found mismatches:\n{output}"
        assert 'ALL FIELDS MATCH' in output, f"MATLAB script did not confirm match:\n{output}"


# ---------------------------------------------------------------------------
# get_channels_by_name / get_channel_by_no
# (uses same example file)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not os.path.exists(SEQ_FILE), reason="202409040423 not present")
class TestChannelLookup:
    @pytest.fixture(autouse=True)
    def load_seq(self):
        self.seq = seq_read(SEQ_FILE)

    def test_get_channels_by_name_returns_list(self):
        result = get_channels_by_name(self.seq, 'MOT')
        assert isinstance(result, list)

    def test_get_channel_by_no_returns_dict(self):
        info = get_channel_by_no(self.seq, 0)
        assert 'chan_no' in info
        assert 'name' in info
        assert 'ival' in info
        assert 'is_analog' in info


# ---------------------------------------------------------------------------
# seq_sort
# ---------------------------------------------------------------------------

def _make_proc_details(times, enabled, channel_no=None, voltage=None, ramp_res=None):
    """Build a minimal proc_details dict for one procedure (1 row)."""
    n = len(times)
    channel_no = channel_no if channel_no is not None else np.zeros(n, dtype=int)
    voltage = voltage if voltage is not None else np.zeros(n)
    ramp_res = ramp_res if ramp_res is not None else np.zeros(n, dtype=int)
    return {
        'dims': np.array([1, n]),
        'save_dims': np.array([n, 1]),
        'time': np.array(times, dtype=float).reshape(1, n),
        'enabled': np.array(enabled, dtype=int).reshape(1, n),
        'channel_no': np.array(channel_no, dtype=int).reshape(1, n),
        'voltage': np.array(voltage, dtype=float).reshape(1, n),
        'ramp_res': np.array(ramp_res, dtype=int).reshape(1, n),
    }


class TestSeqSort:
    def _seq_with(self, proc_details):
        seq = LabviewSeq(version=4)
        seq.proc_details = proc_details
        return seq

    def test_enabled_events_sorted_by_time(self):
        """Enabled events should appear before disabled, sorted by time ascending."""
        pd = _make_proc_details(
            times=[3., 1., 2., 1.],
            enabled=[0, 1, 1, 0],
            channel_no=[10, 20, 30, 40],
            voltage=[3., 1., 2., 1.5],
            ramp_res=[0, 0, 1, 2],
        )
        seq = self._seq_with(pd)
        seq_sort(seq)

        np.testing.assert_array_equal(seq.proc_details['enabled'][0], [1, 1, 0, 0])
        np.testing.assert_array_almost_equal(seq.proc_details['time'][0], [1., 2., 1., 3.])
        np.testing.assert_array_equal(seq.proc_details['channel_no'][0], [20, 30, 40, 10])
        np.testing.assert_array_almost_equal(seq.proc_details['voltage'][0], [1., 2., 1.5, 3.])
        np.testing.assert_array_equal(seq.proc_details['ramp_res'][0], [0, 1, 2, 0])

    def test_already_sorted_unchanged(self):
        """A procedure already sorted should be unchanged."""
        pd = _make_proc_details(
            times=[1., 2., 3., 4.],
            enabled=[1, 1, 0, 0],
        )
        seq = self._seq_with(pd)
        seq_sort(seq)

        np.testing.assert_array_equal(seq.proc_details['enabled'][0], [1, 1, 0, 0])
        np.testing.assert_array_almost_equal(seq.proc_details['time'][0], [1., 2., 3., 4.])

    def test_all_disabled_stable(self):
        """All-disabled procedure: times should end up sorted ascending."""
        pd = _make_proc_details(times=[3., 1., 2.], enabled=[0, 0, 0])
        seq = self._seq_with(pd)
        seq_sort(seq)
        np.testing.assert_array_almost_equal(seq.proc_details['time'][0], [1., 2., 3.])

    def test_values_preserved_as_multiset(self):
        """Sorting must not lose any events — the multiset of values is unchanged."""
        pd = _make_proc_details(
            times=[3., 1., 2., 1.],
            enabled=[0, 1, 1, 0],
            channel_no=[10, 20, 30, 40],
        )
        seq = self._seq_with(pd)
        seq_sort(seq)
        np.testing.assert_array_equal(
            np.sort(seq.proc_details['channel_no'][0]), np.sort([10, 20, 30, 40])
        )

    # Ground truth from MATLAB R2024b: lv_seq_read + lv_seq_sort on 202409040423
    # fmt: off
    # Cols 1-32: zeros; 33-42: ramp times; 43-66: zeros; 67-72: final ramp times
    _MATLAB_TIME_PROC0 = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,   # cols  1-16
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,   # cols 17-32
        1, 2, 2, 5, 5, 50, 50, 100, -100, -5,              # cols 33-42
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,   # cols 43-58
        0, 0, 0, 0, 0, 0, 0, 0,                            # cols 59-66
        0, 10, 100, 100, 1000, 4965,                        # cols 67-72
    ]
    # fmt: on
    _MATLAB_ENABLED_PROC0 = (
        [1] * 40 + [0] * 32
    )
    _MATLAB_CHANNEL_NO_PROC0 = [
        55, 117, 125, 91, 53, 52, 34, 35, 37, 3, 6, 110, 98, 99, 101, 100,
        103, 102, 69, 107, 105, 106, 104, 67, 68, 118, 4, 122, 94, 1, 120, 46,
        73, 113, 109, 0, 7, 0, 7, 73,
        23, 16, 44, 117, 88, 117, 117, 91, 91, 27, 92, 26, 29, 27, 48, 58,
        56, 17, 90, 20, 7, 1, 23, 23, 23, 0, 0, 22, 8, 21, 114, 40,
    ]

    @pytest.mark.skipif(
        not os.path.exists(SEQ_FILE),
        reason="202409040423 sequence file not present",
    )
    def test_matches_matlab_proc0(self):
        """Procedure 0 output must match MATLAB R2024b lv_seq_sort exactly."""
        seq = seq_read(SEQ_FILE)
        seq_sort(seq)
        np.testing.assert_array_almost_equal(
            seq.proc_details['time'][0], self._MATLAB_TIME_PROC0
        )
        np.testing.assert_array_equal(
            seq.proc_details['enabled'][0], self._MATLAB_ENABLED_PROC0
        )
        np.testing.assert_array_equal(
            seq.proc_details['channel_no'][0], self._MATLAB_CHANNEL_NO_PROC0
        )


# ---------------------------------------------------------------------------
# seq_dump
# ---------------------------------------------------------------------------

def _matlab_seq_dump(seq_file, tmp_path, **options):
    """Run MATLAB lv_seq_dump on seq_file and return the file content."""
    import subprocess
    matlab_out = str(tmp_path / "matlab_dump.txt")
    opts_assignments = ''.join(
        f"opts.{k} = {'true' if v else 'false'}; " for k, v in options.items()
    )
    script = (
        "cd('/Users/henry/Documents/MATLAB/lics-codebase'); addpath(genpath('.'));"
        f"seq = lv_seq_read('{seq_file}');"
        f"opts = struct(); {opts_assignments}"
        f"lv_seq_dump(seq, '{matlab_out}', opts);"
    )
    result = subprocess.run(
        [MATLAB_BIN, '-nodisplay', '-nosplash', '-batch', script],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"MATLAB lv_seq_dump failed:\n{result.stdout}\n{result.stderr}"
    with open(matlab_out) as f:
        return f.read()


@pytest.mark.skipif(not os.path.exists(SEQ_FILE), reason="202409040423 not present")
class TestSeqDump:
    @pytest.fixture(autouse=True)
    def load(self):
        self.seq = seq_read(SEQ_FILE)

    def test_returns_filepath_when_target_given(self, tmp_path):
        out_file = str(tmp_path / "dump.txt")
        ret = seq_dump(self.seq, out_file)
        assert ret == out_file
        assert os.path.exists(out_file)

    def test_returns_string_when_no_target(self):
        result = seq_dump(self.seq)
        assert isinstance(result, str)
        assert result.startswith('header\n------\n')
        assert 'version:4\n' in result

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_default_matches_matlab(self, tmp_path):
        """Default options (sort=True, show_disabled=False) must match MATLAB output."""
        matlab_content = _matlab_seq_dump(SEQ_FILE, tmp_path)
        python_content = seq_dump(self.seq)
        matlab_lines = matlab_content.splitlines()
        python_lines = python_content.splitlines()
        for i, (m, p) in enumerate(zip(matlab_lines, python_lines)):
            assert m == p, f"Line {i+1} differs:\n  MATLAB: {m!r}\n  Python: {p!r}"
        assert len(python_lines) == len(matlab_lines), (
            f"Line count differs: Python {len(python_lines)} vs MATLAB {len(matlab_lines)}"
        )

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_show_disabled_matches_matlab(self, tmp_path):
        """show_disabled=True must match MATLAB output."""
        matlab_content = _matlab_seq_dump(SEQ_FILE, tmp_path, show_disabled=True)
        python_content = seq_dump(self.seq, show_disabled=True)
        matlab_lines = matlab_content.splitlines()
        python_lines = python_content.splitlines()
        for i, (m, p) in enumerate(zip(matlab_lines, python_lines)):
            assert m == p, f"Line {i+1} differs:\n  MATLAB: {m!r}\n  Python: {p!r}"
        assert len(python_lines) == len(matlab_lines), (
            f"Line count differs: Python {len(python_lines)} vs MATLAB {len(matlab_lines)}"
        )

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_seperate_disabled_matches_matlab(self, tmp_path):
        """seperate_disabled=True must match MATLAB output."""
        matlab_content = _matlab_seq_dump(SEQ_FILE, tmp_path, seperate_disabled=True)
        python_content = seq_dump(self.seq, seperate_disabled=True)
        matlab_lines = matlab_content.splitlines()
        python_lines = python_content.splitlines()
        for i, (m, p) in enumerate(zip(matlab_lines, python_lines)):
            assert m == p, f"Line {i+1} differs:\n  MATLAB: {m!r}\n  Python: {p!r}"
        assert len(python_lines) == len(matlab_lines), (
            f"Line count differs: Python {len(python_lines)} vs MATLAB {len(matlab_lines)}"
        )


# ---------------------------------------------------------------------------
# seq_quickdump
# ---------------------------------------------------------------------------

# 202409040423 encodes year=2024, month=09, day=04, num=0423
_QD_DATE = [2024, 9, 4]
_QD_NUM = 423


@pytest.mark.skipif(not os.path.exists(SEQ_FILE), reason="202409040423 not present")
class TestSeqQuickdump:
    @pytest.fixture(autouse=True)
    def patch_local_path(self, tmp_path, monkeypatch):
        """Redirect local_path so tests need no lab network paths."""
        import local_paths
        self._dump_out = str(tmp_path / "qd_out.txt")
        dump_out = self._dump_out

        def fake_local_path(path_type, **_):
            if path_type == 'lvseqread':
                return SEQ_FILE
            if path_type == 'lvseqdump':
                return dump_out
            raise KeyError(path_type)

        monkeypatch.setattr(local_paths, 'local_path', fake_local_path)

    def test_output_matches_seq_dump(self):
        """seq_quickdump must produce the same file as seq_dump(seq_read(SEQ_FILE))."""
        ret = seq_quickdump(_QD_DATE, _QD_NUM)
        assert ret == self._dump_out
        expected = seq_dump(seq_read(SEQ_FILE))
        with open(self._dump_out) as f:
            assert f.read() == expected

    def test_explicit_out_path_used(self, tmp_path):
        """When out_path is provided explicitly it takes precedence over lvseqdump."""
        explicit_out = str(tmp_path / "explicit.txt")
        ret = seq_quickdump(_QD_DATE, _QD_NUM, out_path=explicit_out)
        assert ret == explicit_out
        assert os.path.exists(explicit_out)

    def test_dump_kwargs_forwarded(self):
        """dump_kwargs (e.g. show_disabled) are passed through to seq_dump."""
        ret = seq_quickdump(_QD_DATE, _QD_NUM, show_disabled=True)
        assert ret == self._dump_out
        with open(self._dump_out) as f:
            content = f.read()
        # show_disabled=True produces more lines than default (disabled events included)
        default_content = seq_dump(seq_read(SEQ_FILE))
        assert len(content.splitlines()) > len(default_content.splitlines())


# ---------------------------------------------------------------------------
# channel_report
# ---------------------------------------------------------------------------

def _matlab_channel_report(seq_file, which_channel, tmp_path, **options):
    """Run MATLAB lv_seq_channel_report and return the file content."""
    import subprocess
    matlab_out = str(tmp_path / "matlab_report.txt")
    ch_arg = f"'{which_channel}'" if isinstance(which_channel, str) else str(which_channel)
    opts_assignments = ''.join(
        f"opts.{k} = {'true' if v else 'false'}; " for k, v in options.items()
    )
    script = (
        "cd('/Users/henry/Documents/MATLAB/lics-codebase'); addpath(genpath('.'));"
        f"seq = lv_seq_read('{seq_file}');"
        f"opts = struct(); {opts_assignments}"
        f"lv_seq_channel_report(seq, {ch_arg}, '{matlab_out}', opts);"
    )
    result = subprocess.run(
        [MATLAB_BIN, '-nodisplay', '-nosplash', '-batch', script],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"MATLAB lv_seq_channel_report failed:\n{result.stdout}\n{result.stderr}"
    with open(matlab_out) as f:
        return f.read()


def _compare_content(matlab_content, python_content):
    matlab_lines = matlab_content.splitlines()
    python_lines = python_content.splitlines()
    for i, (m, p) in enumerate(zip(matlab_lines, python_lines)):
        assert m == p, f"Line {i+1} differs:\n  MATLAB: {m!r}\n  Python: {p!r}"
    assert len(python_lines) == len(matlab_lines), (
        f"Line count: Python={len(python_lines)}, MATLAB={len(matlab_lines)}"
    )


@pytest.mark.skipif(not os.path.exists(SEQ_FILE), reason="202409040423 not present")
class TestChannelReport:
    @pytest.fixture(autouse=True)
    def load(self):
        self.seq = seq_read(SEQ_FILE)

    def test_returns_filepath_when_target_given(self, tmp_path):
        out = str(tmp_path / "report.txt")
        ret = channel_report(self.seq, 'all', out)
        assert ret == out
        assert os.path.exists(out)

    def test_returns_string_when_no_target(self):
        result = channel_report(self.seq, 'all')
        assert isinstance(result, str)
        assert 'ch no' in result

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_all_matches_matlab(self, tmp_path):
        _compare_content(
            _matlab_channel_report(SEQ_FILE, 'all', tmp_path),
            channel_report(self.seq, 'all'),
        )

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_analog_channel_matches_matlab(self, tmp_path):
        _compare_content(
            _matlab_channel_report(SEQ_FILE, '5.14', tmp_path),
            channel_report(self.seq, '5.14'),
        )

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_digital_channel_matches_matlab(self, tmp_path):
        _compare_content(
            _matlab_channel_report(SEQ_FILE, '6.9', tmp_path),
            channel_report(self.seq, '6.9'),
        )

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_details_false_matches_matlab(self, tmp_path):
        _compare_content(
            _matlab_channel_report(SEQ_FILE, '5.14', tmp_path, details=False),
            channel_report(self.seq, '5.14', details=False),
        )

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_on_only_false_matches_matlab(self, tmp_path):
        _compare_content(
            _matlab_channel_report(SEQ_FILE, '5.14', tmp_path, on_only=False),
            channel_report(self.seq, '5.14', on_only=False),
        )

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_proc_on_only_false_matches_matlab(self, tmp_path):
        _compare_content(
            _matlab_channel_report(SEQ_FILE, '5.14', tmp_path, proc_on_only=False),
            channel_report(self.seq, '5.14', proc_on_only=False),
        )


# ---------------------------------------------------------------------------
# seq_quickreport
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not os.path.exists(SEQ_FILE), reason="202409040423 not present")
class TestSeqQuickreport:
    @pytest.fixture(autouse=True)
    def patch_local_path(self, monkeypatch):
        import local_paths

        def fake_local_path(path_type, **_):
            if path_type == 'lvseqread':
                return SEQ_FILE
            raise KeyError(path_type)

        monkeypatch.setattr(local_paths, 'local_path', fake_local_path)

    def test_output_matches_channel_report(self):
        """seq_quickreport output must match channel_report(seq_read(SEQ_FILE), ch)."""
        result = seq_quickreport(_QD_DATE, _QD_NUM, '5.14')
        expected = channel_report(seq_read(SEQ_FILE), '5.14')
        assert result == expected

    def test_out_file_forwarded(self, tmp_path):
        """Explicit out_file is passed through to channel_report."""
        out = str(tmp_path / "report.txt")
        ret = seq_quickreport(_QD_DATE, _QD_NUM, '5.14', out_file=out)
        assert ret == out
        assert os.path.exists(out)

    def test_kwargs_forwarded(self):
        """channel_report kwargs (e.g. details=False) are forwarded."""
        result_default = seq_quickreport(_QD_DATE, _QD_NUM, '5.14')
        result_no_detail = seq_quickreport(_QD_DATE, _QD_NUM, '5.14', details=False)
        assert len(result_no_detail.splitlines()) < len(result_default.splitlines())


# ---------------------------------------------------------------------------
# seq_clear_disabled
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not os.path.exists(SEQ_FILE), reason="202409040423 not present")
class TestSeqClearDisabled:
    @pytest.fixture(autouse=True)
    def load(self):
        self.seq = seq_read(SEQ_FILE)

    def test_disabled_events_zeroed(self):
        """After clear, every disabled event has time=voltage=channel_no=ramp_res=0."""
        seq_clear_disabled(self.seq)
        mask = self.seq.proc_details['enabled'] == 0
        assert (self.seq.proc_details['time'][mask] == 0).all()
        assert (self.seq.proc_details['voltage'][mask] == 0).all()
        assert (self.seq.proc_details['channel_no'][mask] == 0).all()
        assert (self.seq.proc_details['ramp_res'][mask] == 0).all()

    def test_enabled_events_unchanged(self):
        """Enabled events must not be modified."""
        original = seq_read(SEQ_FILE)
        seq_clear_disabled(self.seq)
        mask = self.seq.proc_details['enabled'] == 1
        np.testing.assert_array_equal(
            self.seq.proc_details['time'][mask], original.proc_details['time'][mask]
        )
        np.testing.assert_array_equal(
            self.seq.proc_details['voltage'][mask], original.proc_details['voltage'][mask]
        )

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_matches_matlab(self, tmp_path):
        """proc_details after Python seq_clear_disabled must match MATLAB lv_seq_clear_disabled."""
        import subprocess

        # MATLAB: read, clear, write result to temp file
        matlab_out = str(tmp_path / "matlab_cleared")
        script = (
            "cd('/Users/henry/Documents/MATLAB/lics-codebase'); addpath(genpath('.'));"
            f"seq = lv_seq_read('{SEQ_FILE}');"
            "seq = lv_seq_clear_disabled(seq);"
            f"lv_seq_write(seq, '{matlab_out}');"
        )
        result = subprocess.run(
            [MATLAB_BIN, '-nodisplay', '-nosplash', '-batch', script],
            capture_output=True, text=True, timeout=120,
        )
        assert result.returncode == 0, f"MATLAB failed:\n{result.stdout}\n{result.stderr}"

        matlab_seq = seq_read(matlab_out)
        seq_clear_disabled(self.seq)

        for field in ('time', 'voltage', 'channel_no', 'ramp_res', 'enabled'):
            np.testing.assert_array_equal(
                self.seq.proc_details[field],
                matlab_seq.proc_details[field],
                err_msg=f"proc_details['{field}'] differs from MATLAB",
            )


# ---------------------------------------------------------------------------
# seq_block_write
# ---------------------------------------------------------------------------

# Fixed inputs used across seq_block_write tests — channel names known to
# exist in 202409040423, proc 0 = 'Cs_MOT_Loading' (0-indexed).
_BW_PROC = 0
_BW_TIMES = [1000.0, 2000.0]
_BW_OFFSETS = [0.0, 0.5]
_BW_CHANNELS = ['3.0_N_V', '6.9']
_BW_VOLTAGES = [1.5, 1.0]
_BW_RAMP_RES = [0, 0]


@pytest.mark.skipif(not os.path.exists(SEQ_FILE), reason="202409040423 not present")
class TestSeqBlockWrite:
    @pytest.fixture(autouse=True)
    def load(self):
        self.seq = seq_read(SEQ_FILE)

    def test_in_seq_not_modified(self):
        """seq_block_write must not mutate the input sequence."""
        original_enabled = self.seq.proc_details['enabled'].copy()
        original_time = self.seq.proc_details['time'].copy()
        seq_block_write(self.seq, _BW_PROC, _BW_TIMES, _BW_OFFSETS,
                        _BW_CHANNELS, _BW_VOLTAGES, _BW_RAMP_RES)
        np.testing.assert_array_equal(self.seq.proc_details['enabled'], original_enabled)
        np.testing.assert_array_equal(self.seq.proc_details['time'], original_time)

    def test_other_procs_unchanged(self):
        """Only the target procedure's proc_details should change."""
        out = seq_block_write(self.seq, _BW_PROC, _BW_TIMES, _BW_OFFSETS,
                              _BW_CHANNELS, _BW_VOLTAGES, _BW_RAMP_RES)
        for field in ('enabled', 'time', 'voltage', 'channel_no', 'ramp_res'):
            np.testing.assert_array_equal(
                out.proc_details[field][1:, :],
                self.seq.proc_details[field][1:, :],
                err_msg=f"proc {field} changed in non-target procedures",
            )

    @pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
    def test_matches_matlab(self, tmp_path):
        """proc_details for the target procedure must match MATLAB lv_seq_block_write."""
        import subprocess
        matlab_out = str(tmp_path / "matlab_block_written")
        script = (
            "cd('/Users/henry/Documents/MATLAB/lics-codebase'); addpath(genpath('.'));"
            f"seq = lv_seq_read('{SEQ_FILE}');"
            f"out = lv_seq_block_write(seq, {_BW_PROC + 1},"
            f" [{' '.join(str(t) for t in _BW_TIMES)}],"
            f" [{' '.join(str(o) for o in _BW_OFFSETS)}],"
            f" {{{', '.join(repr(c) for c in _BW_CHANNELS)}}},"
            f" [{' '.join(str(v) for v in _BW_VOLTAGES)}],"
            f" [{' '.join(str(r) for r in _BW_RAMP_RES)}]);"
            f"lv_seq_write(out, '{matlab_out}');"
        )
        result = subprocess.run(
            [MATLAB_BIN, '-nodisplay', '-nosplash', '-batch', script],
            capture_output=True, text=True, timeout=120,
        )
        assert result.returncode == 0, f"MATLAB failed:\n{result.stdout}\n{result.stderr}"

        matlab_seq = seq_read(matlab_out)
        out = seq_block_write(self.seq, _BW_PROC, _BW_TIMES, _BW_OFFSETS,
                              _BW_CHANNELS, _BW_VOLTAGES, _BW_RAMP_RES)

        for field in ('enabled', 'time', 'voltage', 'channel_no', 'ramp_res'):
            np.testing.assert_array_equal(
                out.proc_details[field][_BW_PROC, :],
                matlab_seq.proc_details[field][_BW_PROC, :],
                err_msg=f"proc_details['{field}'][{_BW_PROC}] differs from MATLAB",
            )
