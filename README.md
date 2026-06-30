# SWE-Adaptive: A Benchmark Dataset for Agentic Adaptive Maintenance of Python Projects

[![Project Status: Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![DOI](https://zenodo.org/badge/DOI/PLACEHOLDER_DOI.svg)](https://doi.org/PLACEHOLDER_DOI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

SWE-Adaptive is a benchmark dataset operationalizing adaptive maintenance as a
reproducible, automatically scorable task: given an archived Python repository
that fails under Python 3.13, restore it to a fully passing state.

## Overview

- **125 instances** spanning 6 breaking-change categories
- Each instance includes a baseline Dockerfile (Python 3.10) and a
  failing target Dockerfile (Python 3.13)
- Automatically scored via `docker build` exit code
- Constructed from 13,469 queried archived Python repositories

## Breaking Change Categories

| Category | Count | Share |
|---|---|---|
| C extension compilation failure (`c_extension`) | 40 | 32.0% |
| No binary wheel for Python 3.13 (`no_wheel`) | 28 | 22.4% |
| Legacy setuptools / distutils patterns (`setuptools_legacy`) | 22 | 17.6% |
| Dependency API removed or changed (`dependency_api`) | 20 | 16.0% |
| Standard library module removed (`stdlib_removed`) | 14 | 11.2% |
| Root cause unclassified (`unknown`) | 1 | 0.8% |
| **Total** | **125** | 100% |

## Repository Structure

```
swe-adaptive/
├── instances/       # Benchmark instances (Dockerfile.test, Dockerfile.py313, BENCHMARK.md)
├── construction/    # Dataset construction pipeline (scraper + auto_benchmark)
├── eval/            # Evaluation harness (run_eval.py, score_instance.py, etc.)
├── results/         # Evaluation results (summary.md, summary.csv)
├── trajectories/    # Agent trajectories from dataset validation experiments
└── paper/           # Paper PDF (after acceptance)
```

## Installation

```bash
git clone https://github.com/ANONYMOUS/swe-adaptive
cd swe-adaptive

# For running evaluations
pip install -e ".[eval]"

# For dataset construction
pip install -e ".[construction]"
```

Requirements: Python 3.8+, Docker 20.0+, Git 2.0+

## Usage

### Running the evaluation harness

```bash
# Evaluate a single instance
python eval/run_eval.py --model <model_name> --instance <instance_id>

# Evaluate all instances
python eval/run_eval.py --model <model_name> --all --resume

# Analyse results
python eval/analyze_runs.py
```

### Constructing new instances

Requires a GitHub personal access token set as `GITHUB_TOKEN`.

```bash
# Step 1: Scrape candidates from GitHub
python construction/find_archived_repos.py \
    --max-repos 2000 \
    --output archived_repos.json

# Step 2: Run automated pipeline
python construction/auto_benchmark.py \
    --input archived_repos.json \
    --output-dir ./

# Step 3: Build instance index
python construction/build_instance_index.py
```

## Dataset Validation

We validate the dataset by evaluating two models from the DeepSeek V4 family
using mini-swe-agent across two step budgets on a 31-instance evaluation subset.
Full results are available in `results/`, and agent trajectories in `trajectories/`.

| Model | Steps | Resolved | Rate |
|---|---|---|---|
| DeepSeek-V4-Flash | 50 | 17/31 | 54.8% |
| DeepSeek-V4-Flash | 100 | 27/31 | 87.1% |
| DeepSeek-V4-Pro | 50 | 17/31 | 54.8% |
| DeepSeek-V4-Pro | 100 | 23/31 | 74.2% |

A supplementary probe using Gemini-3.5-Flash on 13 of the hardest instances is also included, under `trajectories/gemini__gemini-3.5-flash/`.


## Contact

For questions or issues, please open a GitHub issue or contact us at:
ANONYMOUS@ANONYMOUS.edu

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file
for details. The benchmark instances reference third-party repositories which
retain their original licenses.
