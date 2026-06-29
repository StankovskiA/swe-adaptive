# Benchmark: hugie

**Repository:** https://github.com/MantisAI/hugie
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 27 passed, 0 failed

All 27 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `typer` 0.9.x / Click API mismatch: `TyperArgument.make_metavar()` arity changed

```
#9 0.879 tests/test_config.py::test_modify_writes_to_stdout FAILED                [  7%]
#9 0.982 tests/test_endpoint.py::test_create_args FAILED                          [ 25%]
#9 1.025 tests/test_endpoint.py::test_delete_force FAILED                         [ 33%]
#9 1.072 tests/test_endpoint.py::test_delete_no_confirm FAILED                    [ 40%]
...
FAILED tests/test_config.py::test_modify_writes_to_stdout - AssertionError: assert 'medium' in ''
    where '' = <Result TypeError('TyperArgument.make_metavar() takes 1 positional argument but 2 were given')>.stdout

================== 5 failed, 22 passed in 1.25s ==================
```

**Root cause:** `hugie` pins `typer^0.9.0`. typer 0.9.x subclasses Click's `Argument` as `TyperArgument` and overrides `make_metavar()` with a signature that only accepts `self`. A newer Click version (resolved by pip on Python 3.13) changed its internal call to `Argument.make_metavar()` to pass an extra positional argument, causing `TypeError: TyperArgument.make_metavar() takes 1 positional argument but 2 were given`. The CLI runner swallows the exception, making the command silently return an empty result — causing assertion failures in tests that check CLI output.

**Minimal fix:** Upgrade `typer` to `^0.13` in `pyproject.toml`/`setup.cfg`, which fixed this internal Click API compatibility issue.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `typer` 0.9.x `TyperArgument.make_metavar()` overrides Click's method with wrong arity; newer Click passes an extra arg → `TypeError` → silent CLI failures | Upgrade `typer` to `^0.13` |
