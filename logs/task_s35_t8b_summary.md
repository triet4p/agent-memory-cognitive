# S35-T8B Summary — Minimal Temporal Prompt Variant

## What changed

- Added `build_generation_prompt_v3_temporal`.
- Added dispatch aliases: `v3_temporal`, `v3-temporal`, and `v3`.
- Kept the variant narrow: v2 plus one temporal-anchor rule with a Chicago example.

## Why

Some multi-hop failures have the right evidence in recall but require identifying
an anchor event first and comparing candidate events against that date. This phase
tests that one behavior without adding brand or counterfactual prompt rules.

## Verification

All commands passed:

- `uv run python tests/artifacts/test_task_s35_t6_prompt_v2.py`
- `uv run python tests/artifacts/test_task_s35_t8b_temporal_prompt.py`
