# Function Deep Dive - [cogmem_api/engine/retain/link_creation.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_creation.py)

## Purpose
- Mô tả chi tiết các hàm ingestion/retain và chuẩn hóa dữ liệu trước khi ghi graph.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 6 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/retain/link_creation.py`.
- Public/private breakdown: public=6, private=0.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | create_temporal_links_batch | public | async create_temporal_links_batch(conn, bank_id: str, unit_ids: list[str]) -> int | [cogmem_api/engine/retain/link_creation.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_creation.py):9 | documented |
| (module) | create_semantic_links_batch | public | async create_semantic_links_batch(conn, bank_id: str, unit_ids: list[str], embeddings: list[list[float]]) -> int | [cogmem_api/engine/retain/link_creation.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_creation.py):16 | documented |
| (module) | create_causal_links_batch | public | async create_causal_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int | [cogmem_api/engine/retain/link_creation.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_creation.py):22 | documented |
| (module) | create_habit_sr_links_batch | public | async create_habit_sr_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int | [cogmem_api/engine/retain/link_creation.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_creation.py):50 | documented |
| (module) | create_transition_links_batch | public | async create_transition_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int | [cogmem_api/engine/retain/link_creation.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_creation.py):83 | documented |
| (module) | create_action_effect_links_batch | public | async create_action_effect_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int | [cogmem_api/engine/retain/link_creation.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_creation.py):132 | documented |

### Function: (module).create_temporal_links_batch
- Signature: `async create_temporal_links_batch(conn, bank_id: str, unit_ids: list[str]) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_creation.py:9`
- Purpose:
  - Thực thi nghiệp vụ `create_temporal_links_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_creation.py`.
- Inputs:
  - Theo chữ ký: `async create_temporal_links_batch(conn, bank_id: str, unit_ids: list[str]) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
- Side effects:
  - Có khả năng tạo side effect qua call `fetch_event_dates`.
  - Có khả năng tạo side effect qua call `insert_links`.
- Dependency calls:
  - `build_temporal_links`, `fetch_event_dates`, `insert_links`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_creation.py -Pattern "def create_temporal_links_batch|async def create_temporal_links_batch"`

### Function: (module).create_semantic_links_batch
- Signature: `async create_semantic_links_batch(conn, bank_id: str, unit_ids: list[str], embeddings: list[list[float]]) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_creation.py:16`
- Purpose:
  - Thực thi nghiệp vụ `create_semantic_links_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_creation.py`.
- Inputs:
  - Theo chữ ký: `async create_semantic_links_batch(conn, bank_id: str, unit_ids: list[str], embeddings: list[list[float]]) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
- Side effects:
  - Có khả năng tạo side effect qua call `insert_links`.
- Dependency calls:
  - `build_semantic_links`, `insert_links`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_creation.py -Pattern "def create_semantic_links_batch|async def create_semantic_links_batch"`

### Function: (module).create_causal_links_batch
- Signature: `async create_causal_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_creation.py:22`
- Purpose:
  - Thực thi nghiệp vụ `create_causal_links_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_creation.py`.
- Inputs:
  - Theo chữ ký: `async create_causal_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
- Side effects:
  - Có khả năng tạo side effect qua call `insert_links`.
- Dependency calls:
  - `enumerate`, `insert_links`, `lower`, `append`, `strip`, `len`, `clamp_relation_strength`, `str`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_creation.py -Pattern "def create_causal_links_batch|async def create_causal_links_batch"`

### Function: (module).create_habit_sr_links_batch
- Signature: `async create_habit_sr_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_creation.py:50`
- Purpose:
  - Thực thi nghiệp vụ `create_habit_sr_links_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_creation.py`.
- Inputs:
  - Theo chữ ký: `async create_habit_sr_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
- Side effects:
  - Có khả năng tạo side effect qua call `insert_links`.
- Dependency calls:
  - `insert_links`, `len`, `enumerate`, `lower`, `intersection`, `max`, `append`, `strip`, `min`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_creation.py -Pattern "def create_habit_sr_links_batch|async def create_habit_sr_links_batch"`

### Function: (module).create_transition_links_batch
- Signature: `async create_transition_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_creation.py:83`
- Purpose:
  - Thực thi nghiệp vụ `create_transition_links_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_creation.py`.
- Inputs:
  - Theo chữ ký: `async create_transition_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
- Side effects:
  - Có khả năng tạo side effect qua call `insert_links`.
- Dependency calls:
  - `enumerate`, `insert_links`, `len`, `lower`, `get`, `append`, `strip`, `clamp_relation_strength`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_creation.py -Pattern "def create_transition_links_batch|async def create_transition_links_batch"`

### Function: (module).create_action_effect_links_batch
- Signature: `async create_action_effect_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_creation.py:132`
- Purpose:
  - Thực thi nghiệp vụ `create_action_effect_links_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_creation.py`.
- Inputs:
  - Theo chữ ký: `async create_action_effect_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
- Side effects:
  - Có khả năng tạo side effect qua call `insert_links`.
- Dependency calls:
  - `enumerate`, `insert_links`, `len`, `lower`, `intersection`, `max`, `append`, `strip`, `min`, `clamp_relation_strength`, `str`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_creation.py -Pattern "def create_action_effect_links_batch|async def create_action_effect_links_batch"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_link_creation.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_link_creation.md -Pattern "- Verify command:"`

