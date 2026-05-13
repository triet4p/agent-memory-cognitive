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

## Purpose

This skill runs a 5-phase diagnostic on a CogMem test case to answer:
> "Why does this case pass or fail? Which specific facts are missing from recall, and what is blocking them?"

The key principle is the distinction between **answer-relevant facts** (facts whose `text` field contains information that directly supports the correct answer) versus all facts in a gold session. A gold session can contain dozens of facts about painting techniques, tools, and preferences, but only 1–2 of them may be needed to answer the question correctly. We care only about those.

---

## Prerequisites

- CogMem API running at `http://localhost:8888`
- Checkpoint files at `experiments/v14/checkpoints_5/E7_full_c{NNN}.json`
- Output directory: `experiments/v14/diagnostic_s28/` (create if missing)
- Bank ID format: `COGMEM_EXP_v14_e567_c{NNN}` (e.g., `COGMEM_EXP_v14_e567_c001`)

---

## The 5-Phase Workflow

### Phase 0: Load Case Context

Read the checkpoint file:
```
experiments/v14/checkpoints_5/E7_full_c{NNN}.json
```

Extract from `questions[0]`:
- `query` — the user's question
- `gold_answer` — the correct answer
- `gold_session_ids` — list of document_id strings (e.g., `["answer_593bdffd_1", "answer_593bdffd_3"]`)
- `recall_results` — CP5 recalled facts (for reference only; Phase 2 uses the live API)
- `judge.correct`, `judge.score` — CP5 pass/fail

Top-level: `bank_id`, `metrics.judge_accuracy`.

---

### Phase 1: Identify Answer-Relevant Facts

Goal: Find which specific facts from the gold sessions contain the information needed to answer the question correctly. These are the diagnostic target — the facts that must be in top-25 for the model to answer correctly.

**Step 1.1: Fetch facts per gold session using the document_id filter**

For each session ID in `gold_session_ids`:
```
GET http://localhost:8888/v1/default/banks/{bank_id}/facts?document_id={session_id}&limit=100
```

This returns only facts belonging to that session — no client-side filtering needed. Collect all facts across all gold sessions.

Response is a JSON array. Each item:
```json
{
  "id": "uuid-string",
  "text": "User started working on a 1/16-scale German Tiger I tank diorama...",
  "fact_type": "experience",
  "document_id": "answer_593bdffd_3",
  "event_date": "2023-05-27T...",
  "raw_snippet": "..."
}
```

**Step 1.2: Identify answer-relevant facts using LLM judgment**

Given:
- `query`: the question
- `gold_answer`: the correct answer
- All facts collected from gold sessions

Judge each fact: does this fact's **`text` field** contain information that directly supports arriving at the correct answer?

**Rules for judgment:**
- Use only the `text` field — never `raw_snippet` (`raw_snippet` is raw conversation context, too noisy for this judgment)
- A fact is answer-relevant if its text contains a specific piece of information that contributes to the gold answer (e.g., for a counting question, each countable entity; for a factual question, the specific value)
- A fact is NOT answer-relevant merely because it's from a gold session — only include it if its text content is genuinely needed
- Be inclusive for multi-part answers (e.g., if gold_answer lists 5 items, include facts covering each item)
- Think of it this way: if the model only saw these filtered facts (plus noise), would it produce the correct answer?

Output: list of answer-relevant facts — `[{id, document_id, text, fact_type}]`

---

### Phase 2: Two-Level Recall Audit

Goal: Determine whether missing facts are a channel-level miss (never retrieved) or a ranking issue (retrieved but scored too low). Use two recall calls to distinguish.

**Step 2.1: Standard recall (top_k=25)**
```
POST http://localhost:8888/v1/default/banks/{bank_id}/memories/recall
Content-Type: application/json

{"query": "{query}", "top_k": 25, "trace": true}
```

Response:
```json
{
  "results": [
    {
      "id": "uuid",
      "text": "...",
      "type": "experience",
      "score": 0.0023,
      "cross_encoder_score": -6.39,
      "rrf_score": 0.064,
      "rrf_rank": 3,
      "global_rrf_rank": 5,
      "document_id": "answer_593bdffd_3",
      "chunk_id": "...",
      "channel_ranks": {"semantic": 5, "bm25": null, "graph": 2, "temporal": null}
    }
  ],
  "trace": {
    "query_type": "multi_hop",
    "rrf_weights": {"semantic": 1.0, "bm25": 0.8, "graph": 2.4, "temporal": 0.5},
    "fact_types": ["world", "experience", "opinion", "habit", "intention", "action_effect"],
    "timings": {...},
    "cross_encoder_ok": true
  }
}
```

The `trace` shows which query type was classified and what RRF weights were applied — this is critical for understanding channel bias.

**Step 2.2: Wide-net recall (top_k=300)**
```
POST http://localhost:8888/v1/default/banks/{bank_id}/memories/recall
Content-Type: application/json

{"query": "{query}", "top_k": 300, "trace": true}
```

The wide-net recall exposes facts ranked 26–300, giving access to `global_rrf_rank` and `channel_ranks` for facts that the CE batch saw but ranked too low.

**Step 2.3: Classify each answer-relevant fact**

| Situation | Evidence | Root Cause Label |
|-----------|---------|-----------------|
| In top-25 | Appears in Step 2.1 results | **Recalled correctly** |
| In ranks 26–300 with good `channel_ranks` | Appears in Step 2.2 but not 2.1; has channel rank ≤ 20 in at least one channel | **CE suppression** — fact reached CE but scored too low |
| In ranks 26–300 with poor `channel_ranks` | Appears in Step 2.2 but not 2.1; all channel ranks are null or > 100 | **RRF dilution** — very low multi-channel signal, CE didn't help |
| Not found in top-300 | Absent from both recalls | **Channel-level miss** — needs graph analysis (Phase 3) |

**Step 2.4: Collect noise facts**

From Step 2.1 results: facts where `document_id` is NOT in `gold_session_ids` and rank ≤ 10. Record their `channel_ranks` and CE scores — this shows how noise competes with gold facts.

---

### Phase 3: Graph Analysis for Channel-Level Misses

Run this phase only for answer-relevant facts absent from top-300 (confirmed channel-level miss).

**Step 3.1: Search links touching the missing fact**

Use distinctive keywords from the fact's `text`:
```
GET http://localhost:8888/v1/default/banks/{bank_id}/relationships/search?keyword={keyword}&limit=200
```

**Step 3.2: Probe all 7 link types**
```
GET http://localhost:8888/v1/default/banks/{bank_id}/relationships/search?keyword={keyword}&link_type={type}&limit=100
```
For each of: `entity`, `semantic`, `causal`, `temporal`, `s_r_link`, `a_o_causal`, `transition`

Response items:
```json
{
  "from_unit_id": "uuid",
  "from_document_id": "answer_593bdffd_3",
  "from_fact_type": "experience",
  "from_text": "...",
  "to_unit_id": "uuid",
  "to_document_id": "answer_593bdffd_1",
  "to_fact_type": "experience",
  "to_text": "...",
  "link_type": "entity",
  "transition_type": null,
  "weight": 0.85
}
```

**Step 3.3: Assess BFS reachability**

For each link found, ask:
- Is the connected fact (`from_text` / `to_text`) semantically similar to the query? (Is it a likely BFS entry point?)
- Is the link weight strong (> 0.7) or weak (< 0.4)?
- Does the link cross sessions (different `document_id`)? Cross-session semantic links consume BFS budget

Classify the missing fact's connectivity:

| Class | Condition |
|-------|-----------|
| **Well-connected** | ≥ 2 strong entity/causal links (weight > 0.7) to facts in the same session |
| **Weakly connected** | Only low-weight semantic links or links to non-gold sessions |
| **Isolated** | ≤ 1 link total or no links — completely cut off from BFS |
| **BFS-diluted** | Has links, but they route BFS toward non-gold sessions first (cross-session semantic links at threshold=0.6) |

---

### Phase 4: Root Cause Classification

Synthesize from Phases 2 and 3:

| Root Cause | Indicators | Sprint Fix |
|-----------|-----------|------------|
| **CE suppression** | In top-300, good channel_ranks, but CE score very negative | R1-CE: rrf_boost formula |
| **RRF dilution** | In top-300, all channel_ranks null/high — low multi-channel signal | Improve embedding or BM25 coverage |
| **Graph isolation** | Not in top-300; few/no links to BFS entry points | R2b: entity extraction for model names |
| **BFS dilution** | Not in top-300; has cross-session links consuming BFS budget | R2: threshold 0.6 → 0.75 (Wave-2) |
| **Embedding gap** | Not in top-300; semantic_rank null; BM25 rank null | Query vocabulary mismatch — hard to fix without re-embed |
| **Generation error** | All answer-relevant facts in top-25 but model answers wrong | G1/G2/G3/G4 generation prompt fixes |

A case can have multiple root causes across different missing facts.

---

### Phase 5: Write Report

Read the full report template from `references/_REPORT_TEMPLATE.md` and fill it in with the data collected across phases 0–4. Save the completed report to `experiments/v14/diagnostic_s28/{case_id}_report.md`.

---

## Auditing Multiple Cases

When auditing a set of cases (e.g., all 11 FAIL cases from CP5), run each case through the 5-phase workflow and save individual reports. After all audits, create `experiments/v14/diagnostic_s28/SUMMARY.md` with:

- Root cause frequency table (how many FAIL cases have each root cause)
- Pattern comparison: PASS cases vs FAIL cases — what's systematically different about their graph connectivity and channel_ranks?
- Priority fix ordering (fixes covering the most FAIL cases first)

---

## Key Constraints

- **Only `text` field** for answer-relevance judgment — never `raw_snippet`
- **Live API** for recall (not checkpoint data) — checkpoint was before recent reverts
- **Two recall calls** (top_k=25 and top_k=300) are both required for complete diagnosis
- `document_id` in API responses matches the `gold_session_ids` format exactly (e.g., `answer_593bdffd_3`)
- All 7 link types must be checked for channel-level misses: `entity`, `semantic`, `causal`, `temporal`, `s_r_link`, `a_o_causal`, `transition`
