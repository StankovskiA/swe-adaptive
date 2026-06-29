# Benchmark: osd2f

**Repository:** https://github.com/uvacw/osd2f
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 55 passed, 0 failed

All 55 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `asyncpg`, `cffi`, `pydantic-core` pinned to Python 3.9-only wheels; source builds fail on Python 3.13

```
#9 47.48   error: subprocess-exited-with-error
#9 47.48   
#9 47.48   x Building wheel for asyncpg (pyproject.toml) did not run successfully.
#9 47.48   | exit code: 1
#9 47.48   +-> [262 lines of output]
#9 47.48       ...
#9 53.78 Failed to build asyncpg cffi pydantic-core
#9 53.78 error: failed-wheel-build-for-install
#9 53.78 x Failed to build installable wheels for some pyproject.toml based projects
```

**Root cause:** `requirements.txt` pins `asyncpg==0.29.0`, `cffi==1.16.0`, and `pydantic-core==2.18.2`. Each was downloaded as a Python 3.9-specific pre-built wheel (`cp39-manylinux`). On Python 3.13, no pre-built wheels exist for these pinned versions, so pip falls back to building from source. All three are C extension packages whose source in these versions uses internal CPython APIs (`_Py*` structures, private header includes) that were removed or changed in Python 3.13, causing the source builds to fail.

**Minimal fix:** Upgrade all three packages to versions that ship Python 3.13 pre-built wheels:
- `asyncpg>=0.30.0`
- `cffi>=1.17.0`  
- `pydantic-core>=2.27.0` (released alongside pydantic ≥2.10)

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `asyncpg==0.29.0`, `cffi==1.16.0`, `pydantic-core==2.18.2` only have Python 3.9 wheels (`cp39`); source builds fail against Python 3.13 C API | Upgrade to versions with Python 3.13 wheels: `asyncpg>=0.30.0`, `cffi>=1.17.0`, `pydantic-core>=2.27.0` |
