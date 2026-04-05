# S19.6 Manual Tutorial - [docker/test-image.sh](https://github.com/triet4p/agent-memory-cognitive/blob/master/docker/test-image.sh)

## Purpose
- Smoke test end-to-end cho Docker image CogMem trên shell.
- Kiểm tra chuỗi: start container -> health pass -> retain/recall smoke -> validate embeddings mode.

## Source File
- [docker/test-image.sh](https://github.com/triet4p/agent-memory-cognitive/blob/master/docker/test-image.sh)

## Symbol-by-symbol explanation
### Input/config variables
- Nhận IMAGE bắt buộc và nhiều ENV tùy biến: timeout, container name, health URL, smoke URLs, DB mode, LLM/embedding/reranker settings.

### cleanup + trap
- Đảm bảo container test luôn được stop/rm khi kết thúc hoặc lỗi.

### DOCKER_RUN_ARGS
- Build danh sách tham số docker run theo env đã cấu hình.
- Hỗ trợ pass-through nhiều biến runtime cho retain/search stack.

### Optional env injections
- Chỉ thêm LLM base URL / embeddings openai / reranker tei URL khi có giá trị.

### pg0 volume handling
- Nếu smoke DB dùng pg0 thì tự tạo volume dir và mount vào container.

### Health wait loop
- Poll health endpoint từng giây đến timeout.
- Nếu container thoát sớm, in logs và fail ngay.

### Smoke + deterministic guard
- Gọi [scripts/smoke-test-cogmem.sh](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/smoke-test-cogmem.sh) để test retain/recall.
- Nếu yêu cầu non-deterministic embeddings và provider=local, fail khi phát hiện log fallback deterministic.

### Symbol inventory bổ sung (full names)
- SCRIPT_DIR, REPO_ROOT, RED, GREEN, YELLOW, NC, TIMEOUT, CONTAINER_NAME, HEALTH_URL, SMOKE_BASE_URL, SMOKE_DATABASE_URL, SMOKE_PG0_VOLUME_DIR, SMOKE_REQUIRE_NON_DETERMINISTIC, LLM_PROVIDER, LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT, RETAIN_LLM_TIMEOUT, REFLECT_LLM_TIMEOUT, RETAIN_MAX_COMPLETION_TOKENS, RETAIN_EXTRACTION_MODE, EMBEDDINGS_PROVIDER, EMBEDDINGS_LOCAL_MODEL, EMBEDDINGS_OPENAI_MODEL, EMBEDDINGS_OPENAI_BASE_URL, EMBEDDINGS_OPENAI_API_KEY, RERANKER_PROVIDER, RERANKER_LOCAL_MODEL, RERANKER_TEI_URL, RERANKER_TEI_BATCH_SIZE, RERANKER_MAX_CANDIDATES, start_time, end_time, duration

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Người vận hành gọi trực tiếp script để test image sau build.

### Outbound dependencies
- [scripts/smoke-test-cogmem.sh](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/smoke-test-cogmem.sh)
- Docker CLI, curl
- CogMem API endpoint /health

## Runtime implications/side effects
- Tạo/rm container smoke test.
- Có thể ghi dữ liệu pg0 vào volume smoke dir.
- In log container 50 dòng cuối để phục vụ điều tra.

## Failure modes
- IMAGE không được truyền => exit 2.
- Health timeout hoặc container crash sớm.
- Smoke retain/recall fail.
- Runtime rơi vào deterministic embeddings khi local embeddings được yêu cầu.

## Verify commands
```powershell
bash -n docker/test-image.sh
bash docker/test-image.sh cogmem:local
```

