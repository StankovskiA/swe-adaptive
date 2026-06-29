# Instance Template

Copy this directory as `owner__reponame/` when adding a new instance.

Required files:
- `Dockerfile.test` — must exit 0 with tests passing
- `Dockerfile.py313` — must fail during `docker build` (use RUN not CMD for tests)
- `BENCHMARK.md` — see template below

See CONTRIBUTING.md for full requirements.
