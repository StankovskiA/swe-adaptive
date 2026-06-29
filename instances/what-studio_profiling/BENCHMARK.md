# Benchmark: what-studio/profiling

## Test Results (Baseline)
- **30 passed**, 5 failed, 4 skipped, 4 errors, 5 warnings
- Python 3.10 (python:3.10-slim)

## Fix Applied
Installed `requirements.txt` before the editable install — the profiling C extensions require
numpy and other dependencies to be available during the build.

## Failing Tests
5 failures and 4 errors:
- `test_cli.py` (3 failures): CLI argument parsing changed between Python versions and Click
  versions (assertion string mismatches, `'x' object is not callable` in config test).
- `test_stats.py` (2 failures, 4 errors): `TypeError: code expected at least 14 arguments, got 13`
  — Python code objects changed their constructor signature in Python 3.11+; the profiling
  library creates mock `code` objects in tests with the old 13-argument signature.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — the `profiling` package is a C extension (sampling
profiler using ptrace and C-level frame inspection). The C extension fails to build on Python 3.13
due to changes in the Python C API.

## Test Coverage
30 tests pass across: statistical profiling, clock utilities, timer profiling, frozen profile
serialization/deserialization, and profiling context managers.
