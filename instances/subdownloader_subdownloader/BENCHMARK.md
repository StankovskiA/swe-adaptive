# Benchmark: subdownloader

**Repository:** https://github.com/subdownloader/subdownloader
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.7)

**Docker image:** `Dockerfile.test`
**Python version:** 3.7
**Result:** 27 passed, 0 failed

All 27 tests pass on Python 3.7.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 22.73   error: subprocess-exited-with-error
#9 22.73   
#9 22.73   × Getting requirements to build editable did not run successfully.
#9 22.73   │ exit code: 1
#9 22.73   ╰─> [26 lines of output]
#9 22.73       Traceback (most recent call last):
#9 22.73         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 389, in <module>
#9 22.73           main()
#9 22.73           ~~~~^^
#9 22.73         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 373, in main
#9 22.73           json_out["return_val"] = hook(**hook_input["kwargs"])
#9 22.73                                    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^
#9 22.73         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 157, in get_requires_for_build_editable
#9 22.73           return hook(config_settings)
#9 22.73         File "/tmp/pip-build-env-_ygxpqrz/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 481, in get_requires_for_build_editable
#9 22.73           return self.get_requires_for_build_wheel(config_settings)
#9 22.73                  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
#9 22.73         File "/tmp/pip-build-env-_ygxpqrz/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 333, in get_requires_for_build_wheel
#9 22.73           return self._get_build_requires(config_settings, requirements=[])
#9 22.73                  ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
