# Benchmark: pipelinewise-tap-postgres

**Repository:** https://github.com/transferwise/pipelinewise-tap-postgres
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 112 passed, 0 failed

All 112 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 6.040 ERROR: Package 'pipelinewise-tap-postgres' requires a different Python: 3.13.14 not in '<3.10,>=3.7'
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
3.713   Installing build dependencies: started
4.889   Installing build dependencies: finished with status 'done'
4.891   Checking if build backend supports build_editable: started
5.311   Checking if build backend supports build_editable: finished with status 'done'
5.312   Getting requirements to build editable: started
5.603   Getting requirements to build editable: finished with status 'done'
5.606   Preparing editable metadata (pyproject.toml): started
6.006   Preparing editable metadata (pyproject.toml): finished with status 'done'
6.039 INFO: pip is looking at multiple versions of pipelinewise-tap-postgres to determine which version is compatible with other requirements. This could take a while.
6.040 ERROR: Package 'pipelinewise-tap-postgres' requires a different Python: 3.13.14 not in '<3.10,>=3.7'
------
_Dockerfile_tmp_transferwise_pipelinewise-tap-postgres:5
--------------------
   4 |     COPY . .
   5 | >>> RUN pip install --no-cache-dir --upgrade pip \
   6 | >>>  && pip install --no-cache-dir -e . \
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
