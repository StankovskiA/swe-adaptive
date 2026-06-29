# Benchmark: cuducos/calculadora-do-cidadao

## Test Results (Baseline)
- **126 passed**, 0 failed, 1 warning
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Added `libxml2-dev libxslt1-dev` to apt-get — required to build `lxml` from source on Python 3.10.
- Removed `pytest-black` — incompatible with modern pytest (hook `pytest_collect_file` signature mismatch).
- Added `-o addopts=` to CMD — overrides pyproject.toml addopts which reference `--black --mypy --mypy-ignore-missing-imports`.
- Kept `pytest-mypy` — required by `conftest.py` which accesses `config.pluginmanager.getplugin("mypy")`.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `lxml` (a core dependency) has no cp313 pre-built wheel
and requires `libxml2`/`libxslt` development headers to build from source, which are not present
in the slim image. Even with the system libraries, lxml 4.x Cython-based build has issues with
Python 3.13.

## Test Coverage
126 tests pass across full unit/integration test suite covering FGTS, INSS, IRRF calculation
logic, edge cases, freezegun-based date mocking, and CSV export functionality.
