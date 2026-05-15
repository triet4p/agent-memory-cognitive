---
name: cogmem-diagnose
description: >
  Deep-diagnose root causes of CogMem pipeline failures using existing audit reports and
  checkpoint files. Use this skill whenever the user asks to diagnose, classify, or summarize
  why CogMem cases fail — e.g., "diagnose c007", "what's wrong with c000-c010", "summarize
  all failures", "classify failure types", "what's the failure pattern across cases".
  Reads from experiments/v14/diagnostic_s28/ (audit reports) and experiments/v14/checkpoints_5/
  (gold answers). Does NOT re-run any API calls — pure analysis of already-collected data.
  Always invoke this skill before the user asks to "fix" or "improve" recall/generation.
---

# CogMem Diagnose Skill

Reads existing audit reports and checkpoint files to produce a **mechanistic diagnosis** of
each CogMem failure: not just which pipeline stage broke, but WHY it broke — which specific
graph link types are weak, which session is the noise source, which prompt instruction is
missing. The output should be directly actionable for engineers fixing the pipeline.

## ⚠ Execution Rules

**Primary source is the audit report.** The files in `experiments/v14/diagnostic_s28/`
contain everything needed for most diagnoses — read them first. Call the API scripts only
when the audit report does not have enough information to complete the diagnosis (e.g., graph
analysis was not run for a specific fact, or you need to verify a rank with the live pipeline).

**Batch diagnosis: sequential cases, then cross-case synthesis.**
When diagnosing multiple cases, process them one at a time in order — complete the full
Phase 1→2 diagnosis for case N before reading anything for case N+1. Do NOT parallelize
case reads or interleave context between cases; mixing audit data from different cases
pollutes the analysis and produces wrong root-cause attributions. After ALL individual cases
are diagnosed, perform a cross-case synthesis pass: identify which failure mechanisms repeat
across cases, which fix (R1-CE, R2, R2b, G1–G4) would affect the most cases, and whether
any pair of cases share the same root cause (e.g., same noise session, same missing entity).
This synthesis is what populates the Root Cause Breakdown and Priority Fix Order sections
of DIAGNOSIS.md — do not write those sections until all cases are done.

**No shell scripting.** Never write PowerShell, bash, or curl commands to call the API.
Use only the bundled Python scripts via `uv run python`. Windows quoting breaks JSON bodies
in curl/PowerShell, and ad-hoc scripts are unreviewed. Every API call goes through a script:

```
uv run python .claude/skills/cogmem-diagnose/scripts/<script>.py --arg value
```

Run all scripts from the repo root. Use `--help` for full argument list.

---

## Available Scripts

| Script | When to use | Key args |
|--------|-------------|----------|
| `get_fact.py` | Look up full fact text/metadata by keyword or session | `--keyword`, `--document-id`, `--all` |
| `check_recall.py` | Re-run recall and locate specific fact IDs to verify rank data | `--query`, `--top-k`, `--fact-ids` |
| `get_links.py` | Check graph edges for a fact — verify/supplement graph analysis section | `--keyword`, `--link-type`, `--summarize` |
| `test_generate.py` | Run recall + generation end-to-end and compare model answer to gold | `--query`, `--gold-answer`, `--top-k` |

All scripts output JSON. All scripts require `--bank-id`. Default `--api-base` is `http://localhost:8888`.

---

## Core Rule: No Judge

**Never use `judge.correct`, `judge.score`, or judge reasoning text.**
These are unreliable. Pass/fail truth comes from `cogmem-verify` output, not the judge.

## Data Sources

For case `c{NNN}`:
- **Verdict** (required): `experiments/v14/diagnostic_s28/VERDICTS.md` — the true PASS/FAIL
  determination produced by the `cogmem-verify` skill. Read this first. If VERDICTS.md does
  not exist, run `cogmem-verify` before proceeding with diagnosis.
- **Audit report**: `experiments/v14/diagnostic_s28/c{NNN}_report.md` — classification
  table, graph analysis, channel_ranks, noise analysis
- **Checkpoint**: `experiments/v14/checkpoints_5/E7_full_c{NNN}.json` — `gold_answer`
  and any `Note:` lines from the verify step (diagnostically useful thinking-block findings)

If the audit report does not exist → label `Audit pending`, skip.

**Use the verdict from VERDICTS.md as the starting point for each case:**
- `PASS` → apply Rule 7 directly; confirm facts are in top-25 and stop.
- `FAIL` → apply Rules 1–6 in priority order to find the root cause.
- Any `Note:` line from the verify step (e.g., "model double-counted F-15 scale variants
  during reasoning") is a strong hint for which generation rule to apply — use it.

---

## Phase 1: Read and extract

For each case, extract from the audit report:

**From "Answer-Relevant Facts" section:**
- List of answer-relevant fact IDs and which gold answer component they cover
- Any "no fact found in bank" entries → Retain candidates

**From "Answer-Relevant Fact Classification" table:**
- For each fact: Rank, CE score, Semantic rank, BM25 rank, Graph rank, Temporal rank, Classification label

**From "Noise Analysis" section:**
- Type A noise entries (non-gold document_id) at ranks 1–10: count, session IDs, text snippets
- Type B noise entries (gold document_id but non-relevant) at ranks 1–10: count, text snippets
- Generation impact note (verbatim, from report)

**From "Graph Analysis" section (if present):**
- For each analyzed fact: connectivity_class, connectivity_evidence, per-link-type counts and avg_weight

**From checkpoint:**
- `gold_answer` — for sanity check that the report covers the right components

---

## Phase 2: Apply diagnosis rules (priority order)

Apply rules in order. A case may match multiple rules — list all that apply.

### Rule 1 — Retain

**Trigger:** Any gold answer component has no covering fact in the bank.

**Deep diagnosis:**
- Which component is missing (name it from the gold answer)
- Check: does any gold session contain a fact that partially covers this component but wasn't
  matched? (Look for adjacent facts in the report's Answer-Relevant Facts table)
- Likely cause:
  - **Extraction miss**: LLM extraction prompt didn't identify this fact type (e.g., assistant
    recommendation, numerical value, specific name not in user utterance)
  - **Wrong fact type**: fact was stored under a different type that didn't surface
  - **Session boundary**: the fact appeared in a session not in gold_session_ids (cross-session retain)
- Fix direction: Retain pipeline — extraction prompt, fact type coverage, or session scoping

---

### Rule 2 — Recall/Miss

**Trigger:** Classification table has "Channel-level miss" or "RRF dilution" for any fact.

**Deep diagnosis:**
- Note the fact's channel_ranks: which channels are null, which are > 100
- Check if graph analysis section covers this fact:
  - **Isolated** (≤1 link total): fact has no graph edges → BFS cannot reach it regardless of
    entry point. Root cause: entity extraction failed for this fact's key terms, so no entity
    links were created at retain time.
  - **Weakly connected** (only semantic links or links to non-gold): BFS reaches it but via
    weak paths that don't survive the activation threshold
  - **BFS-diluted** (links exist but cross-session links consume BFS budget): high-weight links
    go to non-gold sessions → activation spreads away from target fact → it gets no graph rank
  - If graph analysis not present in report: note which channels were null and why likely
    (semantic=null → vocabulary gap; bm25=null → key term not in tsvector; graph=null → isolated)
- Fix direction: depends on root:
  - Isolated → R2b entity extraction fix (add specific named entities)
  - BFS-diluted → R2 cross-session threshold (0.6 → 0.75)
  - Vocabulary gap → embedding model limitation (hard to fix in Wave-1)

---

### Rule 3 — Recall/CE

**Trigger:** Classification table has "CE suppression" — fact is in top-300, at least one
channel rank ≤ 20, but CE score pushed it below the top-25 cutoff.

**Deep diagnosis — this needs the most detail:**
- State the fact's rank in top-300, CE score, and best channel rank
- Check graph analysis section:
  - What is the connectivity_class? Copy connectivity_evidence verbatim.
  - Which link types have count > 0? Focus on entity and causal links (strongest for BFS).
  - Cross-session link count: high cross-session → BFS budget diluted → fact gets weak graph
    activation → low rrf_rank → even with good channel rank, combined_score was marginal before CE
- Compute the CE gap: what was the combined_score at rank 25 vs this fact?
  If the gap is < 10%, the fix is R1-CE (rrf_boost α parameter).
  If the gap is > 20%, the graph channel rank itself is the problem → fix graph connectivity first.
- Fix direction:
  - Small CE gap: R1-CE rrf_boost (increase α or verify it's applied)
  - Large CE gap + BFS-diluted: R2 threshold first to improve rrf_rank, then R1-CE boost
  - Large CE gap + Isolated: R2b entity extraction to create graph edges

---

### Rule 4 — Recall/Weak

**Trigger:** All answer-relevant facts are in top-25, but at least one has rank 16–25.

**Deep diagnosis:**
- List the facts at rank 16–25, their CE scores, and channel_ranks
- Is the weak rank driven by graph channel being null (graph=null → lower rrf_score → lower rank)?
- Or is CE score mediocre but not suppressive?
- This is a borderline state: the model CAN see the fact, but it's crowded out by higher-ranked
  noise and non-relevant facts at the bottom of the context window
- Fix direction: improve graph channel rank for the specific fact (R2b entity extraction or R2
  threshold) to push it into top-15 naturally

---

### Rule 5 — Generation/Noise

**Trigger:** All answer-relevant facts at rank ≤ 15, but ≥ 3 Type A entries (non-gold session)
at ranks 1–10.

**Deep diagnosis:**
- Name the noise session(s) — what is this session about? (read text snippets from noise table)
- How many Type A entries from this session appear in top-25 total vs ranks 1–10?
- Why did this session rank so high? Two mechanisms:
  - **Cross-session semantic links** (threshold 0.6): noise session was linked to gold session
    via semantic similarity → BFS activated noise facts → high graph rank → high RRF → survived CE
  - **BM25 keyword overlap**: noise session contains domain keywords (e.g., "project", "wedding")
    that match the query → high BM25 rank even without semantic relevance
- What specific confusion does the noise cause? Read the noise text snippets and explain how the
  model likely miscounted or misidentified based on them.
- Fix direction:
  - Cross-session links: R2 threshold (0.6 → 0.75) to prune weak cross-session edges
  - Session coherence: R4 singleton/session penalty to demote sessions with 1–2 facts
  - If noise session has many facts (4+), R4 alone won't help → R2 is primary fix

---

### Rule 6 — Generation

**Trigger:** All answer-relevant facts at rank ≤ 15, noise at ranks 1–10 minimal (< 3 Type A),
no retain/recall issue.

**Deep diagnosis:**
- Confirm: list all answer-relevant facts with their ranks (all should be ≤ 15)
- Identify Type B noise (gold-session, non-relevant) at ranks 1–10: which ones could cause
  miscounting or misinterpretation? (e.g., planning facts that add extra entities, scale variants
  of the same kit, duplicate session references)
- What is the likely generation error mechanism?
  - **Counting error**: model counted adjacent/planning facts as distinct instances
  - **Entity mismatch**: fact uses a different name than the query entity
  - **Scale variant**: same item in different sizes counted as two items
  - **Temporal confusion**: model mixed up "old value" and "updated value" from different sessions
  - **Incomplete enumeration**: model found the first matching fact and stopped
- Fix direction: G1–G4 generation prompt fixes — cite which specific instruction is needed
  (e.g., "count only explicitly purchased items", "scale variants count as one", "prefer
  most recent session for updated values")

---

### Rule 7 — Pass / Pass/Weak

**Trigger:** All answer-relevant facts recalled, no retain/recall issues found.

- `Pass`: all facts at rank ≤ 15
- `Pass/Weak`: facts recalled but some at rank 16–25 (currently passing, fragile)

---

## Phase 3: Output

Read `references/_DIAGNOSIS_TEMPLATE.md` for the exact output format before writing any diagnosis.

Save batch output to: `experiments/v14/diagnostic_s28/DIAGNOSIS.md`
