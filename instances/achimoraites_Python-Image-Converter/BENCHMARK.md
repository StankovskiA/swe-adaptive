# Benchmark: Python-Image-Converter

**Repository:** https://github.com/achimoraites/Python-Image-Converter
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 12 passed, 0 failed

All 12 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 81.03   error: subprocess-exited-with-error
#9 81.03   
#9 81.03   × Getting requirements to build wheel did not run successfully.
#9 81.03   │ exit code: 1
#9 81.03   ╰─> [21 lines of output]
#9 81.03       Traceback (most recent call last):
#9 81.03         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 389, in <module>
#9 81.03           main()
#9 81.03           ~~~~^^
#9 81.03         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 373, in main
#9 81.03           json_out["return_val"] = hook(**hook_input["kwargs"])
#9 81.03                                    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^
#9 81.03         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 143, in get_requires_for_build_wheel
#9 81.03           return hook(config_settings)
#9 81.03         File "/tmp/pip-build-env-iwizx4hp/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 333, in get_requires_for_build_wheel
#9 81.03           return self._get_build_requires(config_settings, requirements=[])
#9 81.03                  ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#9 81.03         File "/tmp/pip-build-env-iwizx4hp/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 301, in _get_build_requires
#9 81.03           self.run_setup()
#9 81.03           ~~~~~~~~~~~~~~^^
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
