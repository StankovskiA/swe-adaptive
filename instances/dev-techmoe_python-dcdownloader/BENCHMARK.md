# Benchmark: dev-techmoe/python-dcdownloader

**Repository:** https://github.com/dev-techmoe/python-dcdownloader
**Language:** Python
**Test framework:** pytest

python-dcdownloader is an async manga/comic downloader using aiohttp. Tests cover the HTTP scheduler (fetching chapter lists, image URLs, downloading) and utility functions.

---

## Dockerfile.test — Baseline (Python 3.7)

**Python version:** 3.7
**Result:** 7 passed

### Special setup

- `flask` installed explicitly: `test/testserver/server.py` uses Flask for the in-process HTTP test server; it is not declared in `requirements.txt` or `install_requires`.
- `test/conftest.py` added: the Flask test server runs on port 32321 but was never started before tests ran. Added a session-scoped `autouse` fixture that calls `server.launch()` (starts a daemon thread) and waits 0.5s before the test session begins.
- `lxml==4.2.5` (and other requirements.txt pins) compile fine on Python 3.7 with `build-essential`.

### Build and run

```bash
docker build -f Dockerfile.test -t dcdownloader_test .
docker run --rm dcdownloader_test
# Expected: 7 passed in ~2s (34 deprecation warnings from aiohttp 3.4.4 on Python 3.7 — benign)
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -r requirements.txt`

`requirements.txt` pins `lxml==4.2.5` (2018 release). That version of lxml ships without pre-built Python 3.13 wheels and its C extension source cannot compile against Python 3.13 because the Python C API changed incompatibly.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t dcdownloader_py313 .
# Expected: Failed to build installable wheels for some pyproject.toml based projects: lxml
```

---

## Errors in Dockerfile.py313

```
Successfully built aiohttp multidict yarl lazy-object-proxy PyYAML wrapt
Failed to build lxml
error: failed-wheel-build-for-install

× Failed to build installable wheels for some pyproject.toml based projects
╰─> lxml
```

**Root cause:** `requirements.txt` hard-pins `lxml==4.2.5`. lxml 4.2.5 has no Python 3.13 pre-built wheel, and its C extension relies on deprecated Python C API structures removed in Python 3.13.

**Minimal fix:** Remove the version pin on `lxml` (or raise it to `>=5.0`) in `requirements.txt` to allow installation of a lxml version that ships Python 3.13-compatible wheels.
