# Function Deep Dive - [cogmem_api/engine/response_models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/response_models.py)

## Purpose
- Mô tả chi tiết các hàm trong module và contract input/output ở mức function-level.
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
- Source module: `cogmem_api/engine/response_models.py`.
- Public/private breakdown: public=0, private=2.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| DispositionTraits | __post_init__ | private | __post_init__(self) -> None | [cogmem_api/engine/response_models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/response_models.py):17 | documented |
| TokenUsage | __add__ | private | __add__(self, other: 'TokenUsage') -> 'TokenUsage' | [cogmem_api/engine/response_models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/response_models.py):45 | documented |

### Function: DispositionTraits.__post_init__
- Signature: `__post_init__(self) -> None`
- Visibility: `private`
- Location: `cogmem_api/engine/response_models.py:17`
- Purpose:
  - Thực thi nghiệp vụ `__post_init__` trong phạm vi `DispositionTraits` của module `cogmem_api/engine/response_models.py`.
- Inputs:
  - Theo chữ ký: `__post_init__(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `getattr`, `isinstance`, `TypeError`, `ValueError`
- Failure modes:
  - Có thể raise: `TypeError`, `ValueError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/response_models.py -Pattern "def __post_init__|async def __post_init__"`

### Function: TokenUsage.__add__
- Signature: `__add__(self, other: 'TokenUsage') -> 'TokenUsage'`
- Visibility: `private`
- Location: `cogmem_api/engine/response_models.py:45`
- Purpose:
  - Thực thi nghiệp vụ `__add__` trong phạm vi `TokenUsage` của module `cogmem_api/engine/response_models.py`.
- Inputs:
  - Theo chữ ký: `__add__(self, other: 'TokenUsage') -> 'TokenUsage'`.
- Outputs:
  - Trả về kiểu: `'TokenUsage'`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `TokenUsage`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/response_models.py -Pattern "def __add__|async def __add__"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_response_models.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_response_models.md -Pattern "- Verify command:"`

