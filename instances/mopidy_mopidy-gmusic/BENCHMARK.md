# Benchmark: mopidy/mopidy-gmusic

**Repository:** https://github.com/mopidy/mopidy-gmusic
**Language:** Python
**Test framework:** pytest

Mopidy-GMusic is a Mopidy extension for playing music from Google Play Music. Tests cover the extension entry point, library backend, playback backend, playlists, session management, a repeating timer utility, and the Last.fm scrobbler frontend.

---

## Dockerfile.test — Baseline (Python 3.10)

**Python version:** 3.10
**Result:** 78 passed

### Special setup

- **PyGObject built from source**: `python3-gi` and `python3-gst-1.0` Debian packages install C extensions compiled for the system Python (3.13 in Bookworm), which have ABI `cpython-313` and cannot be loaded by Python 3.10 or 3.11. PyGObject must be built from source via pip with full build dependencies.
- **`PyGObject<3.45`**: PyGObject 3.45+ requires `girepository-2.0` (GLib 2.80+), but Debian Bookworm ships GLib 2.74 which only provides `girepository-1.0`. Pinning `<3.45` uses the older API.
- **`protobuf<4.0.0`**: gmusicapi uses old protobuf-generated code that is incompatible with protobuf 4.x (`Descriptors cannot be created directly` error at import time).
- **`gir1.2-gst-plugins-base-1.0`**: Required for the `GstPbutils` typelib (`gi.repository.GstPbutils`); missing it causes `ValueError: Namespace GstPbutils not available`.

### System packages required

| Package | Purpose |
|---------|---------|
| `build-essential`, `meson`, `ninja-build`, `pkg-config` | Build toolchain for PyGObject from source |
| `libglib2.0-dev`, `libgirepository1.0-dev`, `libcairo2-dev` | C headers needed by PyGObject build |
| `gstreamer1.0-plugins-base`, `gstreamer1.0-plugins-good` | GStreamer runtime plugins |
| `gir1.2-gstreamer-1.0`, `gir1.2-gst-plugins-base-1.0` | GStreamer GObject introspection typelibs |

### Build and run

```bash
docker build -f Dockerfile.test -t mopidy-gmusic-test .
docker run --rm mopidy-gmusic-test
# Expected: 78 passed in ~2s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -e .`

`mopidy>=3.0.0` now requires `pygobject>=3.50`. PyGObject 3.50+ (current: 3.56.3) switched to using `girepository-2.0`, which is only available in GLib 2.80+. The Python 3.13 Docker image is based on Debian Bookworm, which ships GLib 2.74 — only `girepository-1.0` is available.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t mopidy-gmusic-py313 .
# Expected: ERROR: Dependency 'girepository-2.0' is required but not found.
```

---

## Errors in Dockerfile.py313

```
Collecting pygobject>=3.50 (from Mopidy>=3.0.0->Mopidy-GMusic==4.0.1)
  ...
  × Preparing metadata (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [25 lines of output]
      Run-time dependency girepository-2.0 found: NO  (tried pkg-config and cmake)
      Not looking for a fallback subproject for the dependency girepository-2.0 because:
      Use of fallback dependencies is disabled.
      
      ../meson.build:35:9: ERROR: Dependency 'girepository-2.0' is required but not found.
```

**Root cause:** `mopidy>=3.0.0` pulls `pygobject>=3.50`, which requires GLib 2.80+ for `girepository-2.0`. Python 3.13 Docker images are based on Debian Bookworm (GLib 2.74), which only provides `girepository-1.0`. PyGObject 3.50+ is uninstallable on this platform.

**Minimal fix:** Upgrade the base OS to one with GLib 2.80+ (e.g., Ubuntu 24.04 or Debian Trixie), or pin `PyGObject<3.45` and accept that Mopidy's declared dependency range cannot be satisfied as-specified.
