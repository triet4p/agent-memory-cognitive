# Function Deep Dive - cogmem_api/engine/retain/link_utils.py

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
- Source module: `cogmem_api/engine/retain/link_utils.py`.
- Public/private breakdown: public=5, private=0.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | cosine_similarity | public | cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float | cogmem_api/engine/retain/link_utils.py:17 | documented |
| (module) | build_temporal_links | public | build_temporal_links(unit_dates: dict[str, datetime], window_hours: int=24) -> list[LinkRecord] | cogmem_api/engine/retain/link_utils.py:30 | documented |
| (module) | build_semantic_links | public | build_semantic_links(unit_ids: list[str], embeddings: list[list[float]], threshold: float=0.75) -> list[LinkRecord] | cogmem_api/engine/retain/link_utils.py:52 | documented |
| (module) | insert_links | public | async insert_links(conn, links: list[LinkRecord]) -> int | cogmem_api/engine/retain/link_utils.py:69 | documented |
| (module) | fetch_event_dates | public | async fetch_event_dates(conn, unit_ids: list[str]) -> dict[str, datetime] | cogmem_api/engine/retain/link_utils.py:102 | documented |

### Function: (module).cosine_similarity
- Signature: `cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_utils.py:17`
- Purpose:
  - Thực thi nghiệp vụ `cosine_similarity` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_utils.py`.
- Inputs:
  - Theo chữ ký: `cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float`.
- Outputs:
  - Trả về kiểu: `float`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `sum`, `sqrt`, `len`, `zip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_utils.py -Pattern "def cosine_similarity|async def cosine_similarity"`

### Function: (module).build_temporal_links
- Signature: `build_temporal_links(unit_dates: dict[str, datetime], window_hours: int=24) -> list[LinkRecord]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_utils.py:30`
- Purpose:
  - Thực thi nghiệp vụ `build_temporal_links` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_utils.py`.
- Inputs:
  - Theo chữ ký: `build_temporal_links(unit_dates: dict[str, datetime], window_hours: int=24) -> list[LinkRecord]`.
- Outputs:
  - Trả về kiểu: `list[LinkRecord]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `list`, `timedelta`, `enumerate`, `len`, `items`, `abs`, `max`, `append`, `total_seconds`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_utils.py -Pattern "def build_temporal_links|async def build_temporal_links"`

### Function: (module).build_semantic_links
- Signature: `build_semantic_links(unit_ids: list[str], embeddings: list[list[float]], threshold: float=0.75) -> list[LinkRecord]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_utils.py:52`
- Purpose:
  - Thực thi nghiệp vụ `build_semantic_links` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_utils.py`.
- Inputs:
  - Theo chữ ký: `build_semantic_links(unit_ids: list[str], embeddings: list[list[float]], threshold: float=0.75) -> list[LinkRecord]`.
- Outputs:
  - Trả về kiểu: `list[LinkRecord]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `enumerate`, `len`, `cosine_similarity`, `append`, `float`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_utils.py -Pattern "def build_semantic_links|async def build_semantic_links"`

### Function: (module).insert_links
- Signature: `async insert_links(conn, links: list[LinkRecord]) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_utils.py:69`
- Purpose:
  - Thực thi nghiệp vụ `insert_links` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_utils.py`.
- Inputs:
  - Theo chữ ký: `async insert_links(conn, links: list[LinkRecord]) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
- Side effects:
  - Có khả năng tạo side effect qua call `execute`.
  - Có khả năng tạo side effect qua call `executemany`.
  - Có khả năng tạo side effect qua call `insert_memory_links`.
- Dependency calls:
  - `hasattr`, `len`, `execute`, `executemany`, `insert_memory_links`, `fq_table`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_utils.py -Pattern "def insert_links|async def insert_links"`

### Function: (module).fetch_event_dates
- Signature: `async fetch_event_dates(conn, unit_ids: list[str]) -> dict[str, datetime]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/link_utils.py:102`
- Purpose:
  - Thực thi nghiệp vụ `fetch_event_dates` trong phạm vi `(module)` của module `cogmem_api/engine/retain/link_utils.py`.
- Inputs:
  - Theo chữ ký: `async fetch_event_dates(conn, unit_ids: list[str]) -> dict[str, datetime]`.
- Outputs:
  - Trả về kiểu: `dict[str, datetime]`.
- Side effects:
  - Có khả năng tạo side effect qua call `fetch`.
- Dependency calls:
  - `hasattr`, `fetch`, `str`, `get_unit_event_dates`, `fq_table`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/link_utils.py -Pattern "def fetch_event_dates|async def fetch_event_dates"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_link_utils.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_link_utils.md -Pattern "- Verify command:"`

