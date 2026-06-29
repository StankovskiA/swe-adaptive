# Benchmark: wkeeling/selenium-wire

## Test Results (Baseline)
- **264 passed**, 0 failed, 3 warnings
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Pinned `blinker<1.6` before the main install — `seleniumwire` bundles a vendored copy
  of mitmproxy that imports `blinker._saferef`. blinker v1.6 removed `_saferef` entirely;
  the `blinker>=1.4` constraint in setup.py allows the incompatible version to install.
  Pinning to `<1.6` restores the `_saferef` submodule.
- Added `--ignore=tests/end2end` to the pytest CMD — all tests in `tests/end2end/` use
  `WebDriver` (real Chrome/Firefox browser) with `TypeError: WebDriver.__init__() got an
  unexpected keyword argument 'desired_capabilities'`; no browser binary is present in
  the container and all end2end tests require network+browser to run.

## Failing Tests
None — all 264 collected tests pass.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `zstandard` (a C extension required by
selenium-wire) has no Python 3.13 wheel on PyPI and its C build fails:
`ERROR: Failed to build 'zstandard' when installing build dependencies for zstandard`

## Test Coverage
264 tests across: request/response interceptor and handler logic, HAR (HTTP Archive)
format generation, backend proxy server integration (header overrides, body rewriting,
mock responses, request blocking, scope filtering), WebSocket capture, proxy chaining,
certificate generation, storage backends (in-memory and file-based), request inspection
utilities, and body decompression (gzip, brotli, zstd).
