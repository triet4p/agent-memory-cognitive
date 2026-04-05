# S19.2 Manual Tutorial - cogmem_api/api/__init__.py

## Purpose (Mục đích)
- Cung cấp API factory thống nhất cho runtime CogMem.
- Cho phép bật/tắt HTTP API theo cờ cấu hình.
- Trả về FastAPI app tối thiểu khi HTTP API bị tắt.

## Source File
- cogmem_api/api/__init__.py

## Symbol-by-symbol explanation
### FastAPI
- Symbol import từ fastapi.
- Dùng để tạo app fallback khi http_api_enabled = False.

### MemoryEngine
- Symbol import từ cogmem_api package root.
- Được khai báo trong type hint để ép contract cho create_app.

### create_http_app
- Alias import từ cogmem_api.api.http.create_app.
- Là implementation đầy đủ của HTTP runtime app.

### create_app(memory, http_api_enabled=True, initialize_memory=True)
- Hàm factory chính của module.
- Nhánh http_api_enabled = True: trả về create_http_app(memory, initialize_memory).
- Nhánh http_api_enabled = False: trả về FastAPI(title="CogMem API") không có routes runtime.

### __all__
- Giá trị: ["create_app"].
- Giới hạn public export của module ở API factory.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- cogmem_api/server.py gọi create_app để dựng app ASGI dùng cho runtime.

### Outbound dependencies
- cogmem_api.api.http.create_app: app factory đầy đủ có lifespan và routes.
- fastapi.FastAPI: app fallback tối thiểu khi tắt HTTP layer.

## Runtime implications/side effects
- Khi trả app fallback (http_api_enabled=False), hệ thống không có route retain/recall/health như runtime chuẩn.
- Cờ initialize_memory chỉ có hiệu lực khi đi qua create_http_app.

## Failure modes
- ImportError nếu fastapi không có trong môi trường.
- Sai object truyền vào memory có thể gây lỗi ở app factory của module http.

## Verify commands
```powershell
uv run python -c "from cogmem_api.api import create_app; print(callable(create_app))"
uv run python -c "from cogmem_api.api import create_app; import inspect; print(inspect.signature(create_app))"
```
