# Benchmark: poliastro/poliastro

## Test Results (Baseline)
- **1006 passed**, 14 failed, 13 skipped, 8 xfailed, 1 xpassed, 14 warnings
- Python 3.10 (python:3.10-slim)

## Fix Applied
Added `hypothesis` to pip install — the test suite uses `hypothesis` for property-based testing
of orbital mechanics functions.

## Failing Tests
14 tests fail in `tests/tests_plotting/test_orbit_plotter.py` and `tests/tests_twobody/test_orbit.py`
(Matplotlib2D) — `AttributeError` in matplotlib rendering in the headless Docker environment.
These tests require a display backend or GUI toolkit (Matplotlib needs a display for rendering).

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `astropy` (a core dependency for orbital mechanics
calculations) fails to build: `ModuleNotFoundError: No module named 'setuptools.dep_util'`.
The `setuptools.dep_util` module was removed in setuptools >= 60. `astropy` 4.x uses this
removed module in its build system, and there is no cp313-compatible pre-built wheel for
old astropy versions.

## Test Coverage
1006 tests pass (out of 1041 collected) across: Keplerian orbital mechanics, orbit propagation,
two-body problem, frame transformations, unit handling (via astropy), atmospheric models,
Hohmann transfers, numerical orbit integrators, and maneuver calculations.
