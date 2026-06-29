# Benchmark: Robpol86/libnl

**Repository:** https://github.com/Robpol86/libnl
**Language:** Python
**Test framework:** pytest

Pure-Python port of the Linux Netlink protocol library suite. Tests cover socket allocation, message construction, Netlink send/recv operations, rtnetlink attribute parsing, and nl80211 helpers.

---

## Dockerfile.test — Baseline (Python 3.5)

**Python version:** 3.5
**Result:** 51 passed, 10 skipped, 3 deselected

### Special setup

- **Python 3.5 required**: `libnl/misc.py` uses a `_class_factory()` that creates subclasses of ctypes `_SimpleCData` types. In Python 3.6+, ctypes metaclass validation raises `TypeError: __class__ set to <class '...'> defining 'ClsPyPy' as <class '...'>` at class creation time. This error fires when the module is first imported (module-level `c_int = _class_factory(ctypes.c_int)` etc.), making the entire package unusable on Python 3.6+.

- **Debian Stretch archive repos**: `python:3.5-slim` is based on Debian Stretch whose apt repos have moved to `archive.debian.org`. The sed command in the RUN step patches `/etc/apt/sources.list` to use the archive mirror and removes the dead `stretch-updates` suite.

- **`docopt` and `pygments`**: Required by `tests/test_examples.py` which imports and exercises the example scripts in `examples/`.

- **Kernel-dependent integration tests excluded**: 8 tests open real Netlink sockets and send/receive actual kernel messages. Their expected byte patterns and port numbers are specific to the original CI kernel; in Docker they fail because the process gets PID 1 (so the Netlink port is `1`, not the `\d{3,}` the tests expect) and other kernel-version-dependent behaviour differs. These tests are excluded via `--ignore` and `-k`:
  - `tests/nl/test_nl_connect.py` — real `nl_connect()` call returns `-ENXIO`
  - `tests/nl/test_nl_recv.py` — real `nl_recv()` byte pattern mismatch
  - `tests/nl/test_nl_recvmsgs_default.py` — `test_error`, `test_multipart`, `test_multipart_verbose`
  - `test_nl_socket_modify_cb` / `test_nl_socket_modify_cb_error_verbose` — expect port `\d{3,}` but Docker PID 1 gives port `1`
  - `test_list_interfaces` — iterates real network interfaces with kernel-specific byte patterns

### Build and run

```bash
docker build -f Dockerfile.test -t libnl-test .
docker run --rm libnl-test
# Expected: 51 passed, 10 skipped, 3 deselected in ~5s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -e .`

The package `setup.py` uses a regex (`_VERSION_RE`) to extract author/version/license metadata from `libnl/__init__.py` and stores it in `ALL_DATA`. When setuptools 82+ (bundled with Python 3.13's pip) runs `setup.py` via `exec(code, locals())` inside a build isolation environment, the `_safe_read()` helper returns an empty string and the regex finds no matches, leaving `ALL_DATA` without the `'author'` key. Line 70 of `setup.py` then raises `KeyError: 'author'`.

Additionally, even if the install were patched, the ctypes `_SimpleCData` subclassing in `libnl/misc.py` (broken in Python 3.6+) would prevent the package from being imported on Python 3.13.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t libnl-py313 .
# Expected: KeyError: 'author' during pip install -e .
```

---

## Errors in Dockerfile.py313

```
KeyError: 'author'

note: This error originates from a subprocess, and is likely not a problem with pip.
ERROR: Failed to build 'file:///root/code' when getting requirements to build editable
```

**Root cause:** `setup.py` extracts package metadata via a regex on `libnl/__init__.py`. Modern setuptools (82+) runs `setup.py` via `exec(code, locals())` inside an isolated build environment where the `_safe_read()` helper fails to locate the init file, returning `''`. With no metadata extracted, `ALL_DATA['author']` raises `KeyError`. The underlying library is also fundamentally incompatible with Python 3.6+ (including 3.13) due to ctypes `_SimpleCData` subclassing semantics changing in that version.
