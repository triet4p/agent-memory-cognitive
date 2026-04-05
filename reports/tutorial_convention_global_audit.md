# Tutorial Convention Global Audit Report

## Mục tiêu
- Kiểm tra convention toàn cục của artifacts và tutorial.
- Xác nhận mọi file/symbol (biến, hàm, class ở mức module/script) trong scope Phase D đều được giải thích trong tutorials.

## Scope
- Code scope: `cogmem_api/**`, `scripts/**`, `docker/**` với extension `.py/.sh/.ps1`.
- Tutorial scope: `tutorials/per-file/**` (canonical), `tutorials/functions/**` (deep-dive function-level).
- Artifact convention scope: `logs/task_*.md`, `tests/artifacts/test_task*.py`.

## Nội dung audit
1. File coverage
- Đối chiếu 1-1 `tutorials/per-file/file-manifest.md` với workspace scope thực tế.
- Yêu cầu trạng thái cuối: `done` cho toàn bộ rows.

2. Symbol coverage
- Python: kiểm tra biến cấp module (hằng số và alias chuẩn), hàm và class/method có xuất hiện trong tutorial tương ứng.
- Shell/PowerShell: kiểm tra biến và hàm/class khai báo trong script có xuất hiện trong per-file tutorial.

3. Artifact convention
- Kiểm tra naming contract `task_XXX_summary.md` và `test_taskXXX_*.py`.
- Kiểm tra section bắt buộc trong logs: `## Scope`, `## Outputs Created`, `## Verification Strategy Applied`.
- Kiểm tra pairing giữa log ID và test ID.

## Kết quả xử lý gap trong phiên audit
1. Bổ sung symbol inventory cho các tutorial còn thiếu coverage symbol.
2. Vá convention logs lịch sử:
- `logs/task_711_summary.md`: thêm `## Outputs Created`.
- `logs/task_712_summary.md`: thêm `## Outputs Created`.
- `logs/task_713_summary.md`: thêm `## Outputs Created` và `## Verification Strategy Applied`.

## Gate dùng để kiểm chứng
1. `tests/artifacts/test_task730_tutorial_convention_global_audit.py`
2. `tests/artifacts/test_task002_artifact_conventions.py`
3. `tests/artifacts/test_task729_manual_full_gate.py`

## Kết luận
- Sau khi vá các điểm thiếu, hệ thống đạt trạng thái sẵn sàng để pass audit convention toàn cục và đảm bảo coverage tutorial cho file/symbol theo scope đã khóa.
