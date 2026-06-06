# Prompts System (`cogmem_api/prompts/`)

## Overview

The prompts directory contains the **system prompts** used for LLM-based fact extraction in the retain pipeline. There are three passes (Pass 1, Pass 2, Pass 3) plus a shared utility.

**Files:**

| File | Purpose |
|------|---------|
| `pass1.py` | System prompt + user message builder for Pass 1 (all roles) |
| `pass2.py` | System prompt + user message builder for Pass 2 (user-only) |
| `pass3.py` | `build_pass3_prompt()` — cross-chunk relation discovery over the merged fact list |
| `shared.py` | Temporal hallucination sanitization utilities |

## `pass1.py` — All-Role Extraction

```python
build_pass1_prompt(config) → tuple[prompt: str, mode: str]
```

The returned `mode` determines which variant of the Pass 1 prompt is used. The 4 modes are:

| Mode | Behavior |
|------|----------|
| `concise` | Ask for short, single-sentence facts with core info only |
| `verbose` | Ask for richer facts with context, causes, involved parties |
| `verbatim` | Tell LLM to return the entire chunk as one fact — no summarization |
| `custom` | Inject `retain_mission` + `custom_instructions` into prompt |

The prompt itself instructs the LLM to output **JSON** with this structure:

```json
{
  "facts": [
    {
      "fact_type": "experience|world|opinion|habit|intention|action_effect",
      "what": "...",
      "when": "...",
      "who": "...",
      "why": "...",
      "occurred_start": "ISO datetime or null",
      "occurred_end": "ISO datetime or null",
      "intention_status": "planning|fulfilled|abandoned or null",
      "confidence": 0.0-1.0,
      "labels": {},
      "entities": ["entity1", "entity2"],
      "causal_relations": [...],
      "action_effect_relations": [...],
      "transition_relations": [...],
      "precondition": "...",
      "action": "...",
      "outcome": "...",
      "devalue_sensitive": true/false
    }
  ]
}
```

**Why the `what`/`when`/`who`/`why` split?** Because the LLM often produces very different granularity when given only a "describe this fact" instruction. Splitting fields forces the model to cover each dimension explicitly, which makes `_normalize_llm_facts()` more reliable.

## `pass2.py` — User-Only Persona Extraction

```python
build_pass2_prompt() → str
```

Pass 2 uses a persona-focused prompt tuned for self-referential statements:

```
You are analyzing a user's personal conversation to extract facts about
the user — their opinions, preferences, habits, intentions, and
experiences. Focus on statements that reveal who the user is as a person.
```

The `PASS2_ALLOWED_FACT_TYPES` constant controls which fact types Pass 2 extracts:
- `opinion` — user preferences and beliefs
- `habit` — recurring behaviors
- `intention` — future plans and goals
- `experience` — past events narrated by or about the user

`world` and `action_effect` are excluded from Pass 2. `world` is objective/time-independent (not persona-specific). `action_effect` comes from causal reasoning about outcomes, not self-description.

## `pass3.py` — Cross-Chunk Relation Discovery

```python
build_pass3_prompt(facts: list[tuple[str, str]]) → str   # (fact_text, fact_type) pairs
```

Pass 1 and Pass 2 each see only one chunk at a time, so they miss relationships that span the whole
session. After `dedup_facts()` merges both passes, `_run_pass3()` ([fact_extraction.py](../../cogmem_api/engine/retain/fact_extraction.py))
sends the **entire merged fact list** to the LLM and asks it to identify connections — mutating the
facts in place by appending `causal_relations`, `transition_relations`, and `action_effect_relations`.
It is default-on (`retain_pass3_enabled`) and only runs when the session has 2–30 facts (bounded to
keep the single extra call cheap).

## Strict Typing Addendum (`COGMEM_API_RETAIN_STRICT_TYPING`)

When `COGMEM_API_RETAIN_STRICT_TYPING=true` **and** the retain payload carries an `enabled_fact_types`
allowlist, the extraction prompt gains a strict-typing addendum that tells the model to only emit the
permitted types. This is used by the cognitive-node necessity benchmark to build paired `_full` /
`_ablated` banks (see [Benchmark & Ablation](../ARCHITECTURE/benchmark-ablation.md)).

## `shared.py` — Temporal Hallucination Sanitization

The `sanitize_temporal()` function in `shared.py` is called **before** the LLM prompt is built. It checks whether the input text contains real temporal context or just vague references like "recently" or "some time ago". This context is passed to the prompt so the LLM doesn't hallucinate dates.

However, the actual sanitization happens in `_sanitize_temporal_fact()` in `fact_extraction.py` — correcting the LLM's output after parsing.

## Why Two Separate Pass Prompt Files?

Separating `pass1.py` and `pass2.py` allows independent evolution:

- Pass 1 can be tuned for factual completeness without worrying about persona extraction
- Pass 2 can be tuned for self-referential bias without worrying about diluting assistant content

Both are versioned together and share the same JSON output contract, so `_normalize_llm_facts()` handles both without branching.

## Verify Commands

```bash
# Check prompt files exist and are importable
uv run python -c "
from cogmem_api.prompts.retain.pass1 import build_pass1_prompt
from cogmem_api.prompts.retain.pass2 import build_pass2_prompt, PASS2_ALLOWED_FACT_TYPES
from cogmem_api.config import get_config
p1, mode = build_pass1_prompt(get_config())
p2 = build_pass2_prompt()
print('Pass 1 mode:', mode)
print('Pass 1 prompt length:', len(p1))
print('Pass 2 prompt length:', len(p2))
print('Pass 2 allowed types:', PASS2_ALLOWED_FACT_TYPES)
"
```
