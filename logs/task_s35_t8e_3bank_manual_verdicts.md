# S35-T8E 3-Bank Manual Verdicts

## Run

- Command: `pwsh -NoProfile -Command "& { .\scripts\eval_cogmem_batch_locomo.ps1 -PHASE eval -VERSION v20_t8e_3bank -PROFILES @('E7') -START_INDEX 0 -END_INDEX 93 -TIMEOUT_MS 240000 }"`
- Scope: LoCoMo QA indices `0..93` over retained banks `conv-30`, `conv-26`, and `conv-43`.
- Prompt variant: `COGMEM_API_GENERATE_PROMPT_VARIANT=v3_temporal_list`.
- Recall top-k: `COGMEM_API_EVAL_RECALL_TOP_K=25`.
- `c033` initially lacked a checkpoint after a judge 500; it was rerun separately and completed.

## Scoring Policy

- Manual semantic comparison only: `generated_answer` vs `gold_answer`.
- `judge.correct`, `judge.score`, and `judge.reason` were ignored.
- `PASS`: final answer contains the gold answer or a semantically equivalent answer.
- `PARTIAL`: answer contains a relevant correct piece but is incomplete, under-specific, or non-decisive.
- `FAIL`: wrong answer, missing required gold item(s), over-refusal, or hallucination for blank-gold unanswerable cases.

## Result

- Strict PASS: `49/94` = `52.1%`.
- PARTIAL: `4/94` = `4.3%`.
- PASS + PARTIAL: `53/94` = `56.4%`.
- FAIL: `41/94` = `43.6%`.

## Category Breakdown

| Category | Total | PASS | PARTIAL | FAIL |
|---|---:|---:|---:|---:|
| causal | 7 | 4 | 0 | 3 |
| multi-hop | 5 | 2 | 2 | 1 |
| preference | 11 | 10 | 0 | 1 |
| single-hop | 62 | 31 | 1 | 30 |
| temporal | 9 | 2 | 1 | 6 |

## Verdict Lists

PASS:

- `c000`, `c002`, `c003`, `c006`, `c007`, `c008`, `c010`, `c011`, `c012`, `c014`, `c015`, `c017`, `c018`, `c019`, `c020`, `c021`, `c023`, `c024`, `c026`, `c028`, `c029`, `c033`, `c034`, `c036`, `c038`, `c040`, `c041`, `c042`, `c043`, `c044`, `c045`, `c046`, `c047`, `c052`, `c057`, `c058`, `c059`, `c060`, `c064`, `c070`, `c071`, `c072`, `c074`, `c081`, `c084`, `c086`, `c089`, `c090`, `c091`

PARTIAL:

- `c031`: has rainbow flag and related trans symbols, but does not cleanly answer "transgender symbol".
- `c055`: resolves Seattle game to August 2023, but not "early August".
- `c069`: includes mentoring/coaching as one option, but does not answer decisively as basketball coach.
- `c079`: infers early 2023, but not May 2023.

FAIL:

- `c001`, `c004`, `c005`, `c009`, `c013`, `c016`, `c022`, `c025`, `c027`, `c030`, `c032`, `c035`, `c037`, `c039`, `c048`, `c049`, `c050`, `c051`, `c053`, `c054`, `c056`, `c061`, `c062`, `c063`, `c065`, `c066`, `c067`, `c068`, `c073`, `c075`, `c076`, `c077`, `c078`, `c080`, `c082`, `c083`, `c085`, `c087`, `c088`, `c092`, `c093`

## High-Signal Notes

- T8E still helped the prior list regressions: `c017`, `c052`, and `c064` are PASS in the full 3-bank run.
- The temporal-anchor target `c063` was non-deterministic: it passed in the sparse T8E probe but failed in the full 94 run with "no information".
- Main remaining failure pattern is not top-k size; many failures are missing specific gold items from the answer despite broad recall evidence.
- Several blank-gold negative controls still hallucinate answers: notably `c013`, `c092`, and `c093`.
- Brand/entity disambiguation remains unresolved: `c053`, `c054`, and `c062` are still fail/partial style cases.
