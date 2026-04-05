# S19.3 Manual Tutorial - cogmem_api/engine/embeddings.py

## Purpose (Mục đích)
- Định nghĩa abstraction embeddings dùng chung cho retain/recall.
- Triển khai nhiều provider: local sentence-transformers, OpenAI-compatible, deterministic fallback.
- Chọn provider theo cấu hình môi trường qua get_config().

## Source File
- cogmem_api/engine/embeddings.py

## Symbol-by-symbol explanation
### Embeddings (ABC)
- Contract trừu tượng cho mọi embeddings provider.
- Bắt buộc có: provider_name, dimension, initialize(), encode().

### DeterministicEmbeddings
- Provider không phụ thuộc mô hình ngoài.
- _embed_one(text): băm token bằng SHA-256 vào vector fixed dimension rồi chuẩn hóa L2.
- Dùng cho fallback runtime khi provider chính không khả dụng.

### LocalSTEmbeddings
- Provider local dựa trên sentence-transformers.
- initialize(): import động SentenceTransformer và tải model.
- encode(): gọi model.encode và chuyển kết quả sang list[float].

### OpenAIEmbeddings
- Provider gọi API OpenAI-compatible.
- MODEL_DIMENSIONS: map dimension cho một số model phổ biến.
- initialize(): tạo OpenAI client; nếu model chưa biết dimension thì probe 1 request.
- encode(): gọi embeddings.create và sắp theo index để giữ đúng thứ tự đầu vào.

### create_embeddings_from_env()
- Đọc config embeddings_provider.
- Nhánh local/openai/deterministic tương ứng tạo provider.
- Với openai: bắt buộc có API key, nếu thiếu sẽ raise ValueError.
- Provider không hợp lệ sẽ raise ValueError kèm danh sách hỗ trợ.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- cogmem_api/engine/memory_engine.py gọi create_embeddings_from_env() và khởi tạo model.
- retain/search pipeline dùng embeddings model để sinh query/content vectors.

### Outbound dependencies
- cogmem_api/config.py: EMBEDDING_DIMENSION và get_config().
- sentence_transformers (tùy chọn), openai (tùy chọn), hashlib/math.

## Runtime implications/side effects
- Provider local có chi phí tải model lúc initialize.
- Provider openai phụ thuộc mạng và quota API.
- Fallback deterministic đảm bảo hệ thống không chết nhưng chất lượng semantic retrieval thấp hơn.

## Failure modes
- Thiếu thư viện tùy chọn (sentence-transformers/openai) gây ImportError.
- Provider openai thiếu API key gây ValueError.
- Model dimension mismatch có thể gây lỗi khi ghi/so khớp embedding với DB schema.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.embeddings import DeterministicEmbeddings; e=DeterministicEmbeddings(8); print(e.provider_name, e.dimension, len(e.encode(['hello'])[0]))"
uv run python -c "from cogmem_api.engine.embeddings import create_embeddings_from_env; import cogmem_api.config as c; print(c.get_config().embeddings_provider)"
```
