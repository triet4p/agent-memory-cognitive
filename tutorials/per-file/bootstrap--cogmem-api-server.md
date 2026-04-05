# S19.1 Manual Tutorial - cogmem_api/server.py

## Purpose (Mục đích)
- Tạo ASGI app object ở cấp module để uvicorn import và chạy trực tiếp.
- Khởi tạo MemoryEngine singleton từ cấu hình runtime.
- Gắn HTTP routes thông qua create_app.

## Source File
- cogmem_api/server.py

## Symbol-by-symbol explanation
### _config
- Giá trị: kết quả _get_raw_config().
- Vai trò: snapshot cấu hình tại thời điểm import module.

### _memory
- Giá trị: instance MemoryEngine.
- Vai trò: singleton memory backend dùng chung cho toàn app process.
- Đầu vào quan trọng: database_url, database_schema, db pool size.

### app
- Giá trị: ASGI application do create_app trả về.
- Vai trò: entrypoint runtime chuẩn cho uvicorn (cogmem_api.server:app).

### __main__ guard
- Khi chạy trực tiếp server.py, module sẽ gọi cogmem_api.main.main() thay vì tự chạy uvicorn tại chỗ.
- Mục tiêu: chỉ có một đường startup chuẩn, tránh lệch tham số giữa các entrypoint.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- cogmem_api.main gọi uvicorn.run trỏ tới cogmem_api.server:app.
- ASGI server bên ngoài import trực tiếp app từ module này.

### Outbound dependencies
- cogmem_api.MemoryEngine: lớp engine lấy từ package root.
- cogmem_api.api.create_app: factory tạo FastAPI/ASGI app.
- cogmem_api.config._get_raw_config: đọc runtime settings.

## Runtime implications/side effects
- Module này có side effect khi import: tạo _config, tạo _memory, tạo app ngay lập tức.
- Nếu DB không khả dụng hoặc cấu hình sai, import module có thể fail trước cả khi nhận request.
- Dùng singleton _memory giúp chia sẻ kết nối nhưng làm vòng đời phụ thuộc vào process hiện tại.

## Failure modes
- Lỗi khởi tạo MemoryEngine do DB URL/schema/pool không hợp lệ.
- Lỗi khi create_app nếu dependency HTTP layer bị thiếu.
- Chạy nhiều process worker sẽ tạo nhiều singleton _memory độc lập theo từng process.

## Verify commands
```powershell
uv run python -c "import cogmem_api.server as s; print(type(s.app).__name__)"
uv run python -c "import cogmem_api.server as s; print(type(s._memory).__name__)"
uv run python -c "from cogmem_api.server import _config; print(_config.database_url, _config.database_schema)"
```
