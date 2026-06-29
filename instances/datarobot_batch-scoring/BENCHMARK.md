# Benchmark: datarobot/batch-scoring

**Repository:** https://github.com/datarobot/batch-scoring
**Language:** Python
**Test framework:** pytest

datarobot-batch-scoring is a CLI tool for scoring CSV files against DataRobot's prediction API. It includes a full integration test suite that runs a mock Flask prediction server.

---

## Dockerfile.test — Baseline (Python 3.7)

**Python version:** 3.7
**Result:** 188 passed, 2 deselected, 1 xfailed

### Excluded tests and reasons

| Excluded | Reason |
|----------|--------|
| `test_parse_host_success` | Calls a pytest fixture directly — allowed in pytest 2.x but raises an error in pytest 6.x |
| `test_quotechar_in_keep_cols` | Pre-existing logic bug: `run_batch_predictions` returns `1` instead of `None`; unrelated to Python version compatibility |

### Special setup

- `requirements-test.txt` is not used: it pins `pytest==2.9.0` and `pytest-flake8==0.1` which conflict with modern Python 3.7 install. The pinned packages are replaced with explicit compatible versions below.
- `pytest<6.2` is required: `pytest.yield_fixture` (used throughout conftest, liveserver_fixtures, and test files) was removed in pytest 6.2.0.
- `Flask<2.0` + `Werkzeug<2.0` + `MarkupSafe<2.0` are required: the test suite starts a live Flask server and shuts it down via `werkzeug.server.shutdown` (removed in Werkzeug 2.1); Jinja2 2.x (bundled with Flask 1.x) uses `markupsafe.soft_unicode` (removed in MarkupSafe 2.1).

### Build and run

```bash
docker build -f Dockerfile.test -t datarobot_bs_test .
docker run --rm datarobot_bs_test
# Expected: 188 passed, 2 deselected, 1 xfailed in ~7 minutes
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails at install

`requirements-base.txt` contains `chardet>=3.0.2<3.1.0` (missing comma between version specifiers). Modern setuptools (bundled with Python 3.13) now enforces strict PEP 440 syntax and rejects this as a hard error rather than a warning.

Additionally, `setup.cfg` uses `description-file` (dash-separated key) which newer setuptools also flags during build.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t datarobot_bs_py313 .
# Expected: error in datarobot_batch_scoring setup command: 'install_requires' must be a string or iterable...
```

---

## Errors in Dockerfile.py313

```
error in datarobot_batch_scoring setup command: 'install_requires' must be a string or iterable of
strings containing valid project/version requirement specifiers; Expected comma (within version
specifier), semicolon (after version specifier) or end
    chardet>=3.0.2<3.1.0
           ~~~~~~~^
ERROR: Failed to build 'file:///root/code' when getting requirements to build editable
```

**Root cause:** `requirements-base.txt` specifies `chardet>=3.0.2<3.1.0` without a comma between the two version constraints. Modern setuptools enforces strict PEP 440 version specifier syntax; the missing comma that was silently tolerated in older setuptools is now a fatal build error on Python 3.13.

**Minimal fix:** Change `chardet>=3.0.2<3.1.0` to `chardet>=3.0.2,<3.1.0` in `requirements-base.txt`.
