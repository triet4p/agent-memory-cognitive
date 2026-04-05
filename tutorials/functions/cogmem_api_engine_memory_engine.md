# Function Deep Dive - [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py)

## Purpose
- Mô tả chi tiết các hàm điều phối retain/recall/runtime lifecycle của MemoryEngine.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 19 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/memory_engine.py`.
- Public/private breakdown: public=13, private=6.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | get_current_schema | public | get_current_schema() -> str | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):50 | documented |
| (module) | set_schema_context | public | set_schema_context(schema: str) | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):57 | documented |
| (module) | fq_table | public | fq_table(table_name: str) -> str | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):67 | documented |
| (module) | validate_sql_schema | public | validate_sql_schema(sql: str) -> None | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):73 | documented |
| MemoryEngine | __init__ | private | __init__(self, db_url: str \| None=None, database_schema: str \| None=None, pool_min_size: int \| None=None, pool_max_size: int \| None=None) | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):107 | documented |
| MemoryEngine | initialized | public | initialized(self) -> bool | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):139 | documented |
| MemoryEngine | pool | public | pool(self) -> asyncpg.Pool \| None | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):143 | documented |
| MemoryEngine | initialize | public | async initialize(self) -> None | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):146 | documented |
| MemoryEngine | _bootstrap_schema_objects | private | async _bootstrap_schema_objects(self) -> None | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):178 | documented |
| MemoryEngine | _initialize_embeddings_model | private | async _initialize_embeddings_model(self) -> None | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):201 | documented |
| MemoryEngine | close | public | async close(self) -> None | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):220 | documented |
| MemoryEngine | execute | public | async execute(self, sql: str, *args: Any) -> str | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):236 | documented |
| MemoryEngine | health_check | public | async health_check(self) -> dict[str, Any] | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):245 | documented |
| MemoryEngine | _format_date | private | _format_date(dt: datetime) -> str | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):279 | documented |
| MemoryEngine | _build_retain_llm_config | private | _build_retain_llm_config(self) -> LLMConfig \| None | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):282 | documented |
| MemoryEngine | retain_batch_async | public | async retain_batch_async(self, bank_id: str, contents: list[dict[str, Any]], *, document_id: str \| None=None, fact_type_override: str \| None=None, confidence_score: float \| None=None, document_tags: list[str] \| None=None, return_usage: bool=False, operation_id: str \| None=None) | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):293 | documented |
| MemoryEngine | retain_async | public | async retain_async(self, bank_id: str, content: str, *, context: str='', event_date: datetime \| str \| None=None, document_id: str \| None=None, fact_type_override: str \| None=None, confidence_score: float \| None=None) -> list[str] | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):333 | documented |
| MemoryEngine | _fallback_recall_from_conn | private | async _fallback_recall_from_conn(self, bank_id: str, query: str, fact_types: list[str], max_tokens: int, limit: int) -> list[dict[str, Any]] | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):359 | documented |
| MemoryEngine | recall_async | public | async recall_async(self, bank_id: str, query: str, *, budget: str='mid', max_tokens: int=4096, enable_trace: bool=False, fact_types: list[str] \| None=None, question_date: datetime \| None=None) -> dict[str, Any] | [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py):436 | documented |

### Function: (module).get_current_schema
- Signature: `get_current_schema() -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:50`
- Purpose:
  - Thực thi nghiệp vụ `get_current_schema` trong phạm vi `(module)` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `get_current_schema() -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get`
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
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def get_current_schema|async def get_current_schema"`

### Function: (module).set_schema_context
- Signature: `set_schema_context(schema: str)`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:57`
- Purpose:
  - Thực thi nghiệp vụ `set_schema_context` trong phạm vi `(module)` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `set_schema_context(schema: str)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `set`, `reset`
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
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def set_schema_context|async def set_schema_context"`

### Function: (module).fq_table
- Signature: `fq_table(table_name: str) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:67`
- Purpose:
  - Thực thi nghiệp vụ `fq_table` trong phạm vi `(module)` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `fq_table(table_name: str) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get_current_schema`
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
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def fq_table|async def fq_table"`

### Function: (module).validate_sql_schema
- Signature: `validate_sql_schema(sql: str) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:73`
- Purpose:
  - Thực thi nghiệp vụ `validate_sql_schema` trong phạm vi `(module)` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `validate_sql_schema(sql: str) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `upper`, `search`, `start`, `find`, `rstrip`, `endswith`, `UnqualifiedTableError`
- Failure modes:
  - Có thể raise: `UnqualifiedTableError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def validate_sql_schema|async def validate_sql_schema"`

### Function: MemoryEngine.__init__
- Signature: `__init__(self, db_url: str | None=None, database_schema: str | None=None, pool_min_size: int | None=None, pool_max_size: int | None=None)`
- Visibility: `private`
- Location: `cogmem_api/engine/memory_engine.py:107`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, db_url: str | None=None, database_schema: str | None=None, pool_min_size: int | None=None, pool_max_size: int | None=None)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_get_raw_config`, `get_config`, `getenv`, `parse_pg0_url`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def __init__|async def __init__"`

### Function: MemoryEngine.initialized
- Signature: `initialized(self) -> bool`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:139`
- Purpose:
  - Thực thi nghiệp vụ `initialized` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `initialized(self) -> bool`.
- Outputs:
  - Trả về kiểu: `bool`.
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
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def initialized|async def initialized"`

### Function: MemoryEngine.pool
- Signature: `pool(self) -> asyncpg.Pool | None`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:143`
- Purpose:
  - Thực thi nghiệp vụ `pool` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `pool(self) -> asyncpg.Pool | None`.
- Outputs:
  - Trả về kiểu: `asyncpg.Pool | None`.
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
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def pool|async def pool"`

### Function: MemoryEngine.initialize
- Signature: `async initialize(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:146`
- Purpose:
  - Thực thi nghiệp vụ `initialize` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `async initialize(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Có khả năng tạo side effect qua call `EmbeddedPostgres`.
- Dependency calls:
  - `set`, `EmbeddedPostgres`, `_initialize_embeddings_model`, `create_pool`, `_bootstrap_schema_objects`, `is_running`, `ensure_running`
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
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def initialize|async def initialize"`

### Function: MemoryEngine._bootstrap_schema_objects
- Signature: `async _bootstrap_schema_objects(self) -> None`
- Visibility: `private`
- Location: `cogmem_api/engine/memory_engine.py:178`
- Purpose:
  - Thực thi nghiệp vụ `_bootstrap_schema_objects` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `async _bootstrap_schema_objects(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Có khả năng tạo side effect qua call `execute`.
- Dependency calls:
  - `startswith`, `create_async_engine`, `replace`, `begin`, `dispose`, `execute`, `run_sync`, `text`, `warning`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def _bootstrap_schema_objects|async def _bootstrap_schema_objects"`

### Function: MemoryEngine._initialize_embeddings_model
- Signature: `async _initialize_embeddings_model(self) -> None`
- Visibility: `private`
- Location: `cogmem_api/engine/memory_engine.py:201`
- Purpose:
  - Thực thi nghiệp vụ `_initialize_embeddings_model` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `async _initialize_embeddings_model(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `create_embeddings_from_env`, `info`, `initialize`, `DeterministicEmbeddings`, `warning`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def _initialize_embeddings_model|async def _initialize_embeddings_model"`

### Function: MemoryEngine.close
- Signature: `async close(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:220`
- Purpose:
  - Thực thi nghiệp vụ `close` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `async close(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `getattr`, `callable`, `close`, `hasattr`, `stop`
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
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def close|async def close"`

### Function: MemoryEngine.execute
- Signature: `async execute(self, sql: str, *args: Any) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:236`
- Purpose:
  - Thực thi nghiệp vụ `execute` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `async execute(self, sql: str, *args: Any) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire_with_retry`.
  - Có khả năng tạo side effect qua call `execute`.
- Dependency calls:
  - `validate_sql_schema`, `RuntimeError`, `acquire_with_retry`, `execute`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def execute|async def execute"`

### Function: MemoryEngine.health_check
- Signature: `async health_check(self) -> dict[str, Any]`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:245`
- Purpose:
  - Thực thi nghiệp vụ `health_check` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `async health_check(self) -> dict[str, Any]`.
- Outputs:
  - Trả về kiểu: `dict[str, Any]`.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire_with_retry`.
  - Có khả năng tạo side effect qua call `fetchval`.
- Dependency calls:
  - `bool`, `acquire_with_retry`, `fetchval`
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
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def health_check|async def health_check"`

### Function: MemoryEngine._format_date
- Signature: `_format_date(dt: datetime) -> str`
- Visibility: `private`
- Location: `cogmem_api/engine/memory_engine.py:279`
- Purpose:
  - Thực thi nghiệp vụ `_format_date` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `_format_date(dt: datetime) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `strftime`, `astimezone`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def _format_date|async def _format_date"`

### Function: MemoryEngine._build_retain_llm_config
- Signature: `_build_retain_llm_config(self) -> LLMConfig | None`
- Visibility: `private`
- Location: `cogmem_api/engine/memory_engine.py:282`
- Purpose:
  - Thực thi nghiệp vụ `_build_retain_llm_config` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `_build_retain_llm_config(self) -> LLMConfig | None`.
- Outputs:
  - Trả về kiểu: `LLMConfig | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `LLMConfig`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def _build_retain_llm_config|async def _build_retain_llm_config"`

### Function: MemoryEngine.retain_batch_async
- Signature: `async retain_batch_async(self, bank_id: str, contents: list[dict[str, Any]], *, document_id: str | None=None, fact_type_override: str | None=None, confidence_score: float | None=None, document_tags: list[str] | None=None, return_usage: bool=False, operation_id: str | None=None)`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:293`
- Purpose:
  - Thực thi nghiệp vụ `retain_batch_async` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `async retain_batch_async(self, bank_id: str, contents: list[dict[str, Any]], *, document_id: str | None=None, fact_type_override: str | None=None, confidence_score: float | None=None, document_tags: list[str] | None=None, return_usage: bool=False, operation_id: str | None=None)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `RuntimeError`, `retain_batch`, `_build_retain_llm_config`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def retain_batch_async|async def retain_batch_async"`

### Function: MemoryEngine.retain_async
- Signature: `async retain_async(self, bank_id: str, content: str, *, context: str='', event_date: datetime | str | None=None, document_id: str | None=None, fact_type_override: str | None=None, confidence_score: float | None=None) -> list[str]`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:333`
- Purpose:
  - Thực thi nghiệp vụ `retain_async` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `async retain_async(self, bank_id: str, content: str, *, context: str='', event_date: datetime | str | None=None, document_id: str | None=None, fact_type_override: str | None=None, confidence_score: float | None=None) -> list[str]`.
- Outputs:
  - Trả về kiểu: `list[str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `retain_batch_async`
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
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def retain_async|async def retain_async"`

### Function: MemoryEngine._fallback_recall_from_conn
- Signature: `async _fallback_recall_from_conn(self, bank_id: str, query: str, fact_types: list[str], max_tokens: int, limit: int) -> list[dict[str, Any]]`
- Visibility: `private`
- Location: `cogmem_api/engine/memory_engine.py:359`
- Purpose:
  - Thực thi nghiệp vụ `_fallback_recall_from_conn` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `async _fallback_recall_from_conn(self, bank_id: str, query: str, fact_types: list[str], max_tokens: int, limit: int) -> list[dict[str, Any]]`.
- Outputs:
  - Trả về kiểu: `list[dict[str, Any]]`.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire_with_retry`.
- Dependency calls:
  - `sorted`, `RuntimeError`, `acquire_with_retry`, `hasattr`, `dict`, `float`, `str`, `max`, `append`, `findall`, `len`, `recall_memory_units`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def _fallback_recall_from_conn|async def _fallback_recall_from_conn"`

### Function: MemoryEngine.recall_async
- Signature: `async recall_async(self, bank_id: str, query: str, *, budget: str='mid', max_tokens: int=4096, enable_trace: bool=False, fact_types: list[str] | None=None, question_date: datetime | None=None) -> dict[str, Any]`
- Visibility: `public`
- Location: `cogmem_api/engine/memory_engine.py:436`
- Purpose:
  - Thực thi nghiệp vụ `recall_async` trong phạm vi `MemoryEngine` của module `cogmem_api/engine/memory_engine.py`.
- Inputs:
  - Theo chữ ký: `async recall_async(self, bank_id: str, query: str, *, budget: str='mid', max_tokens: int=4096, enable_trace: bool=False, fact_types: list[str] | None=None, question_date: datetime | None=None) -> dict[str, Any]`.
- Outputs:
  - Trả về kiểu: `dict[str, Any]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `set`, `get`, `RuntimeError`, `lower`, `sorted`, `generate_embeddings_batch`, `str`, `retrieve_all_fact_types_parallel`, `fuse_parallel_results`, `values`, `min`, `apply_combined_scoring`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/memory_engine.py -Pattern "def recall_async|async def recall_async"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_memory_engine.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_memory_engine.md -Pattern "- Verify command:"`

