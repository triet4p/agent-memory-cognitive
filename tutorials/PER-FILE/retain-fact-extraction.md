# `fact_extraction.py` — The Heart of Retain

## Purpose

`fact_extraction.py` is the largest and most complex module in the retain pipeline. It converts raw conversation text into structured `ExtractedFact` objects using an LLM, with three fallback layers if the LLM is unavailable or returns nothing.

It is the **only module** that calls the prompt builders (`build_pass1_prompt`, `build_pass2_prompt`) and the only place where `_sanitize_temporal_fact()` and heuristic type overrides are applied.

## Key Functions

### `extract_facts_from_contents()` — Public Entry Point

```python
async def extract_facts_from_contents(
    contents: list[RetainContent],
    llm_config, agent_name, config, pool, operation_id, schema
) -> tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage]
```

This is the function called by `orchestrator.retain_batch()`. The logic:

```
For each RetainContent in contents:
  ├─ if content.facts is non-empty → _extract_seeded_facts() [programmatic, no LLM]
  ├─ else if llm_config → _extract_facts_with_llm()
  │     ├─ PASS 1 + PASS 2 if two_pass_enabled AND content.messages exists
  │     └─ SINGLE-PASS if no messages (legacy path)
  └─ else → _extract_fallback_facts() [regex split, last resort]
```

**Why the order matters**: `content.facts` is the programmatic path (used in tests with `_BaseFakeLLM`). LLM path is the production path. Fallback is the safety net.

### `_extract_facts_with_llm()` — Two-Pass or Single-Pass

**Two-pass path** (when `content.messages` + `two_pass_enabled=True`):
1. **Pass 1**: All messages, chunked at `retain_pass1_chunk_chars` (default 10K). Each chunk sent to `_call_llm_for_pass1()` → `_normalize_llm_facts()`.
2. **Pass 2**: User-role messages only, chunked at `retain_pass2_chunk_chars` (default 3K). Each chunk sent to `_call_llm_for_pass2()` → `_normalize_llm_facts()` with `mode="concise"` and `extract_causal_links=False`.
3. **Dedup**: `dedup_facts(facts_p1, facts_p2)` — Pass 2 preference for personal types (`opinion`, `habit`, `intention`, `experience`).

**Single-pass path** (legacy, no messages):
- Entire `content.content` chunked at `retain_chunk_size` (default 3K)
- Each chunk → `_call_llm_chunk()` → `_normalize_llm_facts()` with mode from `build_pass1_prompt(config)`

**Why Pass 2 is persona-focused**: The `build_pass2_prompt()` system prompt explicitly tells the LLM to extract "facts about the user — their opinions, preferences, habits, intentions, and experiences." Pass 1 is general-purpose.

### `_normalize_llm_facts()` — The Critical Parsing Function

**Temporal sanitization** (`_sanitize_temporal_fact()`): SLMs hallucinate dates. If the fact text lacks real time context (`"today"`, `"now"`, etc.) and the `occurred_start` contains today's date, it clears the temporal field. World facts always have their temporal fields stripped.

**Type inference** (`_infer_fact_type()`): Regex patterns on text:
- `"always"`, `"usually"`, `"often"`, `"routine"` → `habit`
- `"if"..."then"`, `"led to"`, `"resulted in"` → `action_effect`
- Otherwise → `world`

**Three heuristic overrides**:
1. `world → habit`: LLM classified as `world` but text has habit signals
2. `world → intention`: LLM returned `world` but included `intention_status`
3. `experience → intention`: LLM classified as `experience` but `what` text has future-planning patterns

**Fulfilled intention detection** (`_infer_fulfilled_from_context()`): Checks completion signals (`"finished"`, `"completed"`, `"achieved"`) combined with past-intention markers (`"was planning to"`).

### `_call_llm_chunk()` — LLM HTTP Call

- `temperature=0.1` (low temperature for structured extraction)
- `max_completion_tokens` from config
- `return_usage=True` for token tracking
- Errors: `OutputTooLongError`, `TypeError` (fake LLM), generic `Exception`
- Returns raw JSON → parsed via `parse_llm_json()`

### `_parse_action_effect_triplet()` — A-O Triple Extraction from Text

Last-resort parser for `action_effect` facts when LLM didn't return structured fields:

```python
pattern = r"(?i)(?:if|when)\s+(?P<pre>[^,.;]+),\s*(?P<act>[^,.;]+?)\s*(?:,\s*)?(?:so|then|therefore|which led to|leading to|resulting in)\s+(?P<out>[^.;]+)"
```

Example: "If shop rating is high, then delivery is faster" → `pre="shop rating is high"`, `act="shop rating is high"`, `out="delivery is faster"`.

## Chunking System

Two different chunking strategies:

**`chunk_for_pass1()`** — Sentence-split + accumulate at 10K chars. For all roles, broader context.

**`chunk_for_pass2()`** — Role-filtered + sentence-split at 3K chars. For user-only turns, cleaner persona signals.

## Verify Commands

```bash
# Check LLM call path is exercised
uv run python tests/artifacts/test_task612_retain_prompt_parity.py

# Check two-pass chunking
rg "chunk_for_pass1|chunk_for_pass2" cogmem_api/engine/retain/fact_extraction.py

# Check temporal sanitization
rg "_sanitize_temporal_fact|TODAY_TIME_KEYWORDS" cogmem_api/engine/retain/fact_extraction.py
```
