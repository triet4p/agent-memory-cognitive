# Reflect Pipeline — Lazy Synthesis

## What Is Lazy Synthesis?

Unlike HINDSIGHT's CARA reflect (which runs opinion reinforcement continuously during retain), CogMem uses **lazy synthesis**: opinions and beliefs are only synthesized on-demand at query time, from whatever facts were stored during retain.

This is a deliberate architectural choice. HINDSIGHT's opinion reinforcement scales quadratically with session count — each new session must compare against all accumulated opinions. CogMem avoids this entirely.

## Entry Point: `synthesize_lazy_reflect()`

Located at `cogmem_api/engine/reflect/agent.py::synthesize_lazy_reflect`.

```
synthesize_lazy_reflect(question, retrieval_result, llm_generate, ...)
  ├─→ tools.prepare_lazy_evidence() — normalize candidates to ReflectEvidence
  ├─→ tools.group_evidence_by_network() — group by network_type
  ├─→ prompts.build_lazy_synthesis_prompt() — assemble prompt from evidence
  ├─→ llm_generate(prompt) — call LLM OR fall back to markdown
  └─→ return ReflectSynthesisResult(answer, used_memory_ids, ...)
```

## Step 1 — Evidence Normalization (`tools.py`)

`prepare_lazy_evidence()` converts raw `RetrievalResult` items into `ReflectEvidence` dataclasses:

```
to_reflect_evidence(item) → ReflectEvidence
  - id: unit_id from memory_units
  - text: narrative_fact text
  - raw_snippet: verbatim chunk text (for lossless detail)
  - fact_type: network_type
  - score: RRF combined score
  - network: network_type (same as fact_type)
  - occurred_start: temporal anchor
```

`prepare_lazy_evidence()` filters out malformed items (missing id/text/fact_type), truncates text to 512 chars, and returns the top-N sorted by score.

## Step 2 — Prompt Building (`prompts.py`)

`build_lazy_synthesis_prompt()` assembles the synthesis prompt:

```
System:
You are a helpful assistant. Answer the user's question using only the
provided evidence. If evidence is insufficient, say you don't know.
Do not make up information.

Evidence:
[chunk 1] Fact type: opinion. Text: "User prefers Python for ML (confidence 0.85)"
  Raw: "Python is definitely the best language for machine learning work..."
[chunk 2] Fact type: experience. Text: "User joined DI as ML Engineer in April 2024"
  Raw: "Hey team, excited to share that I just joined DI as an ML Engineer..."

Question: {question}
```

The key design: **both `text` (narrative_fact) and `raw_snippet` are included**. This gives the LLM the compressed summary for quick understanding and the verbatim chunk for exact details when needed.

## Step 3 — LLM Generation or Fallback

`llm_generate` is an injected async callback. If provided, it calls the LLM. If not provided or if it fails, `_default_markdown_answer()` produces a plain-text summary:

```markdown
Based on the retrieved memories:

1. [opinion] User prefers Python for ML (confidence 0.85)
2. [experience] User joined DI as ML Engineer in April 2024

These are the key facts relevant to your question.
```

The fallback is not a failure — the reflect pipeline always produces a usable answer, even without an LLM.

## Opinion Reinforcement (Lazy)

In HINDSIGHT, opinion reinforcement runs after every retain: new facts are compared against all accumulated opinions to reinforce or update beliefs. This is expensive.

In CogMem, this is deferred. When a query triggers reflect, `synthesize_lazy_reflect` reads existing opinion facts and synthesizes them with the new evidence into a coherent answer. The "reinforcement" happens at query time, not at store time.

This is valid because the opinion facts are already stored — their confidence scores reflect accumulated evidence. Lazy synthesis reads them and produces the updated belief state as part of the answer.

## Verify Commands

```bash
# Run reflect test
uv run python tests/artifacts/test_task401_reflect_lazy_synthesis.py

# Check raw_snippet is in evidence
rg "raw_snippet" cogmem_api/engine/reflect/
```
