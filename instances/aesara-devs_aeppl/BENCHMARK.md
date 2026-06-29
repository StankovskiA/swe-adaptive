# Benchmark: aesara-devs/aeppl

## Test Results (Baseline)
- **373 passed**, 11 xfailed, 0 failures
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Pinned `numpy<1.25` — aesara 2.9.4 calls `np.__config__.get_info("blas_opt")` during
  BLAS detection, which was removed in numpy 1.26. Without the pin, aesara's fallback
  triggers an import of `numpy.distutils.mingw32ccompiler` which tries to import
  `distutils.msvccompiler` — a Windows-only module that doesn't exist on Linux, crashing
  the aesara import.
- Installed `libopenblas-dev` — provides BLAS libraries so aesara BLAS detection succeeds
  cleanly with the pinned numpy.
- Uninstalled `pytest-html` — `requirements.txt` includes it but `py.xml` was removed from
  the `py` package in recent versions, causing `ModuleNotFoundError` at collection time.
- Added `-W "ignore:Use shutil.which:DeprecationWarning"` to the pytest CMD — `setup.cfg`
  sets `filterwarnings = error`, which turns a DeprecationWarning emitted by
  `setuptools._distutils.spawn.find_executable` (called by aesara during module
  initialization) into an error. This error leaves `aesara` partially initialized in
  `sys.modules`, causing all subsequent test files to fail with
  `AttributeError: partially initialized module 'aesara'`.

## Failing Tests
0 failures. 11 xfailed tests are expected failures (marked with `@pytest.mark.xfail`).

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — `scipy` (a transitive dependency
via `aesara`) has no pre-built wheel for Python 3.13 and fails to build from source.

## Test Coverage
373 tests pass across: abstract (measurable variable abstraction), censoring, composite
log-probability, convolutions, cumulative sum, distributions, joint log-probability,
log-probability, mixture models, printing/pretty-printing, rewriting rules, scan operations,
tensor operations, transforms (log, scale, affine), and utility functions.
