# S33 — Intention Necessity (Retain-Level Ablation, Strict Extractor)

Status: ✅ Done (2026-05-29)
Methodology: [docs/Ablation-Flow.md](../Ablation-Flow.md). Depends on: [S32](s32-bench-construction.md) foundation.

## Outcome (final, manual verdict)

**Discrimination: 2/16** negative-intention cases (neg_intention_01, neg_intention_14). McNemar
exact 2-sided p ≈ 0.5 (not significant at this n, but the floor result is rigorous).

The full confound chain was removed before measuring:
1. Adaptive router bias → flat router (`adaptive_router_enabled=False` on both arms).
2. Recall-time leakage → retain-level paired banks (`_full` + `_ablated`; `enabled_fact_types`
   drops disabled-type facts at extraction).
3. Extractor leakage → Minimax-M2 as retain LLM + `COGMEM_API_RETAIN_STRICT_TYPING=true`
   adds a strict-typing addendum to the prompt forbidding recast of disabled-type content.
4. Judge unreliability → verdict by hand from `generated_answer` vs gold.

**Honest finding (publishable):** intention typed nodes carry **necessary** information in
~12.5% of conversational plan-not-done queries (the sparse-context edge cases). In the
remaining ~87.5%, the same information is recoverable from `experience`/`world`/`opinion`
facts because conversations about a non-action naturally produce observational state facts
(*"user hasn't written it yet"*, *"book still sitting unopened"*) which are legitimate
non-intention representations — not extractor leakage. Intention's value is therefore
**conditional on conversational density**.

Visualization tool added: `cogmem_bench/visualize.py` emits side-by-side cytoscape graphs
(`_graph.html`) + presenter-ready explanation (`_explanation.md`) for any case.

## Scope
Prove **intention network necessity** rigorously on human-AI casual chat workload, removing
all known confounds: (1) judge unreliability, (2) router policy bias, (3) extractor leakage.
Action_effect and habit are **explicitly out of scope** — deferred to [S34](s34-bench-action-effect-agentic.md)
(agentic workload, action_effect's actual design target).

## What S33 will (and will not) claim

- **Will claim:** "On purpose-built negative-intention questions (plan-but-not-done), the
  `intention` typed network carries unique necessary information — when never created at
  retain and router policy is neutralized, the system cannot answer."
- **Will NOT claim:** anything about action_effect or habit; anything about agentic workloads.

## What we learned through Phase A–D (drives this rescope)

| Run | Result | Why misleading |
|---|---|---|
| Phase B (E7 vs E11, judge-based) | 11/16 intention "accepted" | E11 confounded (removes 3 types); judge passed E9 "[No memories]" abstentions |
| Phase C (E7 vs E9, manual verdict, router fallback) | 15/16 intention discriminate | Router rule "prospective → intention only" biased E7 to win |
| Phase D (E7F vs E9F, flat router) | 2/16 only | But extractor leaked plan-not-done into `experience`/`opinion` (clear smoking guns: `[experience] "User had a NAS idea but did not act on it"`, `[experience] "User has been meaning to learn Spanish... hasn't opened any lessons"`) |

**Conclusion:** the 2/16 floor reflects extractor leakage with Ministral-3B, not type necessity.
**Cách B + stronger extractor** is the truly rigorous test.

## Approach (Cách B: retain-level ablation)

**Per case, two banks are retained:**
- `COGMEM_BENCH_<sid>_full` — extract with all 6 fact types enabled (for the E7F arm).
- `COGMEM_BENCH_<sid>_no_intention` — extract with `enabled_fact_types = {world, experience, opinion, habit, action_effect}` (for the E9F arm). Critically: facts that look like unfulfilled intentions are **dropped entirely** (not recast as experience/opinion).

The ablated arm therefore has **no intention nodes, no intention edges, and no leaked intention-content under other types**. If the ablated arm still cannot answer, the result is content-level necessity — unattackable on extraction or routing grounds.

**Stronger extractor (Minimax-M2) for retain:** the production retain model (Ministral-3B)
leaks aggressively; that confounds "type-design value" with "extractor quality." Using
Minimax (already configured for generation) for retain isolates the design question. Ministral
stays as the answer-generation model (so answer quality isn't a moving variable).

## Code changes (T-1: retain-level ablation wiring)

| File | Change |
|------|--------|
| `cogmem_api/engine/retain/fact_extraction.py` | Add `enabled_fact_types` allowlist; drop facts whose type isn't allowed; update extraction prompt to instruct strict typing ("if fact expresses an unfulfilled plan, type ONLY as `intention`; if not allowed, do not extract at all"). |
| `cogmem_api/engine/retain/link_creation.py` | Skip creating edges originating from or terminating at a disabled type. |
| `cogmem_api/engine/retain/orchestrator.py` | Thread `enabled_fact_types` through `retain_batch()`. |
| `cogmem_api/api/http.py` | Accept `enabled_fact_types` on the retain endpoint payload. |
| `cogmem_bench/gates.py` | For each case, retain TWO banks (full + no-intention); E7F → full bank, E9F → ablated bank. Bank id pattern: `COGMEM_BENCH_<sid>_full` / `<sid>_no_intention`. |
| `cogmem_api/engine/memory_engine.py` | Add `COGMEM_API_RETAIN_LLM_*` env (separate retain LLM endpoint), fallback to main LLM. Used so retain can run on Minimax while generate/judge stay on Ministral. |

## Execution flow

### T1 — Code (above, ~half day)
Land the retain-level ablation + separate retain-LLM env. Update T4 offline test to cover
the `enabled_fact_types` drop logic (unit-test that a "plan" fact is dropped when intention
is disabled, and not silently recast as experience).

### T2 — Re-run necessity batch (clean state)
Banks already wiped (cleanup done 2026-05-28). Specs unchanged (`cogmem_bench/specs/necessity/`
= 16 negative-intention + 4 causal action_effect; action_effect kept for sanity but not the
focus). Generation fixtures re-generated if needed. Then:
- Retain each case **twice** (full + no-intention) into the paired banks (Minimax extractor).
- Gate with flat router (E7F vs E9F) — recall + generate + judge.
- `gate_detail/` per case includes both runs' recall + answers.

### T3 — Manual verdict + statistics
Read each `gate_detail` by hand (judge ignored). Discrimination criterion: E7F names the
unfulfilled plan AND the ablated arm cannot. Compute **McNemar exact p** on the 16
intention cases. Expected: discrimination jumps significantly from the 2/16 floor.

### T4 — Report (intention-only)
Write `experiments/v18/intention_necessity/REPORT.md`:
- Methodology chain (S31 → S32 → S33 phases → cách B). Show how each confound was identified
  and removed.
- Final table: per-case verdict, ablated-arm recall size, discrimination yes/no.
- McNemar result.
- Honest statement of scope: human-AI chat workload; action_effect/habit deferred to S34.

## Exit gate
- ≥6–8 cases (of 16) discriminate after cách B + Minimax retain.
- McNemar p<0.05.
- Per-case manual verification documented; no judge-based-only conclusions.

## Files to write/modify
- New: code per T1 above; `experiments/v18/intention_necessity/REPORT.md`; updated offline tests.
- Reuse: `cogmem_bench/{schema,prompts,generation,fixtures,gates,gate,generate,datasets}.py`,
  `cogmem_bench/specs/necessity/neg_intention_*.json` (16 specs unchanged).
- Out of scope this sprint: action_effect generation infrastructure, habit testing.

## Risks
- **Stronger extractor still leaks**: if Minimax also types "user has been meaning to X but
  hasn't" as experience, the leakage stays. Mitigation: explicit prompt rule + post-extraction
  filter (drop facts whose text matches plan-not-done patterns when intention is disabled).
- **Discrimination still low (~2-3/16)**: would suggest typed intention adds limited value
  even with strict retain — still publishable as honest narrow finding combined with router-bias
  S31/Phase-D analysis.
- **Bank duplication cost**: 40 retains (20×2) — but each ~50-100 nodes; total ~30-60 minutes.
  Not a real bottleneck.
