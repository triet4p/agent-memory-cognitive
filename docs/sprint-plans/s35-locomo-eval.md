# S35 — LoCoMo Evaluation (baseline + cognitive-node ablation)

Status: 🔄 In progress (T1+T2 done 2026-05-30; T3 retain awaiting manual run)
Methodology: [docs/Ablation-Flow.md](../Ablation-Flow.md) + [scripts/eval_cogmem.py](../../scripts/eval_cogmem.py) recall/full pipeline.
Depends on: [S31](s31-graph-only-ablation.md) cross-fact-type ablation methodology + [S34](s34-bench-action-effect-agentic.md) infrastructure.

## Why LoCoMo (and why now)

S31–S34 exhausted what we can claim on **LongMemEval-S** (35 conversations, ~115K tokens each) and on the **purpose-built cogmem_bench** mocks. The published HINDSIGHT paper reports its weakest score on **LoCoMo multi-hop (64.6%)** — exactly the category our SUM-spreading-activation contribution targets. We have not yet measured CogMem on LoCoMo at all.

LoCoMo distilled (5 conversations, 161 QAs spread across 5 categories) is smaller in conv count than LongMemEval-S but each conversation is **dramatically longer** (19-31 sessions/conv vs LongMemEval's ~50 sessions but lighter content density). Question categories match HINDSIGHT's reporting taxonomy (single-hop, multi-hop, temporal, preference, causal) — directly comparable per-category vs published baseline.

This sprint establishes the **LoCoMo baseline** for CogMem (profile `E7` = Full CogMem) and prepares infrastructure for the cross-fact-type ablation sweep (`E7G..E11G`, parallel to what S31 did on LongMemEval). Optionally add `E1` for the strawman floor (≈ HINDSIGHT-equivalent within CogMem code) to quantify "CogMem additions worth X pp".

## Scope

- **Will do (S35-T1..T5):** baseline `E7` (Full CogMem) eval on full LoCoMo distilled (5 convs, 161 QAs); per-category accuracy aggregation; comparison vs HINDSIGHT published 89.61%.
- **Future (post-S35):** ablation sweep `E7G..E11G` reusing the bank infra from this sprint (no re-retain); paired-bank cách B for LoCoMo (if T5 results motivate it).
- **Out of scope:** retain re-engineering, new fact types, prompt rewrites. Pure evaluation sprint.

## Decisions (S35-T1 confirmed defaults)

| Decision | Choice | Rationale |
|---|---|---|
| Sample size | **Full 161 QAs across 5 convs** | Small enough (1-2 day wall time end-to-end) and a stratified subset doesn't gain much when total n=161. |
| Initial profile sweep | **E7** (Full CogMem) — primary; optionally add `E1` for floor diff | E7 = all 6 networks + adaptive router + SUM activation = THE number to claim vs HINDSIGHT 89.61% LoCoMo. E1 (strawman floor, ≈ HINDSIGHT-equivalent within CogMem code) is optional contrast for "CogMem additions worth X pp" story. **NOT E7F or E7G** — those are diagnostic (S33 router-bias removal / S31 graph-channel isolation), not baselines. |
| Bank naming | **`COGMEM_locomo_<sample_id>`** (e.g. `COGMEM_locomo_conv-30`) | Semantic mapping to actual LoCoMo IDs; one bank per conversation; reused across all QAs of that conv (14-46 questions reuse same retain). |
| Eval iteration | **Per-QA** (`--conv-index` 0..160) | Matches `eval_cogmem.py` per-question pattern. Bank reuse keeps cost bounded. |
| Pre-retain phase | **Explicit separate phase** | One `--pipeline recall` call per conv (5 calls total) to populate bank, then 161 `--skip-retain` calls. Avoids 32× redundant retain. |

## Conversation → QA mapping (frozen reference)

| Conv idx | sample_id | QA range (`--conv-index`) | # QAs | # Sessions |
|---|---|---|---|---|
| 0 | conv-30 | 0–13 | 14 | 19 |
| 1 | conv-26 | 14–47 | 34 | 19 |
| 2 | conv-43 | 48–93 | 46 | 29 |
| 3 | conv-50 | 94–131 | 38 | 30 |
| 4 | conv-47 | 132–160 | 29 | 31 |
| | **Total** | **0–160** | **161** | **128** |

Question category distribution: `{single-hop: 109, preference: 17, temporal: 12, multi-hop: 12, causal: 11}`.

## Code changes (S35-T2)

| File | Change |
|---|---|
| `scripts/eval_cogmem_batch_locomo.ps1` | NEW. Two-phase batch: (1) retain 5 banks via first QA of each conv (`--pipeline recall` no `--skip-retain`); (2) eval all 161 QAs across `$PROFILES` with `--skip-retain` and bank id derived from the QA-to-conv mapping. Hardcoded mapping table (mirrors data; idempotent on data changes via dry-run probe). Supports `-PHASE retain|eval|all`, `-PROFILES @("E1","E7G",...)`. |
| `scripts/locomo_mapping_dryrun.py` | NEW. Offline sanity: load `data/locomo_distilled.json`, verify the hardcoded mapping table in the .ps1 matches actual data (would catch silent dataset shifts). |

**No changes to `scripts/eval_cogmem.py`** — its `locomo` fixture loader (lines 358-452) + `get_fixture("locomo", ...)` are already correct.

## Execution flow (T3–T5)

### T3 — Retain 5 banks (~2.5-4h wall time, manual)
```powershell
.\scripts\eval_cogmem_batch_locomo.ps1 -PHASE retain
```
Pre-retains `COGMEM_locomo_conv-30`, `_conv-26`, `_conv-43`, `_conv-50`, `_conv-47` via 5 calls to eval_cogmem with `--pipeline recall` (cheap, no answer gen). Side-effect: 5 banks populated for downstream profile sweeps. Retain is profile-agnostic (all 6 fact types extracted regardless), so any `$PROFILES` value works here — defaults to E7.

### T4 — Eval baseline E7 across 161 QAs (~80 min, manual)
```powershell
.\scripts\eval_cogmem_batch_locomo.ps1 -PHASE eval -PROFILES @("E7")
```
161 `--pipeline full --skip-retain --profile E7` calls; checkpoints under `experiments/v20/checkpoints/`; auto-aggregate when all 161 present.

Optional contrast run (adds ~80 min):
```powershell
.\scripts\eval_cogmem_batch_locomo.ps1 -PHASE eval -PROFILES @("E1")
```
E1 = no router, no SUM, only world/experience/opinion — gives the "CogMem additions worth X pp" diff against E7.

### T5 — Report (analysis only, no compute)
Write `experiments/v20/locomo_e1_baseline/REPORT.md`:
- Overall accuracy (judge-correct rate) on 161 QAs.
- Per-category breakdown (multi-hop, temporal, causal, preference, single-hop).
- Comparison vs HINDSIGHT published (89.61% overall, 64.6% multi-hop).
- If CogMem outperforms HINDSIGHT on multi-hop → SUM spreading activation contribution validated.
- Decide whether ablation sweep (S36) is worth it based on baseline numbers.

## Exit gate
- 5 banks populated successfully (verify via `GET /v1/banks` filter).
- 161 checkpoints exist (`experiments/v20/checkpoints/E7_full_c{000..160}.json`).
- Aggregated report exists with per-category accuracy.
- Sanity check: at least 1 random multi-hop case manually verified (judge-ignored).

## Risks
- **Long conversations (19-31 sessions/conv) ⇒ slow retain.** Each conv may take 30-60 min retain with Minimax. Total ~2.5-4h pre-retain.
- **Generation timeouts.** Multi-hop questions trigger long Ministral think traces. Set `-TIMEOUT_MS 120000` (2 min) per QA; bump if observe timeouts.
- **Disk: per-bank pgvector storage.** 128 unique sessions across 5 banks ≈ similar size to v16 banks (~700 facts each estimate). Manageable.
- **Auto-judge unreliability.** S33/S34 pattern: manually verify aggregate per-category number with spot checks on 5-10 QAs per category.

## Files to write / modify

- New: `scripts/eval_cogmem_batch_locomo.ps1`, `scripts/locomo_mapping_dryrun.py`, `experiments/v20/locomo_e1_baseline/REPORT.md` (after T5).
- Edit: `docs/PLAN.md` (add S35 row).
- Reuse: `scripts/eval_cogmem.py` (locomo fixture loader, ablation profiles, run_pipeline, aggregation).

## Reproducibility note

The hardcoded conv mapping in the .ps1 was derived from `data/locomo_distilled.json` on 2026-05-30. If the dataset is regenerated (e.g., new distill run), re-derive the mapping via `uv run python scripts/locomo_mapping_dryrun.py` (will diff observed vs hardcoded and exit non-zero on mismatch).
