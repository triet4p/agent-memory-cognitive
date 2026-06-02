# S35-T8F Summary

Date: 2026-06-02

## What changed

- Added [scripts/retain_locomo_bank_sessions.py](/f:/ai-ml/agent-memory-cognitive/scripts/retain_locomo_bank_sessions.py) to retain one LoCoMo conversation session-by-session into a target bank.
- Added [tests/artifacts/test_task_s35_t8f_sessionwise_retain.py](/f:/ai-ml/agent-memory-cognitive/tests/artifacts/test_task_s35_t8f_sessionwise_retain.py) to verify the helper enumerates ordered, unique LoCoMo session payloads for the remaining 2-bank scope.

## Why

- The original `scripts.eval_cogmem --pipeline recall` sends the whole LoCoMo conversation in one retain request.
- In [cogmem_api/engine/retain/orchestrator.py](/f:/ai-ml/agent-memory-cognitive/cogmem_api/engine/retain/orchestrator.py), facts are written only after extraction finishes for the full request batch, so banks stay at `0 fact` for a long time and progress is opaque.
- The session-wise helper exposes progress per `D1`, `D2`, ... and avoids one monolithic retain call.

## Verification

- `uv run python tests/artifacts/test_task_s35_t8f_sessionwise_retain.py`
- `conv-50` session-wise retain completed: `30/30` sessions, `total_units=30`.
- `conv-47` session-wise retain reached `D29/31` before manual stop.
- All retain/eval background processes were stopped before handoff.

## Current runtime state

- `COGMEM_locomo_conv-50` is fully retained session-wise.
- `COGMEM_locomo_conv-47` is only partially retained because the run was stopped after `D29`.
- Future rerun for `conv-47` should start with `--delete-bank` to avoid mixing partial and fresh state.
