# S19.6 Manual Tutorial - docker/test-image.sh

## Purpose
- Smoke test end-to-end cho Docker image CogMem trên shell.
- Kiểm tra chuỗi: start container -> health pass -> retain/recall smoke -> validate embeddings mode.

## Source File
- docker/test-image.sh

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
- Gọi scripts/smoke-test-cogmem.sh để test retain/recall.
- Nếu yêu cầu non-deterministic embeddings và provider=local, fail khi phát hiện log fallback deterministic.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Người vận hành gọi trực tiếp script để test image sau build.

### Outbound dependencies
- scripts/smoke-test-cogmem.sh
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
