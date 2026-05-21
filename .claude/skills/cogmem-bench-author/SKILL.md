---
name: cogmem-bench-author
description: >
  Author pre-registered ScenarioSpec JSON for the cognitive-node ablation benchmark
  (docs/Ablation-Flow.md step 0-1). Use this skill when the user asks to write, draft,
  design, or add benchmark scenarios / cases / specs for habit, intention, or
  action_effect — e.g. "author a new intention case", "draft 4 action_effect specs",
  "add habit scenarios to the pilot". Produces JSON files under cogmem_bench/specs/ that
  the generate + gate scripts consume. This is the pre-registration record: the gold fact,
  gold answer, and required metadata are fixed here, BEFORE any conversation is generated.
  Authoring is the only agent-driven step; generation and gating are manual scripts.
---

# CogMem Bench — Author Skill (steps 0-1)

You (the strong model) author `ScenarioSpec` JSON. The gold lives in the spec, never in
the generator. Authoring BEFORE generation is the defense against circularity.

## What to produce

One JSON file per scenario under `cogmem_bench/specs/<set>/` (pilot set:
`cogmem_bench/specs/pilot/`), validated against `cogmem_bench/schema.py::ScenarioSpec`.

## The contract (must validate)

- `target_type` ∈ {intention, action_effect, habit}; `gold_fact.fact_type` must equal it.
- `gold_fact.metadata` must carry the type's structured fields:
  - intention → `intention_status` ∈ {planning, fulfilled, abandoned}
  - action_effect → `precondition`, `action`, `outcome` (+ optional `confidence`)
  - habit → `frequency` (the repetition descriptor)
- `gold_fact.session_index` ∈ `session_plan.gold_session_indices`.
- `session_plan.total_sessions` ∈ [7, 10]; 1–3 gold sessions.
- `gold_answer` must be machine-checkable (a number / status / name).

## Design rules (what makes a case discriminate)

The question must hinge on the **metadata**, not the surface fact — so a
world/experience/opinion-only system provably cannot answer:
- intention: ask whether a plan was followed through (needs final status).
- action_effect: ask what the user does under a precondition and the result (needs the triple).
- habit: ask what the user *usually/typically* does (needs aggregation over repetitions).

Add `traps` (type-confusion, stale-intention, contradiction, volume) that mislead a
w/e/o-only reader. Write a `rationale` explaining why the type's metadata is required.

## Validate before handing off

```
uv run python .claude/skills/cogmem-bench-author/scripts/validate_specs.py --dir cogmem_bench/specs/pilot
```

## Next steps are MANUAL scripts (no skill — run them yourself)

```
uv run python -m cogmem_bench.generate              # step 2: Minimax renders specs -> data/bench/work
uv run python -m cogmem_bench.gate                  # step 3: embedding + discrimination gates -> yield report
```

Generation is long-running and needs only `COGMEM_BENCH_GEN_LLM_*` (Minimax). Gating needs
a running `cogmem-api` with Ministral. Generation and gating are decoupled so you can run,
inspect, and freeze conversations before gating.
