# S35-T7 Summary — Pass 2 Role Policy

## What changed

- Added Pass 2 role resolution for transcript-style inputs with named speakers.
- Kept default chat behavior: if `user` exists, Pass 2 still processes only `user`.
- Added `human` / `participant` pseudo-role expansion for non-machine speaker roles.
- Preserved speaker attribution in inferred/custom speaker chunks via `[role]: ...`.
- Updated the Pass 2 prompt to tell the extractor to preserve named speakers.

## Why

LoCoMo distilled messages use speaker names (`Jon`, `Gina`, etc.) as roles. The old
Pass 2 path only matched `role == "user"`, producing zero Pass 2 chunks for LoCoMo
and similar real-world multi-speaker transcripts.

## Verification

All commands passed:

- `uv run python tests/artifacts/test_task781_chunking.py`
- `uv run python tests/artifacts/test_task782_two_pass_extraction.py`
- `uv run python tests/artifacts/test_task_s35_t7_pass2_role_policy.py`
- `uv run python scripts/locomo_mapping_dryrun.py`

LoCoMo spot measurement after the fix:

- First QA of each conversation now resolves named speaker roles and produces non-zero Pass 2 chunks.
- Counts: `c000=369`, `c014=419`, `c048=680`, `c094=568`, `c132=689`.
