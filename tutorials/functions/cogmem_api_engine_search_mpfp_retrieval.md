# Function Deep Dive - [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py)

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 18 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/search/mpfp_retrieval.py`.
- Public/private breakdown: public=12, private=6.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | load_all_edges_for_frontier | public | async load_all_edges_for_frontier(pool, node_ids: list[str], top_k_per_type: int=20) -> dict[str, dict[str, list[EdgeTarget]]] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):158 | documented |
| (module) | _init_pattern_state | private | _init_pattern_state(seeds: list[SeedNode], pattern: list[str]) -> PatternState | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):233 | documented |
| (module) | _execute_hop | private | _execute_hop(state: PatternState, cache: EdgeCache, config: MPFPConfig) -> set[str] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):246 | documented |
| (module) | _finalize_pattern | private | _finalize_pattern(state: PatternState, config: MPFPConfig) -> PatternResult | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):291 | documented |
| (module) | mpfp_traverse_hop_synchronized | public | async mpfp_traverse_hop_synchronized(pool, pattern_jobs: list[tuple[list[SeedNode], list[str]]], config: MPFPConfig, cache: EdgeCache) -> list[PatternResult] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):300 | documented |
| (module) | mpfp_traverse_async | public | async mpfp_traverse_async(pool, seeds: list[SeedNode], pattern: list[str], config: MPFPConfig, cache: EdgeCache) -> PatternResult | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):379 | documented |
| (module) | rrf_fusion | public | rrf_fusion(results: list[PatternResult], k: int=60, top_k: int=50) -> list[tuple[str, float]] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):399 | documented |
| (module) | fetch_memory_units_by_ids | public | async fetch_memory_units_by_ids(pool, node_ids: list[str], fact_type: str) -> list[RetrievalResult] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):438 | documented |
| EdgeCache | get_neighbors | public | get_neighbors(self, edge_type: str, node_id: str) -> list[EdgeTarget] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):68 | documented |
| EdgeCache | get_normalized_neighbors | public | get_normalized_neighbors(self, edge_type: str, node_id: str, top_k: int) -> list[EdgeTarget] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):72 | documented |
| EdgeCache | is_fully_loaded | public | is_fully_loaded(self, node_id: str) -> bool | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):84 | documented |
| EdgeCache | get_uncached | public | get_uncached(self, node_ids: list[str]) -> list[str] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):88 | documented |
| EdgeCache | add_all_edges | public | add_all_edges(self, edges_by_type: dict[str, dict[str, list[EdgeTarget]]], all_queried: list[str]) | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):92 | documented |
| MPFPGraphRetriever | __init__ | private | __init__(self, config: MPFPConfig \| None=None) | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):476 | documented |
| MPFPGraphRetriever | name | public | name(self) -> str | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):492 | documented |
| MPFPGraphRetriever | retrieve | public | async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str \| None=None, semantic_seeds: list[RetrievalResult] \| None=None, temporal_seeds: list[RetrievalResult] \| None=None, adjacency=None, tags: list[str] \| None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] \| None=None) -> tuple[list[RetrievalResult], MPFPTimings \| None] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):495 | documented |
| MPFPGraphRetriever | _convert_seeds | private | _convert_seeds(self, seeds: list[RetrievalResult] \| None, score_attr: str) -> list[SeedNode] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):643 | documented |
| MPFPGraphRetriever | _find_semantic_seeds | private | async _find_semantic_seeds(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, limit: int=20, threshold: float=0.3, tags: list[str] \| None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] \| None=None) -> list[SeedNode] | [cogmem_api/engine/search/mpfp_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/mpfp_retrieval.py):661 | documented |

### Function: (module).load_all_edges_for_frontier
- Signature: `async load_all_edges_for_frontier(pool, node_ids: list[str], top_k_per_type: int=20) -> dict[str, dict[str, list[EdgeTarget]]]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:158`
- Purpose:
  - Thực thi nghiệp vụ `load_all_edges_for_frontier` trong phạm vi `(module)` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async load_all_edges_for_frontier(pool, node_ids: list[str], top_k_per_type: int=20) -> dict[str, dict[str, list[EdgeTarget]]]`.
- Outputs:
  - Trả về kiểu: `dict[str, dict[str, list[EdgeTarget]]]`.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire_with_retry`.
  - Có khả năng tạo side effect qua call `fetch`.
- Dependency calls:
  - `defaultdict`, `acquire_with_retry`, `str`, `append`, `dict`, `fetch`, `EdgeTarget`, `items`, `fq_table`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def load_all_edges_for_frontier|async def load_all_edges_for_frontier"`

### Function: (module)._init_pattern_state
- Signature: `_init_pattern_state(seeds: list[SeedNode], pattern: list[str]) -> PatternState`
- Visibility: `private`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:233`
- Purpose:
  - Thực thi nghiệp vụ `_init_pattern_state` trong phạm vi `(module)` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `_init_pattern_state(seeds: list[SeedNode], pattern: list[str]) -> PatternState`.
- Outputs:
  - Trả về kiểu: `PatternState`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `sum`, `PatternState`, `len`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def _init_pattern_state|async def _init_pattern_state"`

### Function: (module)._execute_hop
- Signature: `_execute_hop(state: PatternState, cache: EdgeCache, config: MPFPConfig) -> set[str]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:246`
- Purpose:
  - Thực thi nghiệp vụ `_execute_hop` trong phạm vi `(module)` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `_execute_hop(state: PatternState, cache: EdgeCache, config: MPFPConfig) -> set[str]`.
- Outputs:
  - Trả về kiểu: `set[str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `set`, `items`, `len`, `get_normalized_neighbors`, `get`, `is_fully_loaded`, `add`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def _execute_hop|async def _execute_hop"`

### Function: (module)._finalize_pattern
- Signature: `_finalize_pattern(state: PatternState, config: MPFPConfig) -> PatternResult`
- Visibility: `private`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:291`
- Purpose:
  - Thực thi nghiệp vụ `_finalize_pattern` trong phạm vi `(module)` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `_finalize_pattern(state: PatternState, config: MPFPConfig) -> PatternResult`.
- Outputs:
  - Trả về kiểu: `PatternResult`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `items`, `PatternResult`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def _finalize_pattern|async def _finalize_pattern"`

### Function: (module).mpfp_traverse_hop_synchronized
- Signature: `async mpfp_traverse_hop_synchronized(pool, pattern_jobs: list[tuple[list[SeedNode], list[str]]], config: MPFPConfig, cache: EdgeCache) -> list[PatternResult]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:300`
- Purpose:
  - Thực thi nghiệp vụ `mpfp_traverse_hop_synchronized` trong phạm vi `(module)` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async mpfp_traverse_hop_synchronized(pool, pattern_jobs: list[tuple[list[SeedNode], list[str]]], config: MPFPConfig, cache: EdgeCache) -> list[PatternResult]`.
- Outputs:
  - Trả về kiểu: `list[PatternResult]`.
- Side effects:
  - Có khả năng tạo side effect qua call `_execute_hop`.
  - Có khả năng tạo side effect qua call `update`.
- Dependency calls:
  - `max`, `range`, `_init_pattern_state`, `time`, `set`, `len`, `append`, `_finalize_pattern`, `list`, `_execute_hop`, `update`, `add_all_edges`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def mpfp_traverse_hop_synchronized|async def mpfp_traverse_hop_synchronized"`

### Function: (module).mpfp_traverse_async
- Signature: `async mpfp_traverse_async(pool, seeds: list[SeedNode], pattern: list[str], config: MPFPConfig, cache: EdgeCache) -> PatternResult`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:379`
- Purpose:
  - Thực thi nghiệp vụ `mpfp_traverse_async` trong phạm vi `(module)` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async mpfp_traverse_async(pool, seeds: list[SeedNode], pattern: list[str], config: MPFPConfig, cache: EdgeCache) -> PatternResult`.
- Outputs:
  - Trả về kiểu: `PatternResult`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `PatternResult`, `mpfp_traverse_hop_synchronized`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def mpfp_traverse_async|async def mpfp_traverse_async"`

### Function: (module).rrf_fusion
- Signature: `rrf_fusion(results: list[PatternResult], k: int=60, top_k: int=50) -> list[tuple[str, float]]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:399`
- Purpose:
  - Thực thi nghiệp vụ `rrf_fusion` trong phạm vi `(module)` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `rrf_fusion(results: list[PatternResult], k: int=60, top_k: int=50) -> list[tuple[str, float]]`.
- Outputs:
  - Trả về kiểu: `list[tuple[str, float]]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `sorted`, `enumerate`, `items`, `keys`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def rrf_fusion|async def rrf_fusion"`

### Function: (module).fetch_memory_units_by_ids
- Signature: `async fetch_memory_units_by_ids(pool, node_ids: list[str], fact_type: str) -> list[RetrievalResult]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:438`
- Purpose:
  - Thực thi nghiệp vụ `fetch_memory_units_by_ids` trong phạm vi `(module)` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async fetch_memory_units_by_ids(pool, node_ids: list[str], fact_type: str) -> list[RetrievalResult]`.
- Outputs:
  - Trả về kiểu: `list[RetrievalResult]`.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire_with_retry`.
  - Có khả năng tạo side effect qua call `fetch`.
- Dependency calls:
  - `acquire_with_retry`, `from_db_row`, `fetch`, `dict`, `fq_table`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def fetch_memory_units_by_ids|async def fetch_memory_units_by_ids"`

### Function: EdgeCache.get_neighbors
- Signature: `get_neighbors(self, edge_type: str, node_id: str) -> list[EdgeTarget]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:68`
- Purpose:
  - Thực thi nghiệp vụ `get_neighbors` trong phạm vi `EdgeCache` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `get_neighbors(self, edge_type: str, node_id: str) -> list[EdgeTarget]`.
- Outputs:
  - Trả về kiểu: `list[EdgeTarget]`.
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
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def get_neighbors|async def get_neighbors"`

### Function: EdgeCache.get_normalized_neighbors
- Signature: `get_normalized_neighbors(self, edge_type: str, node_id: str, top_k: int) -> list[EdgeTarget]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:72`
- Purpose:
  - Thực thi nghiệp vụ `get_normalized_neighbors` trong phạm vi `EdgeCache` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `get_normalized_neighbors(self, edge_type: str, node_id: str, top_k: int) -> list[EdgeTarget]`.
- Outputs:
  - Trả về kiểu: `list[EdgeTarget]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `sum`, `get_neighbors`, `EdgeTarget`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def get_normalized_neighbors|async def get_normalized_neighbors"`

### Function: EdgeCache.is_fully_loaded
- Signature: `is_fully_loaded(self, node_id: str) -> bool`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:84`
- Purpose:
  - Thực thi nghiệp vụ `is_fully_loaded` trong phạm vi `EdgeCache` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `is_fully_loaded(self, node_id: str) -> bool`.
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
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def is_fully_loaded|async def is_fully_loaded"`

### Function: EdgeCache.get_uncached
- Signature: `get_uncached(self, node_ids: list[str]) -> list[str]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:88`
- Purpose:
  - Thực thi nghiệp vụ `get_uncached` trong phạm vi `EdgeCache` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `get_uncached(self, node_ids: list[str]) -> list[str]`.
- Outputs:
  - Trả về kiểu: `list[str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `is_fully_loaded`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def get_uncached|async def get_uncached"`

### Function: EdgeCache.add_all_edges
- Signature: `add_all_edges(self, edges_by_type: dict[str, dict[str, list[EdgeTarget]]], all_queried: list[str])`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:92`
- Purpose:
  - Thực thi nghiệp vụ `add_all_edges` trong phạm vi `EdgeCache` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `add_all_edges(self, edges_by_type: dict[str, dict[str, list[EdgeTarget]]], all_queried: list[str])`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Có khả năng tạo side effect qua call `update`.
- Dependency calls:
  - `items`, `update`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def add_all_edges|async def add_all_edges"`

### Function: MPFPGraphRetriever.__init__
- Signature: `__init__(self, config: MPFPConfig | None=None)`
- Visibility: `private`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:476`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `MPFPGraphRetriever` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, config: MPFPConfig | None=None)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get_config`, `MPFPConfig`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def __init__|async def __init__"`

### Function: MPFPGraphRetriever.name
- Signature: `name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:492`
- Purpose:
  - Thực thi nghiệp vụ `name` trong phạm vi `MPFPGraphRetriever` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
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
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def name|async def name"`

### Function: MPFPGraphRetriever.retrieve
- Signature: `async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str | None=None, semantic_seeds: list[RetrievalResult] | None=None, temporal_seeds: list[RetrievalResult] | None=None, adjacency=None, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> tuple[list[RetrievalResult], MPFPTimings | None]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:495`
- Purpose:
  - Thực thi nghiệp vụ `retrieve` trong phạm vi `MPFPGraphRetriever` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str | None=None, semantic_seeds: list[RetrievalResult] | None=None, temporal_seeds: list[RetrievalResult] | None=None, adjacency=None, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> tuple[list[RetrievalResult], MPFPTimings | None]`.
- Outputs:
  - Trả về kiểu: `tuple[list[RetrievalResult], MPFPTimings | None]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `MPFPTimings`, `_convert_seeds`, `len`, `EdgeCache`, `list`, `time`, `sum`, `rrf_fusion`, `sort`, `debug`, `add_all_edges`, `mpfp_traverse_hop_synchronized`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def retrieve|async def retrieve"`

### Function: MPFPGraphRetriever._convert_seeds
- Signature: `_convert_seeds(self, seeds: list[RetrievalResult] | None, score_attr: str) -> list[SeedNode]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:643`
- Purpose:
  - Thực thi nghiệp vụ `_convert_seeds` trong phạm vi `MPFPGraphRetriever` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `_convert_seeds(self, seeds: list[RetrievalResult] | None, score_attr: str) -> list[SeedNode]`.
- Outputs:
  - Trả về kiểu: `list[SeedNode]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `getattr`, `append`, `SeedNode`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def _convert_seeds|async def _convert_seeds"`

### Function: MPFPGraphRetriever._find_semantic_seeds
- Signature: `async _find_semantic_seeds(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, limit: int=20, threshold: float=0.3, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> list[SeedNode]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/mpfp_retrieval.py:661`
- Purpose:
  - Thực thi nghiệp vụ `_find_semantic_seeds` trong phạm vi `MPFPGraphRetriever` của module `cogmem_api/engine/search/mpfp_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async _find_semantic_seeds(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, limit: int=20, threshold: float=0.3, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> list[SeedNode]`.
- Outputs:
  - Trả về kiểu: `list[SeedNode]`.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire_with_retry`.
  - Có khả năng tạo side effect qua call `fetch`.
- Dependency calls:
  - `build_tags_where_clause_simple`, `build_tag_groups_where_clause`, `extend`, `append`, `acquire_with_retry`, `SeedNode`, `fetch`, `str`, `fq_table`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/mpfp_retrieval.py -Pattern "def _find_semantic_seeds|async def _find_semantic_seeds"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_mpfp_retrieval.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_mpfp_retrieval.md -Pattern "- Verify command:"`

