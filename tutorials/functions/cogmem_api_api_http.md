# Function Deep Dive - [cogmem_api/api/http.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/api/http.py)

## Purpose
- Mô tả chi tiết các hàm API layer và payload normalization.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 3 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/api/http.py`.
- Public/private breakdown: public=1, private=2.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _parse_query_timestamp | private | _parse_query_timestamp(value: str \| None) -> datetime \| None | [cogmem_api/api/http.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/api/http.py):97 | documented |
| (module) | _build_retain_payload | private | _build_retain_payload(item: RetainItem) -> dict[str, Any] \| None | [cogmem_api/api/http.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/api/http.py):106 | documented |
| (module) | create_app | public | create_app(memory: MemoryEngine, initialize_memory: bool=True) -> FastAPI | [cogmem_api/api/http.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/api/http.py):131 | documented |

### Function: (module)._parse_query_timestamp
- Signature: `_parse_query_timestamp(value: str | None) -> datetime | None`
- Visibility: `private`
- Location: `cogmem_api/api/http.py:97`
- Purpose:
  - Thực thi nghiệp vụ `_parse_query_timestamp` trong phạm vi `(module)` của module `cogmem_api/api/http.py`.
- Inputs:
  - Theo chữ ký: `_parse_query_timestamp(value: str | None) -> datetime | None`.
- Outputs:
  - Trả về kiểu: `datetime | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `fromisoformat`, `replace`, `HTTPException`
- Failure modes:
  - Có thể raise: `HTTPException`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/api/http.py -Pattern "def _parse_query_timestamp|async def _parse_query_timestamp"`

### Function: (module)._build_retain_payload
- Signature: `_build_retain_payload(item: RetainItem) -> dict[str, Any] | None`
- Visibility: `private`
- Location: `cogmem_api/api/http.py:106`
- Purpose:
  - Thực thi nghiệp vụ `_build_retain_payload` trong phạm vi `(module)` của module `cogmem_api/api/http.py`.
- Inputs:
  - Theo chữ ký: `_build_retain_payload(item: RetainItem) -> dict[str, Any] | None`.
- Outputs:
  - Trả về kiểu: `dict[str, Any] | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/api/http.py -Pattern "def _build_retain_payload|async def _build_retain_payload"`

### Function: (module).create_app
- Signature: `create_app(memory: MemoryEngine, initialize_memory: bool=True) -> FastAPI`
- Visibility: `public`
- Location: `cogmem_api/api/http.py:131`
- Purpose:
  - Thực thi nghiệp vụ `create_app` trong phạm vi `(module)` của module `cogmem_api/api/http.py`.
- Inputs:
  - Theo chữ ký: `create_app(memory: MemoryEngine, initialize_memory: bool=True) -> FastAPI`.
- Outputs:
  - Trả về kiểu: `FastAPI`.
- Side effects:
  - Có khả năng tạo side effect qua call `post`.
- Dependency calls:
  - `FastAPI`, `get`, `post`, `JSONResponse`, `VersionResponse`, `_parse_query_timestamp`, `RecallResponse`, `health_check`, `RetainResponse`, `HTTPException`, `RecallResult`, `initialize`
- Failure modes:
  - Có thể raise: `HTTPException`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/api/http.py -Pattern "def create_app|async def create_app"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_api_http.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_api_http.md -Pattern "- Verify command:"`

