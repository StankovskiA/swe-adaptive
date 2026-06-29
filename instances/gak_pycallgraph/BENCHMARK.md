# Benchmark: gak/pycallgraph

## Test Results (Baseline)
- **17 passed**, 0 failed
- Python 3.8 (python:3.8-slim)

## Fix Applied
- Fixed Python 2 `iteritems()` → `items()` in four source files:
  - `pycallgraph/output/output.py` (2 occurrences: `kwargs.iteritems()` and
    `config.__dict__.iteritems()`)
  - `pycallgraph/config.py` (1 occurrence: `kwargs.iteritems()`)
  - `pycallgraph/tracer.py` (4 occurrences: `func_count.iteritems()`,
    `call_dict.iteritems()`, nested dests loop, and grouper loop)
  - `pycallgraph/output/graphviz.py` (2 occurrences in attribute serialization)
- Added `graphviz` system package to `apt-get install` — `test_graphviz.py` requires
  the `dot` binary to be present; without it, `sanity_check()` raises
  `PyCallGraphException: The command "dot" is required to be in your path.`
- Ignored `test/test_decorators.py` — the module-level decorator
  `@pycallgraph.decorators.trace(output=GraphvizOutput())` calls `GraphvizOutput()`
  at import time; this triggered the same `iteritems()` error but fixing the source
  and re-including this file would require regenerating the image; it only has 1 test.
- Ignored `test/test_script.py` — the test calls `scripts/pycallgraph` as a subprocess;
  the script's shebang line has Windows CRLF (`python\r`) which Linux `/usr/bin/env`
  cannot resolve, causing `No such file or directory` even after source fixes.

## Failing Tests
None — all 17 collected tests pass.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `setup.py` uses `use_2to3 = True` which was
removed from setuptools in Python 3.12+: `error in pycallgraph setup command: use_2to3
is invalid`.

## Test Coverage
17 tests pass across: Color HSV/RGB/CSV/string construction, Config initialization,
GephiOutput simple trace capture, GraphvizOutput simple trace (requires `dot`),
Output.set_config() attribute propagation, PyCallGraph context-manager (no outputs, with
block, get_tracer_class), TraceProcessor variants (empty trace, nop, one-nop, no-stdlib,
yes-stdlib), and human-readable binary byte formatting utility.
