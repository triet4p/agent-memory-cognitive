# Function Deep Dive - [cogmem_api/engine/retain/entity_processing.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/entity_processing.py)

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
- Source module: `cogmem_api/engine/retain/entity_processing.py`.
- Public/private breakdown: public=2, private=2.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _normalize_entity_name | private | _normalize_entity_name(entity: str) -> str | [cogmem_api/engine/retain/entity_processing.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/entity_processing.py):11 | documented |
| (module) | _resolve_entity_id | private | _resolve_entity_id(bank_id: str, entity_name: str) -> str | [cogmem_api/engine/retain/entity_processing.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/entity_processing.py):15 | documented |
| (module) | process_entities_batch | public | async process_entities_batch(entity_resolver, conn, bank_id: str, unit_ids: list[str], facts: list[ProcessedFact], log_buffer: list[str] \| None=None, user_entities_per_content: dict[int, list[dict]] \| None=None, entity_labels: list \| None=None) -> list[EntityLink] | [cogmem_api/engine/retain/entity_processing.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/entity_processing.py):21 | documented |
| (module) | insert_entity_links_batch | public | async insert_entity_links_batch(conn, entity_links: list[EntityLink]) -> None | [cogmem_api/engine/retain/entity_processing.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/entity_processing.py):73 | documented |

### Function: (module)._normalize_entity_name
- Signature: `_normalize_entity_name(entity: str) -> str`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/entity_processing.py:11`
- Purpose:
  - Thực thi nghiệp vụ `_normalize_entity_name` trong phạm vi `(module)` của module `cogmem_api/engine/retain/entity_processing.py`.
- Inputs:
  - Theo chữ ký: `_normalize_entity_name(entity: str) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `lower`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/entity_processing.py -Pattern "def _normalize_entity_name|async def _normalize_entity_name"`

### Function: (module)._resolve_entity_id
- Signature: `_resolve_entity_id(bank_id: str, entity_name: str) -> str`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/entity_processing.py:15`
- Purpose:
  - Thực thi nghiệp vụ `_resolve_entity_id` trong phạm vi `(module)` của module `cogmem_api/engine/retain/entity_processing.py`.
- Inputs:
  - Theo chữ ký: `_resolve_entity_id(bank_id: str, entity_name: str) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `str`, `uuid5`, `_normalize_entity_name`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/entity_processing.py -Pattern "def _resolve_entity_id|async def _resolve_entity_id"`

### Function: (module).process_entities_batch
- Signature: `async process_entities_batch(entity_resolver, conn, bank_id: str, unit_ids: list[str], facts: list[ProcessedFact], log_buffer: list[str] | None=None, user_entities_per_content: dict[int, list[dict]] | None=None, entity_labels: list | None=None) -> list[EntityLink]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/entity_processing.py:21`
- Purpose:
  - Thực thi nghiệp vụ `process_entities_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/entity_processing.py`.
- Inputs:
  - Theo chữ ký: `async process_entities_batch(entity_resolver, conn, bank_id: str, unit_ids: list[str], facts: list[ProcessedFact], log_buffer: list[str] | None=None, user_entities_per_content: dict[int, list[dict]] | None=None, entity_labels: list | None=None) -> list[EntityLink]`.
- Outputs:
  - Trả về kiểu: `list[EntityLink]`.
- Side effects:
  - Có khả năng tạo side effect qua call `insert_unit_entities`.
- Dependency calls:
  - `zip`, `items`, `hasattr`, `set`, `enumerate`, `get`, `_resolve_entity_id`, `append`, `insert_unit_entities`, `strip`, `add`, `setdefault`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/entity_processing.py -Pattern "def process_entities_batch|async def process_entities_batch"`

### Function: (module).insert_entity_links_batch
- Signature: `async insert_entity_links_batch(conn, entity_links: list[EntityLink]) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/entity_processing.py:73`
- Purpose:
  - Thực thi nghiệp vụ `insert_entity_links_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/entity_processing.py`.
- Inputs:
  - Theo chữ ký: `async insert_entity_links_batch(conn, entity_links: list[EntityLink]) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Có khả năng tạo side effect qua call `insert_links`.
- Dependency calls:
  - `insert_links`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/entity_processing.py -Pattern "def insert_entity_links_batch|async def insert_entity_links_batch"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_entity_processing.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_entity_processing.md -Pattern "- Verify command:"`

