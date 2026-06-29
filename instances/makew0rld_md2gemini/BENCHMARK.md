# Benchmark: makew0rld/md2gemini

## Test Results (Baseline)
- **59 passed**, 1 failed
- Python 3.8 (python:3.8-slim)

## Fix Applied
None. The original Dockerfile.test works as-is.

## Failing Tests
1 failure in `tests/test_links.py::test_link_in_quote_newline` — an assertion that
checks exact Gemini link rendering output inside a blockquote; the expected and actual
output differ in footnote link formatting. This is a pre-existing edge-case test that
fails on Python 3.8 as well (not a regression introduced by the Docker setup).

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `setup.py` does `from md2gemini import
__version__` at module level, which triggers an import of `md2gemini/__init__.py` (which
in turn imports `mistune`). On Python 3.13, modern pip uses PEP 660 editable installs
with an isolated build environment; in that environment `mistune` has not been installed
yet, so the import fails:
`ModuleNotFoundError: No module named 'mistune'`
`ERROR: Failed to build 'file:///root/code' when getting requirements to build editable`

## Test Coverage
59 tests pass across: plain text conversion, link rendering (inline, reference, footnote),
link functions, markdown links, base URL resolution, codeblock conversion (fenced and
indented), frontmatter stripping, list conversion (ordered and unordered), blockquote
conversion, HTML tag stripping, and custom tag handling.
