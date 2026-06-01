# S35-T8E Summary — Enumeration Completeness Guard

## What changed

- Added `cogmem_api/engine/enumeration_supplements.py`.
- Added recall-side supplements for obvious list/location enumeration queries.
- Supplements use retained facts only and replace low-ranked tail items; they do not increase the final top-k window.
- Added `build_generation_prompt_v3_temporal_list` behind `COGMEM_API_GENERATE_PROMPT_VARIANT=v3_temporal_list`.
- Kept T8B `v3_temporal` isolated and unchanged.
- Updated `scripts/eval_cogmem.py` to load local `.env` with `override=False`, so eval knobs such as `COGMEM_API_EVAL_RECALL_TOP_K=25` are honored without clobbering explicit shell env.

## Why

T8B fixed the temporal-anchor pattern (`c063`) but list-style PASS spot checks
regressed because relevant facts were outside the actually used eval window.
The immediate root cause was that the batch eval process was defaulting to
`top_k=10` instead of the `.env` value `25`; a secondary guard now helps
enumeration queries keep retained location/list facts inside the final window.

## Verification

All commands passed:

- `uv run python tests/artifacts/test_task_s35_t8e_enumeration_supplements.py`
- `uv run python tests/artifacts/test_task_s35_t8b_temporal_prompt.py`
- `uv run python tests/artifacts/test_task_s35_t8_locomo_dates.py`
- `uv run python tests/artifacts/test_task_s35_t6_prompt_v2.py`
- `uv run python scripts/locomo_mapping_dryrun.py`

Additional check:

- With `COGMEM_API_EVAL_RECALL_TOP_K` removed from process env, importing
  `scripts.eval_cogmem` and building the E7 recall payload returned `top_k=25`
  from `.env`.

## Notes

- Existing API server processes must be restarted to pick up the engine/prompt
  code changes.
- To probe the new prompt guard, run the server with
  `COGMEM_API_GENERATE_PROMPT_VARIANT=v3_temporal_list`.
