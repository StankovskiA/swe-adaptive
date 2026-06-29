# Benchmark: YelpArchive/clusterman

## Test Results (Baseline)
- **489 passed**, 95 warnings
- Python 3.7 (python:3.7-slim)

## Fix Applied
- Fixed Debian Stretch (EOL) apt sources — `python:3.7-slim` uses Debian Stretch which reached
  end-of-life in June 2022. The official Debian mirrors no longer serve Stretch packages; all
  `apt-get update` calls fail. Fix: redirect apt sources to `archive.debian.org` and remove
  the `stretch-updates` line (which was only available while Stretch was supported).

## Failing Tests
0 failures. All 489 tests pass out of the box once the apt source fix allows build-essential
to install correctly.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — `matplotlib==3.4.2` has no Python
3.13 wheel and cannot be built from source (the pinned version predates Python 3.13 and uses
incompatible C extension build infrastructure). The build fails at the matplotlib wheel build
step.

## Test Coverage
489 tests pass across: AWS resource management (EC2, spot fleets), Kubernetes cluster
connector (node migration, resource listing), autoscaler algorithms and cost calculations,
signal evaluation (external signals, metric collection), simulator I/O, batch job tracking,
CLI toggle commands, configuration parsing, migration event conditions, monitoring library
integration, draining logic, and utility functions (time parsing, sorting).
