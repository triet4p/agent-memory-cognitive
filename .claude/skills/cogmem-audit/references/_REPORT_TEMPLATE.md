# CogMem Audit Report Template

Save each report to: `experiments/v14/diagnostic_s28/{case_id}_report.md`

---

```markdown
# Diagnostic Report: {case_id}

**Date:** {today}
**Bank:** {bank_id}
**CP5 Result:** PASS / FAIL (score: {score})

---

## Query & Answer

**Query:** {query}
**Gold Answer:** {gold_answer}
**Category:** {category}
**Query Type (live):** {from trace}
**RRF Weights (live):** semantic={w}, bm25={w}, graph={w}, temporal={w}

---

## Answer-Relevant Facts

Identified from gold sessions using LLM judgment on `text` field only.

| # | Document ID | Type | Text (truncated to 120 chars) |
|---|------------|------|-------------------------------|

Total: {N} answer-relevant facts across {M} gold sessions.

---

## Recall Audit

### Correctly Recalled (in top-25)
| Rank | RRF Rank | Global RRF | CE Score | Final Score | Semantic | BM25 | Graph | Temporal | Text |
|------|---------|-----------|---------|------------|---------|------|-------|---------|------|

### In top-300 but outside top-25
| Rank | Global RRF | CE Score | Semantic | BM25 | Graph | Temporal | Root Cause | Text |
|------|-----------|---------|---------|------|-------|---------|-----------|------|

### Missing from top-300 (channel-level miss)
| # | Document ID | Text | Root Cause |
|---|------------|------|-----------|

**Summary:** {X}/{N} correctly recalled | {Y}/{N} in 26-300 | {Z}/{N} completely missing

---

## Noise Analysis (top-10, non-gold)

| Rank | Document ID | Session Type | CE Score | Semantic | Graph | Text Snippet |
|------|------------|-------------|---------|---------|-------|-------------|

---

## Graph Analysis (channel-level misses only)

### Fact: "{text snippet}"

| Link Type | Count | Avg Weight | Cross-Session? | Connected To (text snippet) |
|-----------|-------|-----------|---------------|--------------------------|

**Connectivity:** [Well-connected / Weakly connected / Isolated / BFS-diluted]

---

## Root Cause Summary

| Missing Fact | Root Cause | Evidence | Confidence |
|-------------|-----------|---------|-----------|

---

## Recommended Fix

- **Wave-1 (no re-retain):** ...
- **Wave-2 (re-retain required):** ...
- **Generation prompt:** ...
```
