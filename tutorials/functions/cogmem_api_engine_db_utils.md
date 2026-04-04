# Function Deep Dive - cogmem_api/engine/db_utils.py

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
- Source module: `cogmem_api/engine/db_utils.py`.
- Public/private breakdown: public=2, private=0.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | retry_with_backoff | public | async retry_with_backoff(func, max_retries: int=DEFAULT_MAX_RETRIES, base_delay: float=DEFAULT_BASE_DELAY, max_delay: float=DEFAULT_MAX_DELAY, retryable_exceptions: tuple[type[BaseException], ...]=RETRYABLE_EXCEPTIONS) | cogmem_api/engine/db_utils.py:28 | documented |
| (module) | acquire_with_retry | public | async acquire_with_retry(pool: asyncpg.Pool, max_retries: int=DEFAULT_MAX_RETRIES) | cogmem_api/engine/db_utils.py:62 | documented |

### Function: (module).retry_with_backoff
- Signature: `async retry_with_backoff(func, max_retries: int=DEFAULT_MAX_RETRIES, base_delay: float=DEFAULT_BASE_DELAY, max_delay: float=DEFAULT_MAX_DELAY, retryable_exceptions: tuple[type[BaseException], ...]=RETRYABLE_EXCEPTIONS)`
- Visibility: `public`
- Location: `cogmem_api/engine/db_utils.py:28`
- Purpose:
  - Thực thi nghiệp vụ `retry_with_backoff` trong phạm vi `(module)` của module `cogmem_api/engine/db_utils.py`.
- Inputs:
  - Theo chữ ký: `async retry_with_backoff(func, max_retries: int=DEFAULT_MAX_RETRIES, base_delay: float=DEFAULT_BASE_DELAY, max_delay: float=DEFAULT_MAX_DELAY, retryable_exceptions: tuple[type[BaseException], ...]=RETRYABLE_EXCEPTIONS)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `range`, `RuntimeError`, `func`, `min`, `warning`, `error`, `sleep`
- Failure modes:
  - Có thể raise: `RuntimeError`, `last_exception`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/db_utils.py -Pattern "def retry_with_backoff|async def retry_with_backoff"`

### Function: (module).acquire_with_retry
- Signature: `async acquire_with_retry(pool: asyncpg.Pool, max_retries: int=DEFAULT_MAX_RETRIES)`
- Visibility: `public`
- Location: `cogmem_api/engine/db_utils.py:62`
- Purpose:
  - Thực thi nghiệp vụ `acquire_with_retry` trong phạm vi `(module)` của module `cogmem_api/engine/db_utils.py`.
- Inputs:
  - Theo chữ ký: `async acquire_with_retry(pool: asyncpg.Pool, max_retries: int=DEFAULT_MAX_RETRIES)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire`.
- Dependency calls:
  - `retry_with_backoff`, `acquire`, `release`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/db_utils.py -Pattern "def acquire_with_retry|async def acquire_with_retry"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_db_utils.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_db_utils.md -Pattern "- Verify command:"`

