# Benchmark: Detrous/darksky

**Repository:** https://github.com/Detrous/darksky
**Language:** Python
**Test framework:** pytest

darksky is a Python wrapper for the Dark Sky weather API. It provides both sync (`requests`) and async (`aiohttp`) clients.

---

## Dockerfile.test — Baseline (Python 3.10)

**Python version:** 3.10
**Result:** 20 passed

### Special setup

- `aioresponses` installed explicitly: the CI requirements pin `aioresponses==0.6.0` but it is not in `install_requires`; `test_forecast.py` imports it at module level, causing collection failure.
- `mock` installed explicitly: `test_forecast.py` uses `import mock` (standalone package) for `@mock.patch`; `unittest.mock` is not imported instead.
- `aiohttp==3.5.4` and `multidict` compile without issue on Python 3.10 with `build-essential`.

### Build and run

```bash
docker build -f Dockerfile.test -t darksky_test .
docker run --rm darksky_test
# Expected: 20 passed in ~0.5s (stderr shows aiohttp unclosed-session warnings — benign)
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -e .`

`setup.py` pins `aiohttp==3.5.4`, which depends on `multidict` as a C extension. The old `multidict` source (pre-5.x) cannot compile against Python 3.13 because Python 3.13 made breaking changes to its C API.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t darksky_py313 .
# Expected: Failed to build installable wheels for some pyproject.toml based projects: multidict
```

---

## Errors in Dockerfile.py313

```
Successfully built darksky_weather aiohttp
Failed to build multidict
error: failed-wheel-build-for-install

× Failed to build installable wheels for some pyproject.toml based projects
╰─> multidict
```

**Root cause:** `setup.py` hard-pins `aiohttp==3.5.4` (2018 release). That version of aiohttp depends on `multidict<5.0`, whose C extension source code uses the old Python C API. Python 3.13 removed or changed C API structures that old multidict relied on, causing compilation failure.

**Minimal fix:** Drop the version pin on `aiohttp` in `setup.py` to allow installing `aiohttp>=3.9` which ships a pre-built wheel for Python 3.13.
