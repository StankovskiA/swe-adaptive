# Benchmark: cloudant/python-cloudant

## Test Results (Baseline)
- **174 passed**, 488 failed, 25 skipped, 26 errors
- Python 3.7 (python:3.7-slim)

## Fix Applied
- Patched Debian Stretch EOL apt sources — `python:3.7-slim` uses Debian Stretch whose
  package mirrors are now archived; redirected to `archive.debian.org`.
- Added `-o "python_files=*_tests.py"` to the pytest CMD — the test suite uses the
  `*_tests.py` naming convention rather than pytest's default `test_*.py`, so pytest
  collected 0 tests without this override.

## Failing Tests
488 failures and 26 errors all require a live CouchDB/Cloudant server at
`http://127.0.0.1:5984` — they are integration tests mixed into the unit test directory.
The 174 passing tests are the genuinely offline unit tests (exception handling, constructor
validation, parameter translation, query building).

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — the `cloudant` package uses `setup.py` with
`versioneer` and old-style `distutils` hooks that fail on Python 3.13 (where distutils
was removed from the stdlib).

## Test Coverage
174 tests pass across: client constructor and exception handling, parameter translation
(CouchDB query parameter encoding), query building (Cloudant Query selector validation),
document and database object construction, security document, design document, index, and
view object construction and attribute validation.
