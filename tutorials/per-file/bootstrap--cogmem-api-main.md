# S19.1 Manual Tutorial - cogmem_api/main.py

## Purpose (Mục đích)
- Cung cấp entrypoint CLI để chạy CogMem API bằng uvicorn.
- Map tham số dòng lệnh với cấu hình runtime từ biến môi trường.
- Chuẩn hóa cách khởi chạy app theo module cogmem_api.server:app.

## Source File
- cogmem_api/main.py

## Symbol-by-symbol explanation
### DEFAULT_HOST
- Giá trị mặc định host cho runtime CLI.
- Hiện tại chỉ đóng vai trò hằng số tham chiếu nội bộ file.

### DEFAULT_PORT
- Giá trị mặc định cổng dịch vụ.
- Dùng để tài liệu hóa behavior mặc định của entrypoint.

### DEFAULT_LOG_LEVEL
- Mức log mặc định khi không có cấu hình khác.

### DEFAULT_WORKERS
- Số worker mặc định khi chạy non-reload mode.

### build_parser()
- Tạo argparse parser cho lệnh cogmem-api.
- Đọc raw config bằng _get_raw_config() để set default value theo môi trường hiện tại.
- Khai báo các cờ: host, port, log-level, reload, workers, access-log, proxy-headers, forwarded-allow-ips.

### main()
- Parse args từ CLI.
- Chốt workers về 1 nếu bật reload để tránh conflict chế độ auto-reload.
- Gọi uvicorn.run với target cogmem_api.server:app và toàn bộ cờ runtime.

### __main__ guard
- Khi chạy python -m cogmem_api.main thì hàm main() được gọi trực tiếp.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Người vận hành chạy trực tiếp module main như CLI entrypoint.
- cogmem_api/server.py có nhánh __main__ gọi lại main() để đồng nhất cách startup.

### Outbound dependencies
- cogmem_api.config._get_raw_config: cung cấp default runtime config.
- cogmem_api.server:app: ASGI app object được uvicorn nạp.
- uvicorn: web server thực thi vòng đời ASGI.

## Runtime implications/side effects
- Chế độ reload buộc workers = 1, nên năng lực xử lý song song sẽ thấp hơn production mode.
- Sai tham số forwarded/proxy có thể làm lệch IP thật của client trong môi trường reverse proxy.
- Mọi tham số CLI sẽ override giá trị default lấy từ ENV.

## Failure modes
- ImportError nếu uvicorn chưa cài trong môi trường chạy.
- Lỗi bind host/port khi cổng đã bị chiếm dụng.
- Giá trị log-level ngoài tập cho phép bị argparse chặn ngay ở bước parse.

## Verify commands
```powershell
uv run python -m cogmem_api.main --help
uv run python -c "from cogmem_api.main import build_parser; print(build_parser().prog)"
uv run python -c "from cogmem_api.main import build_parser; print(build_parser().parse_args(['--host','127.0.0.1','--port','8888']))"
```
