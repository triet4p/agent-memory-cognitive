# S35-T8 Probe Summary — Sparse LoCoMo Cases

## What changed

- Added `-INDICES @(...)` to `scripts/eval_cogmem_batch_locomo.ps1`.
- Sparse probes now run only listed QA indices instead of a contiguous range.

## Why

The S35-T8 measurement plan needs exactly 14 known failures plus a small PASS
spot-check set, without re-running a large QA range or increasing top-k.

## Verification

All commands passed:

- `uv run python tests/artifacts/test_task_s35_t8_probe_subset.py`

## Probe run

Command:

- `pwsh -NoProfile -Command "& { .\scripts\eval_cogmem_batch_locomo.ps1 -PHASE eval -VERSION v20_t8a_probe -PROFILES @('E7') -INDICES @(32,37,53,55,59,62,63,69,78,79,81,86,87,0,14,17,52,64) -TIMEOUT_MS 180000 }"`
- `c015` was run separately first because PowerShell `-File` only bound the first array value.

Outputs:

- `experiments/v20_t8a_probe/checkpoints/E7_full_c{000,014,015,017,032,037,052,053,055,059,062,063,064,069,078,079,081,086,087}.json`

Manual read:

| Case | Baseline label | Probe result | Note |
|---|---|---|---|
| c015 | FAIL | PASS | Counterfactual answer says likely no, with grounded support. |
| c032 | REVIEW | FAIL | Still over-conservative on religion. |
| c037 | REVIEW | FAIL | Still misses gold traits; recall/session issue remains. |
| c053 | FAIL | FAIL | Still says outdoor brand name not provided; candidate disambiguation needed. |
| c055 | FAIL | PASS-ish | Resolves `next month` from 2023-07-16 to August 2023. |
| c059 | REVIEW | PASS | Computes 2023-07-16 to 2023-08-09 as ~3 weeks. |
| c062 | REVIEW | FAIL | Still generic local organization, no Good Sports. |
| c063 | FAIL | FAIL | Still fails anchor chain; says no information. |
| c069 | REVIEW | FAIL | Suggests marketing/charity/mentorship, not basketball coach. |
| c078 | FAIL | FAIL | Still only yoga/PT/practice; source/gold mismatch likely. |
| c079 | FAIL | PARTIAL | Infers early-to-mid 2023, not May 2023. |
| c081 | REVIEW | PASS | Resolves Harry Potter trivia to 2023-08-02 / August 2023. |
| c086 | REVIEW | PASS | Suggests travel journaling/blog. |
| c087 | FAIL | FAIL | Still source-absent for Star Wars Ireland locations. |

PASS spot-check regressions:

- c017 old PASS -> probe misses `mountains`.
- c052 old PASS -> probe misses `California`.
- c064 old PASS -> probe misses `New York`.

Decision:

- Do not add T8C/T8D yet under the stop rule. Date plumbing helps date-derived cases, but the current generation behavior regressed enumeration-style PASS cases.

## T8B probe run

Environment confirmed:

- `COGMEM_API_GENERATE_PROMPT_VARIANT="v3_temporal"`
- `COGMEM_API_EVAL_RECALL_TOP_K=25`
- `COGMEM_API_LLM_MODEL=minimax-m2.7`

Command:

- `pwsh -NoProfile -Command "& { .\scripts\eval_cogmem_batch_locomo.ps1 -PHASE eval -VERSION v20_t8b_probe -PROFILES @('E7') -INDICES @(15,32,37,53,55,59,62,63,69,78,79,81,86,87,0,14,17,52,64) -TIMEOUT_MS 180000 }"`
- `c063` initially hit a transient `/generate` 500 and no checkpoint was written.
- Reran `c063` only with `TIMEOUT_MS 240000`; checkpoint was written successfully.

Outputs:

- `experiments/v20_t8b_probe/checkpoints/E7_full_c{000,014,015,017,032,037,052,053,055,059,062,063,064,069,078,079,081,086,087}.json`

Manual read:

| Case | Baseline label | T8B result | Note |
|---|---|---|---|
| c015 | FAIL | FAIL | More conservative than T8A; refuses the counterfactual instead of answering likely no. |
| c032 | REVIEW | FAIL | Still says no evidence Caroline is religious. |
| c037 | REVIEW | FAIL | Still misses gold traits; retrieved/used traits differ from gold. |
| c053 | FAIL | FAIL | Still says outdoor brand name not provided, despite judge marking correct. |
| c055 | FAIL | PASS-ish | Resolves `next month` from 2023-07-16 to August 2023, but not "early August". |
| c059 | REVIEW | PASS | Computes July 16 to August 9 as about three weeks. |
| c062 | REVIEW | FAIL | Still generic local organization, no Good Sports. |
| c063 | FAIL | PASS | Temporal anchor rule works here: identifies Chicago anchor and chooses Seattle before it. |
| c069 | REVIEW | PARTIAL | Mentions coaching/mentoring as one option, but not as a decisive answer. |
| c078 | FAIL | FAIL | Still source/gold mismatch; only yoga/PT/practice in memory. |
| c079 | FAIL | PARTIAL | Infers early 2023, not May 2023. |
| c081 | REVIEW | PASS | Resolves Harry Potter trivia to 2 August 2023 / August 2023. |
| c086 | REVIEW | PASS | Suggests travel journal/blog, plus extra model-kit angle. |
| c087 | FAIL | FAIL | Still source-absent for Star Wars Ireland locations. |

PASS spot-checks:

| Case | Baseline label | T8B result | Note |
|---|---|---|---|
| c000 | PASS | PASS | Still answers job loss + dance passion. |
| c014 | PASS | PASS | Still answers counseling / mental health for trans people. |
| c017 | PASS | FAIL | Still misses `mountains`; only beach + forest. |
| c052 | PASS | FAIL | Still misses `California`; only Smoky Mountains + London. |
| c064 | PASS | FAIL | Still misses `New York`; only Seattle + Chicago. |

Decision:

- T8B is useful for the targeted temporal-anchor pattern (`c063`) and preserves the T8A date-arithmetic wins (`c055`, `c059`, `c081`).
- Do not implement T8C/T8D yet. The stop rule is triggered because enumeration-style known PASS cases still regress (`c017`, `c052`, `c064`), and T8C/T8D would add more prompt pressure before fixing the list-completeness problem.
- Next safer step should be an answer-side completeness guard for list/enumeration questions, or a rerank/query expansion probe for missing named entities, not brand/counterfactual prompt expansion.
