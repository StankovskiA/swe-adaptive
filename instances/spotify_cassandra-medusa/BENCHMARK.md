# Benchmark: cassandra-medusa

**Repository:** https://github.com/spotify/cassandra-medusa
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 37 passed, 0 failed

All 37 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

```
#9 6.144       Traceback (most recent call last):
#9 6.144         File "/tmp/pip-install-ocwec9zl/cassandra-driver_05b83e693872443ca606452a8249c7ee/ez_setup.py", line 114, in use_setuptools
#9 6.144           import pkg_resources
#9 6.144       ModuleNotFoundError: No module named 'pkg_resources'
#9 6.144       
#9 6.144       During handling of the above exception, another exception occurred:
#9 6.144       
#9 6.144       Traceback (most recent call last):
#9 6.144         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 389, in <module>
#9 6.144           main()
#9 6.144           ~~~~^^
#9 6.144         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 373, in main
#9 6.144           json_out["return_val"] = hook(**hook_input["kwargs"])
#9 6.144                                    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^
#9 6.144         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 143, in get_requires_for_build_wheel
#9 6.144           return hook(config_settings)
#9 6.144         File "/tmp/pip-build-env-bj8qrcz4/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 333, in get_requires_for_build_wheel
#9 6.144           return self._get_build_requires(config_settings, requirements=[])
```

**Root cause:** `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

**Minimal fix:** Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+ | Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`. |
