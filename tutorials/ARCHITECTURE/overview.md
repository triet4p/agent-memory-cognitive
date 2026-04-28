# CogMem Architecture Overview

## What Is CogMem?

CogMem is a **cognitively-grounded long-term memory API** for conversational agents. It stores conversation facts as a typed knowledge graph — not as flat vector embeddings — so that queries can traverse semantic, temporal, causal, and habitual relationships between facts.

The core insight: human memory is not a single store. It uses multiple specialized systems (episodic, semantic, habit, prospective) with different neural substrates. CogMem mirrors this with 6 distinct memory networks, each optimized for a different query type.

## Three Pipelines

```
User Input → Retain → Store → Graph Links
                ↓
         Query → Recall → 4-Channel Retrieval → RRF Merge → Rerank → Top-K
                ↓
         Query + Evidence → Reflect → Grounded Answer
```

### Retain Pipeline (`retain_batch`)

Ingests raw conversation turns and outputs stored memory units with graph edges. Runs 6 sub-modules in sequence:

```
Input normalization
  → Fact extraction (LLM or heuristic fallback)
  → Embedding generation (sentence-transformer)
  → Fact storage (upsert to memory_units table)
  → Chunk storage (raw snippets for lossless recall)
  → Entity resolution (normalize + link)
  → Link creation (7 edge types: entity, temporal, semantic, causal, s_r_link, a_o_causal, transition)
```

Entry point: `cogmem_api/engine/retain/orchestrator.py::retain_batch`

Key design decisions:
- **Two-pass extraction**: Pass 1 extracts all facts from all roles; Pass 2 re-extracts only user-role facts for persona signals. Pass 2 results are deduped against Pass 1 with Pass 2 preference for personal fact types (opinion, habit, intention).
- **Lossless raw_snippet**: Every extracted fact stores the original text chunk alongside the LLM-generated narrative. This solves the lossy compression problem where "40%" or "180ms" details get dropped.
- **Heuristic overrides**: The LLM often misclassifies fact types. `_infer_fact_type()` and `_infer_fulfilled_from_context()` apply pattern-based corrections after LLM parsing.

### Search/Recall Pipeline (`recall_async`)

Retrieves relevant facts for a query using 4 parallel channels:

```
Query → Query Analyzer (classify intent + extract temporal constraints)
          ↓
    ┌─────┴──────┬────────────┬────────────┐
 Semantic     BM25        Graph      Temporal
 (vector)    (full-text)  (BFS)     (time-window)
          └─────┬──────┬────────────┬────────────┘
                ↓
         Weighted RRF merge (adaptive weights per query type)
                ↓
         Cross-encoder rerank + recency/temporal boost
                ↓
         Top-K candidates with document_id provenance
```

Entry point: `cogmem_api/engine/search/retrieval.py::retrieve_all_fact_types_parallel`

Key design decisions:
- **Adaptive RRF weights**: Query type determines channel weights. Temporal queries weight the temporal channel 0.40; multi-hop queries weight graph 0.50. This replaces HINDSIGHT's equal-weight RRF.
- **BFS graph retriever is default**: Since S20, `COGMEM_API_GRAPH_RETRIEVER=bfs` is the default (not `link_expansion`). BFS uses SUM aggregation with 3 cycle guards (refractory period, firing quota, saturation ceiling).
- **Prospective guard**: Intention nodes with `status != planning` are filtered out for prospective queries. This required a post-retrieval filter in `_filter_prospective_results()`.

### Reflect Pipeline (`synthesize_lazy_reflect`)

Synthesizes a grounded natural-language answer from retrieved evidence:

```
Retrieved candidates (top-N by RRF score)
  → Filter + normalize into ReflectEvidence
  → Group by network type
  → Build synthesis prompt with evidence chunks + raw_snippets
  → LLM generate OR fallback markdown summary
  → Return answer + used_memory_ids + networks_covered
```

Entry point: `cogmem_api/engine/reflect/agent.py::synthesize_lazy_reflect`

Key design decision: **lazy synthesis** — CogMem does NOT run opinion reinforcement proactively on every retain. Instead, it synthesizes opinions on-demand during reflect. This avoids HINDSIGHT's "opinion reinforcement scales quadratically with session count" bottleneck.

## Memory Engine — The Singleton Root

`cogmem_api/engine/memory_engine.py` holds all runtime state:

```
MemoryEngine
  ├── _pool: asyncpg connection pool (lifetime = app lifetime)
  ├── _embeddings_model: sentence-transformer provider (lazy init)
  ├── _cross_encoder: reranker singleton (lazy init, CE fallback if unavailable)
  ├── _current_schema: ContextVar[str] — per-request schema override
  └── _bank_cache: dict[str, str] — bank_id→bank_key cache
```

The pool is created once at `initialize()` and closed once at `close()`. All DB operations borrow from this pool via `acquire_with_retry()`.

## Fact Types and Why They Matter

Each fact type maps to a different memory system with different retrieval behavior:

| Type | Memory System | Neural Substrate | Special Fields |
|------|--------------|------------------|----------------|
| `world` | Semantic memory | Temporal-parietal cortex | — (time-independent) |
| `experience` | Episodic memory | Hippocampus | `occurred_start`, `occurred_end` |
| `opinion` | Belief system | Prefrontal cortex | `confidence` |
| `habit` | Habit memory (S-R) | Basal ganglia | s_r_link to triggered experiences |
| `intention` | Prospective memory | Prefrontal cortex | `intention_status`: planning/fulfilled/abandoned |
| `action_effect` | A-O learning | Prefrontal + premotor | `precondition`, `action`, `outcome`, `devalue_sensitive` |

The `habit` vs `action_effect` distinction is critical: habits survive outcome devaluation (S-R回路), while action-effects are suppressed when the outcome loses value (A-O回路). This is the same dissociation identified by Dickinson & Balleine (1994).

## Edge Types and Their Semantics

| Edge | Direction | Meaning | Example |
|------|-----------|---------|---------|
| `entity` | Bidirectional | Same entity across facts | `Alice → e_join → e_promo` |
| `temporal` | Directed | Chronological order | `e_join → e_promo (9 months)` |
| `semantic` | Undirected | Cosine similarity ≥ θ | `ML Engineer ↔ AI Team` |
| `causal` | Directed | Opinion shapes action | `o_python → w_proj` |
| `s_r_link` | Directed | Habit reinforces evidence | `h_email → e_standup_prep` |
| `a_o_causal` | Directed | Precondition→Action→Outcome | `ae_quant → e_fix` |
| `transition` | Directed+typed | Lifecycle state change | `i_rust ─fulfilled_by──▶ e_rust_done` |

## Configuration Hierarchy

```
Environment variables (COGMEM_API_*)
  ↓
CogMemRuntimeConfig (service-level: host, port, workers, db_url)
  ↓
CogMemConfig (engine-level: retriever policy, chunk sizes, BFS params)
```

`get_config()` returns a cached `CogMemConfig` singleton. The cache is populated on first call and reused for all subsequent calls within the process lifetime.

## Database Schema (What Exists)

Tables created by migrations:
- `banks` — memory bank registry
- `documents` — source document provenance (bank_id, document_id)
- `memory_units` — the main fact table (all 6 network types in one table, discriminated by `network_type`)
- `unit_entities` — entity membership
- `memory_links` — all 7 edge types in one table, discriminated by `link_type`
- `chunks` — raw snippet storage (lossless layer)

Indexes: HNSW on `embedding` (pgvector), GIN on `text` (BM25), B-tree on `(bank_id, network_type, occurred_start)` (temporal).

## Verify Commands

```bash
# Run the API server
uv run cogmem-api

# Smoke test retain + recall
uv run python tests/artifacts/test_task201_retain_baseline.py

# Check that BFS is default retriever
rg "DEFAULT_GRAPH_RETRIEVER" cogmem_api/config.py
# Expected: DEFAULT_GRAPH_RETRIEVER = "bfs"
```
