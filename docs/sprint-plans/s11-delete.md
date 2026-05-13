# Phase A — Sprint S11: Delete hindsight_api

**Trạng thái:** ✅ Done (task 704)

---

## Mục tiêu sprint
1. Xóa thư mục `hindsight_api` theo đúng phạm vi đã khóa (không dọn dependency/script legacy trong sprint này).
2. Giữ runtime CogMem chạy ổn định sau xóa.

## Phụ thuộc
1. T7.1, T7.2, T7.3 đã PASS.

## Inputs bắt buộc
1. `docs/hindsight_removal_playbook.md`
2. `reports/hindsight_removal_readiness.md`
3. Kết quả test readiness hiện hành (T7.1/T7.2/T7.3)

## Atomic tasks
1. S11.1 Snapshot trước xóa:
	- Ghi nhận các test/artifact còn phụ thuộc vào sự tồn tại thư mục `hindsight_api`.
	- Lưu danh sách ảnh hưởng vào báo cáo sprint.
2. S11.2 Xóa thư mục:
	- Xóa toàn bộ `hindsight_api/`.
	- Không sửa `hindsight-client` trong `pyproject.toml` ở sprint này.
3. S11.3 Ổn định hậu xóa:
	- Sửa các artifact test vỡ vì kiểm tra file tồn tại trong `hindsight_api`.
	- Đảm bảo test không bị "false fail" do thay đổi phạm vi.

## File tác động dự kiến
1. `hindsight_api/**` (xóa)
2. `tests/artifacts/test_task001_inventory.py` (khả năng cao cần cập nhật)
3. `reports/hindsight_delete_only_report.md`
4. `tests/artifacts/test_task704_delete_hindsight_only.py`

## Outputs bắt buộc
1. `reports/hindsight_delete_only_report.md`
2. `logs/task_704_summary.md`
3. `tests/artifacts/test_task704_delete_hindsight_only.py`
4. Danh sách import reference trước/sau xóa trong báo cáo sprint

## Verification
1. `rg -n "from hindsight_api|import hindsight_api" cogmem_api`
2. `Get-ChildItem -Recurse hindsight_api` (kỳ vọng không còn thư mục)
3. `uv run python tests/artifacts/test_task701_idea_coverage_matrix.py`
4. `uv run python tests/artifacts/test_task702_hindsight_removal_gate.py`
5. `uv run python tests/artifacts/test_task703_removal_playbook_contract.py`
6. `uv run python tests/artifacts/test_task704_delete_hindsight_only.py`

## Exit gate
1. Không còn thư mục `hindsight_api`.
2. Runtime `cogmem_api` không import `hindsight_api`.
3. Readiness regression pack PASS.

## Rủi ro và fallback
1. Rủi ro: test lịch sử phụ thuộc file cũ.
2. Fallback: cập nhật test theo contract mới, không làm giảm ý nghĩa kiểm thử isolation.
3. Rủi ro: script/dev-tooling ngoài `cogmem_api` còn gọi package cũ.
4. Fallback: ghi nhận vào backlog kỹ thuật riêng, không mở rộng phạm vi sửa trong sprint xóa-first.
