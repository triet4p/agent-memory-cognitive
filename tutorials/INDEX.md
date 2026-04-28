# CogMem Tutorials — Master Index

This directory contains developer documentation for the CogMem cognitive memory API.

## How to Navigate

| If you want to… | Start here |
|-----------------|-----------|
| Run the API in 5 minutes | `QUICKSTART.md` |
| Understand the system fast | `ARCHITECTURE/overview.md` |
| Configure for production | `CONFIG/env-vars.md` |
| Understand a specific file | `PER-FILE/` (see index below) |
| Troubleshoot an error | `REFERENCE/troubleshooting.md` |
| Contribute code | `LEARNING-PATH.md` (Track C) |

## Directory Structure

```
tutorials/
├── QUICKSTART.md              ← Start here (5 min to running API)
├── LEARNING-PATH.md           ← Reader tracks A / B / C
├── INDEX.md                   ← This file (you are here)
│
├── ARCHITECTURE/              ← System-level docs (why + how, not what)
│   ├── overview.md            ← Big picture: 3 pipelines, 6 networks, Memory Engine
│   ├── retain-pipeline.md     ← Deep dive: retain_batch() + 6 sub-modules
│   ├── search-pipeline.md    ← Deep dive: 4-channel retrieval + adaptive RRF
│   ├── reflect-pipeline.md    ← Deep dive: lazy synthesis
│
├── CONFIG/                    ← Configuration reference
│   ├── env-vars.md           ← All COGMEM_API_* variables with explanations
│   ├── prompts.md            ← Pass 1 / Pass 2 extraction prompts
│   └── running.md            ← Run on host / Docker standalone / Docker compose
│
├── PER-FILE/                  ← Symbol-by-symbol file walkthroughs
│   └── (file-index below)
│
├── REFERENCE/                  ← Quick lookups
│   ├── glossary.md           ← Term definitions
│   ├── troubleshooting.md    ← Common errors and fixes
│   └── function-index.md    ← Quick function lookup table
│
└── (legacy: these have been replaced)
    ├── modules/               ← Superseded by ARCHITECTURE/
    ├── functions/            ← Superseded by PER-FILE/
    ├── per-file/              ← Still valid, see below
    ├── plan.md                ← Broken (Jekyll include)
    ├── idea.md                ← Broken (Jekyll include)
    ├── project-overview.md    ← Broken (Jekyll include)
    ├── README.md              ← Superseded by this INDEX.md
    └── learning-path.md       ← Moved to tutorials/LEARNING-PATH.md
```

## Per-File Doc Index

| Source File | Tutorial |
|-------------|----------|
| `cogmem_api/main.py` | `PER-FILE/runtime-main.md` |
| `cogmem_api/server.py` | `PER-FILE/runtime-server.md` |
| `cogmem_api/api/http.py` | `PER-FILE/api-http.md` |
| `cogmem_api/config.py` | `PER-FILE/config.md` |
| `cogmem_api/engine/memory_engine.py` | `PER-FILE/engine-core.md` |
| `cogmem_api/engine/retain/orchestrator.py` | `PER-FILE/retain-orchestrator.md` |
| `cogmem_api/engine/retain/fact_extraction.py` | `PER-FILE/retain-fact-extraction.md` |
| `cogmem_api/engine/retain/fact_storage.py` | `PER-FILE/retain-fact-storage.md` |
| `cogmem_api/engine/retain/entity_processing.py` | `PER-FILE/retain-entity-processing.md` |
| `cogmem_api/engine/retain/link_creation.py` | `PER-FILE/retain-link-creation.md` |
| `cogmem_api/engine/retain/chunking.py` | `PER-FILE/retain-chunking.md` |
| `cogmem_api/engine/retain/dedup.py` | `PER-FILE/retain-dedup.md` |
| `cogmem_api/engine/search/retrieval.py` | `PER-FILE/search-retrieval.md` |
| `cogmem_api/engine/search/graph_retrieval.py` | `PER-FILE/search-graph-retrieval.md` |
| `cogmem_api/engine/search/fusion.py` | `PER-FILE/search-fusion.md` |
| `cogmem_api/engine/query_analyzer.py` | `PER-FILE/query-analyzer.md` |
| `cogmem_api/engine/reflect/agent.py` | `PER-FILE/reflect-agent.md` |
| `cogmem_api/prompts/retain/pass1.py` | `PER-FILE/prompts-pass1.md` |
| `cogmem_api/prompts/retain/pass2.py` | `PER-FILE/prompts-pass2.md` |
| `scripts/eval_cogmem.py` | `PER-FILE/eval-script.md` |

## Architecture (ARCHITECTURE/) vs Per-File (PER-FILE/) — What's the Difference?

**ARCHITECTURE/ docs** explain *why* each component exists and how it connects to the rest of the system. They are system-focused, not file-focused. Read these first to build mental models.

**PER-FILE/ docs** are symbol-by-symbol walkthroughs of individual source files. They explain *what each function does* and *what each significant block means*. Read these when you need to understand or modify a specific file.

## Status: Active Rewrite (2026-04-28)

The tutorial system is being rewritten from scratch to eliminate:
- Triple redundancy across `modules/`, `functions/`, and `per-file/`
- Broken Jekyll-include files (`plan.md`, `idea.md`, `project-overview.md`)
- Boilerplate deep-dives with no insight value
- Stale sprint-gated organization

New structure: 4-layer top-down (Architecture → Config → Per-File → Reference).

## Verify Commands

```bash
# Check tutorial framework
uv run python tests/artifacts/test_task716_tutorial_framework.py

# Check module-level tutorial
uv run python tests/artifacts/test_task717_tutorial_core.py

# List all tutorial files
rg -l "\.md" tutorials/ARCHITECTURE/ tutorials/CONFIG/ tutorials/PER-FILE/ tutorials/REFERENCE/
```
