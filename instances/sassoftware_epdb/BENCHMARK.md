# Benchmark: epdb

**Repository:** https://github.com/sassoftware/epdb
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 15 passed, 0 failed

All 15 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — Removed stdlib module (PEP 594) — one of several modules deleted in Python 3.13

```
#9 0.953 ImportError while importing test module '/root/code/test/test_client.py'.
#9 0.953 Hint: make sure your test modules/packages have valid Python names.
#9 0.953 Traceback:
#9 0.953 /usr/local/lib/python3.13/importlib/__init__.py:88: in import_module
#9 0.953     return _bootstrap._gcd_import(name[level:], package, level)
#9 0.953            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#9 0.953 test/test_client.py:27: in <module>
#9 0.953     from epdb import epdb_client
#9 0.953 epdb/epdb_client.py:38: in <module>
#9 0.953     import telnetlib
#9 0.953 E   ModuleNotFoundError: No module named 'telnetlib'
#9 0.953 _____________________ ERROR collecting test/test_server.py _____________________
#9 0.953 ImportError while importing test module '/root/code/test/test_server.py'.
#9 0.953 Hint: make sure your test modules/packages have valid Python names.
#9 0.953 Traceback:
```

**Root cause:** Removed stdlib module (PEP 594) — one of several modules deleted in Python 3.13

**Minimal fix:** Upgrade the dependency that imports the removed module.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | Removed stdlib module (PEP 594) — one of several modules deleted in Python 3.13 | Upgrade the dependency that imports the removed module. |
