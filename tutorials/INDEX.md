# CogMem Tutorials — Master Index

This directory contains developer documentation for the CogMem cognitive memory API.

## How to Navigate

| If you want to… | Start here |
|-----------------|-----------|
| Run the API in 5 minutes | `QUICKSTART.md` |
| Understand the system fast | `ARCHITECTURE/overview.md` |
| Configure for production | `CONFIG/env-vars.md` |
| Understand a specific file | `PER-FILE/` (partial — see index below) |
| Understand the necessity benchmark | `ARCHITECTURE/benchmark-ablation.md` |
| Evaluate / diagnose recall failures | `ARCHITECTURE/evaluation.md` |
| Troubleshoot an error | `REFERENCE/troubleshooting.md` |
| Contribute code / run benchmarks | `LEARNING-PATH.md` (Track C / Track D) |

## Directory Structure

```
tutorials/
├── QUICKSTART.md              ← Start here (5 min to running API)
├── LEARNING-PATH.md           ← Reader tracks A / B / C
├── INDEX.md                   ← This file (you are here)
│
├── ARCHITECTURE/              ← System-level docs (why + how, not what)
│   ├── overview.md            ← Big picture: 3 pipelines, 6 networks, Memory Engine
│   ├── retain-pipeline.md     ← Deep dive: retain_batch() + Phase A/B links
│   ├── search-pipeline.md    ← Deep dive: 4-channel retrieval + adaptive RRF
│   ├── reflect-pipeline.md    ← Deep dive: lazy synthesis
│   ├── benchmark-ablation.md  ← cogmem_bench: cognitive-node necessity ablation
│   └── evaluation.md          ← Eval & diagnostics workflow (verify/diagnose/audit)
│
├── CONFIG/                    ← Configuration reference
│   ├── env-vars.md           ← All COGMEM_API_* variables with explanations
│   ├── prompts.md            ← Pass 1 / Pass 2 / Pass 3 extraction prompts
│   └── running.md            ← Run on host / Docker standalone / Docker compose
│
├── PER-FILE/                  ← Symbol-by-symbol file walkthroughs (partial; see index below)
│
├── REFERENCE/                  ← Quick lookups
│   └── troubleshooting.md    ← Common errors and fixes
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

The PER-FILE set is **partial** — only the files below currently have a walkthrough. For everything
else, read the source directly with the [Manual Code Reading Guide](manual-code-reading-guide.md)
as a map.

**Available now:**

| Source File | Tutorial |
|-------------|----------|
| `cogmem_api/config.py` | `PER-FILE/config.md` |
| `cogmem_api/engine/retain/orchestrator.py` | `PER-FILE/retain-orchestrator.md` |
| `cogmem_api/engine/retain/fact_extraction.py` | `PER-FILE/retain-fact-extraction.md` |
| `cogmem_api/engine/retain/chunking.py` | `PER-FILE/retain-chunking.md` |
| `cogmem_api/engine/retain/dedup.py` | `PER-FILE/retain-dedup.md` |

## Architecture (ARCHITECTURE/) vs Per-File (PER-FILE/) — What's the Difference?

**ARCHITECTURE/ docs** explain *why* each component exists and how it connects to the rest of the system. They are system-focused, not file-focused. Read these first to build mental models.

**PER-FILE/ docs** are symbol-by-symbol walkthroughs of individual source files. They explain *what each function does* and *what each significant block means*. Read these when you need to understand or modify a specific file.

## Status: Refreshed (2026-06-06)

The tutorial set was refreshed against the current `main` (through sprints S28–S35) to:
- Correct the search pipeline (6 query types incl. `preference`, real adaptive-RRF weights, SUM/MAX
  retriever options)
- Document the retain Phase A / Phase B link layers, Pass 3, and `enabled_fact_types` / `agentic_transcript`
- Add the `cogmem_bench` necessity-ablation and the eval/diagnostics workflow
- Trim the over-promised PER-FILE / REFERENCE indexes down to what actually exists

Structure: 4-layer top-down (Architecture → Config → Per-File → Reference).

## Verify Commands

```bash
# Check tutorial framework
uv run python tests/artifacts/test_task716_tutorial_framework.py

# Check module-level tutorial
uv run python tests/artifacts/test_task717_tutorial_core.py

# List all tutorial files
rg -l "\.md" tutorials/ARCHITECTURE/ tutorials/CONFIG/ tutorials/PER-FILE/ tutorials/REFERENCE/
```
