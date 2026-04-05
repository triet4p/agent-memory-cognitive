# S19.6 Manual Tutorial - scripts/smoke-test-cogmem.sh

## Purpose
- Smoke test retain/recall cho CogMem API trên môi trường shell (Linux/macOS/WSL).
- Cung cấp kiểm tra nhanh sau khi container/API đã chạy.

## Source File
- scripts/smoke-test-cogmem.sh

## Symbol-by-symbol explanation
### BASE_URL, BANK_ID
- BASE_URL lấy từ đối số đầu hoặc mặc định localhost:8888.
- BANK_ID dùng PID để giảm va chạm.

### Retain request
- Gọi curl POST /memories với item mẫu.
- Parse success bằng python3; nếu không phải True thì fail.

### Recall request
- Gọi curl POST /memories/recall với query mẫu.
- Parse số lượng kết quả; nếu 0 thì fail.

### Màu output RED/GREEN/NC
- In trạng thái PASS/FAIL dễ quan sát trên terminal.

### Symbol inventory bổ sung (full names)
- RETAIN_RESPONSE, SUCCESS, RECALL_RESPONSE, RESULTS_COUNT

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- docker/test-image.sh gọi script này sau khi health check pass.
- Người vận hành có thể gọi trực tiếp để smoke local API.

### Outbound dependencies
- curl, python3, CogMem API endpoints /memories và /memories/recall.

## Runtime implications/side effects
- Tạo dữ liệu ghi nhớ mới trong bank smoke.
- Dừng ngay khi lỗi nhờ set -euo pipefail.

## Failure modes
- Thiếu curl hoặc python3 trên máy chạy.
- API trả JSON khác contract expected.
- Base URL sai hoặc API chưa sẵn sàng.

## Verify commands
```powershell
bash -n scripts/smoke-test-cogmem.sh
bash scripts/smoke-test-cogmem.sh http://localhost:8888
```

