# Function Deep Dive - [cogmem_api/engine/search/graph_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/graph_retrieval.py)

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
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
- Source module: `cogmem_api/engine/search/graph_retrieval.py`.
- Public/private breakdown: public=4, private=2.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| BFSGraphRetriever | __init__ | private | __init__(self, entry_point_limit: int=5, entry_point_threshold: float=0.5, activation_decay: float=0.8, min_activation: float=0.1, batch_size: int=20, refractory_steps: int=1, firing_quota: int=2, activation_saturation: float=2.0) | [cogmem_api/engine/search/graph_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/graph_retrieval.py):84 | documented |
| BFSGraphRetriever | name | public | name(self) -> str | [cogmem_api/engine/search/graph_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/graph_retrieval.py):118 | documented |
| BFSGraphRetriever | retrieve | public | async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str \| None=None, semantic_seeds: list[RetrievalResult] \| None=None, temporal_seeds: list[RetrievalResult] \| None=None, adjacency=None, tags: list[str] \| None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] \| None=None) -> tuple[list[RetrievalResult], MPFPTimings \| None] | [cogmem_api/engine/search/graph_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/graph_retrieval.py):121 | documented |
| BFSGraphRetriever | _retrieve_with_conn | private | async _retrieve_with_conn(self, conn, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, tags: list[str] \| None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] \| None=None) -> list[RetrievalResult] | [cogmem_api/engine/search/graph_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/graph_retrieval.py):162 | documented |
| GraphRetriever | name | public | name(self) -> str | [cogmem_api/engine/search/graph_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/graph_retrieval.py):32 | documented |
| GraphRetriever | retrieve | public | async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str \| None=None, semantic_seeds: list[RetrievalResult] \| None=None, temporal_seeds: list[RetrievalResult] \| None=None, adjacency=None, tags: list[str] \| None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] \| None=None) -> tuple[list[RetrievalResult], MPFPTimings \| None] | [cogmem_api/engine/search/graph_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/graph_retrieval.py):37 | documented |

### Function: BFSGraphRetriever.__init__
- Signature: `__init__(self, entry_point_limit: int=5, entry_point_threshold: float=0.5, activation_decay: float=0.8, min_activation: float=0.1, batch_size: int=20, refractory_steps: int=1, firing_quota: int=2, activation_saturation: float=2.0)`
- Visibility: `private`
- Location: `cogmem_api/engine/search/graph_retrieval.py:84`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `BFSGraphRetriever` của module `cogmem_api/engine/search/graph_retrieval.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, entry_point_limit: int=5, entry_point_threshold: float=0.5, activation_decay: float=0.8, min_activation: float=0.1, batch_size: int=20, refractory_steps: int=1, firing_quota: int=2, activation_saturation: float=2.0)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `max`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/graph_retrieval.py -Pattern "def __init__|async def __init__"`

### Function: BFSGraphRetriever.name
- Signature: `name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/graph_retrieval.py:118`
- Purpose:
  - Thực thi nghiệp vụ `name` trong phạm vi `BFSGraphRetriever` của module `cogmem_api/engine/search/graph_retrieval.py`.
- Inputs:
  - Theo chữ ký: `name(self) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
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
  - `Select-String -Path cogmem_api/engine/search/graph_retrieval.py -Pattern "def name|async def name"`

### Function: BFSGraphRetriever.retrieve
- Signature: `async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str | None=None, semantic_seeds: list[RetrievalResult] | None=None, temporal_seeds: list[RetrievalResult] | None=None, adjacency=None, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> tuple[list[RetrievalResult], MPFPTimings | None]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/graph_retrieval.py:121`
- Purpose:
  - Thực thi nghiệp vụ `retrieve` trong phạm vi `BFSGraphRetriever` của module `cogmem_api/engine/search/graph_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str | None=None, semantic_seeds: list[RetrievalResult] | None=None, temporal_seeds: list[RetrievalResult] | None=None, adjacency=None, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> tuple[list[RetrievalResult], MPFPTimings | None]`.
- Outputs:
  - Trả về kiểu: `tuple[list[RetrievalResult], MPFPTimings | None]`.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire_with_retry`.
- Dependency calls:
  - `acquire_with_retry`, `_retrieve_with_conn`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/graph_retrieval.py -Pattern "def retrieve|async def retrieve"`

### Function: BFSGraphRetriever._retrieve_with_conn
- Signature: `async _retrieve_with_conn(self, conn, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> list[RetrievalResult]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/graph_retrieval.py:162`
- Purpose:
  - Thực thi nghiệp vụ `_retrieve_with_conn` trong phạm vi `BFSGraphRetriever` của module `cogmem_api/engine/search/graph_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async _retrieve_with_conn(self, conn, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> list[RetrievalResult]`.
- Outputs:
  - Trả về kiểu: `list[RetrievalResult]`.
- Side effects:
  - Có khả năng tạo side effect qua call `fetch`.
- Dependency calls:
  - `build_tags_where_clause_simple`, `build_tag_groups_where_clause`, `extend`, `debug`, `defaultdict`, `sorted`, `append`, `fetch`, `from_db_row`, `min`, `items`, `sort`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/graph_retrieval.py -Pattern "def _retrieve_with_conn|async def _retrieve_with_conn"`

### Function: GraphRetriever.name
- Signature: `name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/graph_retrieval.py:32`
- Purpose:
  - Thực thi nghiệp vụ `name` trong phạm vi `GraphRetriever` của module `cogmem_api/engine/search/graph_retrieval.py`.
- Inputs:
  - Theo chữ ký: `name(self) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
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
  - `Select-String -Path cogmem_api/engine/search/graph_retrieval.py -Pattern "def name|async def name"`

### Function: GraphRetriever.retrieve
- Signature: `async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str | None=None, semantic_seeds: list[RetrievalResult] | None=None, temporal_seeds: list[RetrievalResult] | None=None, adjacency=None, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> tuple[list[RetrievalResult], MPFPTimings | None]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/graph_retrieval.py:37`
- Purpose:
  - Thực thi nghiệp vụ `retrieve` trong phạm vi `GraphRetriever` của module `cogmem_api/engine/search/graph_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str | None=None, semantic_seeds: list[RetrievalResult] | None=None, temporal_seeds: list[RetrievalResult] | None=None, adjacency=None, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> tuple[list[RetrievalResult], MPFPTimings | None]`.
- Outputs:
  - Trả về kiểu: `tuple[list[RetrievalResult], MPFPTimings | None]`.
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
  - `Select-String -Path cogmem_api/engine/search/graph_retrieval.py -Pattern "def retrieve|async def retrieve"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_graph_retrieval.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_graph_retrieval.md -Pattern "- Verify command:"`

