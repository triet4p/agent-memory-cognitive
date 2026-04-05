# Function Deep Dive - [cogmem_api/engine/reflect/prompts.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/prompts.py)

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
- Source module: `cogmem_api/engine/reflect/prompts.py`.
- Public/private breakdown: public=1, private=1.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _truncate | private | _truncate(text: str, limit: int) -> str | [cogmem_api/engine/reflect/prompts.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/prompts.py):16 | documented |
| (module) | build_lazy_synthesis_prompt | public | build_lazy_synthesis_prompt(question: str, evidences: list[ReflectEvidence], bank_profile: dict[str, Any] \| None=None, max_snippet_chars: int=280) -> str | [cogmem_api/engine/reflect/prompts.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/prompts.py):23 | documented |

### Function: (module)._truncate
- Signature: `_truncate(text: str, limit: int) -> str`
- Visibility: `private`
- Location: `cogmem_api/engine/reflect/prompts.py:16`
- Purpose:
  - Thực thi nghiệp vụ `_truncate` trong phạm vi `(module)` của module `cogmem_api/engine/reflect/prompts.py`.
- Inputs:
  - Theo chữ ký: `_truncate(text: str, limit: int) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `strip`, `len`, `rstrip`, `max`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/prompts.py -Pattern "def _truncate|async def _truncate"`

### Function: (module).build_lazy_synthesis_prompt
- Signature: `build_lazy_synthesis_prompt(question: str, evidences: list[ReflectEvidence], bank_profile: dict[str, Any] | None=None, max_snippet_chars: int=280) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/reflect/prompts.py:23`
- Purpose:
  - Thực thi nghiệp vụ `build_lazy_synthesis_prompt` trong phạm vi `(module)` của module `cogmem_api/engine/reflect/prompts.py`.
- Inputs:
  - Theo chữ ký: `build_lazy_synthesis_prompt(question: str, evidences: list[ReflectEvidence], bank_profile: dict[str, Any] | None=None, max_snippet_chars: int=280) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `str`, `extend`, `enumerate`, `join`, `append`, `get`, `strip`, `_truncate`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/prompts.py -Pattern "def build_lazy_synthesis_prompt|async def build_lazy_synthesis_prompt"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_reflect_prompts.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_reflect_prompts.md -Pattern "- Verify command:"`

