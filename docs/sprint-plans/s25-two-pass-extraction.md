# Sprint S25: 2-Pass Speaker-Aware Extraction + Prompt Centralization

**Trạng thái:** ✅ Done (tasks 778-785)

**Phụ thuộc:** S24.8 PASS

---

## Context

**Why this change.** E7 evaluation v7 trên LongMemEval cho thấy hệ thống miss 2/5 model kits (Spitfire Mk.V, Camaro). Diagnose qua API `/recall` xác nhận:
- DB chỉ có `world` facts về kỹ thuật — không có `experience` fact "User bought/finished Tamiya 1/48 Spitfire Mk.V" hay "User got 1/24 '69 Camaro at model show".
- Retain pipeline đọc các session đó nhưng chỉ extract assistant's verbose advice (~80% chunk text), bỏ qua user's brief side-notes.

**Root cause architectural.** Single-pass LLM extraction trên mixed-speaker chunk → attention asymmetry: Ministral-3B bị dominate bởi turn dài (assistant), miss turn ngắn (user).

**Theoretical foundation.** Information density asymmetry: user turns dense (goal-oriented utterance), assistant turns verbose (RLHF-tuned inflation). Personal facts memorable nằm ở "human source".

**Outcome mong đợi:**
- Pass 2 capture user-side experience/habit/intention/opinion mà Pass 1 đã miss.
- Spitfire và Camaro experience facts xuất hiện trong DB sau re-retain.
- E7 recall top-20 chứa cả 5 kits.

---

## Architecture Overview

```
HTTP /memories  ──►  RetainItem.messages  (new structured input)
                       │
                       ▼
                  orchestrator.retain_batch
                       │
                       ▼
              fact_extraction.extract_facts_from_contents
                       │
        ┌──────────────┼──────────────┐
        ▼                             ▼
    PASS 1                         PASS 2
  (full chunk,                  (per-speaker turns,
   wide context,                 high-density,
   all 6 fact types)             4 personal types)
        │                             │
        └──────────────┬──────────────┘
                       ▼
                 dedup_facts
                       │
                       ▼
            embedding/storage/links
```

---

## Task 778 — API: structured messages input

**Files:** `cogmem_api/api/http.py`, `cogmem_api/engine/retain/types.py`

- Add `MessageInput(role: str, content: str)` Pydantic model.
- Extend `RetainItem`: add `messages: list[MessageInput] | None = None`. Keep `content: str` for backward compat.
- Validation: at least one of `content` or `messages` must be non-empty.
- `content` field tự động được derive từ `messages` (concat with role prefixes) khi `messages` provided.

---

## Task 779 — Prompt centralization

**New directory:** `cogmem_api/prompts/`

```
cogmem_api/prompts/
  __init__.py
  retain/
    __init__.py
    pass1.py     # _BASE_PROMPT, mode prompts moved from fact_extraction.py
    pass2.py     # NEW: persona-focused prompt (4 fact types only)
    shared.py    # FACT_TYPE_GUIDE, OUTPUT_FORMAT_RULES, RELATIONS blocks
  eval/
    __init__.py
    judge.py     # build_judge_system_prompt moved from eval_helpers.py
    generate.py  # build_generation_prompt moved from eval_helpers.py
```

- Move existing prompt strings out of `fact_extraction.py` and `eval_helpers.py`.
- `eval_helpers.py` only keeps utility (`parse_judge_response`).
- Pass 1 prompt = current `_BASE_PROMPT` with 2 minor edits:
  - Drop "ONLY use 'experience' if the USER (not the assistant) did or experienced something specific"
  - Add: "This is Pass 1 of 2-pass extraction; a second pass focuses on user-only segments."

---

## Task 780 — Pass 2 prompt design

File: `cogmem_api/prompts/retain/pass2.py`

Principles:
- Input is single-speaker text (already filtered to user turns).
- Allowed fact types: `experience`, `habit`, `intention`, `opinion` (no `world`, no `action_effect`).
- Instruction frame: "The text below is from a single speaker describing their own context."
- Be aggressive about brief mentions: "Even a single short statement like 'I bought X' or 'I'm planning Y' MUST be extracted as a separate fact."
- Same JSON output format as Pass 1.

---

## Task 781 — Two chunking strategies

**New file:** `cogmem_api/engine/retain/chunking.py`

**`chunk_for_pass1(messages, max_chars=10000) -> list[Pass1Chunk]`**
- Internal representation: list of `(role, sentence)` tuples.
- Pack sentences into chunks ≤ `max_chars`. Sentences within a single turn CAN be split across chunks.
- Role marker duplication on split: when a chunk cuts in the middle of a speaker's turn, the next chunk MUST prepend the same role marker.
- Render rule: emit role marker whenever (a) first sentence of chunk, or (b) role differs from previous sentence.
- Each `Pass1Chunk` carries: `text`, `chunk_index`, `messages_covered: list[int]`.

**`chunk_for_pass2(messages, target_role="user", max_chars=3000) -> list[Pass2Chunk]`**
- Filter messages where `role == target_role`.
- For each filtered turn: if ≤ max_chars → 1 sub-chunk; else sentence-split into multiple sub-chunks.
- `Pass2Chunk` carries: `text`, `chunk_index`, `source_message_idx`, `sub_chunk_index`, `target_role`.

Chunk ID namespaces:
- `Pass1Chunk.chunk_id_suffix = f"p1_{chunk_index}"`
- `Pass2Chunk.chunk_id_suffix = f"p2_{source_message_idx}_{sub_chunk_index}"`

---

## Task 782 — Refactor `_extract_facts_with_llm` for 2-pass

File: `cogmem_api/engine/retain/fact_extraction.py`

```python
async def _extract_facts_with_llm(content, content_index, llm_config, config):
    if content.messages:
        pass1_chunks = chunk_for_pass1(content.messages, max_chars=...)
        pass2_chunks = chunk_for_pass2(content.messages, target_role="user", max_chars=...)
    else:
        # Backward-compat path: parse "user:" / "assistant:" from plain text
        parsed_messages = _parse_legacy_text(content.content)
        pass1_chunks = chunk_for_pass1(parsed_messages, ...)
        pass2_chunks = chunk_for_pass2(parsed_messages, ...)

    # Pass 1 — full chunks, all 6 fact types
    facts_p1 = []
    for pc in pass1_chunks:
        raw = await _call_llm_chunk(pass1_prompt, pc.text, ...)
        facts_p1 += _normalize_llm_facts(raw, content, content_index, pc.chunk_id_suffix, ...)

    # Pass 2 — user segments only, 4 personal fact types
    facts_p2 = []
    if config.retain_two_pass_enabled:
        for pc in pass2_chunks:
            raw = await _call_llm_chunk(pass2_prompt, pc.text, ...)
            normalized = _normalize_llm_facts(raw, content, content_index, pc.chunk_id_suffix, ...)
            normalized = [f for f in normalized if f.fact_type in PASS2_ALLOWED]
            facts_p2 += normalized

    final_facts = dedup_facts(facts_p1, facts_p2)
    return final_facts, all_chunks, total_usage
```

`PASS2_ALLOWED = {"experience", "habit", "intention", "opinion"}`

---

## Task 783 — Cross-pass dedup

**New file:** `cogmem_api/engine/retain/dedup.py`

Function `dedup_facts(facts_p1, facts_p2) -> list[ExtractedFact]`:
- Key: `(fact_type, normalized_text)` where `normalized_text` = lowercased + whitespace-collapsed + first 120 chars.
- For 4 personal types: same key in both passes → keep Pass 2, drop Pass 1.
- For `world` / `action_effect`: only Pass 1 contributes (Pass 2 cannot extract these).
- Fuzzy match (optional, behind config flag): rapidfuzz `token_set_ratio >= 90` on `text` field.

---

## Task 784 — Config + Eval script update

**`cogmem_api/config.py`** — new env fields:
- `retain_two_pass_enabled: bool = True` (env `COGMEM_API_RETAIN_TWO_PASS_ENABLED`)
- `retain_pass1_chunk_chars: int = 10000` (env `COGMEM_API_RETAIN_PASS1_CHUNK_CHARS`)
- `retain_pass2_chunk_chars: int = 3000` (env `COGMEM_API_RETAIN_PASS2_CHUNK_CHARS`)
- `retain_pass2_target_roles: tuple[str,...] = ("user",)` — for LoCoMo: `("speaker_a", "speaker_b")`

**`scripts/eval_cogmem.py`**: Update `retain_fixture()` to send `messages: [{role, content}]` instead of joined plain text.

---

## Task 785 — Artifact tests

- `tests/artifacts/test_task781_chunking.py`
  - Pass 1 chunker: produces N chunks ≤ max_chars; role marker duplication verified.
  - Pass 2 chunker: only user turns extracted; long user turn sub-chunked correctly.
- `tests/artifacts/test_task782_two_pass_extraction.py`
  - With FakeLLM: Pass 1 gets full chunk, Pass 2 gets user-only text. Both LLM calls happen.
  - Pass 2 fact with `fact_type="world"` → filtered out.
  - `retain_two_pass_enabled=False` → only Pass 1 runs.
- `tests/artifacts/test_task783_dedup.py`
  - Same `(fact_type, normalized_text)` in both passes → keeps Pass 2.
  - Different normalized texts → both kept.
- `tests/artifacts/test_task779_prompt_organization.py`
  - All Pass 1/Pass 2/judge/generate prompts reachable via `cogmem_api.prompts.*`.
  - `eval_helpers.py` no longer contains prompt template strings.

---

## Files to Create

- `cogmem_api/prompts/__init__.py`
- `cogmem_api/prompts/retain/__init__.py`
- `cogmem_api/prompts/retain/pass1.py`
- `cogmem_api/prompts/retain/pass2.py`
- `cogmem_api/prompts/retain/shared.py`
- `cogmem_api/prompts/eval/__init__.py`
- `cogmem_api/prompts/eval/judge.py`
- `cogmem_api/prompts/eval/generate.py`
- `cogmem_api/engine/retain/chunking.py`
- `cogmem_api/engine/retain/dedup.py`
- `tests/artifacts/test_task779_prompt_organization.py`
- `tests/artifacts/test_task781_chunking.py`
- `tests/artifacts/test_task782_two_pass_extraction.py`
- `tests/artifacts/test_task783_dedup.py`

## Files to Modify

- `cogmem_api/api/http.py` — `RetainItem.messages`, `MessageInput`, `_build_retain_payload`
- `cogmem_api/engine/retain/types.py` — `RetainContentDict.messages`, `RetainContent.messages`
- `cogmem_api/engine/retain/fact_extraction.py` — remove prompt constants, split `_extract_facts_with_llm`
- `cogmem_api/engine/retain/orchestrator.py` — propagate `messages` to `RetainContent`
- `cogmem_api/engine/eval_helpers.py` — remove prompt builders
- `cogmem_api/config.py` — new env fields
- `scripts/eval_cogmem.py` — send structured messages

---

## Verification

```bash
uv run python tests/artifacts/test_task779_prompt_organization.py
uv run python tests/artifacts/test_task781_chunking.py
uv run python tests/artifacts/test_task782_two_pass_extraction.py
uv run python tests/artifacts/test_task783_dedup.py
```

### Integration: re-retain LongMemEval
1. Delete bank + re-retain.
2. Diagnose:
   ```bash
   curl -X POST .../recall -d '{"query":"Spitfire Mk.V purchased finished","fact_types":["experience"],"top_k":5}'
   curl -X POST .../recall -d '{"query":"Camaro 69 model kit got","fact_types":["experience"],"top_k":5}'
   ```
   Both queries must return at least 1 `experience` fact mentioning the kit.

### E2E: E7 evaluation
- Question "How many model kits have I worked on or bought?" → recall top-20 contains at least 1 experience fact for each of 5 kits.
- Generated answer mentions at least 4/5 kits.
- Judge `correct=True` or `score >= 0.7`.

### Performance regression
- New retain time (2-pass): expect ~1.5–2.0x baseline. If >2.5x, profile and tune.

---

## Out of Scope (deferred)

- Cross-encoder rerank quality issue (rank-1 cliff).
- Generation prompt rework.
- Embedding model swap.
