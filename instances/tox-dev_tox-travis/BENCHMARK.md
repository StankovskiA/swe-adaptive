# Benchmark: tox-dev/tox-travis

## Test Results (Baseline)
- **55 passed**, 0 failed, 1 xfailed
- Python 3.8 (python:3.8-slim)

## Fix Applied
- Added `pytest-mock` to the pip install step — several test files (`test_after.py`,
  `test_hacks.py`, `test_hooks.py`) use the `mocker` fixture provided by `pytest-mock`.
  Without it, those tests error at collection with `fixture 'mocker' not found`, causing
  12 collection errors that prevented those 12 tests from running.

## Failing Tests
None — all 55 collected tests pass (plus 1 expected-failure marked with `xfail`).

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — the package uses `setup.py` which internally
imports `pkg_resources` (from `setuptools`). In Python 3.13, `setuptools` is no longer
bundled with the interpreter, so `pkg_resources` is not available:
`ModuleNotFoundError: No module named 'pkg_resources'`
`ERROR: Failed to build 'file:///root/code' when getting requirements to build editable`

## Test Coverage
55 tests across: tox environment list generation from Travis CI matrix (factor expansion,
exclusions, Python version detection), Travis-aware environment filtering, post-build hooks
(GitHub status updates), session subcommand integration, utility functions (config dict
parsing), and after-build behavior tests (pull request detection, token handling, Travis
environment variable parsing, polling intervals).
