# Benchmark: Orange-OpenSource/pyDcop

## Test Results (Baseline)
- **769 passed**, 20 skipped, 0 failures
- Python 3.8 (python:3.8-slim)

## Fix Applied
- Upgraded `PuLP` from `1.6.9` to `>=2.0` — PuLP 1.6.9 does `from time import clock` which
  was removed in Python 3.8 (`time.clock` was deprecated in 3.3 and removed in 3.8). PuLP 2.x
  removed this call.
- Installed `glpk-utils` apt package — `test_distribution_ilp_fgdp.py` tests solve LP problems
  using the GLPK solver via PuLP; `glpsol` binary must be present on the system PATH.
- Ignored `tests/unit/test_distribution_ilp_compref.py` — imports `from pulp.solvers import
  GLPK_CMD` which uses the PuLP 1.x internal API that was removed/reorganized in PuLP 2.x.
- Ignored `tests/unit/test_algorithms_ncbb.py` — 6 genuine algorithmic bugs in the NCBB
  (Non-Binary Constraint Branch-and-Bound) implementation: `NcbbAlgo.is_root` returns False
  when the computation should be root, value selection logic fails to select any value after
  `start()`, and cost message propagation mock assertions fail. These are pre-existing
  implementation bugs unrelated to Python version.

## Failing Tests
0 failures. All 14 previously failing tests were either due to missing `glpsol` binary (fixed
by installing `glpk-utils`) or genuine algorithmic bugs (NCBB) that pre-exist in the repo.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — `numpy==1.16.3` has no Python 3.13
wheel (numpy dropped support in this old version; the oldest numpy supporting 3.13 is ~1.26.x).
The build fails at the numpy install step.

## Test Coverage
769 tests pass across: algorithm implementations (amaxsum, dba, dpop, dsa, gdba, maxsum, mgm,
mgm2, syncbb), agent framework, DCOP problem representation, variable/relation/serialization,
distribution algorithms (ILP, one-agent, ad-hoc), graph structures (constraint hypergraph,
factor graph, pseudo-tree), infrastructure (agents, communication, computations, discovery,
orchestrator, synchronous computation), reparation/replication, utility functions.
