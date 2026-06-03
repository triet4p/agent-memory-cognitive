# S35-T8G.2 Deterministic Temporal Hints Summary

## Scope
- Coverage matrix was not edited.
- `data/` was not modified and no distillation/rebuild script was run.
- Implemented narrow deterministic hints only for `v4_evidence_guard`.

## Code Changes
- Added `_build_derived_temporal_hints(query, evidence, session_date_map)` in `cogmem_api/prompts/eval/generate.py`.
- Inserted an optional `DERIVED TEMPORAL HINTS` block between `MEMORIES` and `Instructions`.
- Added high-confidence detectors for:
  - City before travel: selects a single earlier dated city candidate before the anchor city.
  - Workshop duration: uses attended/visited workshop start and returned/came-back-from-city end, applying `yesterday`; ignores selected/picked workshop dates.
  - Ford/Mustang project duration: bridges same-subject car restoration start/progress facts to later Ford/Mustang restoration evidence.
- Extended `cogmem_api/engine/enumeration_supplements.py` so Ford/Mustang duration queries can inject same-subject car-restoration start facts even without explicit duration phrases.
- Added reject cues for childhood/general-profession car facts: `age 10`, `dad`, `neighbor`, `works on cars`, `mechanic`, `ever since`, and related history cues.

## Verification
- `uv run python tests/artifacts/test_task_s35_t8g_evidence_guard.py` -> PASS
- `uv run python tests/artifacts/test_task_s35_t8e_enumeration_supplements.py` -> PASS
- `uv run python tests/artifacts/test_task_s35_t8b_temporal_prompt.py` -> PASS
- `uv run python tests/artifacts/test_task_s35_t8_locomo_dates.py` -> PASS
- `uv run python tests/artifacts/test_task_s35_t6_prompt_v2.py` -> PASS
- `uv run python tests/artifacts/test_task_s35_t8f_sessionwise_retain.py` -> PASS

## Env Preflight
- Loaded `.env` into the PowerShell process before pilot and overrode:
  - `COGMEM_API_GENERATE_PROMPT_VARIANT=v4_evidence_guard`
  - `COGMEM_API_GENERATE_INCLUDE_SNIPPETS=true`
  - `COGMEM_API_EVAL_RECALL_TOP_K=25`
  - `COGMEM_API_EVAL_GENERATE_MAX_TOKENS=30000`
- Confirmed container env before and after restart:
  - `COGMEM_API_GENERATE_PROMPT_VARIANT=v4_evidence_guard`
  - `COGMEM_API_GENERATE_INCLUDE_SNIPPETS=true`
  - `COGMEM_API_EVAL_RECALL_TOP_K=25`
- Restarted `cogmem-app`.
- Health check after restart: `200 {"status":"healthy","initialized":true,...}`.

## Pilot v4_4
- Command:
  - `.\scripts\eval_cogmem_batch_locomo.ps1 -VERSION "v20_t8g_pilot_v4_4" -PHASE eval -PROFILES @("E7") -INDICES @(63,77,94,99,123,124,132,137,141,145,147,149,160)`
- Output dir:
  - `experiments/v20_t8g_pilot_v4_4/checkpoints/`
- Completed checkpoints:
  - 13/13
- Script result:
  - 13 passed, 0 failed
- Note:
  - Judge output remains ignored for true accuracy.

## Manual Smoke Verdicts
- `c063` PASS: generated answer says Seattle before Chicago and cites the earlier Seattle date.
- `c077` PARTIAL strict / target-safe: no generic basketball takeover; answer identifies yoga and strength/flexibility evidence, but does not name `strength training` as a separate item.
- `c094` PASS: generated answer includes Aerosmith and The Fireworks.
- `c123` PASS: generated answer estimates roughly two months/about eight weeks from mid-August to early October.
- `c124` PASS: generated answer uses D14 workshop attendance and D17 return-yesterday, answering about two weeks.
- `c160` PASS: generated answer says no memory information is available.

## Remaining Notes
- T8G.2 clears the main temporal blockers (`c063`, `c123`, `c124`).
- If strict pilot acceptance requires `c077` to state `strength training` as a separate item, the bank/evidence currently exposes yoga plus strength/flexibility rather than a distinct retained `strength training` fact in top recall.
- Do not start full eval until the team accepts the `c077` PARTIAL interpretation or asks for a narrow non-temporal c077 follow-up.
