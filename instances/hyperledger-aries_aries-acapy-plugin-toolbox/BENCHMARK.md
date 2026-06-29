# Benchmark: aries-acapy-plugin-toolbox

**Repository:** https://github.com/hyperledger-aries/aries-acapy-plugin-toolbox
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.7)

**Docker image:** `Dockerfile.test`
**Python version:** 3.7
**Result:** 48 passed, 0 failed

All 48 tests pass on Python 3.7.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `aries-cloudagent` 0.7.x wheel has invalid PEP 440 metadata; pip ≥24.1 rejects it

```
#9 7.742 ERROR: Ignored the following yanked versions: 0.10.0
#9 7.742 ERROR: Could not find a version that satisfies the requirement aries-cloudagent<0.8.0,>=0.7.4 (from aries-acapy-plugin-toolbox) (from versions: 0.2.0, 0.2.1, 0.3.0, 0.3.1, 0.3.2, 0.3.3, 0.3.4, 0.3.5, 0.4.0, 0.4.1, 0.4.2, 0.4.3, 0.4.4, 0.4.5, 0.5.0, 0.5.1, 0.5.2, 0.5.3, 0.5.4, 0.5.5, 0.5.6, 0.6.0rc0, 0.6.0rc1, 0.6.0, 0.7.0rc0, 0.7.0rc1, 0.7.0, 0.7.1rc0, 0.7.1, 0.7.2rc0, 0.7.2, 0.7.3rc0, 0.7.3, 0.7.4rc0, 0.7.4rc1, 0.7.4rc2, 0.7.4rc3, 0.7.4rc4, 0.7.4rc5, 0.7.4, 0.7.5rc0, 0.7.5rc1, 0.7.5, 0.8.0rc0, 0.8.0, 0.8.1rc0, 0.8.1rc1, 0.8.1rc2, 0.8.1, 0.8.2rc0, 0.8.2rc1, 0.8.2rc2, 0.8.2, 0.9.0rc0, 0.9.0, 0.10.0rc0, 0.10.0rc1, 0.10.0rc2, 0.10.1, 0.10.2rc0, 0.10.2, 0.10.3, 0.10.4, 0.10.5, 0.11.0rc1, 0.11.0rc2, 0.11.0, 0.11.1, 0.11.2, 0.11.3, 0.12.0rc0, 0.12.0rc1, 0.12.0rc2, 0.12.0rc3, 0.12.0, 0.12.1rc0, 0.12.1rc1, 0.12.1, 0.12.2rc1, 0.12.2, 0.12.3rc0, 0.12.3, 0.12.4, 0.12.5, 0.12.6, 0.12.7rc0, 0.12.7rc1, 0.12.7rc2, 0.12.7, 0.12.8, 1.0.0rc0, 1.0.0rc1, 1.0.0rc2, 1.0.0rc3, 1.0.0rc4, 1.0.0rc5, 1.0.0rc6, 1.0.0, 1.0.1rc0, 1.0.1rc1, 1.0.1)
#9 7.743 ERROR: No matching distribution found for aries-cloudagent<0.8.0,>=0.7.4
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest pytest-asyncio asynctest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest pytest-asyncio asynctest:
7.726   Downloading aries_cloudagent-0.7.4-py3-none-any.whl.metadata (12 kB)
7.740 WARNING: Ignoring version 0.7.4 of aries-cloudagent since it has invalid metadata:
7.740 Requested aries-cloudagent<0.8.0,>=0.7.4 from https://files.pythonhosted.org/packages/71/b8/6fc7aa59ebe63243b8993d09053e3d7c9242c160688a2852602cb5928a4e/aries_cloudagent-0.7.4-py3-none-any.whl (from aries-cloudagent[askar,bbs,indy]<0.8.0,>=0.7.4->aries-acapy-plugin-toolbox==0.2.0) has invalid metadata: Expected matching RIGHT_PARENTHESIS for LEFT_PARENTHESIS, after version specifier
7.740     python3-indy (>=1.11.1<2) ; extra == 'indy'
7.740                  ~~~~~~~~~^
7.740 Please use pip<24.1 if you need to use this version.
7.740 INFO: pip is looking at multiple versions of aries-acapy-plugin-toolbox to determine which version is compatible with other requirements. This could take a while.
7.742 ERROR: Ignored the following yanked versions: 0.10.0
7.742 ERROR: Could not find a version that satisfies the requirement aries-cloudagent<0.8.0,>=0.7.4 (from aries-acapy-plugin-toolbox) (from versions: 0.2.0, 0.2.1, 0.3.0, 0.3.1, 0.3.2, 0.3.3, 0.3.4, 0.3.5, 0.4.0, 0.4.1, 0.4.2, 0.4.3, 0.4.4, 0.4.5, 0.5.0, 0.5.1, 0.5.2, 0.5.3, 0.5.4, 0.5.5, 0.5.6, 0.6.0rc0, 0.6.0rc1, 0.6.0, 0.7.0rc0, 0.7.0rc1, 0.7.0, 0.7.1rc0, 0.7.1, 0.7.2rc0, 0.7.2, 0.7.3rc0, 0.7.3, 0.7.4rc0, 0.7.4rc1, 0.7.4rc2, 0.7.4rc3, 0.7.4rc4, 0.7.4rc5, 0.7.4, 0.7.5rc0, 0.7.5rc1, 0.7.5, 0.8.0rc0, 0.8.0, 0.8.1rc0, 0.8.1rc1, 0.8.1rc2, 0.8.1, 0.8.2rc0, 0.8.2rc1, 0.8.2rc2, 0.8.2, 0.9.0rc0, 0.9.0, 0.10.0rc0, 0.10.0rc1, 0.10.0rc2, 0.10.1, 0.10.2rc0, 0.10.2, 0.10.3, 0.10.4, 0.10.5, 0.11.0rc1, 0.11.0rc2, 0.11.0, 0.11.1, 0.11.2, 0.11.3, 0.12.0rc0, 0.12.0rc1, 0.12.0rc2, 0.12.0rc3, 0.12.0, 0.12.1rc0, 0.12.1rc1, 0.12.1, 0.12.2rc1, 0.12.2, 0.12.3rc0, 0.12.3, 0.12.4, 0.12.5, 0.12.6, 0.12.7rc0, 0.12.7rc1, 0.12.7rc2, 0.12.7, 0.12.8, 1.0.0rc0, 1.0.0rc1, 1.0.0rc2, 1.0.0rc3, 1.0.0rc4, 1.0.0rc5, 1.0.0rc6, 1.0.0, 1.0.1rc0, 1.0.1rc1, 1.0.1)
7.743 ERROR: No matching distribution found for aries-cloudagent<0.8.0,>=0.7.4
------
_Dockerfile_tmp_hyperledger-aries_aries-acapy-plugin-toolbox:5
--------------------
   4 |     COPY . .
```

**Root cause:** `aries-acapy-plugin-toolbox` pins `aries-cloudagent>=0.7.4,<0.8.0`. The `aries_cloudagent-0.7.4` wheel contains invalid PEP 440 metadata: `python3-indy (>=1.11.1<2)` — missing comma between `>=1.11.1` and `<2`. pip ≥24.1 (bundled with Python 3.13) strictly validates wheel metadata and rejects this entry with `Ignoring version 0.7.4 … has invalid metadata`. All 0.7.x versions have the same issue, so the entire pinned range becomes uninstallable.

**Minimal fix:** Widen the `aries-cloudagent` constraint to `>=1.0.0` (which has valid metadata) and update the code for any breaking API changes in the newer ACA-Py releases.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `aries-cloudagent` 0.7.x wheel metadata contains invalid PEP 440 specifier (`python3-indy (>=1.11.1<2)` — missing comma); pip ≥24.1 (Python 3.13) rejects it → no installable version in `>=0.7.4,<0.8.0` range | Widen constraint to `aries-cloudagent>=1.0.0` in `setup.cfg` |
