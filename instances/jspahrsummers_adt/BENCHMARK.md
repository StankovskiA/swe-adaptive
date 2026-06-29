# Benchmark: adt

**Repository:** https://github.com/jspahrsummers/adt
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 30 passed, 0 failed

All 30 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `typed-ast` C extension fails to compile against Python 3.13 C API

```
#9 8.874   error: subprocess-exited-with-error
#9 8.874   
#9 8.874   x Building wheel for typed-ast (pyproject.toml) did not run successfully.
#9 8.874   | exit code: 1
#9 8.874   +-> [22 lines of output]
#9 8.874       running build_ext
#9 8.874       building '_ast27' extension
#9 8.874       creating build/temp.linux-x86_64-cpython-313/ast27/Custom
#9 8.874       ...
#9 8.874 Failed to build typed-ast
#9 8.874 error: failed-wheel-build-for-install
#9 8.874 x Failed to build installable wheels for some pyproject.toml based projects
```

**Root cause:** `requirements.txt` pins `typed-ast`, a C extension library that embeds a fork of CPython's parser to provide typed AST nodes. `typed-ast` is not maintained for Python 3.8+; its C source files directly reference internal CPython struct layouts and private APIs (`PyArena`, internal `ast.h` headers) that changed significantly in Python 3.13. No pre-built Python 3.13 wheels exist for `typed-ast`, and source compilation fails.

**Minimal fix:** Remove `typed-ast` from `requirements.txt`; replace any usage with Python's stdlib `ast` module directly (Python 3.8+ native AST already includes type annotations) or switch to `mypy`'s internal AST which no longer depends on `typed-ast`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `typed-ast` C extension has no Python 3.13 wheels; source build fails against Python 3.13 C API (changed internal AST/arena structs) | Remove `typed-ast` from `requirements.txt`; use stdlib `ast` module instead |
