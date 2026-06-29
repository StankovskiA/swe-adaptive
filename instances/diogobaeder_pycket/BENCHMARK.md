# Benchmark: diogobaeder/pycket

**Repository:** https://github.com/diogobaeder/pycket
**Language:** Python
**Test framework:** nosetests (tests use nose's `@istest` decorator)

pycket is a Redis/Memcached session backend for Tornado. Tests cover session management, notifications, and functional end-to-end testing.

---

## Dockerfile.test — Baseline (Python 3.8)

**Python version:** 3.8
**Result:** 38 passed

### Excluded tests

| Excluded | Reason |
|----------|--------|
| `test_driver.py` (`MemcachedDriverTest`, 6 tests) | Requires both `python-memcache` package and a running Memcached server; excluded as an optional dependency |

### Special setup

- **nosetests** used instead of pytest: tests use nose's `@istest` decorator (not `test_*` prefix). pytest collects 0 tests from this suite.
- **redis-server** installed and started as a daemon: `SessionManagerTest` (20+ tests) calls `redis.Redis().flushall()` in `setUp`, requiring a live Redis connection.
- `requirements.txt` **not** used: it pins `tornado==2.4.1` (2012 release with `use_2to3` which is invalid in Python 3.12+) and other 2013-era packages. Only `nose` and `redis` are installed explicitly; `tornado` arrives via `pip install -e .`.
- `setup.cfg` `[nosetests]` section stripped: the original config enables `yanc` and `xtraceback` plugins (not installed) and sets `cover-min-percentage=100` which would cause failure even on 100%-passing runs.
- Individual test files specified: `nosetests tests/` (with `__init__.py`) incorrectly collects 0 tests — a known nosetests quirk with package directories; explicit file paths fix this.

### Build and run

```bash
docker build -f Dockerfile.test -t pycket_test .
docker run --rm pycket_test
# Expected: 38 passed in ~4s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -r requirements.txt`

`requirements.txt` pins `tornado==2.4.1` (2012 release). Building this wheel triggers setuptools `use_2to3`, a Python 2→3 compat tool that was removed in Python 3.12 setuptools. Python 3.13's bundled setuptools raises a fatal error.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t pycket_py313 .
# Expected: error in tornado setup command: use_2to3 is invalid.
```

---

## Errors in Dockerfile.py313

```
× Getting requirements to build wheel did not run successfully.
│ exit code: 1
╰─> [1 lines of output]
    error in tornado setup command: use_2to3 is invalid.

note: This error originates from a subprocess, and is likely not a problem with pip.
ERROR: Failed to build 'tornado' when getting requirements to build wheel
```

**Root cause:** `requirements.txt` pins `tornado==2.4.1`, a 2012 release that used `use_2to3=True` in `setup.py` to run Python 2→3 conversion at install time. The `use_2to3` setuptools keyword was formally removed in setuptools 58.3 (2021), and Python 3.13 ships with a setuptools version that raises a fatal error when it encounters it.

**Minimal fix:** Remove the `tornado==2.4.1` pin in `requirements.txt` and upgrade to `tornado>=6.0`.
