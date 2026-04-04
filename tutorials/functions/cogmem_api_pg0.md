# Function Deep Dive - cogmem_api/pg0.py

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
- Source module: `cogmem_api/pg0.py`.
- Public/private breakdown: public=6, private=2.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | parse_pg0_url | public | parse_pg0_url(db_url: str) -> tuple[bool, str \| None, int \| None] | cogmem_api/pg0.py:115 | documented |
| EmbeddedPostgres | __init__ | private | __init__(self, port: int \| None=None, username: str=DEFAULT_USERNAME, password: str=DEFAULT_PASSWORD, database: str=DEFAULT_DATABASE, name: str=DEFAULT_INSTANCE_NAME, **kwargs) | cogmem_api/pg0.py:21 | documented |
| EmbeddedPostgres | _get_pg0 | private | _get_pg0(self) -> Pg0 | cogmem_api/pg0.py:37 | documented |
| EmbeddedPostgres | start | public | async start(self, max_retries: int=5, retry_delay: float=4.0) -> str | cogmem_api/pg0.py:57 | documented |
| EmbeddedPostgres | stop | public | async stop(self) -> None | cogmem_api/pg0.py:80 | documented |
| EmbeddedPostgres | get_uri | public | async get_uri(self) -> str | cogmem_api/pg0.py:91 | documented |
| EmbeddedPostgres | is_running | public | async is_running(self) -> bool | cogmem_api/pg0.py:98 | documented |
| EmbeddedPostgres | ensure_running | public | async ensure_running(self) -> str | cogmem_api/pg0.py:108 | documented |

### Function: (module).parse_pg0_url
- Signature: `parse_pg0_url(db_url: str) -> tuple[bool, str | None, int | None]`
- Visibility: `public`
- Location: `cogmem_api/pg0.py:115`
- Purpose:
  - Thực thi nghiệp vụ `parse_pg0_url` trong phạm vi `(module)` của module `cogmem_api/pg0.py`.
- Inputs:
  - Theo chữ ký: `parse_pg0_url(db_url: str) -> tuple[bool, str | None, int | None]`.
- Outputs:
  - Trả về kiểu: `tuple[bool, str | None, int | None]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `startswith`, `rsplit`, `int`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/pg0.py -Pattern "def parse_pg0_url|async def parse_pg0_url"`

### Function: EmbeddedPostgres.__init__
- Signature: `__init__(self, port: int | None=None, username: str=DEFAULT_USERNAME, password: str=DEFAULT_PASSWORD, database: str=DEFAULT_DATABASE, name: str=DEFAULT_INSTANCE_NAME, **kwargs)`
- Visibility: `private`
- Location: `cogmem_api/pg0.py:21`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `EmbeddedPostgres` của module `cogmem_api/pg0.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, port: int | None=None, username: str=DEFAULT_USERNAME, password: str=DEFAULT_PASSWORD, database: str=DEFAULT_DATABASE, name: str=DEFAULT_INSTANCE_NAME, **kwargs)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - Không phát hiện lời gọi hàm trực tiếp.
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/pg0.py -Pattern "def __init__|async def __init__"`

### Function: EmbeddedPostgres._get_pg0
- Signature: `_get_pg0(self) -> Pg0`
- Visibility: `private`
- Location: `cogmem_api/pg0.py:37`
- Purpose:
  - Thực thi nghiệp vụ `_get_pg0` trong phạm vi `EmbeddedPostgres` của module `cogmem_api/pg0.py`.
- Inputs:
  - Theo chữ ký: `_get_pg0(self) -> Pg0`.
- Outputs:
  - Trả về kiểu: `Pg0`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `Pg0`, `ImportError`
- Failure modes:
  - Có thể raise: `ImportError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/pg0.py -Pattern "def _get_pg0|async def _get_pg0"`

### Function: EmbeddedPostgres.start
- Signature: `async start(self, max_retries: int=5, retry_delay: float=4.0) -> str`
- Visibility: `public`
- Location: `cogmem_api/pg0.py:57`
- Purpose:
  - Thực thi nghiệp vụ `start` trong phạm vi `EmbeddedPostgres` của module `cogmem_api/pg0.py`.
- Inputs:
  - Theo chữ ký: `async start(self, max_retries: int=5, retry_delay: float=4.0) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `info`, `_get_pg0`, `range`, `RuntimeError`, `get_event_loop`, `run_in_executor`, `str`, `sleep`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/pg0.py -Pattern "def start|async def start"`

### Function: EmbeddedPostgres.stop
- Signature: `async stop(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/pg0.py:80`
- Purpose:
  - Thực thi nghiệp vụ `stop` trong phạm vi `EmbeddedPostgres` của module `cogmem_api/pg0.py`.
- Inputs:
  - Theo chữ ký: `async stop(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_get_pg0`, `get_event_loop`, `run_in_executor`, `RuntimeError`, `lower`, `str`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/pg0.py -Pattern "def stop|async def stop"`

### Function: EmbeddedPostgres.get_uri
- Signature: `async get_uri(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/pg0.py:91`
- Purpose:
  - Thực thi nghiệp vụ `get_uri` trong phạm vi `EmbeddedPostgres` của module `cogmem_api/pg0.py`.
- Inputs:
  - Theo chữ ký: `async get_uri(self) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_get_pg0`, `get_event_loop`, `run_in_executor`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/pg0.py -Pattern "def get_uri|async def get_uri"`

### Function: EmbeddedPostgres.is_running
- Signature: `async is_running(self) -> bool`
- Visibility: `public`
- Location: `cogmem_api/pg0.py:98`
- Purpose:
  - Thực thi nghiệp vụ `is_running` trong phạm vi `EmbeddedPostgres` của module `cogmem_api/pg0.py`.
- Inputs:
  - Theo chữ ký: `async is_running(self) -> bool`.
- Outputs:
  - Trả về kiểu: `bool`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_get_pg0`, `get_event_loop`, `run_in_executor`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/pg0.py -Pattern "def is_running|async def is_running"`

### Function: EmbeddedPostgres.ensure_running
- Signature: `async ensure_running(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/pg0.py:108`
- Purpose:
  - Thực thi nghiệp vụ `ensure_running` trong phạm vi `EmbeddedPostgres` của module `cogmem_api/pg0.py`.
- Inputs:
  - Theo chữ ký: `async ensure_running(self) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `is_running`, `start`, `get_uri`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/pg0.py -Pattern "def ensure_running|async def ensure_running"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_pg0.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_pg0.md -Pattern "- Verify command:"`

