# Benchmark: verilab/veripress

## Test Results (Baseline)
- **19 passed**, 33 failed, 8 warnings
- Python 3.9 (python:3.9-slim)

## Fix Applied
Pinned `markupsafe<2.1` in Dockerfile.test — MarkupSafe 2.1 removed `soft_unicode` which broke Jinja2/Flask template rendering used by this static blog generator.

## Failing Tests
33 tests fail due to pytest API incompatibility — the codebase uses `pytest.raises(ValueError, message=...)` syntax which was removed after pytest 4.6. Pinning `pytest>=4.6,<5` preserves the tests that can run.

## Python 3.13 Incompatibility
`pip install -r test-requirements.txt` fails on Python 3.13 — `lxml 4.x` requires `libxml2`/`libxslt` dev headers which are absent, and `feedgen` has no cp313 wheel.

## Test Coverage
19 tests pass across core veripress functionality (theme rendering, post parsing, config handling).
