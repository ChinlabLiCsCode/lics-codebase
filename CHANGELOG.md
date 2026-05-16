# Changelog — MATLAB → Python Conversion

## [In progress]

### labview_sequence/labview.py
Functions remaining to convert from MATLAB:
- `lv_insert_fieldjump.m` → `insert_fieldjump`

Skipped (no callers outside themselves / empty / not needed):
- `lv_seq_get_parameter.m` / `lv_seq_get_params.m`
- `lv_seq_count_pulses.m` (user decision)
- `lv_sequence_var_lookup.m` (empty file)

---

## [2026-05-15] — seq_block_write

### Added
- `seq_block_write` in `labview_sequence/labview.py` (from `lv_seq_block_write.m`)
  - Fills a block of events into a procedure: for each time in `times`, writes `repeat_len` events
    at `time + time_offsets[b]` with the given channel names, voltages, and ramp_res
  - Sorts the procedure first (via `seq_sort` on a deep copy), finds the last enabled slot, and
    inserts from there; stops early if the procedure would overflow
  - Channel names resolved via `get_channels_by_name`; `in_proc_no` is **0-indexed** (MATLAB is 1-indexed)
  - Returns a new `LabviewSeq`; input is not modified

### Tests added (TestSeqBlockWrite)
- `test_in_seq_not_modified`: original sequence is unchanged after the call
- `test_other_procs_unchanged`: only the target procedure's events are affected
- `test_matches_matlab`: Python result vs MATLAB `lv_seq_block_write` ground truth, field-by-field
  for the target procedure

---

## [2026-05-15] — seq_clear_disabled

### Added
- `seq_clear_disabled` in `labview_sequence/labview.py` (from `lv_seq_clear_disabled.m`)
  - Zeroes `time`, `voltage`, `channel_no`, `ramp_res` for every disabled event in-place; returns seq

### Tests added (TestSeqClearDisabled)
- `test_disabled_events_zeroed`: all four fields are 0 for every disabled event after call
- `test_enabled_events_unchanged`: enabled events' time and voltage are unmodified
- `test_matches_matlab`: MATLAB `lv_seq_clear_disabled` + `lv_seq_write` → Python `seq_read`, compared field-by-field against Python result

---

## [2026-05-15] — seq_quickreport

### Added
- `seq_quickreport` in `labview_sequence/labview.py` (from `lv_seq_quickreport.m`)
  - Takes `[year, month, day]`, `num`, `which_channel`; delegates to `seq_read` + `channel_report`
  - `out_file=None` returns string; all `channel_report` kwargs forwarded

### Tests added for seq_quickreport (TestSeqQuickreport)
- `patch_local_path` autouse fixture monkeypatches `local_paths.local_path` (same pattern as `TestSeqQuickdump`)
- `test_output_matches_channel_report`: output equals `channel_report(seq_read(SEQ_FILE), ch)`
- `test_out_file_forwarded`: explicit `out_file` written and returned
- `test_kwargs_forwarded`: `details=False` produces fewer lines than default

---

## [2026-05-15] — channel_report

### Changed
- Replaced the broken pre-existing `get_channel_info` + `channel_report(seq, channel_info_list)`
  pair with a single `channel_report(in_seq, which_channel, out_file=None, *, details, on_only,
  proc_on_only)` matching `lv_seq_channel_report.m` exactly.
  - `which_channel`: `'all'`, name substring, or list of channel numbers
  - `out_file=None` returns content string; string path writes file and returns path
  - `details` defaults to `True` unless `which_channel='all'` (matches MATLAB behaviour)
  - `on_only=True` / `proc_on_only=True`: filter events in detail table
  - Removed `get_channel_info` (was broken — mixed DataFrame/list init); all logic now inline

### Tests added for channel_report (TestChannelReport)
- `test_returns_filepath_when_target_given` / `test_returns_string_when_no_target`
- `test_all_matches_matlab`: `which_channel='all'` vs MATLAB ground truth
- `test_analog_channel_matches_matlab`: `which_channel='5.14'`
- `test_digital_channel_matches_matlab`: `which_channel='6.9'`
- `test_details_false_matches_matlab`, `test_on_only_false_matches_matlab`,
  `test_proc_on_only_false_matches_matlab`: all options variants vs MATLAB

---

## [2026-05-15] — local_paths + seq_quickdump

### Added
- `example_files/example_local_paths.py` — template for machine-specific path configuration
  (mirrors `example_localpath_mac.m`). Copy to `local_paths.py` at repo root and fill in.
  Keys: `lvseqread`, `lvseqdump`, `H`, `V`, `loadparams`, `saveparams`
- `local_paths.py` at repo root — Henry's mac paths (gitignored)
- `local_paths.py` added to `.gitignore`
- `seq_quickdump` in `labview_sequence/labview.py` (from `lv_seq_quickdump.m`)
  - Reads sequence by `[year, month, day]` + `num` using `local_path('lvseqread', ...)`
  - Writes dump via `seq_dump`; output path defaults to `local_path('lvseqdump', ...)` or
    can be overridden with `out_path`; all `seq_dump` kwargs forwarded

### Tests added for seq_quickdump (TestSeqQuickdump)
- `patch_local_path` autouse fixture monkeypatches `local_paths.local_path` so tests need
  no lab network access
- `test_output_matches_seq_dump`: full output matches `seq_dump(seq_read(SEQ_FILE))`
- `test_explicit_out_path_used`: explicit `out_path` arg takes precedence
- `test_dump_kwargs_forwarded`: `show_disabled=True` produces more lines than default

---

## [2026-05-15] — seq_dump

### Added
- `seq_dump` in `labview_sequence/labview.py` (from `lv_seq_dump.m`)
  - Writes a human-readable text dump of a sequence to a file (or returns as string when `in_target=None`)
  - Options: `sort` (default True), `show_disabled` (default False), `seperate_disabled` (default False)
  - `seperate_disabled=True` appends disabled events in a separate block; forced False when `show_disabled=True` (matches MATLAB)
  - Voltage format differs between main loop (`%10.6f`) and `seperate_disabled` block (`%10.4f`) — intentional replication of MATLAB source

### Tests added for seq_dump (TestSeqDump)
- `test_returns_filepath_when_target_given`: confirms file is written and path returned
- `test_returns_string_when_no_target`: confirms string content returned when `in_target=None`
- `test_default_matches_matlab`: line-by-line comparison vs MATLAB `lv_seq_dump` with default options
- `test_show_disabled_matches_matlab`: same with `show_disabled=True`
- `test_seperate_disabled_matches_matlab`: same with `seperate_disabled=True`

---

## [2026-05-14] — seq_write tested against MATLAB

### Tests added for seq_write (TestSeqWrite)
- `test_python_round_trip`: Python write → Python read, checks all major field groups survive intact
- `test_matlab_reads_python_written_file`: Python write → MATLAB `lv_seq_read`, compares every field
  against original MATLAB read of `202409040423`. Confirmed all fields match.

---

## [2026-05-14] — seq_read tested and bug fixed

### Fixed
- Bug in `seq_read`: ramp control group (`ramp_every`, `next_ramp`) was read incorrectly.
  The flat interleaved array `[re0, nr0, re1, nr1, ...]` was being reshaped row-major to `(2, check_num)`
  before slicing with `[0::2]`/`[1::2]`, which sliced *rows* of the 2D array instead of alternating
  elements of the flat array. Removed the erroneous reshape — matches the correct pattern already used
  for `cur_val`/`start_val`/etc.

### Tests added for seq_read (TestSeqRead)
- All fields verified against MATLAB R2024b ground truth on `202409040423`:
  version, timing, primary/digital/secondary_analog shapes, first channel name+ival,
  proc_details shape, procedures names+times, ramp_params (num, cur_val, ramp_every, next_ramp),
  always_ramp, never_ramp
- Round-trip write+read test now also checks ramp_every/next_ramp survive correctly

---

## [2026-05-14] — seq_sort

### Added
- `seq_sort` in `labview_sequence/labview.py` (from `lv_seq_sort.m`)
  - Sorts each procedure's events ascending by time; on ties, enabled=1 events come before enabled=0
  - 6 tests: 4 synthetic (no file dependency) + 2 real-file tests using `202409040423`

---

## [2026-05-14] — Initial scaffold

### Added
- `pyproject.toml` — pytest configuration
- `tests/` directory structure with `__init__.py` files
- `tests/labview_sequence/conftest.py` — shared fixtures
- `tests/labview_sequence/test_labview.py` — initial tests for already-converted functions:
  - `var_lookup` (3 unit tests, no file dependency)
  - `seq_read` / `seq_write` round-trip (skipped until test file present)
  - `get_channels_by_name` / `get_channel_by_no` (skipped until test file present)
- `PROCEDURE.md` — step-by-step conversion guide
- `CHANGELOG.md` — this file

### Already converted (pre-existing in labview_sequence/labview.py)
- `LabviewSeq` dataclass
- `seq_read` (from `lv_seq_read.m`)
- `seq_write` (from `lv_seq_write.m`)
- `read_array` / `write_array` (binary format helpers)
- `read_single` / `write_single` (binary format helpers)
- `get_channel_info` (from `lv_seq_channel_report.m`)
- `channel_report`
- `var_lookup` (from `lv_seq_var_lookup.m`)
- `get_channels_by_name` (from `lv_seq_get_channels_by_name.m`)
- `get_channel_by_no` (from `lv_seq_get_channel_by_no.m`)
