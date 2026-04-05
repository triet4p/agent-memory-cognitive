# Function Deep Dive - [cogmem_api/engine/retain/orchestrator.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/orchestrator.py)

## Purpose
- Mô tả chi tiết các hàm ingestion/retain và chuẩn hóa dữ liệu trước khi ghi graph.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 5 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/retain/orchestrator.py`.
- Public/private breakdown: public=3, private=2.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | utcnow | public | utcnow() -> datetime | [cogmem_api/engine/retain/orchestrator.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/orchestrator.py):18 | documented |
| (module) | parse_datetime_flexible | public | parse_datetime_flexible(value: Any) -> datetime | [cogmem_api/engine/retain/orchestrator.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/orchestrator.py):23 | documented |
| (module) | _maybe_transaction | private | async _maybe_transaction(conn) | [cogmem_api/engine/retain/orchestrator.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/orchestrator.py):34 | documented |
| (module) | _map_results_to_contents | private | _map_results_to_contents(contents: list[RetainContent], extracted_fact_count_by_content: dict[int, int], unit_ids: list[str]) -> list[list[str]] | [cogmem_api/engine/retain/orchestrator.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/orchestrator.py):45 | documented |
| (module) | retain_batch | public | async retain_batch(pool, embeddings_model, llm_config, entity_resolver, format_date_fn, bank_id: str, contents_dicts: list[RetainContentDict], config, document_id: str \| None=None, is_first_batch: bool=True, fact_type_override: str \| None=None, confidence_score: float \| None=None, document_tags: list[str] \| None=None, operation_id: str \| None=None, schema: str \| None=None, outbox_callback: Callable[['asyncpg.Connection'], Awaitable[None]] \| None=None) -> tuple[list[list[str]], TokenUsage] | [cogmem_api/engine/retain/orchestrator.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/orchestrator.py):56 | documented |

### Function: (module).utcnow
- Signature: `utcnow() -> datetime`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/orchestrator.py:18`
- Purpose:
  - Thực thi nghiệp vụ `utcnow` trong phạm vi `(module)` của module `cogmem_api/engine/retain/orchestrator.py`.
- Inputs:
  - Theo chữ ký: `utcnow() -> datetime`.
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
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/orchestrator.py -Pattern "def utcnow|async def utcnow"`

### Function: (module).parse_datetime_flexible
- Signature: `parse_datetime_flexible(value: Any) -> datetime`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/orchestrator.py:23`
- Purpose:
  - Thực thi nghiệp vụ `parse_datetime_flexible` trong phạm vi `(module)` của module `cogmem_api/engine/retain/orchestrator.py`.
- Inputs:
  - Theo chữ ký: `parse_datetime_flexible(value: Any) -> datetime`.
- Outputs:
  - Trả về kiểu: `datetime`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `isinstance`, `TypeError`, `fromisoformat`, `replace`, `type`
- Failure modes:
  - Có thể raise: `TypeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/orchestrator.py -Pattern "def parse_datetime_flexible|async def parse_datetime_flexible"`

### Function: (module)._maybe_transaction
- Signature: `async _maybe_transaction(conn)`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/orchestrator.py:34`
- Purpose:
  - Thực thi nghiệp vụ `_maybe_transaction` trong phạm vi `(module)` của module `cogmem_api/engine/retain/orchestrator.py`.
- Inputs:
  - Theo chữ ký: `async _maybe_transaction(conn)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `getattr`, `callable`, `transaction`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/orchestrator.py -Pattern "def _maybe_transaction|async def _maybe_transaction"`

### Function: (module)._map_results_to_contents
- Signature: `_map_results_to_contents(contents: list[RetainContent], extracted_fact_count_by_content: dict[int, int], unit_ids: list[str]) -> list[list[str]]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/orchestrator.py:45`
- Purpose:
  - Thực thi nghiệp vụ `_map_results_to_contents` trong phạm vi `(module)` của module `cogmem_api/engine/retain/orchestrator.py`.
- Inputs:
  - Theo chữ ký: `_map_results_to_contents(contents: list[RetainContent], extracted_fact_count_by_content: dict[int, int], unit_ids: list[str]) -> list[list[str]]`.
- Outputs:
  - Trả về kiểu: `list[list[str]]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `range`, `len`, `get`, `append`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/orchestrator.py -Pattern "def _map_results_to_contents|async def _map_results_to_contents"`

### Function: (module).retain_batch
- Signature: `async retain_batch(pool, embeddings_model, llm_config, entity_resolver, format_date_fn, bank_id: str, contents_dicts: list[RetainContentDict], config, document_id: str | None=None, is_first_batch: bool=True, fact_type_override: str | None=None, confidence_score: float | None=None, document_tags: list[str] | None=None, operation_id: str | None=None, schema: str | None=None, outbox_callback: Callable[['asyncpg.Connection'], Awaitable[None]] | None=None) -> tuple[list[list[str]], TokenUsage]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/orchestrator.py:56`
- Purpose:
  - Thực thi nghiệp vụ `retain_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/orchestrator.py`.
- Inputs:
  - Theo chữ ký: `async retain_batch(pool, embeddings_model, llm_config, entity_resolver, format_date_fn, bank_id: str, contents_dicts: list[RetainContentDict], config, document_id: str | None=None, is_first_batch: bool=True, fact_type_override: str | None=None, confidence_score: float | None=None, document_tags: list[str] | None=None, operation_id: str | None=None, schema: str | None=None, outbox_callback: Callable[['asyncpg.Connection'], Awaitable[None]] | None=None) -> tuple[list[list[str]], TokenUsage]`.
- Outputs:
  - Trả về kiểu: `tuple[list[list[str]], TokenUsage]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `augment_texts_with_dates`, `dict`, `append`, `extract_facts_from_contents`, `coerce_fact_type`, `generate_embeddings_batch`, `from_extracted_fact`, `get`, `retry_with_backoff`, `_map_results_to_contents`, `TokenUsage`, `utcnow`
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
  - `Select-String -Path cogmem_api/engine/retain/orchestrator.py -Pattern "def retain_batch|async def retain_batch"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_orchestrator.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_orchestrator.md -Pattern "- Verify command:"`

