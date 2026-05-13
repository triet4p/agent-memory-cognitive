# Sprint S24: Retrieval Stack Quality Hardening

**Trạng thái:** ✅ Done (tasks 758-760)

---

## Mục tiêu sprint
1. Tạo Alembic migration bổ sung đầy đủ schema/index còn thiếu mà retrieval code đã assume tồn tại.
2. Đồng bộ code để dùng đúng schema mới — không còn workaround inline.
3. Fix ef_search chưa được set thực tế — đây là accuracy gap quan trọng nhất.
4. Wire document_tags vào retain pipeline để tags thực sự được lưu và có thể dùng cho filtering.

Phụ thuộc: S23 PASS + task 757 hotfixes PASS.

---

## Lý do kỹ thuật

- **BM25 no-index**: `to_tsvector('english', text) @@ to_tsquery(...)` không có GIN index → full sequential scan. Với stored generated column + GIN index: PostgreSQL dùng index scan.
- **search_vector stored vs inline**: `ts_rank_cd(search_vector, ...)` nhanh hơn khi tsvector đã được tính trước.
- **ef_search=40 vs 200**: HNSW default ef_search=40 có accuracy thấp hơn nhiều so với ef_search=200. Đây là **accuracy impact trực tiếp và quan trọng nhất** của sprint này.
- **Partial HNSW indexes**: Mỗi fact_type có partial index riêng → HNSW graph build trên tập nhỏ hơn → approximate nearest neighbor chính xác hơn trong partition.
- **Tags column**: API nhận `tags` từ client nhưng không lưu vào DB → tags filtering luôn crash/no-op.

---

## Task 758 — Alembic migration: Retrieval Quality Schema ✅

**File tạo mới**: `cogmem_api/alembic/versions/20260426_0002_retrieval_quality.py`

```
revision = "20260426_0002"
down_revision = "20260330_0001"
```

Nội dung `upgrade()`:

**Step 1 — search_vector stored generated column + GIN index:**
```python
op.execute("""
    ALTER TABLE memory_units
    ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(text, '') || ' ' || coalesce(raw_snippet, ''))
    ) STORED
""")
op.execute(
    "CREATE INDEX idx_memory_units_search_vector "
    "ON memory_units USING gin(search_vector)"
)
```
Lý do include `raw_snippet`: chứa nhiều keyword quan trọng không xuất hiện trong `text` (extracted fact).

**Step 2 — tags column + GIN index:**
```python
op.add_column("memory_units", sa.Column("tags", sa.ARRAY(sa.Text()), nullable=True))
op.execute(
    "CREATE INDEX idx_memory_units_tags "
    "ON memory_units USING gin(tags) "
    "WHERE tags IS NOT NULL"
)
```

**Step 3 — 6 partial HNSW indexes per fact_type:**
```python
FACT_TYPES = ["world", "experience", "opinion", "habit", "intention", "action_effect"]
for ft in FACT_TYPES:
    op.execute(
        f"CREATE INDEX idx_mu_emb_{ft} "
        f"ON memory_units USING hnsw (embedding vector_cosine_ops) "
        f"WHERE fact_type = '{ft}'"
    )
```

**Step 4 — memory_links covering/composite indexes:**
```python
op.execute(
    "CREATE INDEX idx_memory_links_entity_covering "
    "ON memory_links (from_unit_id) "
    "INCLUDE (to_unit_id, entity_id) "
    "WHERE link_type = 'entity'"
)
op.execute(
    "CREATE INDEX idx_memory_links_to_type_weight "
    "ON memory_links (to_unit_id, link_type, weight DESC)"
)
```

---

## Task 759 — Code adaptations to match new schema ✅

**759.1 — Revert fix 8.7 trong retrieval.py, dùng search_vector column**

File: `cogmem_api/engine/search/retrieval.py` (native BM25 branch)

Dùng:
```python
else:  # native — stored generated column search_vector (migration 20260426_0002)
    query_tsquery = " | ".join(tokens)
    bm25_score_expr = "ts_rank_cd(search_vector, to_tsquery('english', $4))"
    bm25_order_by = f"{bm25_score_expr} DESC"
    bm25_where_filter = "AND search_vector @@ to_tsquery('english', $4)"
    bm25_text_param = query_tsquery
```

**759.2 — Set ef_search=200 trong pool init**

File: `cogmem_api/engine/memory_engine.py`

```python
async def _init_pool_connection(conn: asyncpg.Connection) -> None:
    """Set per-connection HNSW search parameters for accuracy."""
    await conn.execute("SET hnsw.ef_search = 200")
```

Truyền `init=_init_pool_connection` vào `asyncpg.create_pool(...)`.

**Lưu ý**: Không dùng `SET LOCAL` — chỉ có hiệu lực trong transaction. Dùng `SET` (session-level).

**759.3 — Wire document_tags vào fact_storage INSERT**

File: `cogmem_api/engine/retain/fact_storage.py` — thêm `document_tags: list[str] | None = None` vào `insert_facts_batch`.

File: `cogmem_api/engine/retain/orchestrator.py` — pass `document_tags=document_tags` vào `insert_facts_batch`.

**759.4 — Xóa dead code trong FlatQueryAnalyzer**

File: `cogmem_api/engine/query_analyzer.py` — xóa dòng `return None` unreachable sau `return QueryAnalysis(...)`.

---

## Task 760 — Artifact tests + summary log ✅

**`tests/artifacts/test_task758_retrieval_quality.py`** — 8 tests:
1. Migration `20260426_0002` tồn tại, revision chain đúng.
2. Migration tạo đủ indexes.
3. `search_vector` generated column dùng cả `text` và `raw_snippet`.
4. BM25 native path dùng `search_vector` column.
5. `ef_search=200` trong pool init.
6. `insert_facts_batch` có parameter `document_tags`.
7. `orchestrator.py` pass `document_tags`.
8. `FlatQueryAnalyzer.analyze()` không có unreachable `return None`.

**Exit gate:**
1. `uv run python tests/artifacts/test_task758_retrieval_quality.py` — 8/8 tests PASS.
2. `alembic upgrade head` từ clean DB chạy không lỗi.
3. BM25 native path dùng `search_vector` column.
4. `ef_search=200` được set trong pool init.
5. Retain request với `tags=["tag1"]` → tags được lưu vào DB.
6. `FlatQueryAnalyzer.analyze()` không còn dead code.
