# Benchmark Setup

This benchmark assesses an agent's ability to update a Python project's dependencies and source code to support a newer Python version.

## Project

[YAWNING-TITAN](https://github.com/dstl/YAWNING-TITAN) is a cyber security simulation framework. It uses a set of pinned dependencies (`pyproject.toml`) that were written targeting Python 3.8–3.10.

---

## Dockerfile.test — Baseline (Python 3.10.14)

`Dockerfile.test` establishes the working baseline. It builds and runs the full test suite on **Python 3.10.14**, with 225 tests passing and 8 pre-existing GUI test failures unrelated to the Python version.

### What it does

1. **Patches `gym==0.21.0` before installing** — `gym`'s `setup.py` contains `"opencv-python>=3."` (trailing dot), an invalid version specifier that modern setuptools rejects. The fix downloads the source tarball via the PyPI JSON API, replaces the specifier with `"opencv-python>=3.0"`, and installs with `--no-build-isolation` to use the pinned `setuptools==66`.

2. **Pre-installs CPU-only torch** — `pyproject.toml` pins `torch==1.13.1`. Without intervention, pip pulls the GPU build (~2 GB). Installing `torch==1.13.1+cpu` first satisfies the `torch==1.13.1` constraint (PEP 440 local versions are ignored when matching specifiers), keeping the image small.

3. **Installs the project** — `pip install -e ".[dev]"` installs the project in editable mode with all development dependencies including `pytest`.

4. **Creates runtime directories** — The app expects several directories under `~/yawning_titan/` and `~/.local/share/yawning_titan/` to exist at import time. Missing directories cause `FileNotFoundError` before any test runs.

5. **Seeds the database** — Two test fixtures (`tests/gui/__init__.py` and `tests/unit_tests/network/test_network.py`) call live database lookups at module import time, looking up specific UUIDs. The test package data (`tests/_package_data/game_modes.json` and `networks.json`) is copied to the live DB location so these lookups succeed.

### Running

```bash
docker build -f Dockerfile.test -t yawning-titan-test .
docker run --rm yawning-titan-test
```

### Expected result

```
141 passed
```

`tests/gui/`, `tests/e2e_integration_tests/`, and `tests/integration_tests/` are excluded from the CMD — the GUI tests have pre-existing failures due to Django view/DB mismatches, and the integration suites need external services. The 141 unit tests (`tests/unit_tests/`) are the benchmark signal.

---

## Dockerfile.py313 — Failing Target (Python 3.13)

`Dockerfile.py313` attempts a straightforward install of the project on **Python 3.13** without any workarounds. It is expected to fail at build time. This is the starting point for the benchmark task.

### Running

```bash
docker build -f Dockerfile.py313 -t yawning-titan-py313 .
```

### Expected result

The build fails during `pip install -e ".[dev]"`.

---

## Errors in Dockerfile.py313

### Error 1 — `gym==0.21.0`: invalid version specifier

```
error in gym setup command: 'extras_require' must be a dictionary whose values are
strings or lists of strings containing valid project/version requirement specifiers.
```

**Nature:** `gym==0.21.0`'s `setup.py` defines `extras_require` with `"opencv-python>=3."` — a version specifier ending in a bare dot. This was silently accepted by older versions of `setuptools` and `packaging` but is correctly rejected by versions shipped with Python 3.13. The package was last released in 2021 and has not been updated.

**Type:** Dependency incompatibility — `gym==0.21.0` cannot be built on Python 3.13 without patching its source.

---

### Error 2 — `torch==1.13.1`: no Python 3.13 wheel

If gym is worked around, `torch==1.13.1` has no pre-built wheel for Python 3.13 and predates its release. Attempting to build from source would also fail.

**Nature:** The package was released before Python 3.13 existed and has never published a compatible binary.

**Type:** Dependency incompatibility — requires upgrading to `torch>=2.0`.

---

### Error 3 — `gym` → `gymnasium` API migration

`gym` was deprecated and superseded by `gymnasium`. Beyond the package rename, the API has breaking changes:

- `env.step()` now returns 5 values `(obs, reward, terminated, truncated, info)` instead of 4 `(obs, reward, done, info)`
- `env.reset()` now returns `(obs, info)` instead of just `obs`
- `gym.envs.registration.register` moved to `gymnasium`

**Type:** Source code change required — `pyproject.toml` and all source files importing from `gym` must be updated.

---

### Error 4 — `ray[rllib]==2.3.1` and `stable_baselines3==1.6.2`

Both depend on `torch` and `gym`. Updating those pulls in version conflicts with these pinned packages.

**Type:** Cascading dependency update — these must be updated in tandem with `torch` and `gymnasium`.

---

## Benchmark Task

Given `Dockerfile.py313` as a starting point, update the project so that it builds and the test suite passes on Python 3.13. The solution requires:

1. Updating pinned dependencies in `pyproject.toml` to versions compatible with Python 3.13
2. Migrating source code from `gym` to `gymnasium`
3. Adapting any code relying on changed APIs (`step`, `reset`, RLlib, etc.)
