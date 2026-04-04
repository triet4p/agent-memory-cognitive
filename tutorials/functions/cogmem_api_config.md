# Function Deep Dive - cogmem_api/config.py

## Purpose
- Mô tả chi tiết các hàm trong module và contract input/output ở mức function-level.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 8 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/config.py`.
- Public/private breakdown: public=1, private=7.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _read_optional_str | private | _read_optional_str(env_name: str, default: str \| None=None) -> str \| None | cogmem_api/config.py:104 | documented |
| (module) | _read_int | private | _read_int(env_name: str, default: int, minimum: int \| None=None) -> int | cogmem_api/config.py:114 | documented |
| (module) | _read_float | private | _read_float(env_name: str, default: float, minimum: float \| None=None) -> float | cogmem_api/config.py:128 | documented |
| (module) | _read_bool | private | _read_bool(env_name: str, default: bool) -> bool | cogmem_api/config.py:142 | documented |
| (module) | _read_retain_extraction_mode | private | _read_retain_extraction_mode() -> str | cogmem_api/config.py:154 | documented |
| (module) | _read_graph_retriever | private | _read_graph_retriever() -> str | cogmem_api/config.py:163 | documented |
| (module) | _get_raw_config | private | _get_raw_config() -> CogMemRuntimeConfig | cogmem_api/config.py:236 | documented |
| (module) | get_config | public | get_config() -> CogMemConfig | cogmem_api/config.py:271 | documented |

### Function: (module)._read_optional_str
- Signature: `_read_optional_str(env_name: str, default: str | None=None) -> str | None`
- Visibility: `private`
- Location: `cogmem_api/config.py:104`
- Purpose:
  - Thực thi nghiệp vụ `_read_optional_str` trong phạm vi `(module)` của module `cogmem_api/config.py`.
- Inputs:
  - Theo chữ ký: `_read_optional_str(env_name: str, default: str | None=None) -> str | None`.
- Outputs:
  - Trả về kiểu: `str | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `getenv`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/config.py -Pattern "def _read_optional_str|async def _read_optional_str"`

### Function: (module)._read_int
- Signature: `_read_int(env_name: str, default: int, minimum: int | None=None) -> int`
- Visibility: `private`
- Location: `cogmem_api/config.py:114`
- Purpose:
  - Thực thi nghiệp vụ `_read_int` trong phạm vi `(module)` của module `cogmem_api/config.py`.
- Inputs:
  - Theo chữ ký: `_read_int(env_name: str, default: int, minimum: int | None=None) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `getenv`, `max`, `int`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/config.py -Pattern "def _read_int|async def _read_int"`

### Function: (module)._read_float
- Signature: `_read_float(env_name: str, default: float, minimum: float | None=None) -> float`
- Visibility: `private`
- Location: `cogmem_api/config.py:128`
- Purpose:
  - Thực thi nghiệp vụ `_read_float` trong phạm vi `(module)` của module `cogmem_api/config.py`.
- Inputs:
  - Theo chữ ký: `_read_float(env_name: str, default: float, minimum: float | None=None) -> float`.
- Outputs:
  - Trả về kiểu: `float`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `getenv`, `max`, `float`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/config.py -Pattern "def _read_float|async def _read_float"`

### Function: (module)._read_bool
- Signature: `_read_bool(env_name: str, default: bool) -> bool`
- Visibility: `private`
- Location: `cogmem_api/config.py:142`
- Purpose:
  - Thực thi nghiệp vụ `_read_bool` trong phạm vi `(module)` của module `cogmem_api/config.py`.
- Inputs:
  - Theo chữ ký: `_read_bool(env_name: str, default: bool) -> bool`.
- Outputs:
  - Trả về kiểu: `bool`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `getenv`, `lower`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/config.py -Pattern "def _read_bool|async def _read_bool"`

### Function: (module)._read_retain_extraction_mode
- Signature: `_read_retain_extraction_mode() -> str`
- Visibility: `private`
- Location: `cogmem_api/config.py:154`
- Purpose:
  - Thực thi nghiệp vụ `_read_retain_extraction_mode` trong phạm vi `(module)` của module `cogmem_api/config.py`.
- Inputs:
  - Theo chữ ký: `_read_retain_extraction_mode() -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_read_optional_str`, `lower`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/config.py -Pattern "def _read_retain_extraction_mode|async def _read_retain_extraction_mode"`

### Function: (module)._read_graph_retriever
- Signature: `_read_graph_retriever() -> str`
- Visibility: `private`
- Location: `cogmem_api/config.py:163`
- Purpose:
  - Thực thi nghiệp vụ `_read_graph_retriever` trong phạm vi `(module)` của module `cogmem_api/config.py`.
- Inputs:
  - Theo chữ ký: `_read_graph_retriever() -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_read_optional_str`, `lower`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/config.py -Pattern "def _read_graph_retriever|async def _read_graph_retriever"`

### Function: (module)._get_raw_config
- Signature: `_get_raw_config() -> CogMemRuntimeConfig`
- Visibility: `private`
- Location: `cogmem_api/config.py:236`
- Purpose:
  - Thực thi nghiệp vụ `_get_raw_config` trong phạm vi `(module)` của module `cogmem_api/config.py`.
- Inputs:
  - Theo chữ ký: `_get_raw_config() -> CogMemRuntimeConfig`.
- Outputs:
  - Trả về kiểu: `CogMemRuntimeConfig`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `CogMemRuntimeConfig`, `getenv`, `_read_int`, `_read_optional_str`, `_read_float`, `_read_bool`, `_read_retain_extraction_mode`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/config.py -Pattern "def _get_raw_config|async def _get_raw_config"`

### Function: (module).get_config
- Signature: `get_config() -> CogMemConfig`
- Visibility: `public`
- Location: `cogmem_api/config.py:271`
- Purpose:
  - Thực thi nghiệp vụ `get_config` trong phạm vi `(module)` của module `cogmem_api/config.py`.
- Inputs:
  - Theo chữ ký: `get_config() -> CogMemConfig`.
- Outputs:
  - Trả về kiểu: `CogMemConfig`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_get_raw_config`, `CogMemConfig`, `_read_graph_retriever`, `getenv`, `_read_int`, `_read_optional_str`, `_read_float`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/config.py -Pattern "def get_config|async def get_config"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_config.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_config.md -Pattern "- Verify command:"`

