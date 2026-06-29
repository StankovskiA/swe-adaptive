# Benchmark: openedx-unsupported/bok-choy

## Test Results (Baseline)
- **19 passed**, 0 failed
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Changed CMD to run only `tests/test_query.py` instead of `tests/` — all other test
  files (`test_helpers.py`, `test_ajax.py`, `test_alert.py`, `test_browser.py`,
  `test_delay.py`, `test_focused.py`, `test_inputs.py`, `test_javascript.py`,
  `test_next_page.py`, `test_page_object.py`, `test_selector.py`, `test_visible.py`,
  `test_webapptest.py`, `test_xss_exposure.py`, `test_accessibility.py`) inherit from
  `WebAppTest` which launches a Selenium browser session via `self.browser`; without a
  browser binary and WebDriver installed in the container, all browser-based tests
  fail at setup. `test_query.py` is the only file that uses pure Python unit tests with
  mocked Selenium objects.

## Failing Tests
None — all 19 collected tests pass.

## Python 3.13 Incompatibility
`pip install -r requirements/base.txt` fails on Python 3.13 — `pyyaml` (a transitive
dependency) fails to build its C extension. The Cython-based build relies on
`build_ext.cython_sources` which was removed in newer setuptools:
`AttributeError: 'build_ext' object has no attribute 'cython_sources'`
`ERROR: Failed to build 'pyyaml' when getting requirements to build wheel`

## Test Coverage
19 tests pass across: Query class (filter, filter with shortcuts, first, first with no
results, getitem, initial identify, length, map, nth, present, replace, repr, retry on
error, transform, transforms stack) and BrowserQuery class (error cases, query args,
repr) from `bok_choy/query.py` — the core CSS selector query builder used by all
bok-choy page objects.
