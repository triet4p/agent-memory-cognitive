# S19.4 Manual Tutorial - cogmem_api/engine/retain/chunk_storage.py

## Purpose (Mục đích)
- Hỗ trợ lưu chunk metadata cho retain pipeline.
- Trả mapping chunk_index -> chunk_id để nối lại với facts.

## Source File
- cogmem_api/engine/retain/chunk_storage.py

## Symbol-by-symbol explanation
### store_chunks_batch(conn, bank_id, document_id, chunks)
- Nếu conn có hook insert_chunks thì dùng hook để persist thật.
- Nếu không có hook, trả deterministic chunk IDs theo pattern bank_document_index.
- Trả dict ánh xạ chunk_index sang chunk_id.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- orchestrator.py gọi store_chunks_batch khi có chunks và document_id.

### Outbound dependencies
- retain/types.py (ChunkMetadata).

## Runtime implications/side effects
- Nhánh fallback no-op DB vẫn cho deterministic IDs để pipeline downstream hoạt động ổn định.

## Failure modes
- Nếu hook insert_chunks lỗi, transaction retain có thể rollback toàn bộ.
- Nếu chunks rỗng, trả dict rỗng và không tạo chunk mapping.

## Verify commands
```powershell
uv run python -c "import inspect; from cogmem_api.engine.retain.chunk_storage import store_chunks_batch; print(inspect.iscoroutinefunction(store_chunks_batch))"
```
