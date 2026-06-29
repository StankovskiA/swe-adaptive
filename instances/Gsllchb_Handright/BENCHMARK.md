# Benchmark: Handright

**Repository:** https://github.com/Gsllchb/Handright
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 16 passed, 0 failed

All 16 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — Old Pillow `setup.py` uses `exec()` to read version; Python 3.13 `exec()` locals change → `KeyError: '__version__'`

```
#9 9.015   error: subprocess-exited-with-error
#9 9.015   
#9 9.015   × Getting requirements to build wheel did not run successfully.
#9 9.015   │ exit code: 1
#9 9.015   ╰─> [24 lines of output]
#9 9.015       Traceback (most recent call last):
#9 9.015         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 389, in <module>
#9 9.015           main()
#9 9.015           ~~~~^^
#9 9.015         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 373, in main
#9 9.015           json_out["return_val"] = hook(**hook_input["kwargs"])
#9 9.015                                    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^
#9 9.015         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 143, in get_requires_for_build_wheel
#9 9.015           return hook(config_settings)
#9 9.015         File "/tmp/pip-build-env-kto5l11f/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 333, in get_requires_for_build_wheel
#9 9.015           return self._get_build_requires(config_settings, requirements=[])
#9 9.015                  ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#9 9.015         File "/tmp/pip-build-env-kto5l11f/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 301, in _get_build_requires
#9 9.015           self.run_setup()
#9 9.015           ~~~~~~~~~~~~~~^^
```

**Root cause:** `requirements.txt` pins an old version of Pillow whose `setup.py` uses `exec(open("src/PIL/_version.py").read(), {})` to extract `__version__`. Python 3.13 changed how `exec()` populates the `locals()` dict (assignments in the executed code no longer propagate back to the outer scope), so the subsequent `__version__` lookup raises `KeyError: '__version__'`.

**Minimal fix:** Pin `Pillow` to ≥10.0.0 in `requirements.txt`, which ships pre-built Python 3.13 wheels and uses a modern build backend that doesn't rely on `exec()` for version reading.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | Old Pillow `setup.py` uses `exec()` to read `__version__`; Python 3.13 changed `exec()` locals handling → `KeyError: '__version__'` | Pin `Pillow>=10.0.0` in `requirements.txt` |
