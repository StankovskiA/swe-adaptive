# Benchmark: pinject

**Repository:** https://github.com/google/pinject
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 258 passed, 0 failed

All 258 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 7.947   error: subprocess-exited-with-error
#9 7.947   
#9 7.947   × Getting requirements to build editable did not run successfully.
#9 7.947   │ exit code: 1
#9 7.947   ╰─> [26 lines of output]
#9 7.947       Traceback (most recent call last):
#9 7.947         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 389, in <module>
#9 7.947           main()
#9 7.947           ~~~~^^
#9 7.947         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 373, in main
#9 7.947           json_out["return_val"] = hook(**hook_input["kwargs"])
#9 7.947                                    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^
#9 7.947         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 157, in get_requires_for_build_editable
#9 7.947           return hook(config_settings)
#9 7.947         File "/tmp/pip-build-env-l510ug5_/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 481, in get_requires_for_build_editable
#9 7.947           return self.get_requires_for_build_wheel(config_settings)
#9 7.947                  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
#9 7.947         File "/tmp/pip-build-env-l510ug5_/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 333, in get_requires_for_build_wheel
#9 7.947           return self._get_build_requires(config_settings, requirements=[])
#9 7.947                  ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
