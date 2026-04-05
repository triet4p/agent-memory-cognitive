# Function Deep Dive - [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py)

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 13 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/search/tracer.py`.
- Public/private breakdown: public=12, private=1.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| SearchTracer | __init__ | private | __init__(self, query: str, budget: int, max_tokens: int, tags: list[str] \| None=None, tags_match: str \| None=None) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):49 | documented |
| SearchTracer | start | public | start(self) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):98 | documented |
| SearchTracer | record_query_embedding | public | record_query_embedding(self, embedding: list[float]) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):102 | documented |
| SearchTracer | record_temporal_constraint | public | record_temporal_constraint(self, start: datetime \| None, end: datetime \| None) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):106 | documented |
| SearchTracer | add_entry_point | public | add_entry_point(self, node_id: str, text: str, similarity: float, rank: int) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):111 | documented |
| SearchTracer | visit_node | public | visit_node(self, node_id: str, text: str, context: str, event_date: datetime \| None, is_entry_point: bool, parent_node_id: str \| None, link_type: Literal['temporal', 'semantic', 'entity'] \| None, link_weight: float \| None, activation: float, semantic_similarity: float, recency: float, frequency: float, final_weight: float) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):133 | documented |
| SearchTracer | add_neighbor_link | public | add_neighbor_link(self, from_node_id: str, to_node_id: str, link_type: Literal['temporal', 'semantic', 'entity'], link_weight: float, entity_id: str \| None, new_activation: float \| None, followed: bool, prune_reason: str \| None=None, is_supplementary: bool=False) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):214 | documented |
| SearchTracer | prune_node | public | prune_node(self, node_id: str, reason: Literal['already_visited', 'activation_too_low', 'budget_exhausted'], activation: float) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):264 | documented |
| SearchTracer | add_phase_metric | public | add_phase_metric(self, phase_name: str, duration_seconds: float, details: dict[str, Any] \| None=None) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):287 | documented |
| SearchTracer | add_retrieval_results | public | add_retrieval_results(self, method_name: Literal['semantic', 'bm25', 'graph', 'temporal'], results: list[tuple], duration_seconds: float, score_field: str, metadata: dict[str, Any] \| None=None, fact_type: str \| None=None) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):304 | documented |
| SearchTracer | add_rrf_merged | public | add_rrf_merged(self, merged_results: list[tuple]) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):352 | documented |
| SearchTracer | add_reranked | public | add_reranked(self, reranked_results: list[dict[str, Any]], rrf_merged: list) | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):371 | documented |
| SearchTracer | finalize | public | finalize(self, final_results: list[dict[str, Any]]) -> SearchTrace | [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py):418 | documented |

### Function: SearchTracer.__init__
- Signature: `__init__(self, query: str, budget: int, max_tokens: int, tags: list[str] | None=None, tags_match: str | None=None)`
- Visibility: `private`
- Location: `cogmem_api/engine/search/tracer.py:49`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, query: str, budget: int, max_tokens: int, tags: list[str] | None=None, tags_match: str | None=None)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `set`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def __init__|async def __init__"`

### Function: SearchTracer.start
- Signature: `start(self)`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:98`
- Purpose:
  - Thực thi nghiệp vụ `start` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `start(self)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `time`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def start|async def start"`

### Function: SearchTracer.record_query_embedding
- Signature: `record_query_embedding(self, embedding: list[float])`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:102`
- Purpose:
  - Thực thi nghiệp vụ `record_query_embedding` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `record_query_embedding(self, embedding: list[float])`.
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
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def record_query_embedding|async def record_query_embedding"`

### Function: SearchTracer.record_temporal_constraint
- Signature: `record_temporal_constraint(self, start: datetime | None, end: datetime | None)`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:106`
- Purpose:
  - Thực thi nghiệp vụ `record_temporal_constraint` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `record_temporal_constraint(self, start: datetime | None, end: datetime | None)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `TemporalConstraint`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def record_temporal_constraint|async def record_temporal_constraint"`

### Function: SearchTracer.add_entry_point
- Signature: `add_entry_point(self, node_id: str, text: str, similarity: float, rank: int)`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:111`
- Purpose:
  - Thực thi nghiệp vụ `add_entry_point` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `add_entry_point(self, node_id: str, text: str, similarity: float, rank: int)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `min`, `append`, `max`, `EntryPoint`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def add_entry_point|async def add_entry_point"`

### Function: SearchTracer.visit_node
- Signature: `visit_node(self, node_id: str, text: str, context: str, event_date: datetime | None, is_entry_point: bool, parent_node_id: str | None, link_type: Literal['temporal', 'semantic', 'entity'] | None, link_weight: float | None, activation: float, semantic_similarity: float, recency: float, frequency: float, final_weight: float)`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:133`
- Purpose:
  - Thực thi nghiệp vụ `visit_node` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `visit_node(self, node_id: str, text: str, context: str, event_date: datetime | None, is_entry_point: bool, parent_node_id: str | None, link_type: Literal['temporal', 'semantic', 'entity'] | None, link_weight: float | None, activation: float, semantic_similarity: float, recency: float, frequency: float, final_weight: float)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `add`, `min`, `WeightComponents`, `NodeVisit`, `append`, `max`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def visit_node|async def visit_node"`

### Function: SearchTracer.add_neighbor_link
- Signature: `add_neighbor_link(self, from_node_id: str, to_node_id: str, link_type: Literal['temporal', 'semantic', 'entity'], link_weight: float, entity_id: str | None, new_activation: float | None, followed: bool, prune_reason: str | None=None, is_supplementary: bool=False)`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:214`
- Purpose:
  - Thực thi nghiệp vụ `add_neighbor_link` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `add_neighbor_link(self, from_node_id: str, to_node_id: str, link_type: Literal['temporal', 'semantic', 'entity'], link_weight: float, entity_id: str | None, new_activation: float | None, followed: bool, prune_reason: str | None=None, is_supplementary: bool=False)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `LinkInfo`, `append`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def add_neighbor_link|async def add_neighbor_link"`

### Function: SearchTracer.prune_node
- Signature: `prune_node(self, node_id: str, reason: Literal['already_visited', 'activation_too_low', 'budget_exhausted'], activation: float)`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:264`
- Purpose:
  - Thực thi nghiệp vụ `prune_node` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `prune_node(self, node_id: str, reason: Literal['already_visited', 'activation_too_low', 'budget_exhausted'], activation: float)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `append`, `PruningDecision`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def prune_node|async def prune_node"`

### Function: SearchTracer.add_phase_metric
- Signature: `add_phase_metric(self, phase_name: str, duration_seconds: float, details: dict[str, Any] | None=None)`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:287`
- Purpose:
  - Thực thi nghiệp vụ `add_phase_metric` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `add_phase_metric(self, phase_name: str, duration_seconds: float, details: dict[str, Any] | None=None)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `append`, `SearchPhaseMetrics`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def add_phase_metric|async def add_phase_metric"`

### Function: SearchTracer.add_retrieval_results
- Signature: `add_retrieval_results(self, method_name: Literal['semantic', 'bm25', 'graph', 'temporal'], results: list[tuple], duration_seconds: float, score_field: str, metadata: dict[str, Any] | None=None, fact_type: str | None=None)`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:304`
- Purpose:
  - Thực thi nghiệp vụ `add_retrieval_results` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `add_retrieval_results(self, method_name: Literal['semantic', 'bm25', 'graph', 'temporal'], results: list[tuple], duration_seconds: float, score_field: str, metadata: dict[str, Any] | None=None, fact_type: str | None=None)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `enumerate`, `append`, `get`, `RetrievalMethodResults`, `RetrievalResult`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def add_retrieval_results|async def add_retrieval_results"`

### Function: SearchTracer.add_rrf_merged
- Signature: `add_rrf_merged(self, merged_results: list[tuple])`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:352`
- Purpose:
  - Thực thi nghiệp vụ `add_rrf_merged` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `add_rrf_merged(self, merged_results: list[tuple])`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `enumerate`, `append`, `RRFMergeResult`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def add_rrf_merged|async def add_rrf_merged"`

### Function: SearchTracer.add_reranked
- Signature: `add_reranked(self, reranked_results: list[dict[str, Any]], rrf_merged: list)`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:371`
- Purpose:
  - Thực thi nghiệp vụ `add_reranked` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `add_reranked(self, reranked_results: list[dict[str, Any]], rrf_merged: list)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `enumerate`, `get`, `append`, `RerankedResult`, `len`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def add_reranked|async def add_reranked"`

### Function: SearchTracer.finalize
- Signature: `finalize(self, final_results: list[dict[str, Any]]) -> SearchTrace`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tracer.py:418`
- Purpose:
  - Thực thi nghiệp vụ `finalize` trong phạm vi `SearchTracer` của module `cogmem_api/engine/search/tracer.py`.
- Inputs:
  - Theo chữ ký: `finalize(self, final_results: list[dict[str, Any]]) -> SearchTrace`.
- Outputs:
  - Trả về kiểu: `SearchTrace`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `enumerate`, `QueryInfo`, `SearchSummary`, `SearchTrace`, `ValueError`, `time`, `now`, `len`
- Failure modes:
  - Có thể raise: `ValueError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tracer.py -Pattern "def finalize|async def finalize"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_tracer.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_tracer.md -Pattern "- Verify command:"`

