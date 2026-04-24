# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Operational Rules

Key constraints (full detail in sections below):

- **No `hindsight_api` imports** anywhere in `cogmem_api/`. Fork/copy logic instead.
- **Relative imports**: only same-level (`from .x import`). Never `..` or `...` up to parent.
- **Dependency manager**: always `uv add <lib>` — never invent libraries.
- **Coverage docs gate**: never edit `docs/migration_idea_coverage_matrix.md` unless the user explicitly requests an audit.
- **Artifacts required**: after each meaningful task, create `logs/task_<id>_summary.md` and `tests/artifacts/test_<task_name>.py`.
- **No collateral discards**: never run `git checkout`, `git restore`, or any command that discards changes to files outside the current sprint's explicit scope. If a file was not touched by the sprint task, its working-tree state must be preserved exactly.
- **data/ directory is read-only at runtime**: never execute any script or command that writes, overwrites, or deletes files under `data/`. Dataset files (e.g. `data/longmemeval_s_distilled_small.json`, `data/locomo_distilled.json`) are pre-generated artifacts — re-running `distill_dataset.py` or any similar script during a sprint is forbidden unless the user explicitly requests it.

## Coverage Audit Gate (HARD STOP)

Before every task, check explicitly:

- If user did **NOT** request an explicit audit/update of coverage → mark `docs/migration_idea_coverage_matrix.md` as **read-only** for the entire task. Do not touch it.
- If user **did** request an explicit audit → allowed to edit; must cite evidence for every change.
- Violating this gate is a critical process error.

## Commit Message Standard

Propose a commit after every meaningful milestone **only when** artifact + test exist for that milestone.

**Subject line** (English, imperative):
```
feat|fix|chore|docs|refactor: short message
```
Example: `chore: complete sprint-0 artifact baseline checks`

**Description** (English bullet points):
- What changed
- Why it changed
- Verification / test results

Never write a vague description — it must reference the specific files and changes made in that milestone.

## Execution Steps

Pre-check before Step 1: confirm Coverage Gate status (see above).

1. **Read Idea** — study `docs/CogMem-Idea.md` (or the new requirement).
2. **Scan Source** — find the corresponding modules in `hindsight_api`.
3. **Plan** — decompose into atomic tasks (one problem per task).
4. **Implement** — Copy → Modify → `uv add` if needed.
5. **Create Artifact** — write test + summary log.
6. **Verify** — report completion and await next instruction.
7. **Propose Commit** — subject + description in English per the standard above.

## Commands

```bash
# Install dependencies
uv sync

# Run the API server (default: localhost:8888)
uv run cogmem-api

# Run a single test file
uv run python tests/artifacts/test_task201_retain_baseline.py
uv run python tests/retain/test_dialogue_onboarding.py

# Build docs locally
uv run --with mkdocs --with mkdocs-material --with mkdocs-include-markdown-plugin mkdocs build --config-file mkdocs.yml --site-dir site

# Docker build + smoke test
docker build -f docker/standalone/Dockerfile -t cogmem:local .
./docker/test-image.sh cogmem:local          # Linux/macOS
.\docker\test-image.ps1 -Image cogmem:local  # PowerShell
```

## Architecture Overview

CogMem is a **cognitively-grounded long-term memory API** that stores conversation facts as a typed knowledge graph. It is a fork/evolution of the `hindsight_api` baseline.

### Three Pipelines

| Pipeline | Entry point | Purpose |
|----------|-------------|---------|
| **Retain** | `cogmem_api/engine/retain/orchestrator.py` → `retain_batch()` | Ingest text → extract facts via LLM → embed → store → create graph links |
| **Search/Recall** | `cogmem_api/engine/search/retrieval.py` | 4-way parallel retrieval (semantic, BM25, graph, temporal) → weighted RRF merge |
| **Reflect** | `cogmem_api/engine/reflect/agent.py` → `synthesize_lazy_reflect()` | Synthesize a grounded answer from recalled evidence |

### Retain Pipeline Internals

`retain_batch()` orchestrates six sub-modules in sequence:

1. `fact_extraction.py` — LLM prompt → JSON facts (4 modes: concise/verbose/verbatim/custom); falls back to heuristics if LLM unavailable
2. `embedding_processing.py` — sentence-transformer embeddings per fact
3. `fact_storage.py` — upsert `memory_units` rows
4. `chunk_storage.py` — store raw chunk metadata
5. `entity_processing.py` — resolve/insert entity records
6. `link_creation.py` — create 7 edge types: `entity`, `temporal`, `semantic`, `causal`, `s_r_link`, `a_o_causal`, `transition`

### 6 Fact/Network Types

Defined in `cogmem_api/engine/retain/types.py` as `COGMEM_FACT_TYPES`:

| Type | Meaning | Special metadata |
|------|---------|-----------------|
| `world` | Objective, time-independent fact | — |
| `experience` | Past event at a specific time | `occurred_start`, `occurred_end` |
| `opinion` | Belief or preference | `confidence` |
| `habit` | Repeating behaviour | s_r_link to triggered experiences |
| `intention` | Future goal or plan | `intention_status`: planning \| fulfilled \| abandoned |
| `action_effect` | Causal triple | `precondition`, `action`, `outcome`, `confidence`, `devalue_sensitive` |

### Search/Recall Pipeline

`retrieval.py` runs four channels in parallel then merges with `weighted_reciprocal_rank_fusion()`:

- **Semantic**: pgvector cosine similarity
- **BM25**: PostgreSQL full-text search
- **Graph**: pluggable `GraphRetriever` — default `BFSGraphRetriever` (SUM spreading activation with 3 cycle guards: Refractory, Firing Quota, Saturation)
- **Temporal**: time-window filtered search

**Adaptive query routing** (`query_analyzer.py`): classifies query into one of 6 types (`semantic`, `temporal`, `causal`, `prospective`, `preference`, `multi_hop`) and applies per-type RRF weight profiles.

### LLM & Embeddings

- `cogmem_api/engine/llm_wrapper.py` — `LLMConfig` (OpenAI-compatible async HTTP); `parse_llm_json()` strips markdown fences
- `cogmem_api/engine/embeddings.py` — `create_embeddings_from_env()`: local sentence-transformers (`BAAI/bge-small-en-v1.5`) or OpenAI-compatible API
- Runtime LLM: **Ministral-3B** served via Kaggle + NGROK, configured through env vars

### Key Env Vars

```
COGMEM_API_LLM_BASE_URL        # NGROK URL ending with /v1
COGMEM_API_LLM_MODEL           # default: ministral3-3b
COGMEM_API_LLM_API_KEY         # default: ollama
COGMEM_API_RETAIN_LLM_TIMEOUT  # default: 600s
COGMEM_API_RETAIN_EXTRACTION_MODE   # concise | verbose | verbatim | custom
COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS  # default: 13000
COGMEM_API_DATABASE_URL        # default: pg0 (embedded postgres)
```

### REST API

`cogmem_api/api/http.py` — FastAPI app mounted at `/v1/{agent_name}`:

- `PUT /banks/{bank_id}` — create/update memory bank
- `POST /banks/{bank_id}/memories` — retain items
- `POST /banks/{bank_id}/memories/recall` — search/recall
- `GET /banks/{bank_id}/stats` — node count
- `DELETE /banks/{bank_id}` — delete bank

### Test Structure

```
tests/artifacts/     # Sprint artifact tests (task-gated, run as __main__)
tests/retain/        # Dialogue-driven retain pipeline tests
  _shared.py         # Shared: resolve_llm(), make_config(), _BaseFakeLLM
  test_dialogue_*.py # One file per scenario; dual-mode (real LLM or FakeLLM)
```

All tests are standalone scripts — run with `uv run python tests/.../test_xxx.py`. There is no pytest runner. The `_BaseFakeLLM` in `tests/retain/_shared.py` returns a canned `{"facts": [...]}` dict; set `COGMEM_API_LLM_BASE_URL` to switch to real Ministral-3B.

### Important Reference Documents

- `docs/CogMem-Idea.md` — canonical spec for all 4 contributions (6 networks, lossless metadata, SUM activation, adaptive routing)
- `docs/PLAN.md` — sprint plan and task breakdown
- `tutorials/modules/retain-pipeline.md` — retain pipeline deep-dive
- `tutorials/per-file/` — per-file reading guides
