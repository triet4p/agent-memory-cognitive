# S19.2 Manual Tutorial - cogmem_api/api/http.py

## Purpose (Mục đích)
- Cài đặt FastAPI application factory cho runtime CogMem.
- Định nghĩa schema request/response cho health, version, retain, recall.
- Chuẩn hóa chuyển đổi payload HTTP thành contract gọi MemoryEngine.

## Source File
- cogmem_api/api/http.py

## Symbol-by-symbol explanation
### HealthResponse
- Pydantic model cho endpoint /health.
- Trường chính: status, initialized, database, reason.

### VersionResponse
- Pydantic model cho endpoint /version.
- Trả về version package và tên service.

### EntityInput
- Entity phụ đi kèm mỗi item trong retain.
- Trường type có thể None và được normalize về CONCEPT ở bước build payload.

### RetainItem
- Model cho từng phần tử trong RetainRequest.items.
- Hỗ trợ content, timestamp, context, metadata, document_id, entities, tags.

### RetainRequest
- Payload cho endpoint retain.
- Dùng alias async cho trường async_ thông qua ConfigDict + Field(alias="async").

### RetainResponse
- Kết quả endpoint retain.
- Trả success, bank_id, số item đã nhận, unit_ids trả về từ engine.

### RecallRequest
- Payload cho endpoint recall.
- Trường chính: query, types, budget, max_tokens, trace, query_timestamp.

### RecallResult
- Mỗi phần tử kết quả recall trả về cho client.
- Map từ item trong recall_result["results"] của engine.

### RecallResponse
- Payload tổng cho recall endpoint.
- Gồm danh sách results và trace tùy chọn.

### _parse_query_timestamp(value)
- Parse ISO datetime và hỗ trợ hậu tố Z bằng cách đổi sang +00:00.
- Ném HTTPException 400 nếu format không hợp lệ.

### _build_retain_payload(item)
- Chuyển RetainItem thành dict theo contract retain_batch_async.
- Loại item rỗng nếu content chỉ có khoảng trắng.
- Chuẩn hóa entities và tags (lọc phần tử rỗng).

### create_app(memory, initialize_memory=True)
- FastAPI factory cấp module.
- Khai báo lifespan:
  - startup: gắn app.state.memory và tùy chọn initialize engine.
  - shutdown: gọi memory.close().
- Đăng ký 4 route:
  - GET /health
  - GET /version
  - POST /v1/default/banks/{bank_id}/memories
  - POST /v1/default/banks/{bank_id}/memories/recall

### health_endpoint()
- Gọi memory.health_check().
- Trả HTTP 200 nếu healthy, ngược lại 503.

### version_endpoint()
- Trả version package từ cogmem_api.__version__ và service cố định cogmem-api.

### retain_memories(bank_id, payload)
- Build contents từ payload.items qua _build_retain_payload.
- Trả nhanh success với 0 item nếu nội dung rỗng.
- Chặn chế độ async retain bằng HTTP 400.
- Gọi memory.retain_batch_async và map RuntimeError sang HTTP 503.

### recall_memories(bank_id, payload)
- Parse query_timestamp sang datetime.
- Gọi memory.recall_async với budget/max_tokens/trace/fact_types/question_date.
- Chuyển đổi kết quả sang RecallResult, lọc item thiếu id hoặc text.
- Map RuntimeError sang HTTP 503.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- cogmem_api.api.__init__.py gọi create_app của module này khi bật HTTP API.
- cogmem_api.server.py dùng create_app để dựng app runtime.

### Outbound dependencies
- cogmem_api.MemoryEngine: backend xử lý health/retain/recall.
- cogmem_api.__version__: metadata cho endpoint version.
- fastapi, pydantic: framework HTTP + schema validation.

## Runtime implications/side effects
- Nếu initialize_memory=True, app startup sẽ chờ memory.initialize hoàn tất.
- app.state.memory là singleton theo process ASGI, chia sẻ bởi toàn bộ request trong process đó.
- Endpoint retain tự loại bỏ item content rỗng, giúp giảm dữ liệu rác vào pipeline.
- Endpoint recall có thể trả trace lớn khi bật payload.trace.

## Failure modes
- query_timestamp sai format gây HTTP 400 ngay từ parser helper.
- memory backend lỗi (DB, runtime service) sẽ trả HTTP 503 ở retain/recall.
- Dữ liệu retain có item rỗng toàn bộ có thể gây hiểu nhầm vì trả success nhưng items_count = 0.

## Verify commands
```powershell
uv run python -c "from cogmem_api.api.http import create_app; import inspect; print(inspect.signature(create_app))"
uv run python -c "from cogmem_api.api.http import _parse_query_timestamp; print(_parse_query_timestamp('2026-04-05T10:00:00Z'))"
uv run python -c "from cogmem_api.api.http import RetainRequest; x=RetainRequest.model_validate({'items':[{'content':'hello'}],'async':False}); print(x.async_, len(x.items))"
```
