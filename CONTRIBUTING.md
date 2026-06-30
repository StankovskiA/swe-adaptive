# Contributing to SWE-Adaptive

Thank you for your interest in contributing to SWE-Adaptive.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion, please open a GitHub issue with:
- A clear description of the problem
- Steps to reproduce (if applicable)
- Expected vs actual behaviour

### Contributing New Benchmark Instances

New instances must meet these criteria:
1. The repository must be archived on GitHub
2. Tests must pass cleanly on a historical Python version (3.7–3.10)
3. Tests must fail on Python 3.13 due to a genuine breaking change
4. The failure must be reproducible via `docker build -f Dockerfile.py313 .`
5. A root cause analysis must be documented in BENCHMARK.md

See `instances/TEMPLATE/` for the required file format.

### Contributing to the Evaluation Harness or Construction Pipeline

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests where appropriate
4. Submit a pull request with a clear description of the change

## Code of Conduct

Please be respectful and constructive in all interactions.
Issues or pull requests that are disrespectful will be closed.

## Contact

Open a GitHub issue for any questions.
