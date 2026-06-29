# Benchmark: microsoft/mysqltoolsservice

## Test Results (Baseline)
- **443 passed**, 149 failed
- Python 3.8 (python:3.8-slim)

## Fix Applied
- No Dockerfile changes needed — the package installs cleanly on Python 3.8 and most
  tests run offline. Tests were run as-is with `pip install -r requirements.txt && pip install -e .`.

## Failing Tests
149 failures across two categories:
1. **Database-dependent** — tests in `connection/`, `admin/`, `driver/` that require a live
   MySQL server connection (`test_connect`, `test_get_database_info_request_integration`, etc.).
2. **TypeError: 'bool' object is not callable** — tests in `query/` and `scripting/` that
   call `mock.Mock()` return values where newer Python/mock versions return a bool. Pre-existing
   test code incompatibility with modern mock library behavior.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — `cx_freeze` (bundled as a dev
dependency) fails to build its C extension wheel: `Building wheel for cx_freeze
(pyproject.toml) did not run successfully`.

## Test Coverage
443 tests across: capabilities service (DMP/DMPE capabilities, initialization), admin service,
language service (completion, formatting, hover, signature help), metadata service,
JSON-RPC request handling, workspace management, object explorer, connection management
(credential store, auto-complete queries), edit data flow, parsers, query execution framework,
scripting object (select/update/delete/insert templates), task management, and utilities.
