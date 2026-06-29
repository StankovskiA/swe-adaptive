# Benchmark: criteo/biggraphite

## Test Results (Baseline)
- **131 passed**, 54 skipped, 2 warnings
- Python 3.7 (python:3.7-slim)

## Fix Applied
- Used Debian archive.debian.org mirror (`sed -i`) — Python 3.7-slim uses Debian Stretch which
  reached end-of-life; the original deb.debian.org mirrors no longer serve Stretch packages.
  Rewrote `/etc/apt/*.list` to use `archive.debian.org` and removed `stretch-updates` (which
  has no archive).
- Installed optional dependencies with `|| true` to allow partial installs when a package fails
  (graphite-web, carbon, opencensus, testing.cassandra3, etc.).
- Ignored test files that require unavailable services or packages:
  - `tests/drivers/test_elasticsearch.py` — needs a live Elasticsearch instance
  - `tests/plugins/test_carbon.py`, `test_graphite.py`, `test_tags.py` — need carbon/graphite
  - `tests/cli/test_bg_carbon_*.py`, `test_import_whisper.py` — need carbon/whisper binaries
  - `tests/cli/web/` — needs graphite web server
  - `tests/test_metadata_cache.py` — needs Redis/Cassandra services
  - `tests/test_tracing.py` — needs opencensus tracing
  - `tests/test_settings.py` — needs the `graphite` Django settings module
  - `tests/cli/test_command_graphite_web.py` — needs graphite Django app

## Failing Tests
0 failures. 54 skipped tests require a live Cassandra or other service (marked `@unittest.skip`
or skipped via conditions in the test fixtures).

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — `cassandra-driver` (a core storage
backend dependency) fails to build its C extension on Python 3.13. The cassandra-driver uses
Cython-generated C code that is not compatible with the Python 3.13 C API changes.

## Test Coverage
131 tests pass across: Cassandra storage accessor (mocked), LMDB storage backend, glob
operations, retention policy utilities, test utilities, CLI commands (bg_read, bg_write,
bg_fill), web command, and core biggraphite accessor/metric/metadata logic.
