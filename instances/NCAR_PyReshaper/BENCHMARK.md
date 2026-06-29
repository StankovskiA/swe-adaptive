# Benchmark: NCAR/PyReshaper

## Test Results (Baseline)
- **106 passed**, 0 failures
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Installed `numpy`, `netCDF4`, `mpi4py`, `coverage` explicitly — `requirements.txt` only
  listed `asaptools`, but the pyreshaper package imports `numpy` directly. The tests also
  require `netCDF4` for NetCDF file operations, `mpi4py` for MPI-parallel reshaping tests,
  and the `coverage` binary for coverage-instrumented subprocess tests.
- Installed `libopenmpi-dev openmpi-bin` apt packages — required to build `mpi4py` from source
  and to provide the `mpirun` binary used by `test_cli_parallel.py` tests.
- Set `ENV OMPI_ALLOW_RUN_AS_ROOT=1` and `OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1` — OpenMPI 4.x
  refuses to run as root by default (for safety), but Docker containers run as root. These
  env vars opt in to root execution.
- Ignored `tests/test_iobackend.py` — imports `Nio` (PyNIO), a NASA/NCAR-specific scientific
  data format library that is only available via conda/conda-forge and has no pip wheel.

## Failing Tests
0 failures. The only ignored test file uses PyNIO which cannot be installed via pip.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` then `pip install -e .` fails on Python 3.13 — `asaptools`
(the direct requirement) depends on or triggers installation of packages that have no
Python 3.13 wheels or source builds.

## Test Coverage
106 tests pass across: CLI s2smake (specification creation), CLI s2srun with 0, 1, 2, and 4
MPI workers (sequential and parallel reshape operations), reshaper (NetCDF4 backend — variable
selection, exclusion, chunking, appending, missing variable handling, metadata handling, file
format conversion), specification (validation of types and values for all configuration
options, serialization/deserialization), and s2smake/s2srun integration tests.
