# S19.4 Manual Tutorial - cogmem_api/engine/retain/fact_storage.py

## Purpose (Mục đích)
- Ghi ProcessedFact xuống DB theo schema an toàn.
- Bảo đảm bank tồn tại trước khi ghi memory units.
- Chuẩn hóa fact_type, raw_snippet và metadata trước khi persist.

## Source File
- cogmem_api/engine/retain/fact_storage.py

## Symbol-by-symbol explanation
### _DEFAULT_DISPOSITION
- Giá trị disposition mặc định khi tạo bank mới.

### _event_date_for_fact(fact)
- Chọn event_date theo ưu tiên occurred_start -> mentioned_at -> now UTC.

### _prepare_fact_for_storage(fact)
- Chuẩn hóa nội dung trước khi ghi:
  - fact_type,
  - raw_snippet,
  - metadata qua normalize_fact_metadata.

### ensure_bank_exists(conn, bank_id)
- Bảo đảm bank row tồn tại.
- Ưu tiên hook conn.ensure_bank_exists nếu có, nếu không dùng SQL insert with conflict do nothing.

### insert_facts_batch(conn, bank_id, facts, document_id)
- Hàm persist chính cho danh sách facts.
- Ưu tiên hook conn.insert_memory_units nếu có.
- Nếu không có hook: chạy INSERT từng fact vào memory_units với đầy đủ cột (text/raw_snippet/embedding/network_type/fact_type/confidence/metadata...).
- Trả về danh sách id đã tạo.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- orchestrator.py gọi ensure_bank_exists và insert_facts_batch trong transaction retain.

### Outbound dependencies
- memory_engine.fq_table để qualify tên bảng.
- types.py (ProcessedFact + helper normalize).

## Runtime implications/side effects
- Mọi fact được chuẩn hóa tại đây trước khi lưu, giảm drift dữ liệu giữa các extraction path.
- Với fact_type opinion, confidence_score được set để tương thích check constraint schema.

## Failure modes
- DB constraint violation khi dữ liệu ngoài miền hợp lệ (fact_type/network_type/metadata).
- Embedding dimension sai so với cột vector có thể gây lỗi insert.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.retain.fact_storage import _DEFAULT_DISPOSITION; print(_DEFAULT_DISPOSITION)"
uv run python -c "import inspect; from cogmem_api.engine.retain.fact_storage import insert_facts_batch; print(inspect.iscoroutinefunction(insert_facts_batch))"
```
