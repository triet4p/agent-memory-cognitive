# S19.3 Manual Tutorial - [cogmem_api/engine/db_utils.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/db_utils.py)

## Purpose (Mục đích)
- Cung cấp helper retry với exponential backoff cho thao tác DB.
- Chuẩn hóa acquire/release kết nối pool theo async context manager.

## Source File
- [cogmem_api/engine/db_utils.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/db_utils.py)

## Symbol-by-symbol explanation
### DEFAULT_MAX_RETRIES, DEFAULT_BASE_DELAY, DEFAULT_MAX_DELAY
- Bộ tham số mặc định cho cơ chế retry backoff.

### RETRYABLE_EXCEPTIONS
- Tập exception được phép retry: lỗi kết nối asyncpg, timeout, lỗi mạng cơ bản.

### retry_with_backoff(func, ...)
- Chạy async function với tối đa max_retries + 1 lần thử.
- Delay theo cấp số nhân: base_delay * 2^attempt, giới hạn bởi max_delay.
- Ghi warning cho lần retry và error ở lần thất bại cuối.

### acquire_with_retry(pool, max_retries)
- Async context manager để lấy connection từ pool qua retry_with_backoff.
- Bảo đảm release connection trong khối finally.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py) dùng acquire_with_retry cho execute/health/recall fallback.

### Outbound dependencies
- asyncpg.Pool cho acquire/release.
- asyncio.sleep cho delay backoff.
- logging để quan sát retry behavior.

## Runtime implications/side effects
- Retry giúp ổn định khi DB lỗi tạm thời nhưng tăng độ trễ tổng thể của request.
- Cơ chế release trong finally giảm nguy cơ leak connection.

## Failure modes
- Exception không nằm trong RETRYABLE_EXCEPTIONS sẽ không retry và được ném ra ngay.
- Pool bị hỏng kéo dài sẽ gây lỗi sau khi hết số lần retry.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.db_utils import DEFAULT_MAX_RETRIES, RETRYABLE_EXCEPTIONS; print(DEFAULT_MAX_RETRIES, len(RETRYABLE_EXCEPTIONS))"
uv run python -c "import inspect; from cogmem_api.engine.db_utils import acquire_with_retry; print(inspect.isasyncgenfunction(acquire_with_retry))"
```
