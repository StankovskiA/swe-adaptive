# SWE-Adaptive Evaluation Results

Generated: 2026-06-30 09:24 UTC

---

## Overall resolution rate

| Model | Resolved | Total | Rate | Scoring Errors | Timeouts |
|-------|----------|-------|------|----------------|----------|
| `deepseek__deepseek-v4-flash` | 27 | 31 | 87.1% | 0 | 0 |
| `deepseek__deepseek-v4-pro` | 23 | 31 | 74.2% | 0 | 0 |
| `gemini__gemini-3.5-flash` | 6 | 13 | 46.2% | 0 | 0 |

---

## By breaking change type

| Type | `deepseek__deepseek-v4-flash` | `deepseek__deepseek-v4-pro` | `gemini__gemini-3.5-flash` |
|------|---|---|---|
| asyncio_change | 1/1 | 1/1 | — |
| c_extension | 1/1 | 0/1 | 0/1 |
| no_wheel | 11/14 | 9/14 | 2/5 |
| stdlib_removed | 9/10 | 9/10 | 2/4 |

---

## Per-instance results

| Instance | Type | deepseek__deepseek-v4-flash | deepseek__deepseek-v4-pro | gemini__gemini-3.5-flash |
|----------|------|------|------|------|
| `DarkCat09_python-aternos` | no_wheel | ✅ | ❌ | — |
| `MantisAI_hugie` |  | ✅ | ✅ | — |
| `NimbleBoxAI_ChainFury` |  | ✅ | ❌ | ✅ |
| `SebRut_pygrocy` |  | ✅ | ✅ | — |
| `YAWNING-TITAN` | no_wheel | ❌ | ❌ | ❌ |
| `caltechlibrary_handprint` | stdlib_removed | ✅ | ✅ | ✅ |
| `comtravo_ctparse` | stdlib_removed | ✅ | ✅ | — |
| `djantic` | stdlib_removed | ✅ | ✅ | — |
| `drf-openapi-tester` | no_wheel | ✅ | ✅ | — |
| `encode_databases` | no_wheel | ✅ | ✅ | — |
| `fcakyon_pywhisper` | stdlib_removed | ✅ | ✅ | — |
| `femueller_python-n26` | no_wheel | ✅ | ✅ | — |
| `horazont_aioxmpp` | no_wheel | ❌ | ❌ | ❌ |
| `jkwill87_stonky` | no_wheel | ✅ | ✅ | — |
| `litl_backoff` | asyncio_change | ✅ | ✅ | — |
| `mlem` | stdlib_removed | ❌ | ❌ | ❌ |
| `multimeric_PandasSchema` | no_wheel | ✅ | ✅ | — |
| `natelandau_obsidian-metadata` | no_wheel | ✅ | ✅ | — |
| `openedx-unsupported_bok-choy` | no_wheel | ❌ (empty patch) | ❌ (empty patch) | ✅ |
| `panini` | c_extension | ✅ | ❌ | ❌ |
| `poliastro` | stdlib_removed | ✅ | ✅ | ❌ (empty patch) |
| `python-acoustics_python-acoustics` |  | ✅ | ✅ | ✅ |
| `python-consul_python-consul` | stdlib_removed | ✅ | ✅ | — |
| `rhasspy_gruut-ipa` | no_wheel | ✅ | ✅ | — |
| `ripe-updater` | stdlib_removed | ✅ | ✅ | — |
| `sassoftware_epdb` | stdlib_removed | ✅ | ✅ | — |
| `socialpoint-labs_sqlbucket` | no_wheel | ✅ | ✅ | — |
| `thomasgermain_pymultiMATIC` |  | ✅ | ✅ | ❌ (empty patch) |
| `tiangolo_typer-cli` | stdlib_removed | ✅ | ✅ | ✅ |
| `tudorelu_pyjuque` | no_wheel | ✅ | ✅ | ✅ |
| `wkeeling_selenium-wire` | no_wheel | ✅ | ❌ | ❌ (empty patch) |

---

## Token and cost summary

| Model | Total input tokens | Total output tokens | Total cost (USD) | Avg time (s) |
|-------|--------------------|---------------------|------------------|--------------|
| `deepseek__deepseek-v4-flash` | 65,127,159 | 488,172 | $0.5077 | 505 |
| `deepseek__deepseek-v4-pro` | 72,668,997 | 512,659 | $1.3735 | 538 |
| `gemini__gemini-3.5-flash` | 30,456,115 | 1,550,329 | $15.7201 | 789 |

---

## Mean cost on shared instances (n=13)

| Model | Mean cost/instance (USD) | Mean input tokens | Mean output tokens |
|-------|--------------------------|-------------------|--------------------|
| `deepseek__deepseek-v4-flash` | $0.0214 | 3,136,480 | 19,961 |
| `deepseek__deepseek-v4-pro` | $0.0559 | 3,500,745 | 20,938 |
| `gemini__gemini-3.5-flash` | $1.2092 | 2,342,778 | 119,256 |

---

> ✅ resolved  ❌ not resolved  ⚠ scoring error  ⏱ timed out  — not run
