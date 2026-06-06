# CogMem Learning Path

## Reader Tracks

CogMem serves four kinds of readers. Pick the track that matches your goal:

| Track | Goal | Start | Duration |
|-------|------|-------|----------|
| **A. Onboarding** | Understand how the system works, run it locally | `QUICKSTART.md` → `ARCHITECTURE/overview.md` → `ARCHITECTURE/retain-pipeline.md` → `ARCHITECTURE/search-pipeline.md` → `ARCHITECTURE/reflect-pipeline.md` | ~45 min |
| **B. Configuration & Ops** | Deploy, tune, or debug the system | `CONFIG/env-vars.md` → `CONFIG/prompts.md` → `REFERENCE/troubleshooting.md` | ~30 min |
| **C. Deep Dive / Contributing** | Understand code in detail to extend or fix | `ARCHITECTURE/overview.md` → `PER-FILE/` walkthrough (bottom-up) → relevant `ARCHITECTURE/` docs | ~2-3 hrs |
| **D. Benchmarking / Research** | Measure correctness & prove cognitive-node necessity | `ARCHITECTURE/benchmark-ablation.md` → `ARCHITECTURE/evaluation.md` → `docs/Ablation-Flow.md` | ~1 hr |

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
- Why multi-pass extraction exists (Pass 1 all-roles, Pass 2 user-only, Pass 3 cross-chunk relations)
- How `raw_snippet` solves the lossy compression problem
- The fallback hierarchy: seeded → LLM → heuristic
- Phase A (in-session) vs Phase B (cross-bank) link creation

### Step 4: Recall pipeline details (10 min)
Read `ARCHITECTURE/search-pipeline.md`. Focus on:
- The 4 retrieval channels and why they run in parallel
- The 6 query types (incl. `preference`) and how adaptive RRF weights work
- BFS SUM (default) vs the `bfs_max` ablation toggle
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
Read `CONFIG/prompts.md` to understand Pass 1 / Pass 2 / Pass 3 and the 4 extraction modes.

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
| C3: SUM + 3 guards | `graph_retrieval.py::BFSGraphRetriever` (SUM; `bfs_max` for the MAX ablation) |
| C4: adaptive RRF | `query_analyzer.py`, `retrieval.py::resolve_query_routing` |

## Track D — Benchmarking / Research

For proving the cognitive nodes earn their place and measuring correctness.

### Step 1: The necessity argument (20 min)
Read `ARCHITECTURE/benchmark-ablation.md`, then the frozen methodology in `docs/Ablation-Flow.md`.
Focus on:
- Why the generator (Minimax) must differ from the reader (Ministral) — circularity defense
- Pre-registration: gold facts/answers fixed in `ScenarioSpec` JSON *before* generation
- The two gates (embedding + discrimination) and what gets discarded vs patched
- Phase 1 (recall-time) vs Phase 2 (retain-level, `enabled_fact_types`) ablation

### Step 2: Correctness & diagnosis (20 min)
Read `ARCHITECTURE/evaluation.md`. Focus on:
- `eval_cogmem.py` profiles and the mandatory separate judge LLM
- The `cogmem-verify → cogmem-diagnose → cogmem-audit` skill chain
- LongMemEval-S vs LoCoMo tracks

### Try it:
```bash
uv run python -m cogmem_bench.generate --dry-run     # offline wiring check
uv run python -m cogmem_bench.gate --only pilot_intention_01
```
