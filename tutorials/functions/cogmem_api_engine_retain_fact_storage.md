# Function Deep Dive - cogmem_api/engine/retain/fact_storage.py

## Purpose
- Mô tả chi tiết các hàm ingestion/retain và chuẩn hóa dữ liệu trước khi ghi graph.
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
- Source module: `cogmem_api/engine/retain/fact_storage.py`.
- Public/private breakdown: public=2, private=2.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _event_date_for_fact | private | _event_date_for_fact(fact: ProcessedFact) -> datetime | cogmem_api/engine/retain/fact_storage.py:14 | documented |
| (module) | _prepare_fact_for_storage | private | _prepare_fact_for_storage(fact: ProcessedFact) -> ProcessedFact | cogmem_api/engine/retain/fact_storage.py:18 | documented |
| (module) | ensure_bank_exists | public | async ensure_bank_exists(conn, bank_id: str) -> None | cogmem_api/engine/retain/fact_storage.py:36 | documented |
| (module) | insert_facts_batch | public | async insert_facts_batch(conn, bank_id: str, facts: list[ProcessedFact], document_id: str \| None=None) -> list[str] | cogmem_api/engine/retain/fact_storage.py:54 | documented |

### Function: (module)._event_date_for_fact
- Signature: `_event_date_for_fact(fact: ProcessedFact) -> datetime`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_storage.py:14`
- Purpose:
  - Thực thi nghiệp vụ `_event_date_for_fact` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_storage.py`.
- Inputs:
  - Theo chữ ký: `_event_date_for_fact(fact: ProcessedFact) -> datetime`.
- Outputs:
  - Trả về kiểu: `datetime`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `now`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_storage.py -Pattern "def _event_date_for_fact|async def _event_date_for_fact"`

### Function: (module)._prepare_fact_for_storage
- Signature: `_prepare_fact_for_storage(fact: ProcessedFact) -> ProcessedFact`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_storage.py:18`
- Purpose:
  - Thực thi nghiệp vụ `_prepare_fact_for_storage` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_storage.py`.
- Inputs:
  - Theo chữ ký: `_prepare_fact_for_storage(fact: ProcessedFact) -> ProcessedFact`.
- Outputs:
  - Trả về kiểu: `ProcessedFact`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `coerce_fact_type`, `sanitize_raw_snippet`, `normalize_fact_metadata`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_storage.py -Pattern "def _prepare_fact_for_storage|async def _prepare_fact_for_storage"`

### Function: (module).ensure_bank_exists
- Signature: `async ensure_bank_exists(conn, bank_id: str) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/fact_storage.py:36`
- Purpose:
  - Thực thi nghiệp vụ `ensure_bank_exists` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_storage.py`.
- Inputs:
  - Theo chữ ký: `async ensure_bank_exists(conn, bank_id: str) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Có khả năng tạo side effect qua call `execute`.
- Dependency calls:
  - `hasattr`, `execute`, `ensure_bank_exists`, `dumps`, `fq_table`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_storage.py -Pattern "def ensure_bank_exists|async def ensure_bank_exists"`

### Function: (module).insert_facts_batch
- Signature: `async insert_facts_batch(conn, bank_id: str, facts: list[ProcessedFact], document_id: str | None=None) -> list[str]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/fact_storage.py:54`
- Purpose:
  - Thực thi nghiệp vụ `insert_facts_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_storage.py`.
- Inputs:
  - Theo chữ ký: `async insert_facts_batch(conn, bank_id: str, facts: list[ProcessedFact], document_id: str | None=None) -> list[str]`.
- Outputs:
  - Trả về kiểu: `list[str]`.
- Side effects:
  - Có khả năng tạo side effect qua call `insert_memory_units`.
  - Có khả năng tạo side effect qua call `fetchval`.
- Dependency calls:
  - `hasattr`, `_prepare_fact_for_storage`, `append`, `insert_memory_units`, `fetchval`, `str`, `_event_date_for_fact`, `dumps`, `fq_table`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_storage.py -Pattern "def insert_facts_batch|async def insert_facts_batch"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_fact_storage.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_fact_storage.md -Pattern "- Verify command:"`

