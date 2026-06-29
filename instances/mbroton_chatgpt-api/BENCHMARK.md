# Benchmark: chatgpt-api

**Repository:** https://github.com/mbroton/chatgpt-api
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.7)

**Docker image:** `Dockerfile.test`
**Python version:** 3.7
**Result:** 22 passed, 0 failed

All 22 tests pass on Python 3.7.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 2.243 ERROR: Could not find a version that satisfies the requirement pytest_httpx==0.21.2 (from versions: 0.0.1, 0.0.2, 0.0.3, 0.0.4, 0.0.5, 0.1.0, 0.2.0, 0.2.1, 0.3.0, 0.4.0, 0.5.0, 0.6.0, 0.7.0, 0.8.0, 0.9.0, 0.10.0, 0.10.1, 0.11.0, 0.12.0, 0.12.1, 0.13.0, 0.14.0, 0.15.0, 0.16.0, 0.17.0, 0.17.1, 0.17.2, 0.17.3, 0.18.0, 0.19.0, 0.20.0, 0.21.0, 0.21.1, 0.21.2, 0.21.3, 0.22.0, 0.23.0, 0.23.1, 0.24.0, 0.25.0, 0.26.0, 0.27.0, 0.28.0, 0.29.0, 0.30.0, 0.31.0, 0.31.1, 0.31.2, 0.32.0, 0.33.0, 0.34.0, 0.35.0, 0.36.0, 0.36.2)
#9 2.243 ERROR: No matching distribution found for pytest_httpx==0.21.2
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
2.216   Downloading pytest-7.2.0-py3-none-any.whl.metadata (7.8 kB)
2.232 Collecting pytest_httpx==0.21.2 (from -r requirements.txt (line 4))
2.239   Downloading pytest_httpx-0.21.2-py3-none-any.whl.metadata (23 kB)
2.243 WARNING: Ignoring version 0.21.2 of pytest_httpx since it has invalid metadata:
2.243 Requested pytest_httpx==0.21.2 from https://files.pythonhosted.org/packages/92/97/0f4ba2edc925ae9094d89e3396a9cd3e78bf322cefb1610a06307c4a8f21/pytest_httpx-0.21.2-py3-none-any.whl (from -r requirements.txt (line 4)) has invalid metadata: .* suffix can only be used with `==` or `!=` operators
2.243     pytest (<8.*,>=6.*)
2.243             ~~~^
2.243 Please use pip<24.1 if you need to use this version.
2.243 ERROR: Could not find a version that satisfies the requirement pytest_httpx==0.21.2 (from versions: 0.0.1, 0.0.2, 0.0.3, 0.0.4, 0.0.5, 0.1.0, 0.2.0, 0.2.1, 0.3.0, 0.4.0, 0.5.0, 0.6.0, 0.7.0, 0.8.0, 0.9.0, 0.10.0, 0.10.1, 0.11.0, 0.12.0, 0.12.1, 0.13.0, 0.14.0, 0.15.0, 0.16.0, 0.17.0, 0.17.1, 0.17.2, 0.17.3, 0.18.0, 0.19.0, 0.20.0, 0.21.0, 0.21.1, 0.21.2, 0.21.3, 0.22.0, 0.23.0, 0.23.1, 0.24.0, 0.25.0, 0.26.0, 0.27.0, 0.28.0, 0.29.0, 0.30.0, 0.31.0, 0.31.1, 0.31.2, 0.32.0, 0.33.0, 0.34.0, 0.35.0, 0.36.0, 0.36.2)
2.243 ERROR: No matching distribution found for pytest_httpx==0.21.2
------
_Dockerfile_tmp_mbroton_chatgpt-api:5
--------------------
   4 |     COPY . .
   5 | >>> RUN pip install --no-cache-dir --upgrade pip \
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
