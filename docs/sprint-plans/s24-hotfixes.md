# Sprint S24-hotfix: Pipeline Bug Fixes Before Dry Run

**Trạng thái:** ✅ Done (tasks 756-757)

---

## S24-hotfix — Bug Fixes (task 756) ✅

Bug đã fix (2026-04-26):

1. **7.1 FK violation** (`cogmem_api/engine/retain/fact_storage.py`): `insert_facts_batch` thiếu upsert `documents` record trước khi INSERT `memory_units` → `asyncpg.ForeignKeyViolationError` với mọi LongMemEval retain. Fix: executemany upsert `(doc_id, bank_id)` vào `documents` trước vòng lặp INSERT.

2. **7.2 Judge bool coercion** (`scripts/eval_cogmem.py`): `bool("false") == True` — minimax-m2.7 đôi khi trả về `"false"` dạng string. Fix: guard `isinstance(str)` trước `bool()`.

3. **7.3 Keyword recall = 0.0** (`scripts/eval_cogmem.py`): LongMemEval không có `expected_keywords` → `_keyword_recall_metrics` trả về `0.0` gây misleading. Fix: trả về `None` khi không có keywords; tất cả 4 aggregation points dùng list-based accumulation.

4. **URL conflict** (`scripts/eval_cogmem.py`): `resolve_api_base_url` fallback đọc nhầm `COGMEM_API_EVAL_LLM_BASE_URL` (minimax) → CogMem API request bị gửi đến minimax. Fix: đổi fallback sang `COGMEM_API_BASE_URL`; thêm `COGMEM_API_BASE_URL=http://localhost:8888` vào `.env`.

5. **Bank ID double-suffix** (`scripts/eval_cogmem.py`): script luôn append `_c{idx:03d}` kể cả khi `--bank-id` đã đủ → `e567_c000_c000`. Fix: chỉ append khi `--bank-id` không được truyền.

6. **API timeout** (`scripts/eval_cogmem.py`): default `--api-timeout 120s` quá thấp cho retain ~160 chunks (~800s). Fix: tăng default lên 3600s.

7. **Per-turn chunking** (`scripts/eval_cogmem.py`): `retain_fixture` gửi từng turn riêng lẻ → mỗi turn ~100 chars → LLM không có cross-turn context → `{"facts": []}`. Fix: concatenate toàn bộ turns trong session thành 1 content item; thêm `COGMEM_API_RETAIN_CHUNK_SIZE=3000` vào `.env`.

Artifacts: `logs/task_756_summary.md`, `tests/artifacts/test_task756_fixes.py` (9/9 passed).

---

## S24-hotfix task 757 — Session Recall + CE Fallback ✅

Phát hiện sau dry run E7 conv-0:

1. **8.1 TypeError line 1087** (`scripts/eval_cogmem.py`): `recall_keyword_accuracy=None` formatted với `:.3f` → crash. Fix: `kw_str = "null" if kw is None else f"{kw:.3f}"`.

2. **8.2 Missing `dateparser` dependency (PRIMARY)**: Root cause: `dateparser` không có trong `pyproject.toml` → `DateparserQueryAnalyzer.load()` raise `ModuleNotFoundError` → outer try-except bắt silently → lexical fallback không có `document_id` → `session_recall@k = 0.0`. Fix: `uv add dateparser`.

3. **8.3 Cross-encoder silent fallback** (`cogmem_api/engine/memory_engine.py`): Phòng thủ thêm: inner try-except quanh CE block; nếu CE fail → dùng trực tiếp RRF-ordered candidates (có `document_id`).

4. **8.4 Fallback includes document_id** (`cogmem_api/engine/memory_engine.py`): `_fallback_recall_from_conn` SELECT thiếu `document_id`. Fix: thêm `document_id` vào SELECT và result dict.

5. **8.5 Warning log on fallback** (`cogmem_api/engine/memory_engine.py`): Thêm `logger.warning` khi main path và CE fail để dễ debug.

6. **8.6 Remove non-existent columns chunk_id/tags from SQL SELECTs**: `memory_units` không có cột `chunk_id` hay `tags` → `column "chunk_id" does not exist` → fallback. Fix: remove khỏi SELECT trong `retrieval.py` (4 nơi), `graph_retrieval.py` (2 nơi), `link_expansion_retrieval.py` (5 nơi), `mpfp_retrieval.py` (1 nơi).

7. **8.7 search_vector column không tồn tại** (`cogmem_api/engine/search/retrieval.py`): Native BM25 path dùng `ts_rank_cd(search_vector, ...)` — column không có trong schema. Fix tạm: thay bằng `to_tsvector('english', text)` inline. Fix vĩnh viễn: tạo stored generated column trong migration S24 (task 758).

Artifacts: `logs/task_757_summary.md`, `tests/artifacts/test_task757_recall_fixes.py` (8/8 passed).
