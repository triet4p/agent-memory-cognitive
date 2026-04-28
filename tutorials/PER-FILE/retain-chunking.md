# `chunking.py` — Two-Pass Sentence Splitting

## Purpose

`chunking.py` provides two specialized chunking functions for the two-pass pipeline:

- `chunk_for_pass1()` — all roles, larger chunks (10K chars)
- `chunk_for_pass2()` — user-only, smaller chunks (3K chars)

## `chunk_for_pass1()` — Full-Conversation Chunking

```python
def chunk_for_pass1(messages: list[dict], max_chars: int = 10000) → list[Pass1Chunk]
```

Algorithm:
1. Split each message into sentences (`re.split(r"(?<=[.!?])\s+", text)`)
2. Accumulate sentences into a chunk until adding the next sentence would exceed `max_chars`
3. Yield current chunk and start a new one

**Why sentence-split first?** Mid-sentence breaks would split context. A sentence boundary is a semantically clean break point.

**Why `max_chars=10000`?** Pass 1 needs broad context. The LLM handles ~10K tokens comfortably with 64K max completion.

## `chunk_for_pass2()` — Role-Filtered Chunking

```python
def chunk_for_pass2(messages: list[dict], target_role: str = "user", max_chars: int = 3000) → list[Pass2Chunk]
```

Algorithm:
1. Filter messages where `message["role"] == target_role`
2. Join filtered messages with `"\n\n"` (turn separation)
3. Sentence-split, accumulate at `max_chars`

**Why filter by role?** Pass 2 targets persona signals — user opinions, preferences, habits, intentions. Assistant turns dilute these signals.

**Why `max_chars=3000`?** Smaller = less summarization. Persona details are often in short user statements.

## Dataclasses

```python
@dataclass
class Pass1Chunk:
    text: str
    chunk_index: int
    chunk_id_suffix: str  # e.g. "p1_2_7" = pass 1, chunk 2 of 7
    total_chunks: int

@dataclass
class Pass2Chunk:
    text: str
    chunk_index: int
    chunk_id_suffix: str  # e.g. "p2_0_4" = pass 2, chunk 0 of 4
    total_chunks: int
    target_role: str
```

Pass2Chunk has `target_role` field because chunking logic varies by role.

## `chunk_id_suffix` Pattern

`"{pass}_{chunk_index}_{total}"` — e.g. `"p1_0_7"`, `"p1_1_7"`, `"p2_0_4"`.

Used in `chunk_storage.store_chunks_batch()` to build `chunk_id` as `{bank_id}_{document_id}_{suffix}`.

## Verify Commands

```bash
rg "chunk_for_pass1|chunk_for_pass2" cogmem_api/engine/retain/fact_extraction.py

uv run python -c "
from cogmem_api.prompts.retain.chunking import chunk_for_pass1, chunk_for_pass2
msgs = [
    {'role': 'user', 'content': 'I love Python. It is great for ML.'},
    {'role': 'assistant', 'content': 'That is interesting. What about Rust?'},
    {'role': 'user', 'content': 'I am planning to learn Rust next quarter.'},
]
p1 = chunk_for_pass1(msgs, max_chars=50)
p2 = chunk_for_pass2(msgs, target_role='user', max_chars=50)
print(f'Pass 1: {len(p1)} chunks, Pass 2: {len(p2)} chunks')
"
```
