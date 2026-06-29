# Benchmark: openedx-unsupported/xblock-utils

## Test Results (Baseline)
- **62 passed**, 24 failed, 30 warnings
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Added `libxml2-dev libxslt1-dev` to apt-get — `lxml` requires these headers to build from source.
- Added `RUN mkdir -p /root/code/var` at build time — tests read/write to `var/` directory at
  runtime and the directory must exist before the container starts.

## Failing Tests
24 tests fail:
- 11 tests in `tests/unit/test_resources.py` — Django template rendering failures; Mako/Django
  template engine incompatibility with the test setup.
- 11 tests in `tests/integration/test_studio_editable.py` — require Selenium WebDriver/browser.
- 2 tests in `tests/integration/test_base_test.py` — Selenium integration tests.
Note: `setup.cfg` has `addopts = tests` which causes pytest to collect from the full `tests/`
directory even when `tests/unit/` is specified on the command line.

## Python 3.13 Incompatibility
`pip install -r requirements/base.txt` fails on Python 3.13 — `lxml` has no cp313 pre-built wheel
and fails to build from source: `libxml2` and `libxslt` development packages are not installed
in the slim image.

## Test Coverage
62 tests pass across: XBlock helpers, publish-event mixin, settings service, theme configuration,
and various XBlock lifecycle utilities.
