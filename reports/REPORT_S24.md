# Audit Report — Sprint S24: Retrieval Stack Quality Hardening

**Date:** 2026-04-26  
**Scope:** Tasks 758, 759.1–759.4, 760  
**Auditor:** Claude Code  
**Verdict:** Implementation correct in all functional changes. Three issues require action: one critical test regression (test_task757 now fails), one summary file with a wrong filename reference, one stale docstring. Minor design gaps in test coverage noted below.

---

## 1. Files Reviewed

| File | Role |
|---|---|
| `cogmem_api/alembic/versions/20260426_0002_retrieval_quality.py` | New migration (task 758) |
| `cogmem_api/engine/search/retrieval.py` | BM25 native path revert (task 759.1) |
| `cogmem_api/engine/memory_engine.py` | ef_search pool init (task 759.2) |
| `cogmem_api/engine/retain/fact_storage.py` | tags INSERT (task 759.3) |
| `cogmem_api/engine/retain/orchestrator.py` | document_tags pass-through (task 759.3) |
| `cogmem_api/engine/query_analyzer.py` | Dead code removal (task 759.4) |
| `tests/artifacts/test_task758_migration.py` | Artifact: migration |
| `tests/artifacts/test_task7591_bm25_search_vector.py` | Artifact: BM25 revert |
| `tests/artifacts/test_task7592_ef_search.py` | Artifact: ef_search |
| `tests/artifacts/test_task7593_document_tags.py` | Artifact: document_tags |
| `tests/artifacts/test_task7594_flat_query_analyzer.py` | Artifact: dead code |
| `logs/task_758_summary.md` | Summary log |
| `logs/task_759_summary.md` | Summary log |
| `tests/artifacts/test_task757_recall_fixes.py` | Dependency: prior sprint tests |
| `cogmem_api/engine/search/tags.py` | Dependency: tag SQL builders |
| `cogmem_api/engine/retain/types.py` | Dependency: COGMEM_FACT_TYPES |
| `cogmem_api/alembic/versions/20260330_0001_t1_2_schema_extensions.py` | Dependency: migration chain |

---

## 2. Implementation Verification

### 2.1 Migration 20260426_0002 (Task 758)

| Check | Result |
|---|---|
| Revision chain correct: `down_revision = "20260330_0001"` | ✅ |
| `search_vector GENERATED ALWAYS AS STORED` with `text \|\| raw_snippet` | ✅ |
| GIN index `idx_memory_units_search_vector` | ✅ |
| `tags text[] nullable` column + partial GIN index | ✅ |
| 6 partial HNSW indexes matching `COGMEM_FACT_TYPES` | ✅ |
| `idx_memory_links_entity_covering` (INCLUDE covering index) | ✅ |
| `idx_memory_links_to_type_weight` (composite on to_unit_id) | ✅ |
| `downgrade()` reverses in correct order (indexes before columns) | ✅ |
| `FACT_TYPES` in migration matches `COGMEM_FACT_TYPES` in `types.py` | ✅ |

**Migration SQL is structurally correct.** `op.execute()` raw SQL is the correct approach for `GENERATED ALWAYS AS STORED` — Alembic's `op.add_column` doesn't support this PostgreSQL syntax.

### 2.2 BM25 Native Path Revert (Task 759.1)

`retrieval.py` native branch (`else` clause, line 411–416):

```python
else:  # native — stored generated column search_vector (migration 20260426_0002)
    bm25_score_expr = "ts_rank_cd(search_vector, to_tsquery('english', $4))"
    bm25_where_filter = "AND search_vector @@ to_tsquery('english', $4)"
```

| Check | Result |
|---|---|
| `ts_rank_cd(search_vector,` present (uses stored column) | ✅ |
| `search_vector @@ to_tsquery` present | ✅ |
| `to_tsvector('english', text)` absent from retrieval.py | ✅ (confirmed via grep — zero matches) |
| SQL parameter layout unchanged: `$4 = bm25_text_param` | ✅ |
| Tags parameter index `$5 if tokens else $4` consistent with param layout | ✅ |

### 2.3 ef_search=200 Pool Init (Task 759.2)

`memory_engine.py` lines 169–178:

```python
async def _init_pool_connection(conn: asyncpg.Connection) -> None:
    await conn.execute("SET hnsw.ef_search = 200")

self._pool = await asyncpg.create_pool(
    ..., init=_init_pool_connection,
)
```

| Check | Result |
|---|---|
| `_init_pool_connection` defined as local function inside `connect()` | ✅ |
| Uses `SET` (session-level), NOT `SET LOCAL` (transaction-only) | ✅ |
| Passed as `init=` to `asyncpg.create_pool` | ✅ |
| `_bootstrap_schema_objects()` uses own SQLAlchemy engine, not the pool | ✅ (no race condition) |

**Sequencing is correct.** Pool is created first; `init` callback fires on first connection acquire. By that time, `_bootstrap_schema_objects()` (which uses a separate engine) has already applied migrations and installed pgvector. No race condition.

### 2.4 document_tags Wiring (Task 759.3)

**`fact_storage.py`:**
- Signature: `document_tags: list[str] | None = None` ✅
- INSERT column list includes `tags` ✅
- INSERT VALUES has `$15::text[]` ✅
- Value passed: `document_tags or None` ✅

**`orchestrator.py`:**
- `retain_batch()` signature includes `document_tags: list[str] | None = None` (line 69) ✅
- `insert_facts_batch(... document_tags=document_tags)` at line 137 ✅

The `hasattr(conn, "insert_memory_units")` guard (line 67 of fact_storage.py) forwards `document_tags` to the mock/test stub path. This is correct.

### 2.5 FlatQueryAnalyzer Dead Code (Task 759.4)

`query_analyzer.py` lines 620–625:

```python
def analyze(self, query: str, reference_date: datetime | None = None) -> QueryAnalysis:
    return QueryAnalysis(
        temporal_constraint=None,
        query_type="semantic",
        rrf_weights={ch: 1.0 for ch in ("semantic", "bm25", "graph", "temporal")},
    )
```

No trailing `return None`. ✅ The AST-based test (`test_task7594`) correctly verifies this.

---

## 3. Issues Found

### 3.1 🔴 CRITICAL — test_task757 test_8_7 now FAILS (test regression)

**File:** `tests/artifacts/test_task757_recall_fixes.py`, function `test_8_7_native_bm25_no_search_vector` (line 164–183)

The task 757 test was written to verify Fix 8.7 (the *workaround*): that the native BM25 path does NOT use `search_vector` and DOES use inline `to_tsvector`. Task 759.1 reverts exactly this. The three assertions in that test now all fail:

```python
assert "ts_rank_cd(search_vector," not in src    # FAILS — line 413 of retrieval.py has this
assert "search_vector @@ to_tsquery" not in src  # FAILS — line 415 has this
assert "to_tsvector('english', text)" in src     # FAILS — zero occurrences in retrieval.py
```

Running `uv run python tests/artifacts/test_task757_recall_fixes.py` will report 7/8 passed (test 8 fails).

**Action required:** Update `test_8_7_native_bm25_no_search_vector` in `test_task757_recall_fixes.py` to reflect the new state: the column now EXISTS (migration 20260426_0002), so search_vector usage IS correct. The test should be inverted or marked as superseded.

### 3.2 🟠 SIGNIFICANT — Summary log references a non-existent test file

**File:** `logs/task_758_summary.md`

The summary states:
```
## Artifact test file
`tests/artifacts/test_task758_retrieval_quality.py`
```

This file does not exist. The actual test artifacts for S24 are five separate files:
- `test_task758_migration.py` (3 tests)
- `test_task7591_bm25_search_vector.py` (1 test)
- `test_task7592_ef_search.py` (1 test)
- `test_task7593_document_tags.py` (2 tests)
- `test_task7594_flat_query_analyzer.py` (1 test)

The "8/8 PASS" total is accurate (3+1+1+2+1=8), but the filename reference is wrong. The summary header also says "Task 760" but the file is saved as `task_758_summary.md` — this is confusing. There is no `task_760_summary.md`.

**Action required:** Update `logs/task_758_summary.md` to list the five actual test files. Create `logs/task_760_summary.md` or rename the existing file appropriately.

### 3.3 🟡 MINOR — Stale migration name in retrieval.py docstring

**File:** `cogmem_api/engine/search/retrieval.py`, line 320

```python
Alembic migration a3b4c5d6e7f8_add_partial_hnsw_indexes.py.
```

This references a migration that does not exist. The correct file is `20260426_0002_retrieval_quality.py`.

**Action required:** Update the docstring to reference the correct migration file.

---

## 4. Test Design Analysis

### test_task758_migration.py — 3 tests

| Test | Verdict | Notes |
|---|---|---|
| `test_migration_exists_with_correct_chain` | ✅ Correct | Checks file existence and revision strings |
| `test_migration_has_all_required_indexes` | ⚠️ Weak | Loop uses static string `"idx_mu_emb_{ft}"` (NOT an f-string) — same pattern checked 6 times. Does not verify that all 6 fact_types are in `FACT_TYPES` list. Functionally correct for template detection but gives no per-fact-type guarantee. |
| `test_migration_search_vector_includes_raw_snippet` | ✅ Correct | Checks for `raw_snippet` and `to_tsvector` in migration source |

**Gap:** No test verifies `downgrade()` completeness (all indexes dropped in reverse order). The test checks drop patterns for named indexes and partial HNSW template, but not the `DROP COLUMN search_vector` statement.

### test_task7591_bm25_search_vector.py — 1 test

| Test | Verdict | Notes |
|---|---|---|
| `test_bm25_native_path_uses_search_vector_column` | ⚠️ Missing negative assertion | Checks that `search_vector` IS used. Does NOT check that `to_tsvector('english', text)` is absent (the inline fallback removed by this task). If someone accidentally added an inline fallback elsewhere, the test would still pass. |

### test_task7592_ef_search.py — 1 test

| Test | Verdict | Notes |
|---|---|---|
| `test_ef_search_set_in_pool_init` | ✅ Correct | Checks static string presence AND `init=` kwarg. Comprehensive for static analysis. |

### test_task7593_document_tags.py — 2 tests

| Test | Verdict | Notes |
|---|---|---|
| `test_insert_facts_batch_accepts_document_tags` | ✅ Correct | Uses `inspect.signature` — strongest possible signature check |
| `test_orchestrator_passes_document_tags` | ✅ Correct | Checks signature + source string `document_tags=document_tags`. Sufficient. |

**Gap:** No test checks that the INSERT SQL actually contains `tags` column and `$15::text[]`. A static source check for `$15::text[]` would close this.

### test_task7594_flat_query_analyzer.py — 1 test

| Test | Verdict | Notes |
|---|---|---|
| `test_flat_query_analyzer_no_dead_code` | ✅ Excellent | Uses `ast.parse` + `ast.unparse` — robust against whitespace/formatting changes. Correctly detects `return None` after `return QueryAnalysis`. |

---

## 5. Dependency Analysis — Affected Files Not Changed

### tags.py SQL builders

`build_tags_where_clause_simple` and `build_tag_groups_where_clause` generate SQL that references the `tags` column. Previously, executing these against the DB would crash if the column didn't exist. After migration 20260426_0002, `tags text[]` exists. ✅

The GIN index `idx_memory_units_tags WHERE tags IS NOT NULL` will be used by PostgreSQL for GIN array operators (`&&`, `@>`). ✅

### retrieve_temporal_combined (retrieval.py lines 503–556)

Uses `build_tags_where_clause_simple(tags, 7, ...)` with parameter `$7`. This SQL clause references the `tags` column. Previously broken if `tags` was passed. Now correct. ✅

The spreading subquery inside the temporal retrieval loop also uses `tags` at `$7`. Consistent. ✅

### graph_retrieval.py, link_expansion_retrieval.py, mpfp_retrieval.py

These files had `chunk_id` and `tags` removed from their SELECTs in task 757 (fix 8.6). They do NOT select `tags` from `memory_units`. This is correct since `RetrievalResult` has no `tags` attribute and the graph/link retrieval paths don't need tag information. ✅

The new indexes `idx_memory_links_entity_covering` and `idx_memory_links_to_type_weight` will automatically be used by PostgreSQL for queries in `link_expansion_retrieval.py` and `graph_retrieval.py` when applicable. No code changes needed. ✅

### orchestrator.py — chunk_id assignment (pre-existing, not S24)

Line 130: `processed_fact.chunk_id = chunk_id_map.get(extracted_fact.chunk_index)` assigns `chunk_id` to `ProcessedFact`. This field is not persisted to the DB (not in `insert_facts_batch` SQL). This is a pre-existing stub behavior (chunk_storage is unimplemented), not introduced by S24. ✅

---

## 6. Runtime Risk Assessment

| Risk | Severity | Notes |
|---|---|---|
| `SET hnsw.ef_search = 200` fails if pgvector not installed | Low | pgvector is a hard dependency; embedded postgres setup always has it. No error handling in `_init_pool_connection`. Would cause pool acquisition to fail. |
| `search_vector` backfill on existing data during migration | Low | GENERATED column backfills all rows. For eval datasets (< 10K rows), fast. For production, could block writes temporarily. |
| 6 HNSW index creations in single transaction | Low | All non-concurrent, within transaction. Safe for small datasets. For large datasets (> 100K rows), consider `CREATE INDEX CONCURRENTLY` (requires separate transactions, not possible inside Alembic upgrade). |
| `document_tags or None` treats `[]` as NULL | Very Low | Empty list → NULL in DB. Semantically: `tags IS NULL` vs `tags = '{}'`. GIN index handles both as "untagged". Behavior consistent with `include_untagged=True` default. |
| Partial HNSW indexes improve accuracy only with sufficient rows | Very Low | HNSW builds a graph; with < 10 rows per fact_type, brute-force is used anyway. ef_search=200 has no downside in this case. |

---

## 7. Summary Verdict

| Task | Functional Correctness | Test Coverage |
|---|---|---|
| 758 Migration | ✅ Correct | ⚠️ HNSW loop check is pattern-based, not per-type |
| 759.1 BM25 revert | ✅ Correct | ⚠️ Missing negative assertion for inline tsvector |
| 759.2 ef_search | ✅ Correct | ✅ |
| 759.3 document_tags | ✅ Correct | ⚠️ Missing SQL content check for `$15::text[]` |
| 759.4 dead code | ✅ Correct | ✅ (AST-based, strong) |

**The implementation is functionally sound.** All 5 sub-tasks implement exactly what was specified in the plan. No SQL injection risks, no schema mismatches in the changed files, parameter indexing consistent.

**Three actions required before marking S24 complete:**

1. **[CRITICAL]** Fix `test_8_7_native_bm25_no_search_vector` in `test_task757_recall_fixes.py` — invert the 3 assertions to reflect that `search_vector` now EXISTS and IS used correctly.

2. **[SIGNIFICANT]** Update `logs/task_758_summary.md` — correct the artifact file name from `test_task758_retrieval_quality.py` to list the 5 actual files.

3. **[MINOR]** Fix docstring in `retrieval.py` line 320 — replace `a3b4c5d6e7f8_add_partial_hnsw_indexes.py` with `20260426_0002_retrieval_quality.py`.
