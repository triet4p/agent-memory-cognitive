# CogMem — Cognitively-Grounded Long-Term Memory API

CogMem is a production-ready memory API for conversational agents, built on cognitive science principles rather than pure engineering. It stores conversation facts as a typed knowledge graph with 6 specialized memory networks, adaptive query routing, and SUM spreading activation with cycle guards.

**Key capabilities:**
- **6 Memory Networks**: World, Experience, Opinion, Habit, Intention, Action-Effect
- **Two-Pass Extraction**: Speaker-aware fact extraction (user turns isolated to catch personal experiences that get diluted in mixed-speaker chunks)
- **4-Channel Retrieval**: Semantic (pgvector) + BM25 + Graph (BFS SUM + 3 cycle guards) + Temporal, merged via adaptive weighted RRF
- **6 Query Types**: semantic, temporal, causal, prospective, multi-hop, preference — each with optimized channel weights
- **Lossless Context**: `raw_snippet` preserved alongside extracted `text` for accurate generation

## Quick Start

```bash
# Install dependencies
uv sync

# Start the API server (default: localhost:8888)
uv run cogmem-api

# Health check
curl http://localhost:8888/health
```

### Docker

```bash
docker build -f docker/standalone/Dockerfile -t cogmem:local .
docker run -p 8888:8888 cogmem:local
```

## Core API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/{agent}/banks/{bank_id}` | PUT | Create/update memory bank |
| `/v1/{agent}/banks/{bank_id}/memories` | POST | Retain conversation items |
| `/v1/{agent}/banks/{bank_id}/memories/recall` | POST | Search/recall facts |
| `/v1/{agent}/banks/{bank_id}/stats` | GET | Node counts by type |
| `/v1/{agent}/banks/{bank_id}` | DELETE | Delete a bank |

### Retain example

```bash
curl -X POST http://localhost:8888/v1/default/banks/test_bank/memories \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I just bought a Tamiya 1/48 Spitfire Mk.V kit"},
      {"role": "assistant", "content": "Nice! What scale is your Spitfire?"}
    ]
  }'
```

### Recall example

```bash
curl -X POST http://localhost:8888/v1/default/banks/test_bank/memories/recall \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What model kits did I buy?",
    "top_k": 10,
    "snippet_budget": 30000,
    "adaptive_router": true,
    "trace": true
  }'
```

## Configuration

All configuration via environment variables. See [tutorials/CONFIG/env-vars.md](tutorials/CONFIG/env-vars.md) for the full list.

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `COGMEM_API_LLM_BASE_URL` | `http://localhost:11434/v1` | Retain LLM endpoint (Ollama/NGROK) |
| `COGMEM_API_LLM_MODEL` | `ministral3-3b` | Retain extraction model |
| `COGMEM_API_GRAPH_RETRIEVER` | `bfs` | Graph retriever: `bfs` (SUM) or `link_expansion` (MAX) |
| `COGMEM_API_RERANKER_PROVIDER` | `local` | Cross-encoder reranker: `local` or `rrf` |
| `COGMEM_API_RETAIN_TWO_PASS_ENABLED` | `true` | Enable two-pass speaker-aware extraction |
| `COGMEM_API_JUDGE_LLM_MODEL` | — | Judge LLM (must be ≥7B for eval) |

## Documentation

| Document | Description |
|----------|-------------|
| [docs/CogMem-Idea.md](docs/CogMem-Idea.md) | Technical spec — 4 contributions, 6 networks, SUM activation, adaptive routing |
| [docs/PLAN.md](docs/PLAN.md) | Sprint plan and execution history (S0 → S-final) |
| [tutorials/INDEX.md](tutorials/INDEX.md) | Master tutorial index |
| [tutorials/QUICKSTART.md](tutorials/QUICKSTART.md) | 5-minute API walkthrough |
| [tutorials/LEARNING-PATH.md](tutorials/LEARNING-PATH.md) | 3 reader tracks: onboarding, config, deep-dive |
| [tutorials/ARCHITECTURE/overview.md](tutorials/ARCHITECTURE/overview.md) | System overview — 3 pipelines, 6 networks, Memory Engine |
| [tutorials/ARCHITECTURE/retain-pipeline.md](tutorials/ARCHITECTURE/retain-pipeline.md) | Retain pipeline deep-dive: two-pass, fallback hierarchy |
| [tutorials/ARCHITECTURE/search-pipeline.md](tutorials/ARCHITECTURE/search-pipeline.md) | Search pipeline: 4-channel retrieval, adaptive RRF, BFS SUM |
| [tutorials/REFERENCE/troubleshooting.md](tutorials/REFERENCE/troubleshooting.md) | 13 common errors with fixes and diagnostic commands |

## Project Structure

```
.
├── cogmem_api/              # Core API and engine
│   ├── api/http.py          # FastAPI endpoints
│   ├── config.py            # Environment configuration
│   ├── engine/
│   │   ├── memory_engine.py     # Main orchestrator
│   │   ├── retain/             # Retain pipeline (orchestrator, extraction, storage, chunking, dedup)
│   │   └── search/             # Search pipeline (retrieval, fusion, graph, reranking)
│   └── prompts/             # Centralized prompt library
│       ├── retain/pass1.py  # Pass 1 (full chunk, all 6 types)
│       ├── retain/pass2.py  # Pass 2 (user-only, 4 personal types)
│       └── eval/            # Judge + generation prompts
├── scripts/
│   ├── eval_cogmem.py       # Benchmark evaluation script
│   └── ablation_runner.py   # E1-E7 ablation runner
├── tests/artifacts/         # Sprint artifact tests (task-gated, standalone)
├── tutorials/               # Full tutorial library
│   ├── ARCHITECTURE/        # System-level why + how
│   ├── CONFIG/             # Configuration reference
│   ├── PER-FILE/          # Symbol-by-symbol file explanations
│   └── REFERENCE/         # Quick lookups
├── docker/                 # Dockerfile, compose, smoke tests
└── experiments/            # E1-E7 ablation checkpoint output
```

## Running Tests

```bash
# Run a specific artifact test
uv run python tests/artifacts/test_task786_query_routing.py

# Run all retain dialogue tests
uv run python tests/retain/test_dialogue_onboarding.py

# Build docs locally
uv run --with mkdocs --with mkdocs-material --with mkdocs-include-markdown-plugin \
  mkdocs build --config-file mkdocs.yml --site-dir site
```

## Status

- **S0 → S-final**: All sprints complete ✅
- **E7 dry run**: `session_recall@5 = 1.0`, `judge_score = 0.3` on "how many model kits" (4/5 kits found, missing Spitfire Mk.V due to count rubric)
- **Next**: Full benchmark run on LongMemEval-S + LoCoMo (post S-final, deferred)

## References

- HINDSIGHT baseline: Latimer et al. (2025) — 91.4% on LongMemEval, 89.61% on LoCoMo
- Benchmarks: LongMemEval-S (Wu et al., 2025), LoCoMo (Maharana et al., 2024)
- Cognitive foundations: Tulving (1972, 1983), Squire & Zola-Morgan (1991), Baddeley (2000), Dickinson & Balleine (1994)