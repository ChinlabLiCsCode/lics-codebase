# MATLAB → Python Conversion Procedure

Follow these steps for every function, in order.

## Per-function steps

1. **Read the MATLAB source** — understand what it does, its inputs/outputs, and any edge cases.
2. **Check dependencies** — if the function calls others not yet converted, convert those first.
3. **Ask the user for test details** — before writing tests, prompt:
   - What are good representative inputs?
   - Are there edge cases to cover (empty arrays, boundary values, error paths)?
   - Is there example data (files, known output values) to use?
4. **Write the test** — add a test class/function to the relevant `tests/<module>/test_<module>.py`. Use `pytest.mark.skipif` for anything that needs external files not yet present.
5. **Run tests (red)** — confirm the new test fails (or is skipped) before implementing.
6. **Write the Python implementation** — port the MATLAB function, preserving behaviour exactly. Note any MATLAB 1-indexing → 0-indexing conversions explicitly.
7. **Run tests (green)** — confirm all tests pass.
8. **Update CHANGELOG.md** — add an entry under the current date.

## Conventions

- All Python files live in the same subdirectory as their MATLAB counterparts (e.g. `labview_sequence/labview.py`).
- Tests live in `tests/<module>/test_<module>.py`.
- Test data lives in `tests/testdata/<module>/` or the existing `<module>/testdata/` folder.
- Run tests with: `conda run -n lics python -m pytest`
- One module at a time — finish all functions in a module before moving to the next.

## Module order (rough priority)

1. `labview_sequence/labview.py` — partially done; finish remaining MATLAB functions
2. `imaging/` — `load_img`, `load_params`, `save_params`, `build_params`, then fitting/processing
3. `calibration/` — physics utilities (`breit_rabi`, `B_from_uwave`, scattering length functions, etc.)
4. `helperfuncs/` — plotting helpers and math utilities

## Tracking

- Completed functions are recorded in `CHANGELOG.md`.
- Functions still to convert are listed in the MATLAB source tree.
