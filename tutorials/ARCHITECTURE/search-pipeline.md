# Search/Recall Pipeline Deep Dive

## Entry Point: `recall_async`

Located at `cogmem_api/engine/memory_engine.py::recall_async`. This is the top-level recall orchestrator:

```
recall_async(query, bank_id, ...)
  ├─→ embed_query() — generate query vector
  ├─→ retrieval.resolve_query_routing() — classify intent + build RRF weights
  ├─→ retrieval.retrieve_all_fact_types_parallel() — 4-channel parallel fetch
  ├─→ retrieval.fuse_parallel_results() — weighted RRF per fact type
  ├─→ reranking.CrossEncoderReranker.rerank() — neural reranking
  ├─→ reranking.apply_combined_scoring() — recency + temporal boost
  └─→ return MultiBankRecallResult
```

The critical detail: **4 channels run in parallel** for each fact type, then their ranked candidate lists are fused with weighted RRF. The fusion happens **per fact type**, so different network types can rank differently.

## Step 1 — Query Routing (`query_analyzer.py`)

`classify_query_type()` ([query_analyzer.py](../../cogmem_api/engine/query_analyzer.py)) identifies one of **6** query types. The weights below are the actual `_ADAPTIVE_RRF_WEIGHTS` multipliers applied per channel (they are channel *multipliers*, not a probability distribution — `semantic` uses all 1.0 as the neutral baseline):

| Type | Detection Signal (regex) | sem | bm25 | graph | temp |
|------|-------------------------|-----|------|-------|------|
| `semantic` | Default — no other pattern matches | 1.0 | 1.0 | 1.0 | 1.0 |
| `temporal` | `when / today / last / ago / before / during` (or `ago/since` anchor overriding multi-hop) | 0.8 | 0.6 | 0.8 | **2.2** |
| `causal` | `why / cause / because / reason / led to / impact` | 0.8 | 0.7 | **2.4** | 1.0 |
| `prospective` | `will / future / plan / intend / goal / going to` (intention.status=planning only) | 0.9 | 0.8 | **2.0** | 1.4 |
| `preference` | `prefer / favorite / like / recommend / any tips / remind me` | 1.0 | **1.2** | 1.4 | 0.5 |
| `multi_hop` | `connect / related / between / how many / list all / across` | 0.9 | 0.7 | **2.6** | 0.8 |

> Note: there is **no** `entity` query type. Classification priority order is prospective → causal → preference → (multi-hop+temporal anchor → temporal) → multi_hop → temporal → semantic.

`DateparserQueryAnalyzer` is the default temporal extractor. It uses the `dateparser` library to convert natural language time expressions ("last month", "Q2 2025") into datetime constraints for the temporal channel.

**Why adaptive weights matter**: Equal-weight RRF (HINDSIGHT's approach) gives the same weight to all channels. This is wrong for temporal queries — the temporal channel should dominate (×2.2). Causal and multi-hop queries instead lean on the graph channel (×2.4–2.6). CogMem's adaptive routing fixes this.

## Step 2 — Four-Channel Parallel Retrieval (`retrieval.py`)

### Semantic + BM25 Channel

Combined in `retrieve_semantic_bm25_combined()`:
- **Semantic**: pgvector cosine similarity on `embedding` column. HNSW index makes this fast.
- **BM25**: PostgreSQL full-text search using `to_tsvector('english', text)`. The `search_vector` column doesn't exist as a stored column — `to_tsvector()` is applied inline.

These are combined with equal-weight RRF before the graph channel contributes.

### Graph Channel

Uses the **pluggable** `GraphRetriever` interface ([graph_retrieval.py](../../cogmem_api/engine/search/graph_retrieval.py)). The retriever is selected from `COGMEM_API_GRAPH_RETRIEVER` (default `bfs`) and can be overridden **per request** via the `graph_retriever` field on the recall payload. Four implementations exist:

| `COGMEM_API_GRAPH_RETRIEVER` | Class | Notes |
|------|-------|-------|
| `bfs` *(default)* | `BFSGraphRetriever(activation_reducer="sum")` | SUM spreading activation + 3 cycle guards |
| `bfs_max` | `BFSGraphRetriever(activation_reducer="max")` | MAX reducer — ablation toggle (commit `6e20d67`) |
| `mpfp` | `MPFPGraphRetriever` ([mpfp_retrieval.py](../../cogmem_api/engine/search/mpfp_retrieval.py)) | Meta-Path Forward Push, sublinear lazy edge loading |
| `link_expansion` | `LinkExpansionRetriever` ([link_expansion_retrieval.py](../../cogmem_api/engine/search/link_expansion_retrieval.py)) | Single-CTE expansion over entity/semantic/causal/transition edges |

**BFSGraphRetriever** implements spreading activation with 3 cycle guards:

```
Activation: A(v, t+1) = clip[reduce(A(v,t), δ·Σ(w(u,v)·A(u,t)·μ(edge)·refractory(u))), Amax]
  - reduce = SUM (default)  → raw = current + incoming   (accumulate all paths)
  - reduce = MAX (bfs_max)  → raw = max(current, incoming) (single strongest path)
  - refractory(u): 0 if u fired last step, else 1   (COGMEM_API_BFS_REFRACTORY_STEPS=1, blocks ping-pong)
  - firing_quota: node silenced after N fires        (COGMEM_API_BFS_FIRING_QUOTA=2, blocks longer cycles)
  - saturation:  A(v) ≤ Amax                          (COGMEM_API_BFS_ACTIVATION_SATURATION=2.0)
```

Entry points: nodes matching the semantic query vector (`entry_point_limit=5`, `entry_point_threshold=0.5`), with `activation_decay=0.8` and `min_activation=0.1`.

**SUM vs MAX (the default is SUM)**: MAX propagation picks only the single strongest path — if 3 weak evidence sources all point to a node, MAX keeps only the strongest and the other two are wasted. SUM accumulates all contributions, which is better for multi-hop and multi-session queries. `bfs_max` exists purely as an **ablation control** to quantify how much the SUM behaviour contributes (see [Benchmark & Ablation](benchmark-ablation.md) and `scripts/compare_sum_max_graph_only.py`).

### Temporal Channel

Filtered search: `WHERE bank_id=X AND network_type=Y AND occurred_start BETWEEN t_start AND t_end`. Returns nodes within the time window parsed from the query.

### Fusion

`weighted_reciprocal_rank_fusion()` merges all 4 channels:

```
RRF(d) = Σ w_i(q) / (60 + rank_i(d))
```

`rank_i(d)` is the position of document `d` in channel `i`'s sorted list. The constant 60 ensures documents ranked #1 in all channels don't perfectly tie.

## Step 3 — Prospective Guard

After fusion, prospective queries apply a post-filter:

```
_collect_intention_result_ids(conn, bank_id) → Set of intention node IDs with status=planning
_resolve_planning_intention_ids() → Confirm status is planning
_filter_prospective_results() → Remove any intention results where status != planning
```

This is necessary because the temporal or graph channels might retrieve an `intention` fact with status `fulfilled` or `abandoned` — these should not appear in prospective ("what are you planning?") queries.

## Step 4 — Reranking

`CrossEncoderReranker.rerank()` takes top-N candidates (default: 300) and re-scores them with a cross-encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`).

The cross-encoder scores (query, document) pairs with a learned relevance function — better than embedding cosine similarity for capturing query-document semantic fit.

`apply_combined_scoring()` then boosts by:
- **Recency**: `1 + recency_days^-0.3` — recent facts rank slightly higher
- **Temporal match**: if query has explicit time constraint, boost nodes within the window

## Cross-Encoder Fallback

If the cross-encoder model is unavailable or fails, `CrossEncoderReranker.rerank()` raises `CrossEncoderUnavailable`. The outer caller catches this and falls back to the RRF-ordered candidates directly.

This is intentional — the reranker is a quality enhancement, not a correctness requirement. Main retrieval path always succeeds.

## Document Provenance and Recall@k

Retrieved `RetrievalResult` items include `document_id` (the source document for this fact). This is used in eval for **session-level Recall@k**:

```
Recall@k = 1 if any document_id in top-k matches a gold session document_id
         0 otherwise
```

This avoids the problem of keyword-based recall being 0 for benchmarks without keyword annotations.

## Verify Commands

```bash
# Run search fork test
uv run python tests/artifacts/test_task301_search_fork.py

# Run SUM activation test
uv run python tests/artifacts/test_task302_sum_activation.py

# Run adaptive router test
uv run python tests/artifacts/test_task303_adaptive_router.py

# Check prospective guard is wired
rg "_filter_prospective_results|_collect_intention_result_ids" cogmem_api/engine/search/retrieval.py
```
