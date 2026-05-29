# S34 — Action_Effect Necessity (Agentic AI Workload)

Status: 🔄 Planned (after S33)
Methodology: [docs/Ablation-Flow.md](../Ablation-Flow.md). Depends on: [S33](s33-bench-discrimination.md) cách B infrastructure.

## Why a separate sprint

S31–S33 tested `action_effect` on **human-AI casual chat** ("when latency spikes I switch
to int8"). Result: 0/4 discriminate, *but unfairly* — action_effect was never designed for
that workload. Its design target is **agentic AI memory**:

- An AI agent uses tools (search, code exec, API calls, browser, file ops).
- Each tool call yields an observation (success/failure, output, side-effect).
- The agent learns **causal rules** from these observations: `precondition → action → outcome`
  (e.g., "when API X returns 429, retry with backoff" / "when pytest reports flaky network
  failure, rerun with `--no-cache`").
- High information density per session (many tool calls), structured (precondition rooted in
  observable state, outcome rooted in tool result), and causal rules are first-class because
  the agent must apply them in future episodes.

In agentic workload `action_effect` is **non-redundant**: a causal rule like "the Stripe API
rate-limits at 100 req/min" isn't naturally typed as `experience` ("I once hit the limit"),
because the agent needs the *generalized rule*, not the single event. Strict retain on an
agentic conversation should produce action_effect facts that *cannot* be reconstructed from
experiences alone.

S34 builds the benchmark for this proper workload and runs the same rigorous test.

## Scope
- **Will claim:** "On agentic AI conversations (single-agent tool-use; agent-to-agent), the
  `action_effect` typed network carries necessary causal information; removing it (cách B
  retain-level) breaks the system's ability to apply learned causal rules."
- **Will NOT claim:** anything beyond agentic workload; intention re-tested only as sanity check.

## Workload definition

Two variants, both first-class:

**A — Single-agent tool-use trace:** the conversation is the transcript of an AI agent doing
multi-step tasks with tools. Each "session" is one task episode. Tool I/O is part of the
transcript (or summarized in assistant turns).
- Example episode: agent runs a script; pytest fails with network flakiness; agent reruns
  with `--no-cache`; tests pass. → causal rule: `pytest flaky network failure → rerun --no-cache → pass`.

**B — Agent-to-agent dialogue:** two AI agents collaborate (e.g., planner + executor) — each
maintains its own memory of causal rules about its tools AND about the other agent's
behavior. Richer causal structure.

S34 starts with **(A)** because it's tractable; (B) deferred to S35 if needed.

## What needs to be built (the main S34 cost)

| Component | Description |
|---|---|
| **Agentic generation framework** | Generate realistic agent-tool traces. Two paths: (a) script-based — author Python that simulates an agent + fake tool responses, producing deterministic transcripts; (b) LLM-based — use Minimax (or a frontier model) to roleplay the agent + tool environment. (b) is more flexible, (a) more reproducible. Recommend (b) with a strict spec contract per case. |
| **Spec schema extension** | `AgenticScenarioSpec`: scenario_id, tools_used (list), episodes (list of "task" descriptions), gold causal rule (precondition + action + outcome), question (prospective tool-use), gold_answer. Reuses GoldFact / fragments concept. |
| **Generation prompt template** | Instruct the generator to emit a realistic multi-episode trace where tool calls and outcomes are described inline (e.g., `[tool: bash] → [output: pytest FAILED ...]`). Tool inventions are constrained by spec. |
| **Fixture conversion** | Tool-trace → distilled fixture shape (each episode = one session; tool I/O may appear in user/assistant turns). Probably needs a small adapter so retain doesn't get confused by tool tags. |
| **Question types** | Prospective tool-use ("when the agent encounters [precondition], what tool action does it take and what outcome?"). Avoid the "what will they do" trap from S33 — use causal phrasing the router boosts action_effect on (`what does the agent do when X?`). |

## Reuse from S33 (no rebuild)
- **Retain-level ablation** (`enabled_fact_types` wiring) — built in S33 T1.
- **Flat router profiles** (E7F / E10F) — built in S33-pre.
- **Gates** (`run_case_gates`) — works as-is; just point at S34 spec dir.
- **Stronger retain extractor** (Minimax-M2 via `COGMEM_API_RETAIN_LLM_*`) — same env.
- **Manual-verdict workflow** + recall=0 signal.

## Execution flow

### T1 — Workload design + generation prototype (1–2 days, before authoring)
Author 1 small agentic spec by hand. Prototype the generation prompt + trace format with
Minimax. Verify: (a) trace reads as a realistic agent transcript, (b) retain extracts
action_effect facts with `{precondition, action, outcome}` metadata properly, (c) the gold
causal rule is reconstructable. Iterate prompt/format until clean.

### T2 — Spec schema + author batch (~12–16 specs)
Extend `cogmem_bench/schema.py` (or new sibling) for `AgenticScenarioSpec`. Author 12–16
specs across varied tool domains (CI/pytest, HTTP APIs with rate limits, file system,
database queries, browser automation). Each spec contains a gold causal rule + a fulfilled
"trap" rule (a different precondition→action→outcome pair, fully observed, to tempt wrong
answers).

### T3 — Generate + retain (cách B paired banks) + gate (flat router E7F vs E10F)
Same pipeline as S33 T2–T3 but on agentic specs. Bank id pattern:
`COGMEM_BENCH_AGENT_<sid>_full` / `<sid>_no_action_effect`.

### T4 — Manual verdict + statistics
Read each `gate_detail` by hand. Discrimination criterion: E7F gives the correct
`action → outcome`; ablated arm cannot reconstruct the rule (recall=0 or wrong rule).
McNemar exact p over the agentic batch.

### T5 — Report
`experiments/v19/action_effect_agentic/REPORT.md`. Same structure as S33's report:
methodology, per-case verdict, ablated-arm recall, McNemar. Tie back to S33: "typed
network necessity is workload-dependent — intention in chat (S33), action_effect in
agentic (S34)."

## Exit gate
- ≥6–8 cases discriminate (E7F correct / E10F cannot).
- McNemar p<0.05.
- Per-case manual verification documented.
- Agentic generation framework documented as reusable for future workload-specific tests.

## Open questions to decide at S34 T1
- **Generator model for agentic traces:** Minimax-M2 (consistent with S33) or a frontier
  model? Agentic role-play may need stronger reasoning; revisit during prototype.
- **Tool I/O rendering:** inline (`[tool: bash] → ...`) vs structured JSON in assistant turns
  vs prose ("I ran pytest and got...") — affects how retain extracts action_effect metadata.
- **Spec author or LLM-author?** Authoring agentic specs requires domain knowledge per
  tool — could be agent-driven (cogmem-bench-author skill extended) or hand-curated.

## Out of scope
- Habit: no clear agentic workload makes it necessary; defer or write off.
- Intention re-test on agentic workload: optional sanity check; not the primary claim.
- Agent-to-agent (B variant): defer to S35 if A succeeds.

## Risks
- **Generation framework complexity:** agentic traces are harder to generate realistically
  than chat. Mitigation: T1 prototype before committing to author batch.
- **Tool-trace retain extraction:** Ministral/Minimax may not parse tool-tagged content
  cleanly into action_effect facts with proper metadata. May need a retain-prompt extension
  for "agent transcripts."
- **Workload too constrained:** if all specs are similar (e.g., all CI-failure patterns), the
  result generalizes weakly. Mitigation: deliberately diverse tool domains.
