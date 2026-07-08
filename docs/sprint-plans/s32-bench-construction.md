# S32 — Cognitive-Node Ablation Benchmark: Construction Foundation + Pilot

Status: ✅ Foundation done (offline-verified) · 🔄 Live pilot pending user endpoints
Full methodology frozen in [docs/Ablation-Flow.md](../Ablation-Flow.md).

## Motivation

The S31 graph-only ablation (E7G–E11G, 35 LongMemEval-S cases, verdicts 2026-05-17) showed
the three cognitive node types (`habit`, `intention`, `action_effect`) do **not** earn their
place on that benchmark — removing `intention` even *helps* (E7G→E9G: 22→26 PASS). Per-case
analysis confirmed the differences are recall-composition artifacts, not the semantic value
of the typed nodes.

Root cause is **benchmark fit**, not design failure: LongMemEval-S has no prospective,
causal, or habitual question categories (verified categories: `multi-session /
knowledge-update / temporal / single-session / preference`), so it structurally cannot
reward those node types. To answer "are the 3 node types necessary?" honestly we must build
a purpose-built benchmark whose gold answers depend on each type's **structured metadata**
(`intention_status`; `precondition→action→outcome`; habit repetition/aggregation) — questions
a `world/experience/opinion`-only system provably cannot answer.

S32 builds the construction **foundation + a 6-case pilot** to validate the method before
the full 30-case build (S33).

## Key architectural finding (verified)

`AblationProfile.enabled_networks` in `scripts/eval_cogmem.py` is **only echoed into the
checkpoint `ablation_hooks`** — it is never passed to retain. Retain always extracts all 6
fact types; E7G–E11G shared the same retained banks and differed only by filtering `types`
at recall (`cogmem_api/api/http.py:350`). `retain_batch()`'s `fact_type_override`
(`orchestrator.py:67`) forces *all* facts to one type — not a per-type enable/disable.

**Consequence:** the discrimination gate (full PASS / w-e-o FAIL) works purely at recall
time with the existing `types` filter — cheap, one retain, no new recall code. The
retain-level ablation (never *create* the typed nodes/edges) is **deferred to S33**.

## What was built — `cogmem_bench/` package (new, root sibling of cogmem_api/)

| Module | Responsibility |
|--------|----------------|
| `schema.py` | Pre-registration contract: `ScenarioSpec`/`GoldFact`/`Trap`/`SessionPlan`/`GeneratedConversation`/`GateResult`. Per-type metadata validators; `shared_context` canonical ledger. |
| `config.py` | Minimax generator `LLMConfig` from `COGMEM_BENCH_GEN_LLM_*`; `resolve_last_k_verbatim()`. |
| `prompts.py` | Per-session prompt: canonical-facts block + older recaps + last-K verbatim; requests a `recap` field. |
| `generation.py` | **Multi-call** (one LLM call per session) threading consistency forward; `parse_session_response` reuses `parse_llm_json` (strips `<think>`). |
| `fixtures.py` | Emit LongMemEval-distilled JSON → consumed by `eval_cogmem` unchanged. |
| `gates.py` | Type-aware embedding gate + discrimination gate (retain once E7, reuse bank for E11). |
| `datasets.py` | `load_specs`, paths, `work_fixture_path`. |
| `generate.py` | Manual CLI: `python -m cogmem_bench.generate` (Minimax only). |
| `gate.py` | Manual CLI: `python -m cogmem_bench.gate` (needs Ministral API). |

Plus: 6 pilot `ScenarioSpec`s in `cogmem_bench/specs/pilot/` (2 per type), and the
`cogmem-bench-author` skill (the only agent-driven step; generation + gating are manual
scripts).

### Cross-session consistency (multi-call generation)

A single call for 7–10 coherent sessions is unreliable. Generation is multi-call, with three
consistency mechanisms (strongest last):
1. `spec.shared_context` canonical ledger injected into every session prompt.
2. Model-emitted one-line `recap` of each older session.
3. The last `COGMEM_BENCH_GEN_LAST_K_VERBATIM` (default 2; CLI `--last-k`) sessions verbatim.

## New env vars

```
COGMEM_BENCH_GEN_LLM_BASE_URL     # Minimax-M2 endpoint /v1
COGMEM_BENCH_GEN_LLM_MODEL        # default minimax-m2
COGMEM_BENCH_GEN_LLM_API_KEY      # default ollama
COGMEM_BENCH_GEN_LLM_TIMEOUT      # default 600
COGMEM_BENCH_GEN_LAST_K_VERBATIM  # default 2
COGMEM_BENCH_GEN_MAX_TOKENS       # gold/trap session budget; default 16000 (includes <think>)
COGMEM_BENCH_GEN_FILLER_MAX_TOKENS # filler session budget; default 8000
```
Retain/answer stay on Ministral via `COGMEM_API_LLM_*`.

## How to run

```bash
# Author specs (agent skill) -> cogmem_bench/specs/<set>/
uv run python .claude/skills/cogmem-bench-author/scripts/validate_specs.py --dir cogmem_bench/specs/pilot

# Step 2 — generate (Minimax only; long-running, manual)
uv run python -m cogmem_bench.generate              # --dry-run for offline wiring, --only <id>, --last-k N

# Step 3 — gate (needs running cogmem-api with Ministral)
uv run python -m cogmem_bench.gate                  # writes experiments/cogmem_bench/bench_gate_report.md + gate_results.json
```

## Verification (artifacts + tests)

Logs: `logs/task_s32_t1..t5_summary.md`. Tests (all PASS offline):
`tests/artifacts/test_task_s32_{t1_schema,t2_generation,t3_fixtures,t4_gates,t5_scripts}.py`.

Offline-verified: schema validation/round-trip, multi-call generation response-processing
(one call/session, canonical+recap+verbatim consistency), fixture emit→load through the
real harness, gate decision logic, 6 specs valid, generate dry-run, env precedence.

**Live pilot pending:** `python -m cogmem_bench.generate` then `gate` need Minimax +
running Ministral endpoints (unset in dev env). Run on the Kaggle+NGROK setup → yields
`experiments/cogmem_bench/bench_gate_report.md`.

## Deferred to S33

- Multi-call already done in S32. Full 30-case authoring + generation.
- Retain-level ablation (`enabled_networks` gates extraction — never create typed nodes/edges).
- Final per-type stats: Δ + McNemar on ≥6–8 discriminative cases/type.

## Guardrails honored

- Coverage gate: no audit requested → `docs/migration_idea_coverage_matrix.md` untouched.
- No `hindsight_api` imports; `cogmem_bench` uses absolute `cogmem_api.*` imports + same-level relative.

## Files

- New package: `cogmem_bench/{__init__,schema,config,prompts,generation,fixtures,gates,datasets,generate,gate}.py`
- New: `cogmem_bench/specs/pilot/*.json` (6), `.claude/skills/cogmem-bench-author/`
- Edited: `CLAUDE.md` (env docs)
- Reused unchanged: `cogmem_api/config.py`, `cogmem_api/engine/llm_wrapper.py`, `scripts/eval_cogmem.py`
