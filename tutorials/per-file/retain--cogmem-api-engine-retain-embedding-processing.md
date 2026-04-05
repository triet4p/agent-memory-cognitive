# S19.4 Manual Tutorial - cogmem_api/engine/retain/embedding_processing.py

## Purpose (Mục đích)
- Điều phối tiền xử lý text trước khi sinh embedding.
- Bổ sung tín hiệu thời gian và entity vào chuỗi đầu vào embedding.
- Ủy quyền sinh embedding batch cho embedding_utils.

## Source File
- cogmem_api/engine/retain/embedding_processing.py

## Symbol-by-symbol explanation
### augment_texts_with_dates(facts, format_date_fn)
- Tạo chuỗi augmented cho từng fact:
  - thêm time anchor nếu có occurred_start/mentioned_at,
  - thêm danh sách entities nếu có.

### generate_embeddings_batch(embeddings_model, texts)
- Wrapper gọi embedding_utils.generate_embeddings_batch.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- orchestrator.py gọi augment_texts_with_dates và generate_embeddings_batch trước khi tạo ProcessedFact.

### Outbound dependencies
- retain/embedding_utils.py.
- retain/types.py (ExtractedFact).

## Runtime implications/side effects
- Việc thêm thông tin thời gian/entities vào text embedding giúp tăng khả năng truy hồi theo temporal/entity context.

## Failure modes
- format_date_fn không đúng contract có thể gây lỗi khi augment.
- embeddings_model trả shape bất thường sẽ lỗi ở bước downstream.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.retain.embedding_processing import augment_texts_with_dates; print(callable(augment_texts_with_dates))"
uv run python -c "import inspect; from cogmem_api.engine.retain.embedding_processing import generate_embeddings_batch; print(inspect.iscoroutinefunction(generate_embeddings_batch))"
```
