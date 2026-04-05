# S19.6 Manual Tutorial - [docker/standalone/start-all.sh](https://github.com/triet4p/agent-memory-cognitive/blob/master/docker/standalone/start-all.sh)

## Purpose
- Entry script trong container standalone để khởi chạy CogMem API và chờ readiness.
- Hỗ trợ tùy chọn chờ dependency DB trước khi start API.

## Source File
- [docker/standalone/start-all.sh](https://github.com/triet4p/agent-memory-cognitive/blob/master/docker/standalone/start-all.sh)

## Symbol-by-symbol explanation
### API_COMMAND, API_HEALTH_URL, API_STARTUP_WAIT_SECONDS
- Cấu hình lệnh chạy API, URL health check và timeout chờ khởi động.

### COGMEM_WAIT_FOR_DEPS block
- Khi bật, script parse COGMEM_API_DATABASE_URL và chờ TCP PostgreSQL sẵn sàng bằng đoạn Python inline.
- Timeout chờ dependency điều khiển bởi COGMEM_DEP_WAIT_SECONDS.

### ${API_COMMAND} & + API_PID
- Khởi chạy API ở background để script có thể poll health song song.

### cleanup + trap
- Bắt INT/TERM để dừng API process sạch sẽ.

### Health wait loop
- Poll health endpoint từng giây đến khi pass hoặc hết timeout.
- Nếu process API chết sớm thì thoát theo exit code của API.

### Final wait
- Khi API healthy, script giữ foreground bằng wait API_PID để container sống theo vòng đời API.

### Symbol inventory bổ sung (full names)
- api_ready

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Dockerfile standalone dùng script này làm entrypoint/cmd để khởi chạy app.

### Outbound dependencies
- Binary/command cogmem-api (hoặc command từ COGMEM_API_COMMAND).
- curl để health check.
- Python runtime để chờ dependency DB (nếu bật).

## Runtime implications/side effects
- Có thể trì hoãn startup đáng kể nếu dependency DB chưa sẵn sàng.
- Khi nhận signal dừng, script chủ động tắt API process để tránh zombie.

## Failure modes
- API command không tồn tại hoặc crash khi startup.
- Health endpoint không lên trước timeout.
- Cấu hình DB URL sai khi bật wait_for_deps.

## Verify commands
```powershell
bash -n docker/standalone/start-all.sh
uv run python -c "from pathlib import Path; print(Path('docker/standalone/start-all.sh').exists())"
```

