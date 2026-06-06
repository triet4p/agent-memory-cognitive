# Evaluation & Diagnostics

CogMem is evaluated on long-horizon memory benchmarks (LongMemEval-S, LoCoMo) and has a dedicated
**diagnosis workflow** for understanding *why* individual cases pass or fail. This page maps the
moving parts; the deep logic lives in the agent skills, not here.

## The benchmark scripts

| Script | Role |
|--------|------|
| `scripts/eval_cogmem.py` | Main eval driver — retain a fixture, recall + generate, judge answers. Profiles like `E7` select a config. |
| `scripts/retain_locomo_bank_sessions.py` | Session-wise retain helper for the LoCoMo dataset |
| `scripts/locomo_mapping_dryrun.py` | Offline check of LoCoMo question→session mapping before a full run |
| `scripts/diagnose_bank.py` | Inspect a retained bank's facts / edges for a case |
| `scripts/compare_sum_max_graph_only.py` | SUM vs MAX graph-only ablation (see [Search Pipeline](search-pipeline.md)) |

Eval requires a separate, stronger **judge** LLM — `COGMEM_API_JUDGE_LLM_BASE_URL` /
`COGMEM_API_JUDGE_LLM_MODEL` must be set explicitly (the framework refuses to silently reuse the 3B
retain model, which would make judgments circular). See [Environment Variables](../CONFIG/env-vars.md).

## The diagnosis workflow (skills)

When a case fails, three skills run in order. They operate on **already-collected** data — none of
them re-runs API calls except where noted — so diagnosis is cheap and repeatable.

```
cogmem-verify  →  cogmem-diagnose  →  cogmem-audit
  (ground truth)    (classify why)      (deep single-case audit)
```

1. **`cogmem-verify`** — re-checks pass/fail by comparing the pipeline's *actual generated answer*
   against the gold answer, instead of trusting `judge.correct` / `judge.score`. Its verdict is the
   ground truth the other skills build on. Run this **first**.

2. **`cogmem-diagnose`** — reads existing audit reports and gold-answer checkpoints to classify *why*
   cases fail (recall gap vs generation gap vs judge noise) and summarize failure patterns across a
   range of cases. Pure analysis — no API calls.

3. **`cogmem-audit`** — a structured single-case deep dive: identifies the answer-relevant facts,
   recall gaps, and graph-connectivity issues for one bank, and recommends fixes. Use it when
   `diagnose` flags a case as worth investigating.

> These are user-invoked skills. Invoke them by name (e.g. "verify c007", "diagnose c000–c010",
> "audit c014"); each skill's own definition documents the exact inputs and report shape.

## The two benchmark tracks

- **LongMemEval-S** — multi-session QA with answer-relevant facts spread across long histories. The
  primary correctness benchmark; drives the `eval_cogmem.py` profiles.
- **LoCoMo** — session-wise conversational memory. Retained via
  `scripts/retain_locomo_bank_sessions.py`; mapping validated with `locomo_mapping_dryrun.py`.

## How this relates to the necessity benchmark

This page is about **correctness on existing benchmarks** (is the answer right?). The
[Benchmark & Ablation](benchmark-ablation.md) page is about **necessity** (does a given cognitive
node change the answer?). They share the same retain/recall API and the same judge, but answer
different questions.

## Verify Commands

```bash
# Run the eval driver on a small fixture (needs a running judge LLM)
COGMEM_API_LOG_LEVEL=debug uv run python scripts/eval_cogmem.py --fixture short --profile E7 --verbose

# Offline LoCoMo mapping check
uv run python scripts/locomo_mapping_dryrun.py

# Inspect a retained bank
uv run python scripts/diagnose_bank.py --help
```
