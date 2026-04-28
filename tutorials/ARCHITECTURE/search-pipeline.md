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

`classify_query_type()` identifies one of 6 query types:

| Type | Detection Signal | RRF Weights |
|------|-----------------|-------------|
| `semantic` | Descriptive text, no entity/time signals | sem=0.50, bm25=0.20, graph=0.20, temp=0.10 |
| `temporal` | Date/time expressions | sem=0.20, bm25=0.20, graph=0.20, temp=0.40 |
| `entity` | Named entities, proper nouns | sem=0.20, bm25=0.30, graph=0.40, temp=0.10 |
| `causal` | "Why / because / reason" | sem=0.10, bm25=0.10, graph=0.40, temp=0.10 (+ Action-Effect priority) |
| `prospective` | "Planning /打算/sắp" | sem=0.20, bm25=0.15, graph=0.35, temp=0.30 (intention.status=planning only) |
| `multi_hop` | Relational pronouns, indirect reference | sem=0.15, bm25=0.10, graph=0.50, temp=0.25 |

`DateparserQueryAnalyzer` is the default temporal extractor. It uses the `dateparser` library to convert natural language time expressions ("last month", "Q2 2025") into datetime constraints for the temporal channel.

**Why adaptive weights matter**: Equal-weight RRF (HINDSIGHT's approach) gives `w=0.25` to all channels. This is wrong for temporal queries — the temporal channel should dominate. CogMem's adaptive routing fixes this.

## Step 2 — Four-Channel Parallel Retrieval (`retrieval.py`)

### Semantic + BM25 Channel

Combined in `retrieve_semantic_bm25_combined()`:
- **Semantic**: pgvector cosine similarity on `embedding` column. HNSW index makes this fast.
- **BM25**: PostgreSQL full-text search using `to_tsvector('english', text)`. The `search_vector` column doesn't exist as a stored column — `to_tsvector()` is applied inline.

These are combined with equal-weight RRF before the graph channel contributes.

### Graph Channel

Uses the **pluggable** `GraphRetriever` interface. Factory: `get_default_graph_retriever()` → returns `BFSGraphRetriever` by default (since S20).

**BFSGraphRetriever** (`graph_retrieval.py`) implements SUM spreading activation with 3 cycle guards:

```
Activation: A(v, t+1) = clip[A(v,t) + δ·Σ(w(u,v)·A(u,t)·μ(edge)·refractory(u)), Amax]
  - refractory(u): 0 if u fired at t, else 1 (blocks 2-node ping-pong)
  - firing_quota: node silenced after 2 fires (blocks longer cycles)
  - saturation: A(v) ≤ 2.0 (blocks score explosion)
```

Traverse budget: `max_nodes=50, max_depth=3` by default. Entry: nodes matching semantic query vector.

**Why SUM instead of MAX**: MAX propagation picks only the single strongest path. If 3 weak evidence sources all point to a node, MAX takes only the strongest — two sources are wasted. SUM accumulates all contributions, which is better for multi-hop and multi-session queries.

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
