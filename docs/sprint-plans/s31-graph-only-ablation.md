# S31 — Graph-Only Ablation Study (E7G–E11G)

## Motivation

E7–E11 ablations run with the full 4-channel stack (semantic + BM25 + graph + temporal) plus CE reranking. The CE reranker assigns identical scores to facts with identical text, regardless of which graph channel found them. This **masks graph-channel differences**: if a fact's text is the same whether it was retrieved via habit nodes or not, CE produces the same combined_score → same rank → no observable E8 vs E7 difference.

**Graph-only mode** eliminates this masking by:
1. Zeroing semantic/BM25/temporal RRF weights → only BFS graph activation contributes to `rrf_score`
2. Skipping CE reranking → `rrf_score` is the final ranking signal

With graph-only mode, any rank difference between E7G and E8G–E11G is **directly attributable** to the removed node type's contribution to BFS spreading activation.

---

## What Changes (3 files, 1 new profile variant)

### 1. `cogmem_api/engine/query_analyzer.py` — Add `GraphOnlyQueryAnalyzer`

```python
class GraphOnlyQueryAnalyzer(QueryAnalyzer):
    """Returns graph-only RRF weights: graph=1.0, all other channels=0.0.

    Pair with skip_reranker=True for pure graph ablation.
    """

    def load(self) -> None:
        pass

    def analyze(self, query: str, reference_date: datetime | None = None) -> QueryAnalysis:
        return QueryAnalysis(
            temporal_constraint=None,
            query_type="multi_hop",
            rrf_weights={"semantic": 0.0, "bm25": 0.0, "graph": 1.0, "temporal": 0.0},
        )
```

### 2. `cogmem_api/api/http.py` — Add `skip_reranker` + `graph_only` to `RecallRequest`

```python
class RecallRequest(BaseModel):
    ...
    skip_reranker: bool = False   # NEW: bypass CE, rank by rrf_score only
    graph_only: bool = False      # NEW: zero semantic/BM25/temporal weights
```

Pass through in `recall_memories` handler:
```python
recall_result = await app.state.memory.recall_async(
    ...
    skip_reranker=payload.skip_reranker,
    graph_only=payload.graph_only,
)
```

### 3. `cogmem_api/engine/memory_engine.py` — Wire `skip_reranker` + `graph_only` through `recall_async`

Add parameters:
```python
async def recall_async(
    self,
    ...
    skip_reranker: bool = False,
    graph_only: bool = False,
) -> dict[str, Any]:
```

Select query analyzer:
```python
from cogmem_api.engine.query_analyzer import FlatQueryAnalyzer, GraphOnlyQueryAnalyzer
if graph_only:
    query_analyzer_override = GraphOnlyQueryAnalyzer()
elif not adaptive_router:
    query_analyzer_override = FlatQueryAnalyzer()
else:
    query_analyzer_override = None
```

Restructure the CE block (lines ~621–688) to add `skip_reranker` fast path:
```python
if merged_candidates:
    candidate_limit = min(...)
    top_candidates = merged_candidates[:candidate_limit]

    if skip_reranker:
        from cogmem_api.engine.search.types import ScoredResult
        scored = [
            ScoredResult(candidate=c, cross_encoder_score=0.0, cross_encoder_score_normalized=c.rrf_score)
            for c in top_candidates
        ]
        for sr in scored:
            sr.combined_score = sr.candidate.rrf_score
            sr.weight = sr.combined_score
        cross_encoder_ok = True
    else:
        try:
            # ... existing CE block with R4 singleton penalty + C-1 floor ...
            cross_encoder_ok = True
        except Exception as ce_exc:
            # ... existing fallback ...
```

### 4. `scripts/eval_cogmem.py` — Add E7G–E11G profiles

Add to `AblationProfile` dataclass:
```python
@dataclass(frozen=True)
class AblationProfile:
    ...
    skip_reranker: bool = False
    graph_only: bool = False
```

Add profiles:
```python
"E7G": AblationProfile(
    profile_id="E7G",
    description="E7 graph-only (no CE, graph channel only)",
    enabled_networks=("world", "experience", "opinion", "habit", "intention", "action_effect"),
    recall_fact_types=("world", "experience", "opinion", "habit", "intention", "action_effect"),
    adaptive_router_enabled=True,
    sum_activation_enabled=True,
    skip_reranker=True,
    graph_only=True,
),
"E8G": AblationProfile(..., enabled_networks=(...no habit...), skip_reranker=True, graph_only=True),
"E9G": AblationProfile(..., enabled_networks=(...no intention...), skip_reranker=True, graph_only=True),
"E10G": AblationProfile(..., enabled_networks=(...no action_effect...), skip_reranker=True, graph_only=True),
"E11G": AblationProfile(..., enabled_networks=("world","experience","opinion"), skip_reranker=True, graph_only=True),
```

Update `build_recall_payload`:
```python
payload: JsonDict = {
    ...
    "skip_reranker": profile.skip_reranker,
    "graph_only": profile.graph_only,
}
```

---

## How to Run

```powershell
# E7G: full CogMem, graph-only ranking
.\scripts\eval_cogmem_batch.ps1 -VERSION v16 -PROFILE_ E7G -START_INDEX 0 -END_INDEX 34

# E8G: minus habit, graph-only ranking
.\scripts\eval_cogmem_batch.ps1 -VERSION v16 -PROFILE_ E8G -START_INDEX 0 -END_INDEX 34

# ... E9G, E10G, E11G similarly
```

Checkpoints land in `experiments/v16/checkpoints-cross-fact-type/E7G_full_c*.json`.

---

## Expected Outcome

| Profile | Hypothesis |
|---------|-----------|
| E7G vs E7 | E7G accuracy lower (CE adds signal beyond graph) |
| E7G vs E8G | Gap = habit's graph contribution |
| E7G vs E11G | Largest gap = all 3 CogMem types' graph contribution |

If E7G ≈ E8G ≈ E11G, then CogMem-specific graph edges carry no unique recall signal and the contribution seen in E7 comes from CE + multi-channel consensus.

If E7G >> E11G, then graph edges from habit/intention/action_effect directly cause recall improvements measurable without CE.

---

## Files to Modify (3)

| File | Change |
|------|--------|
| `cogmem_api/engine/query_analyzer.py` | Add `GraphOnlyQueryAnalyzer` class |
| `cogmem_api/api/http.py` | Add `skip_reranker`, `graph_only` to `RecallRequest`; pass to `recall_async` |
| `cogmem_api/engine/memory_engine.py` | Add params + restructure CE block with `skip_reranker` guard |
| `scripts/eval_cogmem.py` | Add fields to `AblationProfile`; add E7G–E11G; update `build_recall_payload` |

---

## Prerequisites

- E7–E11 runs complete on v16 bank (baseline comparison)
- v16 bank retained with cross_fact_type=True
