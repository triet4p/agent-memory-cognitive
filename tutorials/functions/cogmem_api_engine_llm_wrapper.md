# Function Deep Dive - [cogmem_api/engine/llm_wrapper.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/llm_wrapper.py)

## Purpose
- Mô tả chi tiết các hàm trong module và contract input/output ở mức function-level.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 4 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/llm_wrapper.py`.
- Public/private breakdown: public=3, private=1.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | sanitize_llm_output | public | sanitize_llm_output(text: str \| None) -> str \| None | [cogmem_api/engine/llm_wrapper.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/llm_wrapper.py):15 | documented |
| (module) | parse_llm_json | public | parse_llm_json(raw: str) -> Any | [cogmem_api/engine/llm_wrapper.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/llm_wrapper.py):29 | documented |
| LLMConfig | call | public | async call(self, messages: list[dict[str, str]], response_format: type \| None=None, scope: str \| None=None, temperature: float=0.1, max_completion_tokens: int \| None=None, return_usage: bool=False, skip_validation: bool=False, **_: Any) -> Any | [cogmem_api/engine/llm_wrapper.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/llm_wrapper.py):56 | documented |
| LLMConfig | _post_chat_completions | private | async _post_chat_completions(self, payload: dict[str, Any]) -> dict[str, Any] | [cogmem_api/engine/llm_wrapper.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/llm_wrapper.py):120 | documented |

### Function: (module).sanitize_llm_output
- Signature: `sanitize_llm_output(text: str | None) -> str | None`
- Visibility: `public`
- Location: `cogmem_api/engine/llm_wrapper.py:15`
- Purpose:
  - Thực thi nghiệp vụ `sanitize_llm_output` trong phạm vi `(module)` của module `cogmem_api/engine/llm_wrapper.py`.
- Inputs:
  - Theo chữ ký: `sanitize_llm_output(text: str | None) -> str | None`.
- Outputs:
  - Trả về kiểu: `str | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `sub`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/llm_wrapper.py -Pattern "def sanitize_llm_output|async def sanitize_llm_output"`

### Function: (module).parse_llm_json
- Signature: `parse_llm_json(raw: str) -> Any`
- Visibility: `public`
- Location: `cogmem_api/engine/llm_wrapper.py:29`
- Purpose:
  - Thực thi nghiệp vụ `parse_llm_json` trong phạm vi `(module)` của module `cogmem_api/engine/llm_wrapper.py`.
- Inputs:
  - Theo chữ ký: `parse_llm_json(raw: str) -> Any`.
- Outputs:
  - Trả về kiểu: `Any`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `strip`, `startswith`, `endswith`, `loads`, `sub`, `split`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/llm_wrapper.py -Pattern "def parse_llm_json|async def parse_llm_json"`

### Function: LLMConfig.call
- Signature: `async call(self, messages: list[dict[str, str]], response_format: type | None=None, scope: str | None=None, temperature: float=0.1, max_completion_tokens: int | None=None, return_usage: bool=False, skip_validation: bool=False, **_: Any) -> Any`
- Visibility: `public`
- Location: `cogmem_api/engine/llm_wrapper.py:56`
- Purpose:
  - Thực thi nghiệp vụ `call` trong phạm vi `LLMConfig` của module `cogmem_api/engine/llm_wrapper.py`.
- Inputs:
  - Theo chữ ký: `async call(self, messages: list[dict[str, str]], response_format: type | None=None, scope: str | None=None, temperature: float=0.1, max_completion_tokens: int | None=None, return_usage: bool=False, skip_validation: bool=False, **_: Any) -> Any`.
- Outputs:
  - Trả về kiểu: `Any`.
- Side effects:
  - Có khả năng tạo side effect qua call `_post_chat_completions`.
- Dependency calls:
  - `TokenUsage`, `hasattr`, `_post_chat_completions`, `get`, `str`, `int`, `OutputTooLongError`, `sanitize_llm_output`, `parse_llm_json`, `model_json_schema`, `model_dump`, `model_validate`
- Failure modes:
  - Có thể raise: `OutputTooLongError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/llm_wrapper.py -Pattern "def call|async def call"`

### Function: LLMConfig._post_chat_completions
- Signature: `async _post_chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]`
- Visibility: `private`
- Location: `cogmem_api/engine/llm_wrapper.py:120`
- Purpose:
  - Thực thi nghiệp vụ `_post_chat_completions` trong phạm vi `LLMConfig` của module `cogmem_api/engine/llm_wrapper.py`.
- Inputs:
  - Theo chữ ký: `async _post_chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]`.
- Outputs:
  - Trả về kiểu: `dict[str, Any]`.
- Side effects:
  - Có khả năng tạo side effect qua call `post`.
- Dependency calls:
  - `rstrip`, `endswith`, `ValueError`, `AsyncClient`, `raise_for_status`, `json`, `post`
- Failure modes:
  - Có thể raise: `ValueError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/llm_wrapper.py -Pattern "def _post_chat_completions|async def _post_chat_completions"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_llm_wrapper.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_llm_wrapper.md -Pattern "- Verify command:"`

