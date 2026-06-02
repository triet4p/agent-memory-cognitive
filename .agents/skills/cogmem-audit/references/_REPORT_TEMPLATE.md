# CogMem Audit Report Template

Save each report to: `experiments/v14/diagnostic_s28/{case_id}_report.md`

**STRICT RULES for filling this template:**
- Use these exact section headings — do not rename, reorder, or add sections
- Every table must be complete — no truncation, no "..." rows, no "showing 3 of 25"
- Exit gate blocks (✅ Phase N) are working notes only — do NOT copy them into this file
- The Answer-Relevant Facts section contains ONLY the table — do NOT include Step 1.1/1.2/1.3 headers, decomposition text, or session fetch summaries from the workflow
- `run_phase2.py` top25 output has 25 rows → the "Full Top-25" table has 25 rows
- `run_phase2.py` top300_extended output → every row goes into "In top-300 but outside top-25" — do NOT filter to gold-only or answer-relevant-only
- `run_phase3.py` summary_table has 7 rows → the Graph Analysis table has 7 rows (including 0-count types)
- **All UUIDs must be complete 36-char format** (e.g., `c450e31f-bfea-4d1c-9037-c7fb924f7f9f`) — never truncate to 8 chars, never use `????` or `...`
- **Do NOT add "CP5 Judge Result"** or any `judge.correct`/`judge.score` fields — these are not part of this report
- **Noise Analysis must use the pipe-table format** — never replace with a prose summary, even if noise count is 0 (show empty table with a note row)
- **Answer-Relevant Fact Classification: one row per UUID** — never group facts by category, type, or component label

---

```markdown
# Diagnostic Report: {case_id}

**Date:** {today}
**Bank:** {bank_id}

---

## Query & Answer

**Query:** {query}
**Gold Answer:** {gold_answer}
**Category:** {category}
**Query Type (live):** {from trace.query_type}
**RRF Weights (live):** semantic={w}, bm25={w}, graph={w}, temporal={w}

---

## Answer-Relevant Facts

Matched from gold sessions against gold answer components. Each row covers one discrete component of the gold answer.

| # | Gold Answer Component | ID (full UUID) | Document ID | Type | Text (truncated to 120 chars) |
|---|-----------------------|----------------|------------|------|-------------------------------|

Total: {N} answer-relevant facts across {M} gold sessions. Retain failures (no fact in bank): {list components or "none"}.

---

## Recall Audit

### Full Top-25 (all 25 rows — do not truncate)

| Rank | ID (full UUID) | Document ID | Gold? | RRF Rank | Global RRF | CE Score | Final Score | Semantic | BM25 | Graph | Temporal | Text (80 chars) |
|------|----------------|-------------|-------|----------|-----------|---------|------------|---------|------|-------|---------|-----------------|

### Answer-Relevant Fact Classification (one row per fact — no exceptions)

| # | ID (full UUID) | Session | In Top-25? | Rank (top-300) | Global RRF | CE Score | Semantic | BM25 | Graph | Temporal | Classification |
|---|----------------|---------|-----------|---------------|-----------|---------|---------|------|-------|---------|----------------|

Classification labels: **Recalled correctly** | **CE suppression** | **RRF dilution** | **Channel-level miss** | **Retain failure (absent from bank)**

Facts outside top-25 (require Phase 3): {list ids, or "none"}

**Summary:** {X}/{N} correctly recalled | {Y}/{N} in 26–300 | {Z}/{N} channel-level miss | {W}/{N} retain failure

### In top-300 but outside top-25 (ALL rows from run_phase2.py top300_extended output — do not filter by gold_tag or relevance)

| Rank | Global RRF | CE Score | Semantic | BM25 | Graph | Temporal | Classification | Text |
|------|-----------|---------|---------|------|-------|---------|---------------|------|

### Missing from top-300

| # | Document ID | Gold Answer Component | Text | Note |
|---|------------|----------------------|------|------|

---

## Noise Analysis (top-25)

Two types: **A = session noise** (non-gold document_id) | **B = fact noise** (gold document_id but not answer-relevant)

| Rank | ID (full UUID) | Document ID | Type | CE Score | Semantic | BM25 | Graph | Text Snippet |
|------|----------------|------------|------|---------|---------|------|-------|-------------|

Generation impact: {note whether noise at high ranks could cause miscounting or confusion}

---

## Graph Analysis (facts outside top-25)

Run once per fact using `run_phase3.py`. All 7 link types must appear — include rows with count=0.

### Fact: "{text snippet}" (id: {id}, global_rrf_rank: {N})

| Link Type | Count | Avg Weight | Cross-Session Count | Cross-Session to Non-Gold | Sample (from → to, weight) |
|-----------|-------|-----------|--------------------|--------------------------|-----------------------------|
| entity    |       |            |                    |                          |                             |
| semantic  |       |            |                    |                          |                             |
| causal    |       |            |                    |                          |                             |
| temporal  |       |            |                    |                          |                             |
| s_r_link  |       |            |                    |                          |                             |
| a_o_causal|       |            |                    |                          |                             |
| transition|       |            |                    |                          |                             |

**Connectivity class:** {Well-connected / Weakly connected / Isolated / BFS-diluted}
**Evidence:** {one-line from run_phase3.py connectivity_evidence — do not interpret, copy as-is}
```
