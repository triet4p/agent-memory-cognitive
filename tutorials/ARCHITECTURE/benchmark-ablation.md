# Benchmark & Ablation (`cogmem_bench`)

## The claim being proved

CogMem adds three *cognitive-node* fact types — `intention`, `action_effect`, `habit` — on top of a
plain `world` / `experience` / `opinion` (w/e/o) memory. The `cogmem_bench` package exists to prove
these nodes are **necessary**, not decorative:

> There exist realistic question classes — prospective, causal, and habitual — whose answers depend
> on the structured metadata of `intention` / `action_effect` / `habit`, and on which a w/e/o-only
> system fails while the full system succeeds.

The frozen methodology lives in [`docs/Ablation-Flow.md`](../../docs/Ablation-Flow.md). This page is
the tutorial-level map of it. `cogmem_bench` is a **separate package** from `cogmem_api`; it reuses
only the API's config + `LLMConfig`.

## Why a separate, stronger generator

Conversations are rendered by a **cross-model** generator (Minimax-M2) that is deliberately *not* the
Ministral model under test. The generator writes only surface dialogue text; the gold facts and
answers are fixed by humans *before* generation. This separation is what makes the benchmark
circularity-proof. Generator settings are read from `COGMEM_BENCH_GEN_LLM_*` (see
[Environment Variables](../CONFIG/env-vars.md) and the full block in `CLAUDE.md`).

## The pipeline

```
Step 0  Pre-register     frozen success criterion (McNemar p<0.05 on ≥6–8 discriminative cases/type)
Step 1  Author specs     ScenarioSpec JSON — gold_fact, question, gold_answer, traps, session_plan
   │                      (the ONLY agent-driven step → `cogmem-bench-author` skill)
   ▼
Step 2  Generate         Minimax renders each spec → 7–10 session dialogue, frozen as static JSON
   │                      uv run python -m cogmem_bench.generate   (one LLM call per session)
   ▼
Step 3  Gate             two verification gates → yield report
          ├─ embedding gate     : retain under fixed E7 config, confirm gold stored as intended type
          └─ discrimination gate: keep only cases where FULL passes AND w/e/o FAILS
   │                      uv run python -m cogmem_bench.gate
   ▼
Step 5  Ablate           Phase 1 (recall-time, fast)  : filter recall fact types → w/e/o vs all
          │              Phase 2 (retain-level, slow) : retain paired banks where typed nodes are
          │                                              never created (closes the "edges still existed" loophole)
   ▼
Step 6  Report           per type: discriminative N, full %, w/e/o %, Δ, McNemar p
```

Only **Step 1 (authoring)** is agent-driven, via the `cogmem-bench-author` skill — it writes
`ScenarioSpec` JSON under `cogmem_bench/specs/`. Generation and gating are manual scripts.

## Where the specs live

```
cogmem_bench/specs/
├── pilot/          pilot_{intention,action_effect,habit}_NN.json   (Step 4 — 2 per type, yield check)
├── necessity/      neg_intention_NN.json, ae_causal_NN.json        (sparse-context necessity set, S33)
└── agentic/        agentic_ae_NN_*.json                            (agentic action_effect set, S34)
```

Each `ScenarioSpec` is the pre-registration record: `scenario_id`, `target_type`, `gold_fact` (typed
fact + metadata, e.g. `intention_status=abandoned`), `question`, machine-checkable `gold_answer`,
`traps`, and a `session_plan` deciding which of the 7–10 sessions carry gold vs distractor turns.

## How ablation is wired into the API

The benchmark drives the same retain/recall API, toggled by two payload fields (documented in
[Retain Pipeline](retain-pipeline.md)):

- **Recall-time (Phase 1)** — recall with `types` restricted to w/e/o vs all six. Fast; banks are
  retained once and frozen.
- **Retain-level (Phase 2)** — `enabled_fact_types` on the retain payload drops disallowed types at
  ingestion, so the typed nodes/edges are *never created*. `cogmem_bench.gate --retain-level-ablation`
  retains **two banks per case** (`<bank>_full` + `<bank>_ablated`). Pairing this with
  `COGMEM_API_RETAIN_STRICT_TYPING=true` adds a strict-typing addendum to the extraction prompt so the
  ablated bank cannot smuggle a node back in under a different label.

## Reading the results

Expect — and keep — a **clean-but-imperfect** separation (a couple of full-failures, the odd
w/e/o-pass). A perfect 30/30 is a red flag for leakage, not a win. The S33 (intention) and S34
(action_effect) runs report per-type discriminative N, the FULL vs w/e/o pass rates, the gap Δ, and
the McNemar p-value; see the report commits and `docs/` for the latest numbers.

## Related

- Per-case diagnosis of *why* a bank passes or fails: [Evaluation & Diagnostics](evaluation.md)
- SUM-vs-MAX graph ablation (a different axis): `scripts/compare_sum_max_graph_only.py`,
  [Search Pipeline](search-pipeline.md)

## Verify Commands

```bash
# Offline wiring check (no LLM calls)
uv run python -m cogmem_bench.generate --dry-run

# Gate a single pilot case against a running cogmem-api
uv run python -m cogmem_bench.gate --only pilot_intention_01

# List authored specs
rg -l "scenario_id" cogmem_bench/specs/
```
