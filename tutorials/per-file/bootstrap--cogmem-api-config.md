# S19.1 Manual Tutorial - cogmem_api/config.py

## Purpose (Mục đích)
- Tập trung toàn bộ contract cấu hình runtime cho CogMem.
- Chuẩn hóa việc đọc biến môi trường, ép kiểu và fallback default.
- Cung cấp 2 lớp config: raw runtime config và engine config có cache.

## Source File
- cogmem_api/config.py

## Symbol-by-symbol explanation
### Nhóm ENV_* constants
- Vai trò: định danh đầy đủ tên biến môi trường COGMEM_API_*.
- Các nhóm chính:
  - Runtime cơ bản: database, host, port, log level, workers.
  - LLM/retain/reflect: provider, model, timeout, mission, instructions.
  - Retrieval/search: graph retriever, text extension, MPFP, BFS guards.
  - Embeddings/reranker: provider, model, endpoint, batch size, candidate limit.

### Nhóm DEFAULT_* constants
- Vai trò: fallback chuẩn khi ENV không có hoặc không hợp lệ.
- Đáng chú ý:
  - DEFAULT_DATABASE_URL = pg0 (hỗ trợ embedded flow).
  - DEFAULT_GRAPH_RETRIEVER = bfs.
  - DEFAULT_BFS_* và DEFAULT_MPFP_TOP_K_NEIGHBORS định nghĩa guard và độ rộng truy hồi.

### DATABASE_SCHEMA, DB_POOL_MIN_SIZE, DB_POOL_MAX_SIZE
- Vai trò: giá trị module-level đọc ENV tại import time.
- Lưu ý: đây là snapshot tức thời, khác với các trường lấy qua hàm _get_raw_config().

### ALLOWED_RETAIN_EXTRACTION_MODES, ALLOWED_GRAPH_RETRIEVERS
- Vai trò: whitelist để chống cấu hình sai mode/retriever.

### _read_optional_str(env_name, default)
- Đọc chuỗi tùy chọn từ ENV.
- Trim khoảng trắng; chuỗi rỗng trả về default.

### _read_int(env_name, default, minimum)
- Đọc số nguyên từ ENV với fallback khi parse lỗi.
- Có thể ép ngưỡng min để tránh giá trị âm/0 ngoài ý muốn.

### _read_float(env_name, default, minimum)
- Tương tự _read_int nhưng cho kiểu float.

### _read_bool(env_name, default)
- Parse bool từ tập giá trị yes/no chuẩn.
- Giá trị không nhận diện được sẽ fallback default.

### _read_retain_extraction_mode()
- Chuẩn hóa extraction mode về lowercase.
- Nếu ngoài whitelist thì trả về default an toàn.

### _read_graph_retriever()
- Chuẩn hóa graph retriever về lowercase.
- Nếu ngoài whitelist thì rơi về bfs.

### CogMemRuntimeConfig (dataclass, frozen)
- Mục đích: biểu diễn cấu hình runtime nguyên bản cho service entrypoint.
- Trường chính: DB, host/port, worker, LLM timeout, retain options, pool size.

### CogMemConfig (dataclass, frozen)
- Mục đích: config view cho các module engine/search.
- Bổ sung trường retrieval, reranker, embeddings và BFS guard.

### _cached_config
- Cache singleton kiểu CogMemConfig.
- Giúp giảm đọc/parsing ENV lặp lại ở tầng engine.

### _get_raw_config()
- Đọc toàn bộ runtime config từ ENV mỗi lần được gọi.
- Áp dụng helper parse và minimum guard.

### get_config()
- Trả về CogMemConfig dạng cached.
- Lần đầu sẽ xây từ _get_raw_config() + các trường bổ sung.

### Symbol inventory bổ sung (full names)
- ENV_DATABASE_URL, ENV_DATABASE_SCHEMA, ENV_HOST, ENV_PORT, ENV_LOG_LEVEL, ENV_WORKERS, ENV_LLM_PROVIDER, ENV_LLM_MODEL, ENV_LLM_API_KEY, ENV_LLM_BASE_URL, ENV_LLM_TIMEOUT, ENV_RETAIN_LLM_TIMEOUT, ENV_REFLECT_LLM_TIMEOUT, ENV_RETAIN_MAX_COMPLETION_TOKENS, ENV_RETAIN_CHUNK_SIZE, ENV_RETAIN_EXTRACT_CAUSAL_LINKS, ENV_RETAIN_EXTRACTION_MODE, ENV_RETAIN_MISSION, ENV_RETAIN_CUSTOM_INSTRUCTIONS, ENV_RECALL_MAX_CONCURRENT, ENV_DB_POOL_MIN_SIZE, ENV_DB_POOL_MAX_SIZE, ENV_GRAPH_RETRIEVER, ENV_TEXT_SEARCH_EXTENSION, ENV_MPFP_TOP_K_NEIGHBORS, ENV_BFS_REFRACTORY_STEPS, ENV_BFS_FIRING_QUOTA, ENV_BFS_ACTIVATION_SATURATION, ENV_EMBEDDINGS_PROVIDER, ENV_EMBEDDINGS_LOCAL_MODEL, ENV_EMBEDDINGS_OPENAI_MODEL, ENV_EMBEDDINGS_OPENAI_BASE_URL, ENV_EMBEDDINGS_OPENAI_API_KEY, ENV_RERANKER_PROVIDER, ENV_RERANKER_LOCAL_MODEL, ENV_RERANKER_TEI_URL, ENV_RERANKER_TEI_BATCH_SIZE, ENV_RERANKER_MAX_CANDIDATES, DEFAULT_EMBEDDING_DIMENSION, EMBEDDING_DIMENSION, DEFAULT_DATABASE_SCHEMA, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_LOG_LEVEL, DEFAULT_WORKERS, DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL, DEFAULT_LLM_BASE_URL, DEFAULT_LLM_TIMEOUT, DEFAULT_RETAIN_LLM_TIMEOUT, DEFAULT_REFLECT_LLM_TIMEOUT, DEFAULT_RETAIN_MAX_COMPLETION_TOKENS, DEFAULT_RETAIN_CHUNK_SIZE, DEFAULT_RETAIN_EXTRACT_CAUSAL_LINKS, DEFAULT_RETAIN_EXTRACTION_MODE, DEFAULT_RETAIN_MISSION, DEFAULT_RETAIN_CUSTOM_INSTRUCTIONS, DEFAULT_RECALL_MAX_CONCURRENT, DEFAULT_DB_POOL_MIN_SIZE, DEFAULT_DB_POOL_MAX_SIZE, DEFAULT_TEXT_SEARCH_EXTENSION, DEFAULT_RERANKER_PROVIDER, DEFAULT_RERANKER_LOCAL_MODEL, DEFAULT_RERANKER_TEI_BATCH_SIZE, DEFAULT_RERANKER_MAX_CANDIDATES, DEFAULT_BFS_REFRACTORY_STEPS, DEFAULT_BFS_FIRING_QUOTA, DEFAULT_BFS_ACTIVATION_SATURATION, DEFAULT_EMBEDDINGS_PROVIDER, DEFAULT_EMBEDDINGS_LOCAL_MODEL, DEFAULT_EMBEDDINGS_OPENAI_MODEL

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- cogmem_api.main.py dùng _get_raw_config() để set CLI defaults.
- cogmem_api.server.py dùng _get_raw_config() để dựng MemoryEngine.
- Các module engine/search dùng get_config() để lấy retrieval/LLM settings.

### Outbound dependencies
- os: đọc biến môi trường.
- dataclasses.dataclass: khai báo immutable config object.
- dotenv.find_dotenv, dotenv.load_dotenv (nếu có): nạp ENV từ file .env.

## Runtime implications/side effects
- Khi import module, có thể load .env ngay lập tức nếu python-dotenv đã cài.
- get_config() dùng cache nên thay đổi ENV sau lần gọi đầu không tự phản ánh, trừ khi reset cache.
- Các default value ảnh hưởng trực tiếp behavior runtime, đặc biệt retriever và timeouts.

## Failure modes
- Giá trị ENV sai kiểu số bị fallback về default, có thể che lỗi cấu hình nếu không có giám sát.
- Cấu hình ngoài whitelist tự động rơi về default, có thể làm người vận hành tưởng đã bật mode khác.
- Nếu phụ thuộc vào thay đổi ENV nóng trong process đang chạy, cache _cached_config gây sai kỳ vọng.

## Verify commands
```powershell
uv run python -c "from cogmem_api.config import _get_raw_config; print(_get_raw_config())"
uv run python -c "from cogmem_api.config import get_config; c=get_config(); print(c.graph_retriever, c.recall_max_concurrent)"
uv run python -c "import cogmem_api.config as cfg; print(cfg.DEFAULT_GRAPH_RETRIEVER, cfg.ALLOWED_GRAPH_RETRIEVERS)"
```

