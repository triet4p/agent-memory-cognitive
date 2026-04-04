# S11 - Hindsight Delete-Only Report

## Mục tiêu
- Thực thi đúng phạm vi S11: chỉ xóa thư mục `hindsight_api/`.
- Không mở rộng sang dọn dependency/script legacy ngoài phạm vi sprint này.

## Snapshot trước xóa

### 1) Runtime import references (cogmem_api)
- Command: `Select-String -Pattern 'from hindsight_api|import hindsight_api'` trên `cogmem_api/**/*.py`
- Result: `NO_MATCH_IN_COGMEM_API`

### 2) Artifact/test references liên quan `hindsight_api`
- `tests/artifacts/test_task001_inventory.py:20` -> `repo_root / "hindsight_api" / "models.py"`
- `tests/artifacts/test_task001_inventory.py:21` -> `repo_root / "hindsight_api" / "engine" / "retain" / "orchestrator.py"`
- `tests/artifacts/test_task001_inventory.py:22` -> `repo_root / "hindsight_api" / "engine" / "search" / "retrieval.py"`
- `tests/artifacts/test_task001_inventory.py:30` -> `models_path = repo_root / "hindsight_api" / "models.py"`

Đánh giá snapshot:
- Phụ thuộc tồn tại thư mục tập trung ở artifact test `test_task001_inventory.py`.
- Không phát hiện import runtime `hindsight_api` trong `cogmem_api`.

## Thực thi S11
1. Xóa toàn bộ thư mục `hindsight_api/`.
2. Cập nhật `tests/artifacts/test_task001_inventory.py` để phù hợp baseline hậu xóa:
   - Bỏ các assertion yêu cầu file trong `hindsight_api` tồn tại.
   - Thêm assertion bắt buộc thư mục `hindsight_api` không còn tồn tại.
   - Giữ gate isolation: cấm import `hindsight_api` trong `cogmem_api`.

## Snapshot sau xóa

### 1) Runtime import references (cogmem_api)
- Command: `Select-String -Pattern 'from hindsight_api|import hindsight_api'` trên `cogmem_api/**/*.py`
- Result: `NO_MATCH_IN_COGMEM_API`

### 2) Trạng thái thư mục
- Command: kiểm tra `Test-Path hindsight_api`
- Result: `HINDSIGHT_API_DIRECTORY_NOT_FOUND`

## Verification
- `uv run python tests/artifacts/test_task701_idea_coverage_matrix.py` -> `PASS`
- `uv run python tests/artifacts/test_task702_hindsight_removal_gate.py` -> `PASS`
- `uv run python tests/artifacts/test_task703_removal_playbook_contract.py` -> `PASS`
- `uv run python tests/artifacts/test_task704_delete_hindsight_only.py` -> `PASS`

## Kết luận
- Đã hoàn tất sprint S11 theo delete-first scope.
- Không còn thư mục `hindsight_api`.
- Runtime `cogmem_api` vẫn giữ isolation (không import `hindsight_api`).
- Readiness regression pack (701/702/703) không bị regression sau khi xóa.
