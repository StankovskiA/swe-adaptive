# Benchmark: moshi4/GBKviz

## Test Results (Baseline)
- **10 passed**, 3 failed, 1 warning
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Added `protobuf<=3.20.3` — newer protobuf breaks the installed dependencies.
- Added `altair>=4.0,<5` — GBKviz imports from `altair.vegalite.v4` which was the pre-altair-5
  import path. Altair 5 reorganized its module structure and removed the `vegalite.v4` submodule.

## Failing Tests
3 tests fail:
- `test_draw_genbank_fig` — `AttributeError` in the drawing code (altair/bokeh rendering issue).
- `test_genome_align_run_nucleotide` — `FileNotFoundError`: requires `nucmer`/`mummer` binary.
- `test_genome_align_run_protein` — `FileNotFoundError`: requires `promer`/`mummer` binary.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `reportlab` (a PDF rendering dependency) fails to build
because `ft2build.h` (FreeType2 development headers) are missing. The Python 3.13 slim image has
no pre-built cp313 wheel for `reportlab`, and building from source requires system FreeType2 headers.

## Test Coverage
10 tests pass across: GenBank file parsing, sequence extraction, GBK feature manipulation,
genome comparison utilities, and visualization layout logic that doesn't require rendering.
