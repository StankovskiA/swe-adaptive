# Benchmark: fcakyon/pywhisper

## Repository
**GitHub:** https://github.com/fcakyon/pywhisper  
**Description:** OpenAI Whisper speech-to-text model with extra features.

## Baseline
- **Python version:** 3.8
- **Test command:** `pytest tests/test_normalizer.py -v`
- **Result:** 4 passed

## Python 3.13 Failure
- **Test command:** `pytest tests/ -v` (run at image build time)
- **Result:** Build fails — cannot install the package (`pip install -e .` fails)

### Error
```
ModuleNotFoundError: No module named 'pkg_resources'
Getting requirements to build editable: finished with status 'error'
ERROR: Failed to build 'file:///root/code' when getting requirements to build editable
```

### Root Cause
`setup.py` uses `import pkg_resources` from `setuptools` to parse `requirements.txt`:
```python
from pkg_resources import parse_requirements
install_requires=[str(r) for r in pkg_resources.parse_requirements(open("requirements.txt"))]
```
In Python 3.13, `pkg_resources` is no longer available in pip's build isolation environment (PEP 517 build backends no longer guarantee its presence).

## Minimal Fix
Replace the `pkg_resources.parse_requirements()` call in `setup.py` with a direct file read:

```diff
-import pkg_resources
-from setuptools import setup, find_packages
+from setuptools import setup, find_packages

 def get_requirements():
-    return [str(r) for r in pkg_resources.parse_requirements(
-        open(os.path.join(os.path.dirname(__file__), "requirements.txt"))
-    )]
+    with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as f:
+        return [line.strip() for line in f if line.strip() and not line.startswith("#")]
```
