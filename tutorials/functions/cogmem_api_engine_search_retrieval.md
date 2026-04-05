# Function Deep Dive - [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py)

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 12 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/search/retrieval.py`.
- Public/private breakdown: public=7, private=5.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _select_fact_types_for_query | private | _select_fact_types_for_query(query_type: QueryType, fact_types: list[str]) -> list[str] | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):77 | documented |
| (module) | _apply_query_type_evidence_priority | private | _apply_query_type_evidence_priority(candidates: list[MergedCandidate], query_type: QueryType) -> list[MergedCandidate] | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):84 | documented |
| (module) | _collect_intention_result_ids | private | _collect_intention_result_ids(results_by_fact_type: dict[str, ParallelRetrievalResult]) -> list[str] | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):120 | documented |
| (module) | _resolve_planning_intention_ids | private | async _resolve_planning_intention_ids(pool, bank_id: str, candidate_ids: list[str]) -> set[str] | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):132 | documented |
| (module) | _filter_prospective_results | private | _filter_prospective_results(parallel_result: ParallelRetrievalResult, planning_intention_ids: set[str]) -> ParallelRetrievalResult | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):154 | documented |
| (module) | resolve_query_routing | public | resolve_query_routing(query_text: str, question_date: datetime \| None=None, query_analyzer: QueryAnalyzer \| None=None) -> QueryRoutingDecision | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):183 | documented |
| (module) | fuse_parallel_results | public | fuse_parallel_results(parallel_result: ParallelRetrievalResult, query_type: QueryType \| None=None, rrf_weights: dict[str, float] \| None=None, k: int=60) -> list[MergedCandidate] | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):206 | documented |
| (module) | get_default_graph_retriever | public | get_default_graph_retriever() -> GraphRetriever | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):240 | documented |
| (module) | set_default_graph_retriever | public | set_default_graph_retriever(retriever: GraphRetriever) -> None | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):271 | documented |
| (module) | retrieve_semantic_bm25_combined | public | async retrieve_semantic_bm25_combined(conn, query_emb_str: str, query_text: str, bank_id: str, fact_types: list[str], limit: int, tags: list[str] \| None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] \| None=None) -> dict[str, tuple[list[RetrievalResult], list[RetrievalResult]]] | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):277 | documented |
| (module) | retrieve_temporal_combined | public | async retrieve_temporal_combined(conn, query_emb_str: str, bank_id: str, fact_types: list[str], start_date: datetime, end_date: datetime, budget: int, semantic_threshold: float=0.1, tags: list[str] \| None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] \| None=None) -> dict[str, list[RetrievalResult]] | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):441 | documented |
| (module) | retrieve_all_fact_types_parallel | public | async retrieve_all_fact_types_parallel(pool, query_text: str, query_embedding_str: str, bank_id: str, fact_types: list[str], thinking_budget: int, question_date: datetime \| None=None, query_analyzer: QueryAnalyzer \| None=None, graph_retriever: GraphRetriever \| None=None, tags: list[str] \| None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] \| None=None) -> MultiFactTypeRetrievalResult | [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py):708 | documented |

### Function: (module)._select_fact_types_for_query
- Signature: `_select_fact_types_for_query(query_type: QueryType, fact_types: list[str]) -> list[str]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/retrieval.py:77`
- Purpose:
  - Thực thi nghiệp vụ `_select_fact_types_for_query` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `_select_fact_types_for_query(query_type: QueryType, fact_types: list[str]) -> list[str]`.
- Outputs:
  - Trả về kiểu: `list[str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `list`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def _select_fact_types_for_query|async def _select_fact_types_for_query"`

### Function: (module)._apply_query_type_evidence_priority
- Signature: `_apply_query_type_evidence_priority(candidates: list[MergedCandidate], query_type: QueryType) -> list[MergedCandidate]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/retrieval.py:84`
- Purpose:
  - Thực thi nghiệp vụ `_apply_query_type_evidence_priority` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `_apply_query_type_evidence_priority(candidates: list[MergedCandidate], query_type: QueryType) -> list[MergedCandidate]`.
- Outputs:
  - Trả về kiểu: `list[MergedCandidate]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `sorted`, `enumerate`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def _apply_query_type_evidence_priority|async def _apply_query_type_evidence_priority"`

### Function: (module)._collect_intention_result_ids
- Signature: `_collect_intention_result_ids(results_by_fact_type: dict[str, ParallelRetrievalResult]) -> list[str]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/retrieval.py:120`
- Purpose:
  - Thực thi nghiệp vụ `_collect_intention_result_ids` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `_collect_intention_result_ids(results_by_fact_type: dict[str, ParallelRetrievalResult]) -> list[str]`.
- Outputs:
  - Trả về kiểu: `list[str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `set`, `values`, `list`, `add`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def _collect_intention_result_ids|async def _collect_intention_result_ids"`

### Function: (module)._resolve_planning_intention_ids
- Signature: `async _resolve_planning_intention_ids(pool, bank_id: str, candidate_ids: list[str]) -> set[str]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/retrieval.py:132`
- Purpose:
  - Thực thi nghiệp vụ `_resolve_planning_intention_ids` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `async _resolve_planning_intention_ids(pool, bank_id: str, candidate_ids: list[str]) -> set[str]`.
- Outputs:
  - Trả về kiểu: `set[str]`.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire_with_retry`.
  - Có khả năng tạo side effect qua call `fetch`.
- Dependency calls:
  - `set`, `acquire_with_retry`, `str`, `fetch`, `fq_table`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def _resolve_planning_intention_ids|async def _resolve_planning_intention_ids"`

### Function: (module)._filter_prospective_results
- Signature: `_filter_prospective_results(parallel_result: ParallelRetrievalResult, planning_intention_ids: set[str]) -> ParallelRetrievalResult`
- Visibility: `private`
- Location: `cogmem_api/engine/search/retrieval.py:154`
- Purpose:
  - Thực thi nghiệp vụ `_filter_prospective_results` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `_filter_prospective_results(parallel_result: ParallelRetrievalResult, planning_intention_ids: set[str]) -> ParallelRetrievalResult`.
- Outputs:
  - Trả về kiểu: `ParallelRetrievalResult`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `ParallelRetrievalResult`, `_filter_channel`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def _filter_prospective_results|async def _filter_prospective_results"`

### Function: (module).resolve_query_routing
- Signature: `resolve_query_routing(query_text: str, question_date: datetime | None=None, query_analyzer: QueryAnalyzer | None=None) -> QueryRoutingDecision`
- Visibility: `public`
- Location: `cogmem_api/engine/search/retrieval.py:183`
- Purpose:
  - Thực thi nghiệp vụ `resolve_query_routing` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `resolve_query_routing(query_text: str, question_date: datetime | None=None, query_analyzer: QueryAnalyzer | None=None) -> QueryRoutingDecision`.
- Outputs:
  - Trả về kiểu: `QueryRoutingDecision`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `analyze`, `QueryRoutingDecision`, `DateparserQueryAnalyzer`, `get_adaptive_rrf_weights`
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
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def resolve_query_routing|async def resolve_query_routing"`

### Function: (module).fuse_parallel_results
- Signature: `fuse_parallel_results(parallel_result: ParallelRetrievalResult, query_type: QueryType | None=None, rrf_weights: dict[str, float] | None=None, k: int=60) -> list[MergedCandidate]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/retrieval.py:206`
- Purpose:
  - Thực thi nghiệp vụ `fuse_parallel_results` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `fuse_parallel_results(parallel_result: ParallelRetrievalResult, query_type: QueryType | None=None, rrf_weights: dict[str, float] | None=None, k: int=60) -> list[MergedCandidate]`.
- Outputs:
  - Trả về kiểu: `list[MergedCandidate]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `weighted_reciprocal_rank_fusion`, `_apply_query_type_evidence_priority`, `append`, `get_adaptive_rrf_weights`
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
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def fuse_parallel_results|async def fuse_parallel_results"`

### Function: (module).get_default_graph_retriever
- Signature: `get_default_graph_retriever() -> GraphRetriever`
- Visibility: `public`
- Location: `cogmem_api/engine/search/retrieval.py:240`
- Purpose:
  - Thực thi nghiệp vụ `get_default_graph_retriever` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `get_default_graph_retriever() -> GraphRetriever`.
- Outputs:
  - Trả về kiểu: `GraphRetriever`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get_config`, `lower`, `MPFPGraphRetriever`, `info`, `BFSGraphRetriever`, `LinkExpansionRetriever`, `warning`
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
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def get_default_graph_retriever|async def get_default_graph_retriever"`

### Function: (module).set_default_graph_retriever
- Signature: `set_default_graph_retriever(retriever: GraphRetriever) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/search/retrieval.py:271`
- Purpose:
  - Thực thi nghiệp vụ `set_default_graph_retriever` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `set_default_graph_retriever(retriever: GraphRetriever) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
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
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def set_default_graph_retriever|async def set_default_graph_retriever"`

### Function: (module).retrieve_semantic_bm25_combined
- Signature: `async retrieve_semantic_bm25_combined(conn, query_emb_str: str, query_text: str, bank_id: str, fact_types: list[str], limit: int, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> dict[str, tuple[list[RetrievalResult], list[RetrievalResult]]]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/retrieval.py:277`
- Purpose:
  - Thực thi nghiệp vụ `retrieve_semantic_bm25_combined` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `async retrieve_semantic_bm25_combined(conn, query_emb_str: str, query_text: str, bank_id: str, fact_types: list[str], limit: int, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> dict[str, tuple[list[RetrievalResult], list[RetrievalResult]]]`.
- Outputs:
  - Trả về kiểu: `dict[str, tuple[list[RetrievalResult], list[RetrievalResult]]]`.
- Side effects:
  - Có khả năng tạo side effect qua call `fetch`.
- Dependency calls:
  - `sub`, `max`, `fq_table`, `build_tags_where_clause_simple`, `build_tag_groups_where_clause`, `join`, `extend`, `lower`, `append`, `get_config`, `fetch`, `dict`
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
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def retrieve_semantic_bm25_combined|async def retrieve_semantic_bm25_combined"`

### Function: (module).retrieve_temporal_combined
- Signature: `async retrieve_temporal_combined(conn, query_emb_str: str, bank_id: str, fact_types: list[str], start_date: datetime, end_date: datetime, budget: int, semantic_threshold: float=0.1, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> dict[str, list[RetrievalResult]]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/retrieval.py:441`
- Purpose:
  - Thực thi nghiệp vụ `retrieve_temporal_combined` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `async retrieve_temporal_combined(conn, query_emb_str: str, bank_id: str, fact_types: list[str], start_date: datetime, end_date: datetime, budget: int, semantic_threshold: float=0.1, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> dict[str, list[RetrievalResult]]`.
- Outputs:
  - Trả về kiểu: `dict[str, list[RetrievalResult]]`.
- Side effects:
  - Có khả năng tạo side effect qua call `fetch`.
- Dependency calls:
  - `build_tags_where_clause_simple`, `build_tag_groups_where_clause`, `extend`, `replace`, `append`, `fetch`, `total_seconds`, `get`, `set`, `list`, `str`, `add`
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
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def retrieve_temporal_combined|async def retrieve_temporal_combined"`

### Function: (module).retrieve_all_fact_types_parallel
- Signature: `async retrieve_all_fact_types_parallel(pool, query_text: str, query_embedding_str: str, bank_id: str, fact_types: list[str], thinking_budget: int, question_date: datetime | None=None, query_analyzer: QueryAnalyzer | None=None, graph_retriever: GraphRetriever | None=None, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> MultiFactTypeRetrievalResult`
- Visibility: `public`
- Location: `cogmem_api/engine/search/retrieval.py:708`
- Purpose:
  - Thực thi nghiệp vụ `retrieve_all_fact_types_parallel` trong phạm vi `(module)` của module `cogmem_api/engine/search/retrieval.py`.
- Inputs:
  - Theo chữ ký: `async retrieve_all_fact_types_parallel(pool, query_text: str, query_embedding_str: str, bank_id: str, fact_types: list[str], thinking_budget: int, question_date: datetime | None=None, query_analyzer: QueryAnalyzer | None=None, graph_retriever: GraphRetriever | None=None, tags: list[str] | None=None, tags_match: TagsMatch='any', tag_groups: list[TagGroup] | None=None) -> MultiFactTypeRetrievalResult`.
- Outputs:
  - Trả về kiểu: `MultiFactTypeRetrievalResult`.
- Side effects:
  - Có khả năng tạo side effect qua call `acquire_with_retry`.
- Dependency calls:
  - `time`, `resolve_query_routing`, `_select_fact_types_for_query`, `MultiFactTypeRetrievalResult`, `get_default_graph_retriever`, `acquire_with_retry`, `run_graph_for_fact_type`, `gather`, `get`, `ParallelRetrievalResult`, `_collect_intention_result_ids`, `retrieve_semantic_bm25_combined`
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
  - `Select-String -Path cogmem_api/engine/search/retrieval.py -Pattern "def retrieve_all_fact_types_parallel|async def retrieve_all_fact_types_parallel"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_retrieval.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_retrieval.md -Pattern "- Verify command:"`

