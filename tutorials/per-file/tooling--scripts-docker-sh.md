# S19.6 Manual Tutorial - scripts/docker.sh

## Purpose
- Wrapper shell để build/chạy CogMem Docker theo hai mode: embedded (pg0) hoặc external (compose/external URL).
- Chuẩn hóa truyền ENV runtime (LLM, schema, timeout, retain knobs) cho container.

## Source File
- scripts/docker.sh

## Symbol-by-symbol explanation
### Mode/config variables
- Đọc mode từ đối số đầu (`embedded` mặc định).
- Nạp toàn bộ ENV quan trọng: image, port, schema, pg0 volume, compose paths, LLM configs.

### DOCKER_ARGS
- Mảng tham số `docker run` dùng chung cho cả mode.
- Bao gồm mapping cổng và ENV runtime cốt lõi.

### if [ -n "${LLM_BASE_URL}" ]
- Chỉ thêm COGMEM_API_LLM_BASE_URL khi có cấu hình.

### case "${MODE}"
- embedded:
  - build image bằng docker/standalone/Dockerfile
  - mount volume pg0
  - chạy `docker run` trực tiếp.
- external:
  - nếu có COGMEM_EXTERNAL_DATABASE_URL: chạy container đơn với DB URL ngoài.
  - nếu không có: chạy `docker compose up --build` với compose file external-pg.
- default:
  - mode không hợp lệ => exit 2.

### Symbol inventory bổ sung (full names)
- IMAGE, PORT, LOG_LEVEL, SCHEMA, REPO_ROOT, COMPOSE_FILE, COMPOSE_ENV_FILE, DOCKER_INCLUDE_LOCAL_MODELS, DOCKER_PRELOAD_ML_MODELS, LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT, RETAIN_LLM_TIMEOUT, REFLECT_LLM_TIMEOUT, RETAIN_MAX_COMPLETION_TOKENS, RETAIN_EXTRACTION_MODE

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Người vận hành gọi trực tiếp script này để chạy môi trường local.
- docs/runbook có thể dùng script này làm command chuẩn.

### Outbound dependencies
- docker/standalone/Dockerfile.
- docker/docker-compose/external-pg/docker-compose.yaml.
- .env khi chạy compose external mode.
- Docker CLI và Docker Compose.

## Runtime implications/side effects
- Build image, khởi chạy container/stack, có thể pull image base mới.
- embedded mode ghi dữ liệu pg0 vào COGMEM_PG0_VOLUME_DIR.
- external compose mode có thể dựng thêm DB service tùy compose file.

## Failure modes
- Docker/compose chưa cài đặt hoặc daemon không chạy.
- .env thiếu trong external compose mode.
- Mode sai giá trị (không phải embedded/external).

## Verify commands
```powershell
bash -n scripts/docker.sh
uv run python -c "from pathlib import Path; print(Path('scripts/docker.sh').exists())"
```

