# S35-T8E Probe Summary

## Run

Environment:

- `COGMEM_API_GENERATE_PROMPT_VARIANT="v3_temporal_list"`
- `COGMEM_API_EVAL_RECALL_TOP_K=25`
- `COGMEM_API_LLM_MODEL=minimax-m2.7`

Command:

- `pwsh -NoProfile -Command "& { .\scripts\eval_cogmem_batch_locomo.ps1 -PHASE eval -VERSION v20_t8e_probe -PROFILES @('E7') -INDICES @(15,32,37,53,55,59,62,63,69,78,79,81,86,87,0,14,17,52,64) -TIMEOUT_MS 240000 }"`

Outputs:

- `experiments/v20_t8e_probe/checkpoints/E7_full_c{000,014,015,017,032,037,052,053,055,059,062,063,064,069,078,079,081,086,087}.json`

## Manual Read

| Case | Baseline label | T8E result | Note |
|---|---|---|---|
| c015 | FAIL | PASS | Answers likely no, with explicit uncertainty and grounded support. |
| c032 | REVIEW | FAIL | Still says Caroline would not be considered religious. |
| c037 | REVIEW | FAIL | Judge marks correct, but answer misses gold traits: thoughtful/authentic/driven. |
| c053 | FAIL | FAIL | Still refuses to name Under Armour; says company unspecified. |
| c055 | FAIL | PASS-ish | Resolves Seattle game to August 2023, but not "early August". |
| c059 | REVIEW | PASS | Computes July 16 to August 9 as 24 days, about three weeks. |
| c062 | REVIEW | FAIL | Still no Good Sports; says no specific prominent charity organization. |
| c063 | FAIL | PASS | Temporal-anchor chain works: identifies Seattle before Chicago. |
| c069 | REVIEW | PARTIAL | Includes mentoring/coaching, but not as a decisive answer. |
| c078 | FAIL | FAIL | Still only yoga/PT/rehab; gold exercises remain source-absent. |
| c079 | FAIL | PARTIAL | Infers early 2023, not May 2023. |
| c081 | REVIEW | PASS | Resolves Harry Potter trivia to 2 August 2023 / August 2023. |
| c086 | REVIEW | PASS | Gives travel writing / travel blog. |
| c087 | FAIL | FAIL | Still source-absent for Star Wars Ireland locations. |

PASS spot-checks:

| Case | Baseline label | T8E result | Note |
|---|---|---|---|
| c000 | PASS | PASS | Still answers job loss + dance passion. |
| c014 | PASS | PASS | Still answers counseling / mental health for trans people. |
| c017 | PASS | PASS | Recovered beach, forest, and mountains. |
| c052 | PASS | PASS | Recovered Smoky Mountains, London, and California; includes extra UK/conference note. |
| c064 | PASS | PASS | Recovered Seattle, Chicago, and New York/NYC. |

## Recall Window Check

The T8E recall windows for the previous PASS regressions now include the missing
evidence:

- `c017`: mountains at rank 19, forest at rank 6/15, beach at rank 1/5/11.
- `c052`: California at ranks 21/22/25, London at ranks 6/24, Smoky Mountains at ranks 1/10/11.
- `c064`: NYC at rank 24, Chicago at ranks 4/23, Seattle at ranks 2/5/25.

## Decision

- Keep T8E. It fixes the enumeration/list regressions that blocked further prompt work and preserves T8B temporal wins.
- Do not merge T8C/T8D into T8E yet. The next safe step is to probe one isolated T8C brand/entity disambiguation rule against `c053` and `c062`, using the same 5 PASS spot checks.
- T8D counterfactual is lower priority because T8E already recovers `c015` without a dedicated counterfactual rule.
