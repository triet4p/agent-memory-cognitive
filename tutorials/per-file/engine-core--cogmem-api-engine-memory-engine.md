# S19.3 Manual Tutorial - [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py)

## Purpose (Mục đích)
- Cung cấp lớp runtime trung tâm để quản lý DB pool, retain, recall và health check.
- Đảm bảo thao tác SQL luôn an toàn theo schema qualification.
- Điều phối embedded PostgreSQL (pg0), embeddings provider và các luồng search/rerank.

## Source File
- [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py)

## Symbol-by-symbol explanation
### _current_schema
- ContextVar lưu schema hiện hành theo ngữ cảnh thực thi async/task.

### _PROTECTED_TABLES
- Danh sách bảng bắt buộc phải truy cập dưới dạng schema.table.

### _VALIDATE_SQL_SCHEMAS
- Cờ bật/tắt guard kiểm tra SQL unqualified.

### UnqualifiedTableError
- Exception phát sinh khi phát hiện SQL truy cập bảng bảo vệ mà thiếu prefix schema.

### get_current_schema()
- Trả schema từ context; fallback về config.DATABASE_SCHEMA.

### set_schema_context(schema)
- Context manager đổi schema tạm thời trong phạm vi khối lệnh.

### fq_table(table_name)
- Tạo chuỗi tên bảng đầy đủ: <schema>.<table_name>.

### validate_sql_schema(sql)
- Parse SQL text bằng regex để phát hiện FROM/JOIN/INTO/UPDATE/DELETE trên bảng bảo vệ.
- Ném UnqualifiedTableError nếu tên bảng không có dấu chấm schema.

### MemoryEngine.__init__
- Khởi tạo cấu hình runtime:
  - parse db_url và nhận biết chế độ pg0.
  - cấu hình pool min/max.
  - nạp runtime_config + engine_config.
  - chuẩn bị các state nội bộ (_pool, _embeddings_model, _cross_encoder, ...).

### MemoryEngine.initialized, pool
- Property phản ánh trạng thái khởi tạo và pool hiện có.

### MemoryEngine.initialize()
- Đường khởi tạo chính:
  - set schema context.
  - nếu dùng pg0 thì ensure_running để lấy db_url.
  - khởi tạo embeddings model (có fallback deterministic).
  - tạo asyncpg pool nếu có db_url.
  - bootstrap schema/tables.

### MemoryEngine._bootstrap_schema_objects()
- Dùng SQLAlchemy async engine để:
  - tạo schema nếu chưa có,
  - thử tạo extension vector,
  - set search_path,
  - create_all từ Base.metadata.

### MemoryEngine._initialize_embeddings_model()
- Tạo embeddings provider theo ENV.
- Nếu lỗi, fallback sang DeterministicEmbeddings để hệ thống vẫn chạy.

### MemoryEngine.close()
- Đóng pool (nếu có), dừng pg0 (nếu engine tự khởi động), reset trạng thái initialized.

### MemoryEngine.execute(sql, *args)
- Validate SQL schema trước khi execute.
- Dùng acquire_with_retry để lấy connection và chạy câu lệnh.

### MemoryEngine.health_check()
- Trả payload health cho endpoint /health.
- Báo mode embedded_pg0/no_database_url và trạng thái kết nối DB.

### MemoryEngine._format_date(dt)
- Chuẩn hóa datetime về UTC định dạng YYYY-MM-DD cho retain pipeline.

### MemoryEngine._build_retain_llm_config()
- Tạo LLMConfig cho retain nếu llm_base_url có cấu hình.
- Nếu không có base_url thì trả None để retain chạy non-LLM path tương ứng.

### MemoryEngine.retain_batch_async(...)
- Guard initialized/pool.
- Import retain_batch động tại runtime.
- Truyền đầy đủ dependency (pool, embeddings, llm_config, entity_resolver, config, schema).
- Hỗ trợ return usage tùy chọn.

### MemoryEngine.retain_async(...)
- Wrapper cho một item retain đơn lẻ dựa trên retain_batch_async.

### MemoryEngine._fallback_recall_from_conn(...)
- Recall fallback khi pipeline chính lỗi:
  - đọc rows từ DB (hoặc conn.recall_memory_units nếu có).
  - chấm lexical score theo giao query terms.
  - cắt theo max_tokens và limit.

### MemoryEngine.recall_async(...)
- Recall chính:
  - validate trạng thái engine.
  - lọc effective fact types theo COGMEM_FACT_TYPES.
  - sinh query embedding.
  - chạy retrieve_all_fact_types_parallel + fuse RRF.
  - rerank bằng CrossEncoderReranker + combined scoring.
  - build trace khi enable_trace.
- Nếu bất kỳ lỗi nào trong đường chính: fallback sang lexical_db_scan.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- [cogmem_api/server.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/server.py) giữ instance MemoryEngine ở cấp module.
- [cogmem_api/api/http.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/api/http.py) gọi retain_batch_async/recall_async/health_check.

### Outbound dependencies
- [cogmem_api/config.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/config.py): ENV/runtime config.
- [cogmem_api/models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/models.py): Base.metadata cho bootstrap schema.
- [cogmem_api/pg0.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/pg0.py): embedded PostgreSQL lifecycle.
- [cogmem_api/engine/db_utils.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/db_utils.py): acquire_with_retry.
- [cogmem_api/engine/embeddings.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/embeddings.py): provider + fallback.
- [cogmem_api/engine/retain/orchestrator.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/orchestrator.py) và engine/search/*: retain/recall pipeline.

## Runtime implications/side effects
- initialize() có side effect lớn: có thể khởi động pg0, tạo schema, tạo extension và tạo bảng.
- recall_async bắt broad exception để fallback lexical scan, nên lỗi pipeline chính có thể bị che nếu không bật trace/log.
- validate_sql_schema tăng an toàn schema isolation nhưng có thể chặn SQL tùy biến nếu không qualify đúng.

## Failure modes
- DB URL sai hoặc DB không sẵn sàng: create_pool thất bại.
- pgvector extension không tạo được: cảnh báo, có thể ảnh hưởng semantic search.
- embeddings provider lỗi: fallback deterministic làm chất lượng retrieval giảm.
- Cross-encoder/parallel retrieval lỗi: recall chuyển sang fallback lexical scan.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.memory_engine import fq_table, get_current_schema; print(get_current_schema(), fq_table('memory_units'))"
uv run python -c "from cogmem_api.engine.memory_engine import validate_sql_schema; validate_sql_schema('SELECT * FROM public.memory_units'); print('ok')"
uv run python -c "from cogmem_api.engine.memory_engine import MemoryEngine; m=MemoryEngine(db_url=None); print(m.initialized, m.pool is None)"
```
