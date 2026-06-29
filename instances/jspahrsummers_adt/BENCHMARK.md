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

### Error — unknown

```
#9 8.874   error: subprocess-exited-with-error
#9 8.874   
#9 8.874   × Building wheel for typed-ast (pyproject.toml) did not run successfully.
#9 8.874   │ exit code: 1
#9 8.874   ╰─> [22 lines of output]
#9 8.874       running bdist_wheel
#9 8.874       running build
#9 8.874       running build_py
#9 8.874       creating build/lib.linux-x86_64-cpython-313/typed_ast
#9 8.874       copying typed_ast/__init__.py -> build/lib.linux-x86_64-cpython-313/typed_ast
#9 8.874       copying typed_ast/ast3.py -> build/lib.linux-x86_64-cpython-313/typed_ast
#9 8.874       copying typed_ast/conversions.py -> build/lib.linux-x86_64-cpython-313/typed_ast
#9 8.874       copying typed_ast/ast27.py -> build/lib.linux-x86_64-cpython-313/typed_ast
#9 8.874       creating build/lib.linux-x86_64-cpython-313/typed_ast/tests
#9 8.874       copying ast3/tests/test_basics.py -> build/lib.linux-x86_64-cpython-313/typed_ast/tests
#9 8.874       running build_ext
#9 8.874       building '_ast27' extension
#9 8.874       creating build/temp.linux-x86_64-cpython-313/ast27/Custom
#9 8.874       creating build/temp.linux-x86_64-cpython-313/ast27/Parser
#9 8.874       creating build/temp.linux-x86_64-cpython-313/ast27/Python
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
