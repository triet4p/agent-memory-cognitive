---
name: cogmem-audit
description: >
  Systematic diagnostic audit of a CogMem memory bank for a specific LongMemEval test case.
  Use this skill whenever the user asks to audit, diagnose, inspect, analyze, or investigate
  a specific case (e.g., "audit c001", "why does c029 fail", "check graph for c014",
  "diagnose case c007", "analyze recall for c000"). Also use it when the user asks to
  compare PASS vs FAIL cases, investigate root causes of recall failures, or check graph
  structure for a particular bank. The skill produces a structured report identifying
  answer-relevant facts, recall gaps, graph connectivity issues, and recommended fixes.
---

# CogMem Audit Skill

## ⚠ MANDATORY EXECUTION RULES — READ BEFORE ANYTHING ELSE

These rules are non-negotiable and override any other instinct:

1. **Execute the 5 phases in order. Do not skip any phase.**
   - Phase 3 (graph analysis) is required for ANY fact outside top-25, not just channel-level misses.
   - Do not stop at Phase 2 and write the report.

2. **Use ONLY the 3 bundled scripts — no others exist.**
   - Phase 1: `fetch_session_facts.py` — Phase 2: `run_phase2.py` — Phase 3: `run_phase3.py`
   - NEVER use `curl`, PowerShell `Invoke-WebRequest`, or raw HTTP — Windows quoting breaks JSON bodies.
   - Run with `uv run python .claude/skills/cogmem-audit/scripts/<name>.py` from the repo root.

3. **Both recall calls MUST include `--trace`.**
   - `--top-k 25 --trace` for standard recall
   - `--top-k 300 --trace` for wide-net recall
   - WITHOUT `--trace`: the `channel_ranks` field in each result is `null` (the whole field, not a dict). This means you forgot `--trace`, NOT that the fact is missing from all channels. If you see `"channel_ranks": null` instead of `"channel_ranks": {"semantic": ..., "bm25": ..., "graph": ..., "temporal": ...}`, re-run with `--trace`.

4. **Do not over-explain between steps.**
   - Execute each step, show a concise summary of what you found, then move immediately to the next step.
   - No lengthy reasoning blocks about what you're "about to do". Just do it.

5. **Never summarize or truncate script output when populating tables.**
   - The top-25 table must have exactly 25 rows — not 5 "interesting" rows. Show every result.
   - The top-300-extended table must show every fact outside top-25 that appeared in the output — not just the ones with gold_tag=gold.
   - Phase 3 summary_table must show all 7 link type rows — even rows with count=0.
   - If a script outputs 200 links, record the summary stats (count, avg_weight, cross_session_count) from the JSON — do not eyeball and estimate.
   - **Fact IDs must be shown in full (complete UUID, e.g. `c450e31f-bfea-4d1c-9037-c7fb924f7f9f`) in every table and every exit gate block.** Never truncate to 8 chars or add `...`. Full IDs are required for cross-referencing facts across sections and for future debugging.

6. **The report file must follow `references/_REPORT_TEMPLATE.md` exactly.**
   - Use the exact section headings from the template. Do not rename, reorder, or add sections.
   - The exit gate outputs (✅ Phase N complete blocks) are working notes — they appear during execution but are NOT written into the report file.
   - The report file contains only what the template defines.

7. **Report all channel_ranks correctly.**
   - With `--trace`, each result has `"channel_ranks": {"semantic": N_or_null, "bm25": N_or_null, "graph": N_or_null, "temporal": N_or_null}`.
   - A channel value being `null` means that channel did NOT retrieve the fact.
   - ALL channels null (with `--trace` present) = fact has empty source_ranks = impossible for a fact with positive rrf_score → re-verify you used `--trace`.

---

## Purpose

This skill runs a 5-phase diagnostic on a CogMem test case to answer:
> "Why does this case pass or fail? Which specific facts are missing from recall, and what is blocking them?"

The key principle: **answer-relevant facts** are facts whose `text` field directly supports the correct answer. A gold session may contain 20+ facts; only 1–3 are answer-relevant. Diagnose only those.

---

## Prerequisites

- CogMem API running at `http://localhost:8888`
- Checkpoint files at `experiments/v14/checkpoints_5/E7_full_c{NNN}.json`
- Output directory: `experiments/v14/diagnostic_s28/` (create if missing)
- Bank ID format: `COGMEM_EXP_v14_e567_c{NNN}` (e.g., `COGMEM_EXP_v14_e567_c001`)

## API Scripts

Three scripts, one per phase — no others exist:

| Script | Phase | Purpose |
|--------|-------|---------|
| `scripts/fetch_session_facts.py` | Phase 1 | Fetch all facts for one gold session |
| `scripts/run_phase2.py` | Phase 2 | Both recalls (top-25 + top-300) with trace, merged output |
| `scripts/run_phase3.py` | Phase 3 | All 7 link types in one shot, with connectivity classification |

All scripts: `uv run python .claude/skills/cogmem-audit/scripts/<name>.py --help` for usage.
Default API base: `http://localhost:8888`.

---

## 5-Phase Workflow

### Phase 0: Load Case Context

Read the checkpoint file:
```
experiments/v14/checkpoints_5/E7_full_c{NNN}.json
```

Extract from `questions[0]`:
- `query` — the user's question
- `gold_answer` — the correct answer
- `gold_session_ids` — list of document_id strings (e.g., `["answer_593bdffd_1", "answer_593bdffd_3"]`)

Top-level: `bank_id`.

**▶ Phase 0 exit gate — output this block before continuing:**
```
✅ Phase 0 complete
- bank_id: {bank_id}
- query: "{query}"
- gold_sessions: {N} ({list of session ids})
- gold_answer: "{gold_answer}"
```
If any field is missing, re-read the checkpoint file.

---

### Phase 1: Identify Answer-Relevant Facts

Goal: for each discrete component of the gold answer, find the fact(s) from the gold sessions whose `text` directly provides that piece of information.

**The gold answer is the single source of truth.** Do not make independent relevance judgments — derive coverage mechanically from the gold answer text.

**Step 1.1: Decompose the gold answer into components**

Before fetching any facts, break `gold_answer` into discrete, independently verifiable components. Each component is one specific claim the answer makes:
- Counting queries: each counted entity is one component (e.g., "F-15 Eagle kit", "Spitfire Mk.V 1/48 kit")
- Factual queries: each distinct value is one component (e.g., "Gold level requires 120 stars")
- Causal queries: the cause and effect are separate components

Write out the numbered component list now.

**Step 1.2: Fetch facts per gold session**

For each session in `gold_session_ids`:
```
uv run python .claude/skills/cogmem-audit/scripts/fetch_session_facts.py \
    --bank-id {bank_id} \
    --document-id {session_id}
```

Response: JSON array of `{id, text, fact_type, document_id, event_date, raw_snippet}`.

**Step 1.3: Match facts to components**

For each gold answer component, find the fact(s) whose `text` field directly mentions that component.

Rules:
- Use only `text` — NEVER `raw_snippet`
- A fact's `text` must directly contribute that specific piece (for counting: names the entity; for factual: states the value)
- Being in a gold session does NOT make a fact answer-relevant
- One fact can cover multiple components; one component can be covered by multiple facts — list all
- Be inclusive: if the gold answer counts 5 items, all 5 must have a covering fact
- If NO fact in any gold session covers a component → mark it **"no fact found in bank"** — this is a retain failure, tracked separately from recall failure

Output: the component → fact mapping table, plus a flat deduped list of all covering fact IDs to track through Phase 2–3.

**▶ Phase 1 exit gate — output this block before continuing:**
```
✅ Phase 1 complete
- Sessions fetched: {N}/{N} gold sessions
- Gold answer components: {N}

Component → Fact mapping:
| # | Gold Answer Component | Covering Fact ID (full UUID) | In Bank? |
|---|-----------------------|------------------------------|----------|
| 1 | {component text}      | {fact uuid}                  | Yes / No fact found in bank |

Answer-relevant facts ({N} total, deduped):
| # | ID (full UUID) | document_id | text (60 chars) |
|---|----------------|-------------|-----------------|
```
⛔ If fetch_session_facts.py was NOT run for every gold session → go back and run it.
⛔ If any component shows "No fact found in bank" → retain failure. Note it; Phase 2 will confirm absence from top-300.
⛔ If any fact row is missing its `id` → it cannot be tracked in Phase 2. Re-check Step 1.3.

---

### Phase 2: Two-Level Recall Audit

Goal: for each answer-relevant fact, determine whether it reached top-25, and if not, why not.

**Run ONE command — it handles both recall calls with trace guaranteed:**
```
uv run python .claude/skills/cogmem-audit/scripts/run_phase2.py \
    --bank-id {bank_id} \
    --query "{query}" \
    --gold-session-ids "{session_id_1},{session_id_2},..."
```

This runs top-25 and top-300 with `trace=True`, validates channel_ranks are populated (exits with error if trace failed), and outputs a single JSON with:
- `trace.query_type` and `trace.rrf_weights` — record these in the report header
- `top25` — all 25 results with channel_ranks
- `top300_extended` — ranks 26–300 only
- `facts_by_id` — dict keyed by fact `id` for instant lookup

**Step 2.3: Classify EVERY answer-relevant fact — no exceptions**

Before searching the recall results, write out every answer-relevant fact from Phase 1 as a row in a working table. Then look up each one by `id` in the top-25 and top-300 results. Every fact must get a classification — do not skip any.

| Situation | Evidence | Root Cause Label |
|-----------|---------|-----------------|
| In top-25 results | Found in Step 2.1 | **Recalled correctly** |
| In ranks 26–300, any channel rank ≤ 20 | Found in Step 2.2 | **CE suppression** |
| In ranks 26–300, all channel ranks null or > 100 | Found in Step 2.2 | **RRF dilution** |
| Not in top-300 at all | Absent from Step 2.2 | **Channel-level miss** |

For each answer-relevant fact, record: rank in top-300, `global_rrf_rank`, `rrf_rank`, `cross_encoder_score`, `combined_score`, semantic/bm25/graph/temporal channel rank.

If a fact appears in the same document_id as another answer-relevant fact but under a different `id`, track them separately — they may have different recall paths.

**Step 2.4: Noise analysis (top-25)**

Noise is any fact in top-25 that does NOT help the model produce the correct answer. There are two types:

**Type A — Session noise**: `document_id` is NOT in `gold_session_ids`. Completely unrelated session occupying a slot that should go to a gold fact.

**Type B — Fact noise**: `document_id` IS in `gold_session_ids` but the fact is NOT in the answer-relevant list from Phase 1. Right session, wrong part — adjacent facts about techniques, tools, or plans that could confuse the model when counting or identifying the answer.

**Before building the noise table, write out the answer-relevant ID set:**
```
Answer-relevant IDs (from Phase 1, deduped):
- {uuid-1}
- {uuid-2}
- ...
```
This set is your exclusion list. Any top-25 fact whose `id` appears in this set is answer-relevant — skip it. Every other fact is noise.

⚠ **Minimum requirement: the noise table MUST contain at least 10 rows.**

Go through ALL 25 results from top25 in order. For each row, check: is this `id` in the exclusion list above? If YES → skip. If NO → add to noise table (Type A if document_id not in gold_session_ids, else Type B). Do not stop early. Do not group or skip rows that "look similar".

For each noise fact, record: full ID, rank, document_id, type (A or B), CE score, channel_ranks.
At the end, note: which noise facts at ranks 1–10 could plausibly cause a generation error (count-adjacent, topic-adjacent facts that might be miscounted or misattributed).

**▶ Phase 2 exit gate — output this block before continuing:**
```
✅ Phase 2 complete
- run_phase2.py: ✓ executed (not recall.py manually)
- channel_ranks format: dict ✓  (if null anywhere → re-run run_phase2.py)
- query_type: {query_type}
- rrf_weights: semantic={w}, bm25={w}, graph={w}, temporal={w}

Classification ({N}/{N} answer-relevant facts — every fact must have a row):
| # | id (full UUID) | Rank | Global RRF | CE | Sem | BM25 | Graph | Temporal | Classification |
|---|----------------|------|-----------|-----|-----|------|-------|---------|----------------|

Summary (count directly from classification table rows above — do not estimate):
- Recalled correctly: {count rows where Classification = "Recalled correctly"}/{N}
- CE suppression:     {count}/{N}
- RRF dilution:       {count}/{N}
- Channel-level miss: {count}/{N}
- Retain failure:     {count}/{N}

Facts outside top-25 needing Phase 3 (ONLY IDs that are in the answer-relevant list AND absent from top25 results):
{list ids or "none"}
```
⛔ If any answer-relevant fact is missing from the classification table → find it in facts_by_id and add it.
⛔ If channel_ranks is null for ANY result → re-run run_phase2.py (trace was not applied).
⛔ If noise table has fewer than 10 rows → missed Type B facts. Re-scan ALL 25 top25 rows against answer-relevant list and add every non-answer-relevant fact.
⛔ "Facts outside top-25 needing Phase 3" must contain ONLY IDs from the answer-relevant list. IDs not in the answer-relevant list must NOT appear here, regardless of their recall status.

---

### Phase 3: Graph Analysis

**Run Phase 3 ONLY for facts that satisfy BOTH conditions:**
1. The fact `id` is in the answer-relevant list from Phase 1
2. The fact `id` is NOT found in the `top25` array from run_phase2.py

Facts that are in top-25 (even at rank 23–25) do NOT need Phase 3. Facts not in the answer-relevant list do NOT need Phase 3, even if they are outside top-25.

Use the "Facts outside top-25 needing Phase 3" list from the Phase 2 exit gate as your exact input — run once per ID in that list, no more.

For each such fact, pick a distinctive keyword from its `text` (proper noun, model name, domain-specific term).

**Run ONE command per fact — it probes all 7 link types automatically:**
```
uv run python .claude/skills/cogmem-audit/scripts/run_phase3.py \
    --bank-id {bank_id} \
    --keyword "{distinctive keyword}" \
    --gold-session-ids "{session_id_1},{session_id_2},..."
```

Output includes:
- `summary_table` — one row per link type: count, avg_weight, cross_session_count, cross_session_to_non_gold
- `connectivity_class` — auto-classified: Well-connected / Weakly connected / Isolated / BFS-diluted
- `connectivity_evidence` — one-line justification
- `details[link_type].summary.samples` — 3 sample links per type for spot-checking

Read the output and verify/override `connectivity_class` if the auto-classification misses context (e.g., entity links that connect to wrong entities).

**▶ Phase 3 exit gate — output this block before continuing:**
```
✅ Phase 3 complete
Facts outside top-25 requiring graph analysis: {N}

| # | Keyword used | run_phase3.py run? | Connectivity class | Override? |
|---|--------------|-------------------|-------------------|-----------|
| 1 | "{keyword}"  | ✓                 | BFS-diluted        | No        |
| 2 | ...
```
⛔ If ANY fact outside top-25 is missing from this table → run run_phase3.py for it now.
⛔ "run_phase3.py run?" must be ✓ for every row — not ✗ or "skipped".

---

### Phase 4: Write Report

**▶ Pre-flight checklist — ALL boxes must be ✓ before writing a single line of the report:**
```
🔍 Pre-flight check:
□ Phase 0: bank_id, query, gold_sessions, gold_answer extracted (no CP5 fields)
□ Phase 1: fetch_session_facts run for ALL {N} gold sessions
□ Phase 1: {N} answer-relevant facts identified, each with a valid UUID id
□ Phase 2: run_phase2.py executed (not recall.py called manually)
□ Phase 2: channel_ranks is a dict (not null) in all results
□ Phase 2: classification table has exactly {N} rows — one per answer-relevant fact
□ Phase 2: noise table has ≥ 10 rows, NONE of which appear in the answer-relevant list
□ Phase 3: run_phase3.py executed for EVERY fact outside top-25 ({M} facts)
□ references/_REPORT_TEMPLATE.md read
```
⛔ Any ✗ box = incomplete audit. Fix it before writing the report. Do not write a partial report.

Read `references/_REPORT_TEMPLATE.md` for the exact template structure.

Fill in all sections with data from phases 0–4 and save to:
```
experiments/v14/diagnostic_s28/{case_id}_report.md
```

(e.g., `c001_report.md` for case c001)

---

## Auditing Multiple Cases

Run all 35 cases (c000–c034) through the 5-phase workflow. After all cases, write `experiments/v14/diagnostic_s28/SUMMARY.md` with:
- Root cause frequency table across all 35 cases
- Statistical comparison: PASS vs FAIL — what's systematically different in graph connectivity and channel_ranks?
- Priority fix ordering (fixes covering the most FAIL cases first)

---

## Quick Reference: Key Response Fields

When `--trace` is active, each result in `/memories/recall` contains:

| Field | Meaning |
|-------|---------|
| `id` | Fact UUID — use this to match answer-relevant facts |
| `document_id` | Session ID (matches gold_session_ids format) |
| `rrf_rank` | Rank within its per-fact-type RRF fusion (pre-global merge) |
| `global_rrf_rank` | Rank across ALL fact types, sorted by rrf_score (pre-CE) |
| `cross_encoder_score` | CE score (typically negative; less negative = better) |
| `score` / `combined_score` | Final score after CE × rrf_boost × recency × temporal |
| `channel_ranks.semantic` | Rank in semantic channel (null = not retrieved by semantic) |
| `channel_ranks.bm25` | Rank in BM25 channel |
| `channel_ranks.graph` | Rank in BFS graph channel |
| `channel_ranks.temporal` | Rank in temporal channel |
| `trace.query_type` | Detected query type (semantic/causal/multi_hop/etc.) |
| `trace.rrf_weights` | Per-channel RRF weights used |

`channel_ranks` being `null` (not a dict) = `--trace` was not passed. Re-run with `--trace`.
