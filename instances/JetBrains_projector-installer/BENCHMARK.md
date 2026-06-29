# Benchmark: projector-installer

**Repository:** https://github.com/JetBrains/projector-installer
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 39 passed, 0 failed

All 39 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 10.19   error: subprocess-exited-with-error
#9 10.19   
#9 10.19   × Getting requirements to build editable did not run successfully.
#9 10.19   │ exit code: 1
#9 10.19   ╰─> [29 lines of output]
#9 10.19       Traceback (most recent call last):
#9 10.19         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 389, in <module>
#9 10.19           main()
#9 10.19           ~~~~^^
#9 10.19         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 373, in main
#9 10.19           json_out["return_val"] = hook(**hook_input["kwargs"])
#9 10.19                                    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^
#9 10.19         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 157, in get_requires_for_build_editable
#9 10.19           return hook(config_settings)
#9 10.19         File "/tmp/pip-build-env-tnzmtgkp/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 481, in get_requires_for_build_editable
#9 10.19           return self.get_requires_for_build_wheel(config_settings)
#9 10.19                  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
#9 10.19         File "/tmp/pip-build-env-tnzmtgkp/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 333, in get_requires_for_build_wheel
#9 10.19           return self._get_build_requires(config_settings, requirements=[])
#9 10.19                  ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
