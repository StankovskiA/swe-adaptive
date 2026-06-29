# Benchmark: YelpArchive/send_nsca

## Test Results (Baseline)
- **15 passed**, 0 failed
- Python 3.7 (python:3.7-slim)

## Fix Applied
- Added `unittest2` and `mock` packages — test files import `from unittest2 import TestCase`
  and `import mock`; both are Python 2-era backports not included in requirements.txt.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `setup.py` uses `tests_require` which is an
unsupported keyword in the Python 3.13 / modern setuptools combination, causing
`get_requires_for_build_editable` to fail before the package can be installed.

## Test Coverage
15 tests across: NSCA config parsing (encryption method, comments, password limits, unknown
keys), TCP connection logic (connect flow, disconnect, timeout, single/multi socket), protocol
limits (code, hostname, output, service name), and smoke-test packet encoding.
