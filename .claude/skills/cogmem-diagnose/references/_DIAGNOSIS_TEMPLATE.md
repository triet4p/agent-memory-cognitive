# CogMem Diagnosis Output Templates

Read this file before writing any output in Phase 3.

---

## Single Case

```
c{NNN} — {Label} [+ {Label2} if multiple]

{LABEL}:
  Fact {short_id} ("{text snippet}") — {classification from audit report}
  channel_ranks: semantic={N|null}, bm25={N|null}, graph={N|null}, temporal={N|null}
  Graph: {connectivity_class} — {connectivity_evidence verbatim}
  Root: {specific mechanism — e.g., "Entity X not extracted → no entity links → BFS cannot reach"}
  Fix: {specific fix reference — e.g., R2b entity extraction / R1-CE rrf_boost / R2 threshold}

{LABEL2} (if applicable):
  ...
```

**Example (c007):**
```
c007 — Generation/Noise + Recall/Miss

RECALL/MISS:
  Fact 9648370e ("User's friend Jen got married last weekend") — channel-level miss
  channel_ranks: semantic=null, bm25=null, graph=null, temporal=null
  Graph: Isolated — no entity/causal links found for "Jen Tom wedding"
  Root: Entity "Jen" not extracted as named entity → no graph edges → BFS cannot reach this fact
  Fix: R2b entity extraction — add wedding participant names as entities

GENERATION/NOISE:
  Noise session: answer_81b971b8_2 (user's sister's wedding — different persona)
  3 Type A entries at ranks 4, 22 — "User feels a high from attending sister's wedding"
  Why high rank: cross-session semantic links (threshold 0.6) activated noise via BFS
  Confusion: sister's wedding looks identical to gold entries → model counts 4 instead of 3
  Fix: R2 cross-session threshold (0.6 → 0.75) to prune sister's wedding session links
```

---

## Batch — write to `experiments/v14/diagnostic_s28/DIAGNOSIS.md`

```markdown
# CogMem Failure Diagnosis

Generated: {date}
Cases: {N} total — {pass} Pass, {pass_weak} Pass/Weak, {fail_count} with failures, {audit_pending} Audit pending

## Diagnosis Table

| Case | Gold Answer | Label | Mechanism (one line) |
|------|-------------|-------|----------------------|
| c000 | 2 | Generation/Noise | 11 Type A facts from 2e4430d8_2 at ranks 1–2; BM25 overlap on "project" |
| c001 | 5 kits | Recall/CE | Tiger I rank 27; BFS-diluted (6 cross-session links); CE gap 9% → R1-CE + R2 |
| c007 | 3 weddings | Generation/Noise + Recall/Miss | sister's wedding at rank 4; Jen fact isolated |
| ...  | ...         | ...   | ... |

## Failure Summary

| Label | Count | Cases |
|-------|-------|-------|
| Retain | N | c???, ... |
| Recall/Miss | N | c???, ... |
| Recall/CE | N | c???, ... |
| Recall/Weak | N | c???, ... |
| Generation/Noise | N | c???, ... |
| Generation | N | c???, ... |
| Pass | N | c???, ... |
| Pass/Weak | N | c???, ... |
| Audit pending | N | c???, ... |

## Root Cause Breakdown (for engineers)

Group by mechanism — these map directly to code fixes:

### Cross-session noise (→ R2: raise threshold 0.6 → 0.75)
Cases: {list} — noise session IDs and Type A count at ranks 1–10

### Graph isolation (→ R2b: entity extraction for specific terms)
Cases: {list} — fact IDs and missing entity terms

### CE suppression, small gap < 10% (→ R1-CE: verify rrf_boost α)
Cases: {list} — fact ranks and CE gap %

### CE suppression, large gap > 20% (→ R2/R2b first, then R1-CE)
Cases: {list} — fact ranks and connectivity class

### Generation prompt gaps (→ G1–G4: specific instruction per case)
Cases: {list} — error mechanism per case (counting / entity mismatch / scale variant / temporal)

## Priority Fix Order

1. {most common mechanism} — {N} cases — {specific fix}
2. ...
```
