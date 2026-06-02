# S35-T8G Summary - Evidence Guard Accuracy Lift

## What changed

- Added prompt variant `v4_evidence_guard` behind `COGMEM_API_GENERATE_PROMPT_VARIANT=v4_evidence_guard`.
- Kept legacy, `v2`, `v3_temporal`, and `v3_temporal_list` dispatch paths intact.
- Added query-relevant snippet windows for generation source lines, prioritizing query terms, named entities, list-category aliases, and explicit duration phrases.
- Added strict causal negative-control wording for `why` questions to prevent entity-swapped or tangential causal inference.
- Added explicit-duration wording for `how long` / `take` / `for before` questions so stated durations in facts/snippets win before date arithmetic.
- Extended enumeration recall supplements beyond locations to bands, books/authors, games, activities/events, gifts/items, collectibles, family members, sports/exercises, classes, beers, pet tricks, shows/movies, instruments, and countries/cities.
- Added a special sports/exercise guard for "supplement basketball training" style queries so generic basketball facts are not boosted unless they mention add-on exercises such as yoga or strength training.

## Why

Manual T8E results showed several failures were not pure retain misses. The new changes target two failure families:

- Recall window misses where a retained item exists but is not in the final top-k, such as `The Fireworks` for band enumeration.
- Generation misses where the right evidence is present but hidden in irrelevant snippet prefixes, over-refused, or treated with weak guards, such as explicit Mustang duration evidence and temporal/location chains.

## Verification

All commands passed:

- `uv run python tests/artifacts/test_task_s35_t8g_evidence_guard.py`
- `uv run python tests/artifacts/test_task_s35_t8e_enumeration_supplements.py`
- `uv run python tests/artifacts/test_task_s35_t8b_temporal_prompt.py`
- `uv run python tests/artifacts/test_task_s35_t8_locomo_dates.py`
- `uv run python tests/artifacts/test_task_s35_t8e_3bank_checkpoints.py`
- `uv run python tests/artifacts/test_task_s35_t8e_full_checkpoint_completeness.py`
- `uv run python tests/artifacts/test_task_s35_t6_prompt_v2.py`

## Deferred full eval

Full `c000..c160` live eval was not run in this implementation pass because the already-running localhost server must be restarted to load the new prompt/supplement code. Running against the existing process would risk producing a mislabeled T8G result.

Suggested command after restarting `uv run cogmem-api`:

```powershell
$env:COGMEM_API_GENERATE_PROMPT_VARIANT = "v4_evidence_guard"
$env:COGMEM_API_GENERATE_INCLUDE_SNIPPETS = "true"
.\scripts\eval_cogmem_batch_locomo.ps1 -VERSION "v20_t8g_evidence_guard" -PHASE eval -PROFILES @("E7") -START_INDEX 0 -END_INDEX 160
```

Manual verdicting should still use generated answers directly, not judge correctness.
