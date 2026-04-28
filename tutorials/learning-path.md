# CogMem Learning Path

## Reader Tracks

CogMem serves three kinds of readers. Pick the track that matches your goal:

| Track | Goal | Start | Duration |
|-------|------|-------|----------|
| **A. Onboarding** | Understand how the system works, run it locally | `QUICKSTART.md` → `ARCHITECTURE/overview.md` → `ARCHITECTURE/retain-pipeline.md` → `ARCHITECTURE/search-pipeline.md` → `ARCHITECTURE/reflect-pipeline.md` | ~45 min |
| **B. Configuration & Ops** | Deploy, tune, or debug the system | `CONFIG/env-vars.md` → `CONFIG/prompts.md` → `REFERENCE/troubleshooting.md` | ~30 min |
| **C. Deep Dive / Contributing** | Understand code in detail to extend or fix | `ARCHITECTURE/overview.md` → `PER-FILE/` walkthrough (bottom-up) → relevant `ARCHITECTURE/` docs | ~2-3 hrs |

## Track A — Onboarding

### Step 1: Run it locally (10 min)
Follow `QUICKSTART.md` to start the API, send a retain request, and run a recall query. Get the API running before reading further.

### Step 2: Understand the big picture (15 min)
Read `ARCHITECTURE/overview.md`. Focus on:
- The three pipelines (retain / recall / reflect) and how data flows between them
- The 6 memory networks and why they exist
- The Memory Engine singleton and what state it holds

### Step 3: Retain pipeline details (10 min)
Read `ARCHITECTURE/retain-pipeline.md`. Focus on:
- Why two-pass extraction exists
- How `raw_snippet` solves the lossy compression problem
- The fallback hierarchy: LLM → seeded → heuristic

### Step 4: Recall pipeline details (10 min)
Read `ARCHITECTURE/search-pipeline.md`. Focus on:
- The 4 retrieval channels and why they run in parallel
- How adaptive RRF weights work
- BFS SUM vs HINDSIGHT MAX
- The prospective guard for intention filtering

### Verify your understanding:
```bash
uv run python tests/artifacts/test_task201_retain_baseline.py
uv run python tests/artifacts/test_task302_sum_activation.py
```

## Track B — Configuration & Ops

### Step 1: Environment variables
Read `CONFIG/env-vars.md`. Key groups:
- **Database**: `DATABASE_URL`, `DB_POOL_*`
- **LLM**: `LLM_BASE_URL`, `LLM_MODEL`, `RETAIN_*_TIMEOUT`
- **Retriever**: `GRAPH_RETRIEVER`, `BFS_*` params
- **Judge**: `JUDGE_LLM_*`

### Step 2: Extraction prompts
Read `CONFIG/prompts.md` to understand Pass 1 vs Pass 2 and the 4 extraction modes.

### Step 3: Common issues
Read `REFERENCE/troubleshooting.md` before hitting your first bug. Common issues:
- `ModuleNotFoundError: No module named 'dateparser'` — run `uv add dateparser`
- FK violations on first retain — fixed in S24 hotfix (task 756)
- Cross-encoder silent fallback — expected behavior when CE unavailable

## Track C — Deep Dive

### Prerequisites
- Understand the three pipelines from Track A
- Have read `ARCHITECTURE/overview.md`

### Bottom-up reading order:

1. `cogmem_api/config.py` — env var reading and config caching
2. `cogmem_api/engine/memory_engine.py` — singleton holding pool, embeddings, CE
3. `cogmem_api/engine/retain/orchestrator.py` — retain transaction orchestrator
4. `cogmem_api/engine/retain/fact_extraction.py` — most complex module; focus on fallback hierarchy
5. `cogmem_api/engine/retain/fact_storage.py` — memory_units upsert with document_id
6. `cogmem_api/engine/retain/link_creation.py` — all 7 edge types
7. `cogmem_api/engine/search/retrieval.py` — 4-channel orchestration and RRF fusion
8. `cogmem_api/engine/search/graph_retrieval.py` — BFS SUM with cycle guards
9. `cogmem_api/engine/query_analyzer.py` — query type classification
10. `cogmem_api/engine/reflect/agent.py` — lazy synthesis vs HINDSIGHT CARA

### Key files for specific contributions:

| Contribution | Key File(s) |
|--------------|-------------|
| C1: 6 networks + 7 edges | `retain/types.py`, `link_creation.py` |
| C2: raw_snippet lossless | `fact_extraction.py`, `memory_engine.py` |
| C3: SUM + 3 guards | `graph_retrieval.py::BFSGraphRetriever` |
| C4: adaptive RRF | `query_analyzer.py`, `retrieval.py::resolve_query_routing` |
