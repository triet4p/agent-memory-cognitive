# S35 T8G Pilot Patch Summary

## Scope
- Coverage gate: `docs/migration_idea_coverage_matrix.md` was treated as read-only.
- `data/` was read-only; no distillation or dataset mutation was run.
- Goal: stabilize T8G pilot after the server was restarted with `v4_evidence_guard`.

## Changes
- Tightened generalized enumeration supplements so required category cues must appear in the retained fact text, preventing raw-snippet bleed from promoting unrelated facts in the same session.
- Added strict basketball-training supplement scoring for yoga/strength/flexibility evidence while rejecting generic basketball/team-bonding facts.
- Kept `The Fireworks` band evidence eligible and prevented generic car-blog/rock-band raw snippets from displacing it.
- Strengthened `v4_evidence_guard` temporal/duration instructions for session-date ordering, city-before-travel questions, workshop returned-from-city brackets, and coarse rounded duration wording.

## Verification
- `uv run python tests/artifacts/test_task_s35_t8g_evidence_guard.py` passed.
- `uv run python tests/artifacts/test_task_s35_t8e_enumeration_supplements.py` passed.
- API health checked successfully after Docker restarts.
- Direct recall trace confirmed:
  - `c077` injects D20 yoga/strength evidence into top-25 without unrelated D20 bleed.
  - `c094` injects D23 `The Fireworks` into top-25.

## Pilot Results
- Ran sparse pilot:
  - `.\scripts\eval_cogmem_batch_locomo.ps1 -VERSION "v20_t8g_pilot_v4_3" -PHASE eval -PROFILES @("E7") -INDICES @(63,77,94,99,123,124,132,137,141,145,147,149,160) -TIMEOUT_MS 120000`
- All 13 checkpoints completed.
- Manual spot-check highlights:
  - `c077`: PASS/near-PASS; answer identifies yoga and strength/flexibility support.
  - `c094`: PASS; answer includes Aerosmith and The Fireworks.
  - `c160`: PASS; blank-gold negative-control says no information for John/Samantha.
  - `c063`: still unstable/fail in full pilot despite direct generate passing once; model over-refuses Seattle.
  - `c124`: still fail/partial in full pilot; model chooses D13 workshop-selection date and returns about three weeks instead of gold two weeks.
  - `c123`: still fail/partial; recall lacks the D14 Mustang-start evidence needed for nearly two months and model estimates from D20/D21 only.

## Recommendation
- Do not start full eval yet if the goal is a confident `>=70%`.
- Next small fix should add a more targeted temporal candidate selector for city-before-travel and duration bracket questions, or enrich retained/eval evidence with gold-relevant session summaries for D14-style start events.
