# Benchmark Setup

This benchmark assesses an agent's ability to update a Python project's dependencies
and source code to support a newer Python version.

## Project

[panini](https://github.com/lwinterface/panini) is a modern framework for building
streaming microservices on top of NATS using asyncio. It uses a set of pinned
dependencies (`setup.py`, `requirements/defaults.txt`) that were written targeting
Python 3.8–3.10.

---

## Dockerfile.test — Baseline (Python 3.10)

`Dockerfile.test` establishes the working baseline. It builds and runs the full
test suite on **Python 3.10**, with **70 tests passing** and no pre-existing failures.

### What it does

1. **Install NATS server** — The test suite requires a NATS server running on
   `127.0.0.1:4222`. The official `nats-server` binary (v2.10.7) is downloaded and
   installed into `/usr/local/bin` inside the container; the CMD starts it before
   invoking pytest.

2. **Restore original imports** — The working tree has all intra-package imports
   rewritten to use an absolute benchmark-collection path
   (`from success_benchmark.panini.panini.* import …`). These are invalid when panini
   is installed normally. A `git checkout HEAD -- panini/ tests/ examples/` step
   inside the build restores the original relative imports before installation.

### Running

```bash
docker build -f Dockerfile.test -t panini-test .
docker run --rm panini-test
```

### Expected result

```
70 passed in 60.87s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

`Dockerfile.py313` attempts a straightforward install of the project on
**Python 3.13** without any workarounds. It is expected to fail at build time.
This is the starting point for the benchmark task.

### Running

```bash
docker build -f Dockerfile.py313 -t panini-py313 .
```

### Expected result

The build fails during `pip install -r requirements/defaults.txt`.

---

## Errors in Dockerfile.py313

### Error 1 — `aiohttp==3.8.1`: `longintrepr.h` removed in Python 3.13

```
aiohttp/_websocket.c:198:12: fatal error: longintrepr.h: No such file or directory
  198 |   #include "longintrepr.h"
      |            ^~~~~~~~~~~~~~~
compilation terminated.
error: command '/usr/bin/gcc' failed with exit code 1
ERROR: Failed building wheel for aiohttp
```

**Nature:** `longintrepr.h` is a CPython internal header that was deprecated in
Python 3.12 (relocated to `cpython/longintrepr.h`) and removed entirely in Python
3.13. `aiohttp==3.8.1` was released in 2022 and its Cython-generated C extension
(`aiohttp/_websocket.c`) still includes the old path. There are no pre-built
Python 3.13 wheels for this version, and the source build fails.

**Type:** Build toolchain issue (C extension incompatible with Python 3.13 C API)

---

### Error 2 — `yarl==1.7.2`: `longintrepr.h` removed in Python 3.13

```
yarl/_quoting_c.c:198:12: fatal error: longintrepr.h: No such file or directory
  198 |   #include "longintrepr.h"
      |            ^~~~~~~~~~~~~~~
compilation terminated.
error: command '/usr/bin/gcc' failed with exit code 1
ERROR: Failed building wheel for yarl
```

**Nature:** Same root cause as `aiohttp`: the Cython-generated C extension in
`yarl==1.7.2` includes `longintrepr.h`. `yarl` is also a direct dependency of
`aiohttp`, so it must be upgraded alongside it.

**Type:** Build toolchain issue (C extension incompatible with Python 3.13 C API)

---

## Benchmark Task

Given `Dockerfile.py313` as a starting point, update the project so that it builds
and the test suite passes on Python 3.13. The solution requires:

1. Upgrade `aiohttp==3.8.1` to a version that ships Python 3.13-compatible wheels
   (e.g. `aiohttp>=3.9.0`).
2. Upgrade `yarl==1.7.2` to a compatible version (e.g. `yarl>=1.9.0`); aiohttp 3.9+
   also requires this upgrade.
3. Update the pinned version in both `setup.py` (`install_requires`) and
   `requirements/defaults.txt`, and verify that `aiohttp-cors==0.7.0` remains
   compatible with the upgraded aiohttp.

The fix is purely dependency updates — no panini source code changes are required.
