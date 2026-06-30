# SWE-Adaptive Evaluation — Analysis Report

Generated: 2026-06-30 09:32 UTC

---

## Overall Summary

| Model | Resolved | Total | Rate | Avg Steps | Avg Tokens | Avg Cost | Avg Time (s) |
|-------|----------|-------|------|-----------|------------|----------|--------------|
| `deepseek__deepseek-v4-flash` | 27 | 31 | 87.1% | 56.8 | 2116624 | $0.0164 | 505 |
| `deepseek__deepseek-v4-pro` | 23 | 31 | 74.2% | 58.9 | 2360699 | $0.0443 | 538 |
| `gemini__gemini-3.5-flash` | 6 | 13 | 46.2% | 39.4 | 2462034 | $1.3100 | 789 |

---

## Resolution by Breaking Change Type

| Breaking Change Type | Resolved | Total | Rate |
|----------------------|----------|-------|------|
| asyncio_change | 2 | 2 | 100.0% |
| c_extension | 1 | 3 | 33.3% |
| no_wheel | 22 | 33 | 66.7% |
| stdlib_removed | 20 | 24 | 83.3% |

---

## Resolution by Folder

| Folder | Resolved | Total | Rate |
|--------|----------|-------|------|
| success_benchmark | 11 | 11 | 100.0% |
| success_benchmark_manual | 21 | 31 | 67.7% |
| validated_success_benchmark | 24 | 33 | 72.7% |

---

## Failure Analysis (unresolved instances)

| Model | Instance | Failure Category | Steps | Hit Limit | Final Error |
|-------|----------|-----------------|-------|-----------|-------------|
| deepseek-v4-flash | `YAWNING-TITAN` | no_dockerfile | 100 | ✓ | Agent did not generate Dockerfile.py313 |
| deepseek-v4-flash | `horazont_aioxmpp` | no_dockerfile | 100 | ✓ | Agent did not generate Dockerfile.py313 |
| deepseek-v4-flash | `mlem` | no_dockerfile | 100 | ✓ | Agent did not generate Dockerfile.py313 |
| deepseek-v4-flash | `openedx-unsupported_bok-choy` | no_dockerfile | 86 |  | Agent did not generate Dockerfile.py313 |
| deepseek-v4-pro | `DarkCat09_python-aternos` | no_dockerfile | 100 | ✓ | Agent did not generate Dockerfile.py313 |
| deepseek-v4-pro | `YAWNING-TITAN` | no_dockerfile | 100 | ✓ | Agent did not generate Dockerfile.py313 |
| deepseek-v4-pro | `horazont_aioxmpp` | no_dockerfile | 100 | ✓ | Agent did not generate Dockerfile.py313 |
| deepseek-v4-pro | `openedx-unsupported_bok-choy` | no_dockerfile | 66 |  | Agent did not generate Dockerfile.py313 |
| deepseek-v4-pro | `wkeeling_selenium-wire` | no_dockerfile | 100 | ✓ | Agent did not generate Dockerfile.py313 |
| gemini-3.5-flash | `YAWNING-TITAN` | no_dockerfile | 58 |  | Agent did not generate Dockerfile.py313 |
| gemini-3.5-flash | `horazont_aioxmpp` | no_dockerfile | 25 |  | Agent did not generate Dockerfile.py313 |
| gemini-3.5-flash | `mlem` | no_dockerfile | 66 |  | Agent did not generate Dockerfile.py313 |
| gemini-3.5-flash | `panini` | no_dockerfile | 33 |  | Agent did not generate Dockerfile.py313 |
| gemini-3.5-flash | `poliastro` | no_dockerfile | 4 |  | Agent did not generate Dockerfile.py313 |
| gemini-3.5-flash | `thomasgermain_pymultiMATIC` | no_dockerfile | ? |  | Agent did not generate Dockerfile.py313 |
| gemini-3.5-flash | `wkeeling_selenium-wire` | no_dockerfile | 24 |  | Agent did not generate Dockerfile.py313 |
| deepseek-v4-pro | `NimbleBoxAI_ChainFury` | test_failure | 100 | ✓ | ERROR: failed to build: failed to solve: process "/bin/sh -c python -m pytest tests/ -v -q" did not  |
| deepseek-v4-pro | `mlem` | test_failure | ? |  | ERROR: failed to build: failed to solve: process "/bin/sh -c pip install --no-cache-dir     cloudpic |
| deepseek-v4-pro | `panini` | test_failure | 100 | ✓ | ERROR: failed to build: failed to solve: process "/bin/sh -c pip install -r requirements/defaults.tx |

**Failure category counts:**

| Category | Count |
|----------|-------|
| no_dockerfile | 16 |
| test_failure | 3 |

---

## Test File Modifications

- ❌ deepseek-v4-flash / `YAWNING-TITAN` — tests/e2e_integration_tests/test_generic_env_e2e.py, tests/integration_tests/env/test_five_node_def.py, tests/integration_tests/env/test_nsa_node_env.py, tests/integration_tests/env/test_stable_baselines_compliance.py, tests/integration_tests/generic_env/test_env_reset.py, tests/integration_tests/generic_env/test_graph_embedding_observations.py, tests/integration_tests/generic_env/test_high_value_node_and_entry_nodes_matching.py, tests/integration_tests/generic_env/test_new_entry_nodes.py, tests/integration_tests/generic_env/test_new_high_value_node.py, tests/integration_tests/generic_env/test_new_vulnerabilities.py
- ❌ deepseek-v4-pro / `YAWNING-TITAN` — tests/e2e_integration_tests/test_generic_env_e2e.py, tests/integration_tests/env/test_five_node_def.py, tests/integration_tests/env/test_nsa_node_env.py, tests/integration_tests/env/test_stable_baselines_compliance.py, tests/integration_tests/generic_env/test_end_rewards_are_multiplied_by_end_state.py, tests/integration_tests/generic_env/test_env_reset.py, tests/integration_tests/generic_env/test_graph_embedding_observations.py, tests/integration_tests/generic_env/test_high_value_node_and_entry_nodes_matching.py, tests/integration_tests/generic_env/test_natural_spreading.py, tests/integration_tests/generic_env/test_new_entry_nodes.py, tests/integration_tests/generic_env/test_new_high_value_node.py, tests/integration_tests/generic_env/test_new_vulnerabilities.py, tests/integration_tests/test_network_interface.py
- ❌ deepseek-v4-flash / `horazont_aioxmpp` — tests/forms/test_fields.py, tests/test_service.py, tests/xso/test_model.py, tests/xso/test_types.py
- ❌ deepseek-v4-pro / `horazont_aioxmpp` — tests/bookmarks/test_service.py, tests/forms/test_fields.py, tests/test_service.py, tests/test_utils.py, tests/xso/test_model.py
- ✅ deepseek-v4-flash / `jkwill87_stonky` — tests/test_api.py
- ✅ deepseek-v4-pro / `jkwill87_stonky` — tests/test_api.py
- ✅ deepseek-v4-flash / `litl_backoff` — tests/test_backoff_async.py
- ✅ deepseek-v4-pro / `litl_backoff` — tests/test_backoff_async.py
- ❌ deepseek-v4-flash / `mlem` — tests/api/test_commands.py, tests/cli/test_main.py, tests/contrib/test_bitbucket.py, tests/contrib/test_docker/test_pack.py, tests/contrib/test_numpy.py, tests/contrib/test_onnx.py, tests/contrib/test_pandas.py, tests/core/test_data_type.py, tests/core/test_metadata.py
- ❌ deepseek-v4-pro / `mlem` — tests/cli/test_main.py
- ✅ deepseek-v4-flash / `multimeric_PandasSchema` — test/test_validation.py
- ✅ deepseek-v4-pro / `multimeric_PandasSchema` — test/test_schema.py, test/test_validation.py
- ✅ deepseek-v4-pro / `natelandau_obsidian-metadata` — tests/questions_test.py
- ✅ deepseek-v4-pro / `poliastro` — tests/test_maneuver.py
- ✅ deepseek-v4-pro / `thomasgermain_pymultiMATIC` — tests/test_mapper.py
- ✅ deepseek-v4-flash / `tudorelu_pyjuque` — tests/test_BotController.py
- ✅ deepseek-v4-pro / `tudorelu_pyjuque` — tests/test_BotController.py
- ✅ gemini-3.5-flash / `tudorelu_pyjuque` — tests/test_BotController.py

---

## Dependency-only Fixes

Instances resolved by changing only dependency/config files (no Python source changes required):

- deepseek-v4-flash / `MantisAI_hugie` — Dockerfile.py313, pyproject.toml
- deepseek-v4-pro / `MantisAI_hugie` — Dockerfile.py313, pyproject.toml
- gemini-3.5-flash / `NimbleBoxAI_ChainFury` — Dockerfile.py313, pyproject.toml, server/pyproject.toml
- deepseek-v4-flash / `comtravo_ctparse` — Dockerfile.py313, requirements_dev.txt
- deepseek-v4-pro / `comtravo_ctparse` — Dockerfile.py313, requirements_dev.txt
- deepseek-v4-flash / `djantic` — Dockerfile.py313, pyproject.toml, setup.py, tox.ini
- deepseek-v4-pro / `djantic` — Dockerfile.py313, pyproject.toml, setup.py
- deepseek-v4-flash / `drf-openapi-tester` — .gitignore, Dockerfile.py313, poetry.lock, pyproject.toml
- deepseek-v4-pro / `drf-openapi-tester` — .gitignore, Dockerfile.py313, poetry.lock, pyproject.toml
- deepseek-v4-flash / `encode_databases` — Dockerfile.py313, requirements.txt
- deepseek-v4-pro / `encode_databases` — Dockerfile.py313, requirements.txt, setup.py
- deepseek-v4-flash / `femueller_python-n26` — Dockerfile.py313, requirements.txt
- deepseek-v4-pro / `femueller_python-n26` — Dockerfile.py313, requirements.txt
- gemini-3.5-flash / `openedx-unsupported_bok-choy` — Dockerfile.py313, requirements/dev.txt, requirements/needle.txt, requirements/test.txt
- deepseek-v4-flash / `panini` — Dockerfile.py313, requirements/defaults.txt, setup.py
- deepseek-v4-flash / `rhasspy_gruut-ipa` — Dockerfile.py313, requirements_dev.txt
- deepseek-v4-pro / `rhasspy_gruut-ipa` — Dockerfile.py313, requirements_dev.txt
- deepseek-v4-flash / `ripe-updater` — Dockerfile.py313, requirements.txt
- deepseek-v4-pro / `ripe-updater` — Dockerfile.py313, requirements.txt
- deepseek-v4-pro / `sassoftware_epdb` — Dockerfile.py313, setup.py
- deepseek-v4-flash / `thomasgermain_pymultiMATIC` — Dockerfile.py313, requirements.txt
- deepseek-v4-flash / `tiangolo_typer-cli` — Dockerfile.py313, pyproject.toml, requirements.txt
- deepseek-v4-pro / `tiangolo_typer-cli` — Dockerfile.py313, pyproject.toml, requirements.txt

---

## Agent Behaviour Patterns

- **Agent signalled completion (vs. cut off by step/time limit)**: 44/75
- **Hit step limit (100 steps)**: 10/75
- **Timed out**: 0/75
- **Empty patch (no file changes)**: 7/75
- **No Dockerfile generated**: 16/75
- **Avg steps — resolved**: 48.2
- **Avg steps — unresolved**: 66.4
- **Cache hit rate** (all runs): 94.8%
  — hit: 154,014,800 tokens / miss: 8,399,922 tokens

---

## Gemini Subset — Cross-Model Comparison (13 instances)

Resolution rate of each model restricted to the 13 instance(s) evaluated by Gemini:

| Instance | Type | deepseek-v4-flash | deepseek-v4-pro | gemini-3.5-flash |
|----------|------|---|---|---|
| `NimbleBoxAI_ChainFury` | — | ✅ | ❌ | ✅ |
| `YAWNING-TITAN` | no_wheel | ❌ | ❌ | ❌ |
| `caltechlibrary_handprint` | stdlib_removed | ✅ | ✅ | ✅ |
| `horazont_aioxmpp` | no_wheel | ❌ | ❌ | ❌ |
| `mlem` | stdlib_removed | ❌ | ❌ | ❌ |
| `openedx-unsupported_bok-choy` | no_wheel | ❌ | ❌ | ✅ |
| `panini` | c_extension | ✅ | ❌ | ❌ |
| `poliastro` | stdlib_removed | ✅ | ✅ | ❌ |
| `python-acoustics_python-acoustics` | — | ✅ | ✅ | ✅ |
| `thomasgermain_pymultiMATIC` | — | ✅ | ✅ | ❌ |
| `tiangolo_typer-cli` | stdlib_removed | ✅ | ✅ | ✅ |
| `tudorelu_pyjuque` | no_wheel | ✅ | ✅ | ✅ |
| `wkeeling_selenium-wire` | no_wheel | ✅ | ❌ | ❌ |

| **Resolution rate** | | 9/13 (69.2%) | 6/13 (46.2%) | 6/13 (46.2%) |

---

## Per-instance Detail

| Model | Instance | Type | Resolved | Steps | Limit | Tokens | Cost | Time (s) | Dockerfile | Dep Only | Tests |
|-------|----------|------|----------|-------|-------|--------|------|---------|------------|----------|-------|
| deepseek-v4-flash | `DarkCat09_python-aternos` | no_wheel | ✅ | 76 |  | 3,534,134 | $0.0265 | 431 | ✓ |  |  |
| deepseek-v4-flash | `MantisAI_hugie` | — | ✅ | 49 |  | 1,388,169 | $0.0126 | 268 | ✓ | ✓ |  |
| deepseek-v4-flash | `NimbleBoxAI_ChainFury` | — | ✅ | 54 |  | 2,277,151 | $0.0181 | 371 | ✓ |  |  |
| deepseek-v4-flash | `SebRut_pygrocy` | — | ✅ | 44 |  | 1,266,200 | $0.0119 | 153 | ✓ |  |  |
| deepseek-v4-flash | `YAWNING-TITAN` | no_wheel | ❌ | 100 | ✓ | 5,509,757 | $0.0321 | 722 | ✗ |  | ✓ |
| deepseek-v4-flash | `caltechlibrary_handprint` | stdlib_removed | ✅ | 100 | ✓ | 3,797,049 | $0.0246 | 1001 | ✓ |  |  |
| deepseek-v4-flash | `comtravo_ctparse` | stdlib_removed | ✅ | 21 |  | 212,043 | $0.0042 | 219 | ✓ | ✓ |  |
| deepseek-v4-flash | `djantic` | stdlib_removed | ✅ | 50 |  | 1,110,742 | $0.0111 | 247 | ✓ | ✓ |  |
| deepseek-v4-flash | `drf-openapi-tester` | no_wheel | ✅ | 45 |  | 1,265,632 | $0.0127 | 417 | ✓ | ✓ |  |
| deepseek-v4-flash | `encode_databases` | no_wheel | ✅ | 41 |  | 1,146,701 | $0.0111 | 298 | ✓ | ✓ |  |
| deepseek-v4-flash | `fcakyon_pywhisper` | stdlib_removed | ✅ | 50 |  | 1,664,879 | $0.0162 | 817 | ✓ |  |  |
| deepseek-v4-flash | `femueller_python-n26` | no_wheel | ✅ | 28 |  | 371,735 | $0.0055 | 133 | ✓ | ✓ |  |
| deepseek-v4-flash | `horazont_aioxmpp` | no_wheel | ❌ | 100 | ✓ | 3,664,450 | $0.0231 | 529 | ✗ |  | ✓ |
| deepseek-v4-flash | `jkwill87_stonky` | no_wheel | ✅ | 37 |  | 1,073,468 | $0.0131 | 253 | ✓ |  | ✓ |
| deepseek-v4-flash | `litl_backoff` | asyncio_change | ✅ | 45 |  | 1,328,663 | $0.0123 | 202 | ✓ |  | ✓ |
| deepseek-v4-flash | `mlem` | stdlib_removed | ❌ | 100 | ✓ | 4,380,060 | $0.0254 | 815 | ✗ |  | ✓ |
| deepseek-v4-flash | `multimeric_PandasSchema` | no_wheel | ✅ | 32 |  | 652,474 | $0.0082 | 136 | ✓ |  | ✓ |
| deepseek-v4-flash | `natelandau_obsidian-metadata` | no_wheel | ✅ | 86 |  | 4,983,398 | $0.0334 | 641 | ✓ |  |  |
| deepseek-v4-flash | `openedx-unsupported_bok-choy` | no_wheel | ❌ | 86 |  | 3,769,086 | $0.0250 | 1717 | ✗ |  |  |
| deepseek-v4-flash | `panini` | c_extension | ✅ | 69 |  | 2,677,615 | $0.0195 | 873 | ✓ | ✓ |  |
| deepseek-v4-flash | `poliastro` | stdlib_removed | ✅ | 66 |  | 1,628,738 | $0.0122 | 1965 | ✓ |  |  |
| deepseek-v4-flash | `python-acoustics_python-acoustics` | — | ✅ | 79 |  | 4,171,829 | $0.0280 | 529 | ✓ |  |  |
| deepseek-v4-flash | `python-consul_python-consul` | stdlib_removed | ✅ | 50 |  | 1,988,837 | $0.0173 | 476 | ✓ |  |  |
| deepseek-v4-flash | `rhasspy_gruut-ipa` | no_wheel | ✅ | 29 |  | 472,615 | $0.0063 | 156 | ✓ | ✓ |  |
| deepseek-v4-flash | `ripe-updater` | stdlib_removed | ✅ | 35 |  | 1,244,754 | $0.0121 | 134 | ✓ | ✓ |  |
| deepseek-v4-flash | `sassoftware_epdb` | stdlib_removed | ✅ | 23 |  | 498,156 | $0.0085 | 149 | ✓ |  |  |
| deepseek-v4-flash | `socialpoint-labs_sqlbucket` | no_wheel | ✅ | 20 |  | 378,990 | $0.0064 | 164 | ✓ |  |  |
| deepseek-v4-flash | `thomasgermain_pymultiMATIC` | — | ✅ | 51 |  | 1,273,226 | $0.0120 | 315 | ✓ | ✓ |  |
| deepseek-v4-flash | `tiangolo_typer-cli` | stdlib_removed | ✅ | 47 |  | 1,116,313 | $0.0112 | 314 | ✓ | ✓ |  |
| deepseek-v4-flash | `tudorelu_pyjuque` | no_wheel | ✅ | 50 |  | 1,544,014 | $0.0140 | 404 | ✓ |  | ✓ |
| deepseek-v4-flash | `wkeeling_selenium-wire` | no_wheel | ✅ | 98 |  | 5,224,453 | $0.0334 | 805 | ✓ |  |  |
| deepseek-v4-pro | `DarkCat09_python-aternos` | no_wheel | ❌ | 100 | ✓ | 5,484,109 | $0.0932 | 899 | ✗ | ✓ |  |
| deepseek-v4-pro | `MantisAI_hugie` | — | ✅ | 24 |  | 534,377 | $0.0232 | 152 | ✓ | ✓ |  |
| deepseek-v4-pro | `NimbleBoxAI_ChainFury` | — | ❌ | 100 | ✓ | 6,065,438 | $0.0814 | 607 | ✓ |  |  |
| deepseek-v4-pro | `SebRut_pygrocy` | — | ✅ | 31 |  | 805,813 | $0.0274 | 151 | ✓ |  |  |
| deepseek-v4-pro | `YAWNING-TITAN` | no_wheel | ❌ | 100 | ✓ | 7,630,702 | $0.0901 | 703 | ✗ |  | ✓ |
| deepseek-v4-pro | `caltechlibrary_handprint` | stdlib_removed | ✅ | 50 |  | 1,329,558 | $0.0373 | 710 | ✓ |  |  |
| deepseek-v4-pro | `comtravo_ctparse` | stdlib_removed | ✅ | 13 |  | 124,422 | $0.0096 | 198 | ✓ | ✓ |  |
| deepseek-v4-pro | `djantic` | stdlib_removed | ✅ | 30 |  | 980,285 | $0.0296 | 169 | ✓ | ✓ |  |
| deepseek-v4-pro | `drf-openapi-tester` | no_wheel | ✅ | 41 |  | 1,031,901 | $0.0276 | 270 | ✓ | ✓ |  |
| deepseek-v4-pro | `encode_databases` | no_wheel | ✅ | 46 |  | 1,705,328 | $0.0381 | 336 | ✓ | ✓ |  |
| deepseek-v4-pro | `fcakyon_pywhisper` | stdlib_removed | ✅ | 50 |  | 1,459,813 | $0.0391 | 695 | ✓ |  |  |
| deepseek-v4-pro | `femueller_python-n26` | no_wheel | ✅ | 44 |  | 1,352,667 | $0.0322 | 240 | ✓ | ✓ |  |
| deepseek-v4-pro | `horazont_aioxmpp` | no_wheel | ❌ | 100 | ✓ | 3,960,057 | $0.0574 | 676 | ✗ |  | ✓ |
| deepseek-v4-pro | `jkwill87_stonky` | no_wheel | ✅ | 50 |  | 1,758,534 | $0.0421 | 317 | ✓ |  | ✓ |
| deepseek-v4-pro | `litl_backoff` | asyncio_change | ✅ | 49 |  | 1,867,758 | $0.0434 | 519 | ✓ |  | ✓ |
| deepseek-v4-pro | `mlem` | stdlib_removed | ❌ | ? |  | 5,865,564 | $0.0761 | 1291 | ✓ |  | ✓ |
| deepseek-v4-pro | `multimeric_PandasSchema` | no_wheel | ✅ | 42 |  | 1,222,916 | $0.0325 | 207 | ✓ |  | ✓ |
| deepseek-v4-pro | `natelandau_obsidian-metadata` | no_wheel | ✅ | 69 |  | 3,419,655 | $0.0627 | 427 | ✓ |  | ✓ |
| deepseek-v4-pro | `openedx-unsupported_bok-choy` | no_wheel | ❌ | 66 |  | 2,167,384 | $0.0443 | 1306 | ✗ |  |  |
| deepseek-v4-pro | `panini` | c_extension | ❌ | 100 | ✓ | 3,391,646 | $0.0485 | 747 | ✓ | ✓ |  |
| deepseek-v4-pro | `poliastro` | stdlib_removed | ✅ | 66 |  | 2,667,841 | $0.0497 | 2082 | ✓ |  | ✓ |
| deepseek-v4-pro | `python-acoustics_python-acoustics` | — | ✅ | 78 |  | 2,833,725 | $0.0521 | 525 | ✓ |  |  |
| deepseek-v4-pro | `python-consul_python-consul` | stdlib_removed | ✅ | 53 |  | 2,383,597 | $0.0477 | 539 | ✓ |  |  |
| deepseek-v4-pro | `rhasspy_gruut-ipa` | no_wheel | ✅ | 50 |  | 1,085,853 | $0.0277 | 270 | ✓ | ✓ |  |
| deepseek-v4-pro | `ripe-updater` | stdlib_removed | ✅ | 30 |  | 831,280 | $0.0257 | 156 | ✓ | ✓ |  |
| deepseek-v4-pro | `sassoftware_epdb` | stdlib_removed | ✅ | 37 |  | 893,111 | $0.0233 | 132 | ✓ | ✓ |  |
| deepseek-v4-pro | `socialpoint-labs_sqlbucket` | no_wheel | ✅ | 26 |  | 458,356 | $0.0215 | 151 | ✓ |  |  |
| deepseek-v4-pro | `thomasgermain_pymultiMATIC` | — | ✅ | 70 |  | 2,142,314 | $0.0412 | 398 | ✓ |  | ✓ |
| deepseek-v4-pro | `tiangolo_typer-cli` | stdlib_removed | ✅ | 61 |  | 1,812,865 | $0.0417 | 521 | ✓ | ✓ |  |
| deepseek-v4-pro | `tudorelu_pyjuque` | no_wheel | ✅ | 50 |  | 1,638,369 | $0.0458 | 561 | ✓ |  | ✓ |
| deepseek-v4-pro | `wkeeling_selenium-wire` | no_wheel | ❌ | 100 | ✓ | 4,276,418 | $0.0614 | 711 | ✗ |  |  |
| gemini-3.5-flash | `NimbleBoxAI_ChainFury` | — | ✅ | 29 |  | 1,248,034 | $1.1180 | 569 | ✓ | ✓ |  |
| gemini-3.5-flash | `YAWNING-TITAN` | no_wheel | ❌ | 58 |  | 4,410,023 | $2.3740 | 1235 | ✗ |  |  |
| gemini-3.5-flash | `caltechlibrary_handprint` | stdlib_removed | ✅ | 28 |  | 1,756,085 | $1.0618 | 717 | ✓ |  |  |
| gemini-3.5-flash | `horazont_aioxmpp` | no_wheel | ❌ | 25 |  | 2,887,442 | $2.0806 | 1011 | ✗ | ✓ |  |
| gemini-3.5-flash | `mlem` | stdlib_removed | ❌ | 66 |  | 4,454,683 | $1.9871 | 1505 | ✗ |  |  |
| gemini-3.5-flash | `openedx-unsupported_bok-choy` | no_wheel | ✅ | 30 |  | 588,358 | $0.1530 | 296 | ✓ | ✓ |  |
| gemini-3.5-flash | `panini` | c_extension | ❌ | 33 |  | 2,924,670 | $2.3044 | 1191 | ✗ | ✓ |  |
| gemini-3.5-flash | `poliastro` | stdlib_removed | ❌ | 4 |  | 78,952 | $0.5744 | 496 | ✗ |  |  |
| gemini-3.5-flash | `python-acoustics_python-acoustics` | — | ✅ | 64 |  | 5,146,814 | $1.6196 | 1016 | ✓ |  |  |
| gemini-3.5-flash | `thomasgermain_pymultiMATIC` | — | ❌ | ? |  | 0 | — | 254 | ✗ |  |  |
| gemini-3.5-flash | `tiangolo_typer-cli` | stdlib_removed | ✅ | 49 |  | 2,402,132 | $0.4625 | 386 | ✓ |  |  |
| gemini-3.5-flash | `tudorelu_pyjuque` | no_wheel | ✅ | 63 |  | 5,506,476 | $1.8238 | 1192 | ✓ |  | ✓ |
| gemini-3.5-flash | `wkeeling_selenium-wire` | no_wheel | ❌ | 24 |  | 602,775 | $0.1607 | 395 | ✗ |  |  |

---

> ✅ resolved  ❌ not resolved  ✓ yes  ✗ no  — n/a
