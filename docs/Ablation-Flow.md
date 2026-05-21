The one-line claim you're proving
"There exist realistic question classes — prospective, causal, and habitual — whose answers depend on the structured metadata of intention / action_effect / habit, and on which a world/experience/opinion-only system fails while the full system succeeds."

Everything below serves that sentence.

Step 0 — Pre-register (before any generation)
Write down, frozen, before you see results:

Per type, the question pattern that forces its metadata:
intention → "Did the user follow through on X?" (needs intention_status)
action_effect → "What does the user do when [precondition], and what's the result?" (needs precondition→action→outcome)
habit → "What does the user usually do for X?" (needs repetition/aggregation)
Success criterion: necessity claimed if full > w/e/o-only with McNemar p<0.05 on ≥6–8 discriminative cases per type (~20+ total).
This pre-registration is your defense against circularity.

Step 1 — Author scenario specs (human-defined skeleton)
Per case, a fixed contract — the gold lives here, never in the generator:


- scenario_id, target_type (intention|action_effect|habit)
- gold_fact: the typed fact + its metadata (e.g. status=abandoned)
- question, gold_answer (machine-checkable: number/status/name)
- traps: [type-confusion | stale-intention | contradiction | volume]
- session_plan: which of 7–10 sessions carry gold vs distractor
Author ~10 per type (≈30 specs) to net ~20+ after the gate.

Step 2 — Generate (Minimax renders the skeleton)
Minimax-M2 produces natural 7–10 session dialogue that embeds the spec's facts. It writes surface text only. Cross-model on purpose (generator ≠ Ministral reader). Then freeze each conversation as static JSON — never regenerate at eval time.

Step 3 — Two verification gates (the reject/regenerate loop)
Embedding gate: retain the conversation under the fixed production E7 config (no per-case tuning), check the gold fact was stored as the intended type. If not → reject, fix spec or regenerate.
Discrimination gate: run full (E7) vs w/e/o-only → keep only cases where full PASSES and w/e/o FAILS. Non-discriminative cases are discarded, not patched.
Step 4 — Pilot small first
Run Steps 1–3 on 2 specs per type (6 cases) end-to-end. This tells you the yield (how many survive the gate) and a first read on the gap. If yield ≈80%, generate ~38 to net 30. If the loop is broken, you learn it in ~1h, not after an 8h batch.

Step 5 — Two-phase ablation (cheap iteration, then paper-grade)
Phase 1 (recall-time, fast): retain the full accepted set once, freeze the banks. Ablate by filtering recall_fact_types → w/e/o vs all. Iterate freely; this carries most of the signal.
Phase 2 (retain-level, one-time overnight): separate retains where the typed nodes/edges are never created (enabled_networks ablation): full + w/e/o-only (+ per-type if you want to isolate each). ≤5 background passes, frozen banks. This closes the "but the edges still existed" loophole.
Step 6 — Report
Per type: discriminative N, full %, w/e/o %, Δ, McNemar p. Expect — and keep — a clean-but-imperfect separation (a couple of full-failures, the odd w/e/o-pass). Perfect 30/30 is a red flag, not a win.

Why this is the best version
One-time costs stay one-time: generate once, retain once per config, ablate cheaply — the 8h is amortized, not per-experiment.
Circularity-proof: specs and golds pre-registered and authored before generation; extraction config fixed; cases that don't discriminate are dropped, not tuned.
Statistically honest: powered per-type, frozen fixtures, significance reported.
The concrete next artifact is the scenario-spec schema from Step 1 — it's the contract the generator renders against and the pre-registration record. Want me to draft that schema (plus one fully worked example per node type) so you can sanity-check the shape before we build the skill around it?