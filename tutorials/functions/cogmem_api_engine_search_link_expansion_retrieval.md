# Function Deep Dive - [cogmem_api/engine/search/link_expansion_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/link_expansion_retrieval.py)

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
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
- Source module: `cogmem_api/engine/search/link_expansion_retrieval.py`.
- Public/private breakdown: public=2, private=3.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _find_semantic_seeds | private | async _find_semantic_seeds(conn, query_embedding_str: str, bank_id: str, fact_type: str, limit: int=20, threshold: float=0.3, tags: list[str] \| None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] \| None=None) -> list[RetrievalResult] | [cogmem_api/engine/search/link_expansion_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/link_expansion_retrieval.py):39 | documented |
| LinkExpansionRetriever | __init__ | private | __init__(self, causal_weight_threshold: float=0.3) | [cogmem_api/engine/search/link_expansion_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/link_expansion_retrieval.py):93 | documented |
| LinkExpansionRetriever | name | public | name(self) -> str | [cogmem_api/engine/search/link_expansion_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/link_expansion_retrieval.py):104 | documented |
| LinkExpansionRetriever | retrieve | public | async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str \| None=None, semantic_seeds: list[RetrievalResult] \| None=None, temporal_seeds: list[RetrievalResult] \| None=None, adjacency=None, tags: list[str] \| None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] \| None=None) -> tuple[list[RetrievalResult], MPFPTimings \| None] | [cogmem_api/engine/search/link_expansion_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/link_expansion_retrieval.py):107 | documented |
| LinkExpansionRetriever | _expand_combined | private | async _expand_combined(self, conn, seed_ids: list, fact_type: str, budget: int) -> tuple[list, list, list, list] | [cogmem_api/engine/search/link_expansion_retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/link_expansion_retrieval.py):254 | documented |

### Function: (module)._find_semantic_seeds
- Signature: `async _find_semantic_seeds(conn, query_embedding_str: str, bank_id: str, fact_type: str, limit: int=20, threshold: float=0.3, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> list[RetrievalResult]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/link_expansion_retrieval.py:39`
- Purpose:
  - Thực thi nghiệp vụ `_find_semantic_seeds` trong phạm vi `(module)` của module `cogmem_api/engine/search/link_expansion_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async _find_semantic_seeds(conn, query_embedding_str: str, bank_id: str, fact_type: str, limit: int=20, threshold: float=0.3, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> list[RetrievalResult]`.
- Outputs:
  - Trả về kiểu: `list[RetrievalResult]`.
- Side effects:
  - Có khả năng tạo side effect qua call `fetch`.
- Dependency calls:
  - `build_tags_where_clause_simple`, `build_tag_groups_where_clause`, `extend`, `append`, `fetch`, `from_db_row`, `dict`, `fq_table`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/link_expansion_retrieval.py -Pattern "def _find_semantic_seeds|async def _find_semantic_seeds"`

### Function: LinkExpansionRetriever.__init__
- Signature: `__init__(self, causal_weight_threshold: float=0.3)`
- Visibility: `private`
- Location: `cogmem_api/engine/search/link_expansion_retrieval.py:93`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `LinkExpansionRetriever` của module `cogmem_api/engine/search/link_expansion_retrieval.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, causal_weight_threshold: float=0.3)`.
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
  - `Select-String -Path cogmem_api/engine/search/link_expansion_retrieval.py -Pattern "def __init__|async def __init__"`

### Function: LinkExpansionRetriever.name
- Signature: `name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/link_expansion_retrieval.py:104`
- Purpose:
  - Thực thi nghiệp vụ `name` trong phạm vi `LinkExpansionRetriever` của module `cogmem_api/engine/search/link_expansion_retrieval.py`.
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
  - `Select-String -Path cogmem_api/engine/search/link_expansion_retrieval.py -Pattern "def name|async def name"`

### Function: LinkExpansionRetriever.retrieve
- Signature: `async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str | None=None, semantic_seeds: list[RetrievalResult] | None=None, temporal_seeds: list[RetrievalResult] | None=None, adjacency=None, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> tuple[list[RetrievalResult], MPFPTimings | None]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/link_expansion_retrieval.py:107`
- Purpose:
  - Thực thi nghiệp vụ `retrieve` trong phạm vi `LinkExpansionRetriever` của module `cogmem_api/engine/search/link_expansion_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async retrieve(self, pool, query_embedding_str: str, bank_id: str, fact_type: str, budget: int, query_text: str | None=None, semantic_seeds: list[RetrievalResult] | None=None, temporal_seeds: list[RetrievalResult] | None=None, adjacency=None, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> tuple[list[RetrievalResult], MPFPTimings | None]`.
- Outputs:
  - Trả về kiểu: `tuple[list[RetrievalResult], MPFPTimings | None]`.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire_with_retry`.
- Dependency calls:
  - `time`, `MPFPTimings`, `len`, `debug`, `acquire_with_retry`, `list`, `str`, `tanh`, `dict`, `max`, `setdefault`, `set`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/link_expansion_retrieval.py -Pattern "def retrieve|async def retrieve"`

### Function: LinkExpansionRetriever._expand_combined
- Signature: `async _expand_combined(self, conn, seed_ids: list, fact_type: str, budget: int) -> tuple[list, list, list, list]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/link_expansion_retrieval.py:254`
- Purpose:
  - Thực thi nghiệp vụ `_expand_combined` trong phạm vi `LinkExpansionRetriever` của module `cogmem_api/engine/search/link_expansion_retrieval.py`.
- Inputs:
  - Theo chữ ký: `async _expand_combined(self, conn, seed_ids: list, fact_type: str, budget: int) -> tuple[list, list, list, list]`.
- Outputs:
  - Trả về kiểu: `tuple[list, list, list, list]`.
- Side effects:
  - Có khả năng tạo side effect qua call `fetch`.
- Dependency calls:
  - `fq_table`, `fetch`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/link_expansion_retrieval.py -Pattern "def _expand_combined|async def _expand_combined"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_link_expansion_retrieval.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_link_expansion_retrieval.md -Pattern "- Verify command:"`

