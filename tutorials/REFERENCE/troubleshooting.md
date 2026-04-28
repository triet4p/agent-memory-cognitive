# Troubleshooting Guide

## Common Errors and Fixes

### `ModuleNotFoundError: No module named 'dateparser'`

**Symptom**: Recall returns empty results, server log shows:
```
"Recall main path failed, using lexical fallback: No module named 'dateparser'"
```

**Cause**: `DateparserQueryAnalyzer` requires the `dateparser` library. It was added as a dependency in task 757.

**Fix**:
```bash
uv add dateparser
```

The `dateparser` library is needed for parsing natural language time expressions in queries ("last week", "Q2 2025", "3 months ago").

---

### `asyncpg.ForeignKeyViolationError` on First Retain

**Symptom**: Every LongMemEval retain call fails with:
```
asyncpg.ForeignKeyViolationError: insert or update on table "memory_units" violates foreign key constraint
```

**Cause**: The `insert_facts_batch()` was inserting `memory_units` rows before the corresponding `documents` row existed. FK from `memory_units.document_id → documents.document_id` failed.

**Fix**: This was fixed in task 756. The fix ensures `documents` is upserted before `memory_units` in `fact_storage.py`. If you see this error, verify your `fact_storage.py` includes the upsert.

---

### `bool("false") == True` — Judge Score String Coercion

**Symptom**: Eval judge always returns `"false"` as a string instead of boolean `False`, causing `bool("false") == True`.

**Cause**: The minimax-m2.7 LLM sometimes returns the string `"false"` as the judge score. `bool("false")` in Python evaluates to `True` because `"false"` is a non-empty string.

**Fix**: Guard with `isinstance(str)` before calling `bool()`:
```python
judge_str = str(judge_result).strip().lower()
if judge_str in ("true", "1", "yes"):
    score = True
elif judge_str in ("false", "0", "no"):
    score = False
# else: handle unexpected value
```

---

### `recall_keyword_accuracy=None` Formatted with `:.3f`

**Symptom**: `TypeError: unsupported format character 'f' at index 0` when formatting recall metrics.

**Cause**: `recall_keyword_accuracy` can be `None` (when no keywords are available in the benchmark). Formatting `None` with `:.3f` raises `TypeError`.

**Fix**: Guard with null check:
```python
kw_str = "null" if kw is None else f"{kw:.3f}"
```

---

### `column "chunk_id" does not exist`

**Symptom**: Retrieval falls back to lexical search, server log may show:
```
column "chunk_id" does not exist
```

**Cause**: The `memory_units` table schema never included `chunk_id` or `tags` columns. Retrieval SQL was selecting these non-existent columns, causing PostgreSQL errors.

**Fix**: Remove `chunk_id` and `tags` from SELECT statements in all retrieval files:
- `retrieval.py` (4 places)
- `graph_retrieval.py` (2 places)
- `link_expansion_retrieval.py` (5 places)
- `mpfp_retrieval.py` (1 place)

---

### Cross-Encoder Silent Fallback

**Symptom**: Server log shows warnings like:
```
"Cross-encoder unavailable, using RRF order directly"
```

**Cause**: The cross-encoder model failed to load (not installed, wrong path, or OOM). The reranking step degrades to a pass-through that returns RRF-ordered candidates.

**Is this a bug?** No. This is expected behavior. The cross-encoder is a quality enhancement, not a correctness requirement. Main retrieval path always succeeds. The warning exists so operators can detect when CE is down if they want to fix it.

---

### `COGMEM_API_GRAPH_RETRIEVER=link_expansion` — Old Default

**Symptom**: Graph traversal uses MAX propagation instead of SUM.

**Cause**: Before S20, the default graph retriever was `link_expansion`. S20 changed the default to `bfs` (SUM + 3 cycle guards). If you see MAX behavior, check your `.env`.

**Fix**: Set `COGMEM_API_GRAPH_RETRIEVER=bfs` in `.env`.

---

### Long retain times or timeouts

**Symptom**: Retain API call times out or takes > 10 minutes for long conversations.

**Cause**: The default timeout for retain is `120s` (2 minutes). For 100+ turn conversations with two-pass extraction, this is too short.

**Fix**: Increase `COGMEM_API_RETAIN_LLM_TIMEOUT=600` in `.env`. Also ensure `COGMEM_API_RETAIN_CHUNK_SIZE=3000` is set so backend chunks large inputs.

---

### `search_vector` column does not exist

**Symptom**: BM25 retrieval fails, falls back to semantic-only search.

**Cause**: The native BM25 path (`DEFAULT_TEXT_SEARCH_EXTENSION = "native"`) was using `ts_rank_cd(search_vector, ...)` which requires a stored `search_vector` column that doesn't exist in the schema.

**Fix (temporary)**: Changed to `to_tsvector('english', text)` applied inline in the SQL. **Fix (permanent)**: A migration should create a stored generated column for `search_vector`.

---

### Intentions with `status=fulfilled` Still Showing in Prospective Queries

**Symptom**: Query "what are you planning to do?" returns fulfilled intentions.

**Cause**: The prospective guard was missing in older versions. `_filter_prospective_results()` filters `intention` nodes with `status != "planning"` after the graph retrieval step.

**Fix**: Verify `_filter_prospective_results()` is called in `retrieve_all_fact_types_parallel()` for prospective query types.

---

## Diagnostic Commands

```bash
# Check which graph retriever is configured
rg "DEFAULT_GRAPH_RETRIEVER" cogmem_api/config.py

# Check if dateparser is installed
uv run python -c "import dateparser; print('dateparser OK')"

# Check DB schema
uv run python -c "
import asyncpg
import os
async def check():
    conn = await asyncpg.connect(os.getenv('COGMEM_API_DATABASE_URL', 'postgresql://postgres@localhost:5432/cogmem'))
    rows = await conn.fetch(\"SELECT column_name FROM information_schema.columns WHERE table_name='memory_units'\")
    print('memory_units columns:', [r['column_name'] for r in rows])
    await conn.close()
import asyncio
asyncio.run(check())
"

# Run the eval script with verbose logging
COGMEM_API_LOG_LEVEL=debug uv run python scripts/eval_cogmem.py --fixture short --profile E7 --verbose
```
