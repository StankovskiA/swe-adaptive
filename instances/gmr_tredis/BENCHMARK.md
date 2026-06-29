# Benchmark: gmr/tredis

**Repository:** https://github.com/gmr/tredis
**Language:** Python
**Test framework:** pytest (tornado AsyncTestCase)

tredis is an asynchronous Redis client for Tornado. Tests cover strings, hashes, lists, sets, sorted sets, scripting, server commands, and more.

---

## Dockerfile.test — Baseline (Python 3.7)

**Python version:** 3.7
**Result:** 192 passed, 5 deselected

### Excluded tests

| Excluded | Reason |
|----------|--------|
| `cluster_behavior_tests.py` | Requires a multi-node Redis cluster |
| `cluster_tests.py` | Requires a multi-node Redis cluster |
| `failover_tests.py` | Requires Redis cluster with master/replica failover |
| `MigrationTests` (keys_tests.py) | Requires a second Redis instance via `NODE1_PORT` env var |
| `test_on_close_callback_invoked` (connect_tests.py) | `CLIENT KILL` command fails with `ERR No such client` on the bundled Redis version — Redis changed `CLIENT KILL` syntax between versions |

### Special setup

- **Python 3.7** used instead of 3.10: `tornado<5` uses `collections.MutableMapping`, which was removed from `collections` in Python 3.10 (moved to `collections.abc`). Python 3.7 retains the alias.
- **redis-server** installed and started as a daemon: all tests connect to Redis in `setUp`.
- `test-requirements.txt` **not** installed: it pulls in `nose`, `codecov`, `coverage` which aren't needed for pytest.
- **pytest.ini** added with `python_classes = *Tests` and `python_files = *_tests.py`: tredis test files are named `*_tests.py` (plural) and test classes are named `*Tests`, neither of which matches pytest's defaults (`test_*.py` / `Test*`).
- `setup.cfg` `[nosetests]` section stripped: original config enables coverage reporting plugins not installed, causing nosetests to fail.

### Build and run

```bash
docker build -f Dockerfile.test -t tredis-test .
docker run --rm tredis-test
# Expected: 192 passed in ~4s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -r requirements.txt`

`requirements.txt` pins `hiredis>=0.2.0,<1`. Building this wheel requires compiling a C extension that is incompatible with Python 3.13's CPython internals.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t tredis-py313 .
# Expected: ERROR: Failed to build 'hiredis' when getting requirements to build wheel
```

---

## Errors in Dockerfile.py313

```
ERROR: Failed to build 'hiredis' when getting requirements to build wheel
```

**Root cause:** `requirements.txt` pins `hiredis<1` (versions from ~2016). hiredis is a C extension. The old hiredis C code uses CPython APIs that were removed or changed in Python 3.13.

**Minimal fix:** Upgrade `hiredis` to `>=2.0.0` which supports Python 3.12+.
