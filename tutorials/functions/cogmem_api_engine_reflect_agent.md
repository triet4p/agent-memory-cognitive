# Function Deep Dive - [cogmem_api/engine/reflect/agent.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/agent.py)

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
- Source module: `cogmem_api/engine/reflect/agent.py`.
- Public/private breakdown: public=1, private=1.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _default_markdown_answer | private | _default_markdown_answer(question: str, evidence_lines: list[str]) -> str | [cogmem_api/engine/reflect/agent.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/agent.py):13 | documented |
| (module) | synthesize_lazy_reflect | public | synthesize_lazy_reflect(question: str, retrieved_items: list[Any], llm_generate: Callable[[str], str] \| None=None, bank_profile: dict[str, Any] \| None=None, max_evidence: int=8, include_prompt: bool=False) -> ReflectSynthesisResult | [cogmem_api/engine/reflect/agent.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/agent.py):30 | documented |

### Function: (module)._default_markdown_answer
- Signature: `_default_markdown_answer(question: str, evidence_lines: list[str]) -> str`
- Visibility: `private`
- Location: `cogmem_api/engine/reflect/agent.py:13`
- Purpose:
  - Thực thi nghiệp vụ `_default_markdown_answer` trong phạm vi `(module)` của module `cogmem_api/engine/reflect/agent.py`.
- Inputs:
  - Theo chữ ký: `_default_markdown_answer(question: str, evidence_lines: list[str]) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `join`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/agent.py -Pattern "def _default_markdown_answer|async def _default_markdown_answer"`

### Function: (module).synthesize_lazy_reflect
- Signature: `synthesize_lazy_reflect(question: str, retrieved_items: list[Any], llm_generate: Callable[[str], str] | None=None, bank_profile: dict[str, Any] | None=None, max_evidence: int=8, include_prompt: bool=False) -> ReflectSynthesisResult`
- Visibility: `public`
- Location: `cogmem_api/engine/reflect/agent.py:30`
- Purpose:
  - Thực thi nghiệp vụ `synthesize_lazy_reflect` trong phạm vi `(module)` của module `cogmem_api/engine/reflect/agent.py`.
- Inputs:
  - Theo chữ ký: `synthesize_lazy_reflect(question: str, retrieved_items: list[Any], llm_generate: Callable[[str], str] | None=None, bank_profile: dict[str, Any] | None=None, max_evidence: int=8, include_prompt: bool=False) -> ReflectSynthesisResult`.
- Outputs:
  - Trả về kiểu: `ReflectSynthesisResult`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `prepare_lazy_evidence`, `build_lazy_synthesis_prompt`, `ReflectSynthesisResult`, `append`, `llm_generate`, `_default_markdown_answer`, `strip`, `len`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/agent.py -Pattern "def synthesize_lazy_reflect|async def synthesize_lazy_reflect"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_reflect_agent.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_reflect_agent.md -Pattern "- Verify command:"`

