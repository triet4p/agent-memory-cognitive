# S19.1 Manual Tutorial - [cogmem_api/pg0.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/pg0.py)

## Purpose (Mục đích)
- Cung cấp lớp adapter quản lý PostgreSQL nhúng (pg0-embedded) cho môi trường local/dev.
- Chuẩn hóa vòng đời start/stop/check/ensure của DB nhúng theo async interface.
- Parse DB URL dạng pg0 để tách instance name và port.

## Source File
- [cogmem_api/pg0.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/pg0.py)

## Symbol-by-symbol explanation
### logger
- Logger module-level để ghi trạng thái start/stop DB nhúng.

### DEFAULT_USERNAME, DEFAULT_PASSWORD, DEFAULT_DATABASE, DEFAULT_INSTANCE_NAME
- Bộ hằng số mặc định cho provisioning instance pg0.

### EmbeddedPostgres
- Lớp bọc pg0.Pg0 để đưa API đồng nhất kiểu async.

### EmbeddedPostgres.__init__
- Lưu cấu hình instance (port, username, password, database, name).
- Khởi tạo self._pg0 = None để lazy-init backend object.

### EmbeddedPostgres._get_pg0
- Lazy import pg0.Pg0.
- Tạo instance Pg0 khi cần lần đầu.
- Nếu thiếu package, raise ImportError với hướng dẫn cài extra embedded-db.

### EmbeddedPostgres.start(max_retries, retry_delay)
- Khởi động pg0 bằng run_in_executor để không block event loop.
- Có retry + exponential backoff khi lỗi startup.
- Trả về URI kết nối nếu thành công.

### EmbeddedPostgres.stop()
- Dừng instance pg0 qua executor.
- Nếu instance không chạy, nuốt lỗi not running để thao tác idempotent.

### EmbeddedPostgres.get_uri()
- Lấy URI hiện hành từ pg0.info.

### EmbeddedPostgres.is_running()
- Kiểm tra trạng thái running của instance.
- Bất kỳ exception nào thì trả về False theo hướng an toàn.

### EmbeddedPostgres.ensure_running()
- Nếu instance đã chạy thì trả URI hiện tại.
- Nếu chưa chạy thì gọi start() để tự khởi động.

### parse_pg0_url(db_url)
- Parse chuỗi DB URL thành tuple: (is_pg0, instance_name, port).
- Hỗ trợ 2 dạng:
  - pg0
  - pg0://<instance_name>[:port]

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Runtime/config layer có thể dùng parse_pg0_url để nhận biết mode embedded DB.
- Memory/bootstrap flow có thể gọi EmbeddedPostgres để quản lý vòng đời DB local.

### Outbound dependencies
- pg0.Pg0: engine PostgreSQL nhúng.
- asyncio: chuyển thao tác blocking sang executor.
- logging: ghi sự kiện runtime.

## Runtime implications/side effects
- Lần gọi _get_pg0 đầu tiên mới tạo instance thật, giúp giảm overhead import ban đầu.
- Start có retry nên thời gian khởi động có thể kéo dài khi lỗi hạ tầng cục bộ.
- Credentials mặc định phù hợp local/dev, không nên giữ nguyên cho môi trường production.

## Failure modes
- Thiếu package pg0-embedded gây ImportError.
- Port conflict hoặc dữ liệu instance hỏng làm start thất bại sau tối đa số lần retry.
- parse_pg0_url ném ValueError nếu port sau dấu : không parse được sang int.

## Verify commands
```powershell
uv run python -c "from cogmem_api.pg0 import parse_pg0_url; print(parse_pg0_url('pg0')); print(parse_pg0_url('pg0://demo:5544'))"
uv run python -c "from cogmem_api.pg0 import EmbeddedPostgres; e=EmbeddedPostgres(); print(e.name, e.database)"
uv run python -c "from cogmem_api.pg0 import parse_pg0_url; print(parse_pg0_url('postgresql://x'))"
```
