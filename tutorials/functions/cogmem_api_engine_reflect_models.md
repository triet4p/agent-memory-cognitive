# Function Deep Dive - cogmem_api/engine/reflect/models.py

## Purpose
- Mô tả chi tiết các hàm lazy synthesis và chuẩn hóa evidence cho bước phản hồi.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 2 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/reflect/models.py`.
- Public/private breakdown: public=0, private=2.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| ReflectEvidence | _validate_text | private | _validate_text(cls, value: str) -> str | cogmem_api/engine/reflect/models.py:26 | documented |
| ReflectEvidence | _normalize_raw_snippet | private | _normalize_raw_snippet(cls, value: str \| None) -> str \| None | cogmem_api/engine/reflect/models.py:34 | documented |

### Function: ReflectEvidence._validate_text
- Signature: `_validate_text(cls, value: str) -> str`
- Visibility: `private`
- Location: `cogmem_api/engine/reflect/models.py:26`
- Purpose:
  - Thực thi nghiệp vụ `_validate_text` trong phạm vi `ReflectEvidence` của module `cogmem_api/engine/reflect/models.py`.
- Inputs:
  - Theo chữ ký: `_validate_text(cls, value: str) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `field_validator`, `strip`, `ValueError`
- Failure modes:
  - Có thể raise: `ValueError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/models.py -Pattern "def _validate_text|async def _validate_text"`

### Function: ReflectEvidence._normalize_raw_snippet
- Signature: `_normalize_raw_snippet(cls, value: str | None) -> str | None`
- Visibility: `private`
- Location: `cogmem_api/engine/reflect/models.py:34`
- Purpose:
  - Thực thi nghiệp vụ `_normalize_raw_snippet` trong phạm vi `ReflectEvidence` của module `cogmem_api/engine/reflect/models.py`.
- Inputs:
  - Theo chữ ký: `_normalize_raw_snippet(cls, value: str | None) -> str | None`.
- Outputs:
  - Trả về kiểu: `str | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `field_validator`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/models.py -Pattern "def _normalize_raw_snippet|async def _normalize_raw_snippet"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_reflect_models.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_reflect_models.md -Pattern "- Verify command:"`

