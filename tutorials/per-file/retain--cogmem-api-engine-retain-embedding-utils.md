# S19.4 Manual Tutorial - cogmem_api/engine/retain/embedding_utils.py

## Purpose (Mục đích)
- Cung cấp helper sinh embeddings cho retain pipeline.
- Hỗ trợ deterministic fallback khi không có model encoder khả dụng.

## Source File
- cogmem_api/engine/retain/embedding_utils.py

## Symbol-by-symbol explanation
### _deterministic_embedding(text, dimension)
- Sinh vector ổn định bằng hash token (SHA-256) và chuẩn hóa L2.

### generate_embeddings_batch(embeddings_model, texts, dimension)
- Nếu embeddings_model có encode thì dùng trực tiếp và ép float.
- Nếu không có model phù hợp thì fallback deterministic cho từng text.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- embedding_processing.py gọi generate_embeddings_batch.
- memory_engine fallback lexical/retain paths gián tiếp phụ thuộc hàm này qua orchestrator.

### Outbound dependencies
- cogmem_api/config.py (EMBEDDING_DIMENSION).
- hashlib/math và typing Sequence.

## Runtime implications/side effects
- Fallback deterministic giúp pipeline không dừng khi model embeddings unavailable.
- Chất lượng semantic retrieval từ fallback thấp hơn model embeddings thật.

## Failure modes
- embeddings_model.encode trả dữ liệu không phải sequence sẽ rơi về fallback logic theo nhánh kiểm tra.
- dimension <= 0 làm deterministic vector rỗng.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.retain.embedding_utils import generate_embeddings_batch; import asyncio; print(asyncio.run(generate_embeddings_batch(None,['hello'],dimension=8))[0])"
uv run python -c "from cogmem_api.engine.retain.embedding_utils import _deterministic_embedding; print(len(_deterministic_embedding('hello', 16)))"
```
