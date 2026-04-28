# Environment Variables Reference

## Quick Lookup Table

| Variable | Default | What It Controls |
|----------|---------|-----------------|
| `COGMEM_API_DATABASE_URL` | `pg0` | DB connection. `pg0` = embedded postgres; `postgresql://...` for external |
| `COGMEM_API_DATABASE_SCHEMA` | `public` | PostgreSQL schema (rarely needs changing) |
| `COGMEM_API_HOST` | `0.0.0.0` | Bind address |
| `COGMEM_API_PORT` | `8888` | HTTP port |
| `COGMEM_API_LOG_LEVEL` | `info` | Logging verbosity |
| `COGMEM_API_WORKERS` | `1` | uvicorn worker count |
| `COGMEM_API_LLM_BASE_URL` | `None` | OpenAI-compatible LLM endpoint (e.g. ngrok URL for Ministral-3B) |
| `COGMEM_API_LLM_MODEL` | `gpt-4o-mini` | Model name sent to LLM endpoint |
| `COGMEM_API_LLM_API_KEY` | `ollama` | API key (default `ollama` works for local LLM) |
| `COGMEM_API_LLM_TIMEOUT` | `120s` | General LLM call timeout |
| `COGMEM_API_RETAIN_LLM_TIMEOUT` | `120s` | Timeout for retain fact extraction calls |
| `COGMEM_API_REFLECT_LLM_TIMEOUT` | `120s` | Timeout for reflect synthesis calls |
| `COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS` | `64000` | Max tokens for retain LLM output |
| `COGMEM_API_RETAIN_CHUNK_SIZE` | `3000` | Character chunk size for single-pass extraction |
| `COGMEM_API_RETAIN_EXTRACTION_MODE` | `concise` | Fact extraction mode: `concise\|verbose\|verbatim\|custom` |
| `COGMEM_API_RETAIN_EXTRACT_CAUSAL_LINKS` | `true` | Whether to extract causal relations during retain |
| `COGMEM_API_RETAIN_TWO_PASS_ENABLED` | `true` | Enable two-pass extraction (Pass1 all-roles + Pass2 user-only) |
| `COGMEM_API_RETAIN_PASS1_CHUNK_CHARS` | `10000` | Max chars per Pass 1 chunk |
| `COGMEM_API_RETAIN_PASS2_CHUNK_CHARS` | `3000` | Max chars per Pass 2 chunk |
| `COGMEM_API_RETAIN_PASS2_TARGET_ROLES` | `user` | Which roles to extract in Pass 2 (comma-separated) |
| `COGMEM_API_RETAIN_MISSION` | `None` | Custom mission statement injected into extraction prompts |
| `COGMEM_API_RETAIN_CUSTOM_INSTRUCTIONS` | `None` | Additional instructions for extraction prompts |
| `COGMEM_API_GRAPH_RETRIEVER` | `bfs` | Graph traversal strategy: `bfs\|link_expansion\|mpfp` |
| `COGMEM_API_BFS_REFRACTORY_STEPS` | `1` | Guard 1: refractory period (steps a node is silenced after firing) |
| `COGMEM_API_BFS_FIRING_QUOTA` | `2` | Guard 2: max times a node can fire before saturation |
| `COGMEM_API_BFS_ACTIVATION_SATURATION` | `2.0` | Guard 3: saturation ceiling (max activation per node) |
| `COGMEM_API_TEXT_SEARCH_EXTENSION` | `native` | BM25 backend: `native` (pg built-in) or `pg_trgm` |
| `COGMEM_API_MPFP_TOP_K_NEIGHBORS` | `20` | MPFP retriever: number of neighbors per pattern node |
| `COGMEM_API_EMBEDDINGS_PROVIDER` | `local` | `local` (sentence-transformers) or `openai` |
| `COGMEM_API_EMBEDDINGS_LOCAL_MODEL` | `BAAI/bge-small-en-v1.5` | Local sentence-transformer model |
| `COGMEM_API_RERANKER_PROVIDER` | `rrf` | Reranker: `rrf` (pass-through), `local`, or `tei` (external) |
| `COGMEM_API_RERANKER_LOCAL_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder model for reranking |
| `COGMEM_API_DB_POOL_MIN_SIZE` | `2` | asyncpg pool minimum connections |
| `COGMEM_API_DB_POOL_MAX_SIZE` | `10` | asyncpg pool maximum connections |
| `COGMEM_API_RECALL_MAX_CONCURRENT` | `32` | Max concurrent recall operations |
| `COGMEM_API_JUDGE_LLM_MODEL` | `minimax-m2.7` | LLM used for LLM-as-judge evaluation |
| `COGMEM_API_JUDGE_LLM_BASE_URL` | `None` | Judge LLM endpoint (must be ≥7B model) |

## Key Decisions Explained

### Why `pg0` as default?

`pg0` triggers embedded PostgreSQL via `pg0.py` (a thin process spawner). It's only for local dev. In production or eval, set `COGMEM_API_DATABASE_URL=postgresql://user:pass@host:5432/db`.

### Why `bfs` as default graph retriever?

Before S20, `link_expansion` was the default — but this uses MAX propagation (single strongest path wins). The CogMem contribution C3 is **SUM propagation with cycle guards** implemented in `BFSGraphRetriever`. Making it the default ensures all experiments E1-E7 use the correct SUM path except E1 (baseline, which explicitly uses MAX).

If you need the old MAX behavior for a specific experiment, set `COGMEM_API_GRAPH_RETRIEVER=link_expansion`.

### Why two-pass extraction?

Pass 1 extracts facts from ALL conversation turns (user + assistant). Assistant turns often contain system-level or analytical content that reveals user preferences indirectly.

Pass 2 re-runs extraction on USER-ONLY turns with a persona-focused prompt (from `prompts/retain/pass2.py`). This catches user-expressed opinions, intentions, and habits that might get diluted in mixed conversations.

The two results are deduped: if Pass 2 returns a fact also in Pass 1, Pass 2's version is kept for `opinion`, `habit`, `intention`, and `experience` types. `world` and `action_effect` facts from Pass 1 take precedence.

### What does `RETAIN_EXTRACTION_MODE` do?

It changes the system prompt sent to the LLM in Pass 1:

- **`concise`** (default): Asks for short, single-sentence facts. Best overall quality/speed tradeoff.
- **`verbose`**: Asks for longer facts with context. More detail but more tokens.
- **`verbatim`**: Returns the entire chunk as a single fact. No summarization. Useful when you want exact recall with raw_snippet.
- **`custom`**: Uses `RETAIN_MISSION` + `RETAIN_CUSTOM_INSTRUCTIONS` to define a domain-specific extraction prompt.

### BFS cycle guards — what do they prevent?

SUM aggregation on a graph with cycles will diverge (activate → amplify → re-activate → infinite loop). Three guards prevent this:

1. **Refractory period** (`BFS_REFRACTORY_STEPS=1`): A node that fired at step `t` cannot fire at step `t+1`. This blocks 2-node ping-pong (`A→B→A`).

2. **Firing quota** (`BFS_FIRING_QUOTA=2`): After a node fires twice, it is silenced for the remainder of this retrieval. This blocks longer cycles.

3. **Saturation ceiling** (`BFS_ACTIVATION_SATURATION=2.0`): Node activation is capped at 2.0 even if many paths converge. This blocks score explosion.

Without all three guards, SUM retrieval either diverges or produces inflated scores that corrupt RRF ranking.

### Why separate judge LLM?

The LLM-as-judge for evaluation should be strictly stronger than the LLM used for retain extraction. The eval framework **requires** `COGMEM_API_JUDGE_LLM_BASE_URL` and `COGMEM_API_JUDGE_LLM_MODEL` to be set explicitly — it will fail with an error if judge config is missing, instead of silently falling back to the retain model.

This is intentional: using the same 3B model for both extraction and judgment produces circular results.

## Minimal `.env` for Local Dev

```bash
COGMEM_API_LLM_BASE_URL=http://localhost:11434/v1
COGMEM_API_LLM_MODEL=ministral3-3b
COGMEM_API_LLM_API_KEY=ollama
COGMEM_API_DATABASE_URL=pg0
COGMEM_API_GRAPH_RETRIEVER=bfs
```

## Minimal `.env` for Eval

```bash
# Retain (local SLM via ngrok)
COGMEM_API_LLM_BASE_URL=https://xxxx.ngrok.io/v1
COGMEM_API_LLM_MODEL=ministral3-3b
COGMEM_API_LLM_API_KEY=ollama

# Judge (stronger model for LLM-as-judge)
COGMEM_API_JUDGE_LLM_BASE_URL=https://yyyy.ngrok.io/v1
COGMEM_API_JUDGE_LLM_MODEL=qwen3-7b
COGMEM_API_JUDGE_LLM_API_KEY=ollama

# Database (external pg)
COGMEM_API_DATABASE_URL=postgresql://user:pass@pg-host:5432/cogmem
COGMEM_API_GRAPH_RETRIEVER=bfs
```

## Verify Commands

```bash
# Check effective config values
uv run python -c "
from cogmem_api.config import get_config
c = get_config()
print('graph_retriever:', c.graph_retriever)
print('bfs_refractory_steps:', c.bfs_refractory_steps)
print('bfs_firing_quota:', c.bfs_firing_quota)
print('bfs_activation_saturation:', c.bfs_activation_saturation)
print('retain_two_pass_enabled:', c.retain_two_pass_enabled)
print('retain_extraction_mode:', c.retain_extraction_mode)
"

# Check env vars are read
rg "COGMEM_API_" .env 2>nul || echo "No .env found — using all defaults"
```
