# S19.5 Manual Tutorial - [cogmem_api/engine/search/trace.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/trace.py)

## Purpose (Mục đích)
- Định nghĩa toàn bộ schema trace phục vụ debug và visualization cho search.
- Lưu cả kiến trúc mới 4-way retrieval lẫn trường legacy cho graph traversal.

## Source File
- [cogmem_api/engine/search/trace.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/trace.py)

## Symbol-by-symbol explanation
### TemporalConstraint, QueryInfo, EntryPoint
- Model metadata truy vấn, embedding và entry points.

### WeightComponents, LinkInfo, NodeVisit, PruningDecision
- Model theo dõi chi tiết lan truyền activation và quyết định cắt nhánh.

### SearchPhaseMetrics
- Model đo hiệu năng theo phase.

### RetrievalResult, RetrievalMethodResults
- Model kết quả từng retrieval method.

### RRFMergeResult, RerankedResult
- Model kết quả sau hợp nhất RRF và sau rerank.

### SearchSummary
- Thống kê tổng quan của một phiên search.

### SearchTrace
- Model gốc bao trùm toàn bộ trace.
- Hỗ trợ to_json, to_dict và các helper truy vấn theo node, path, link type.

### Symbol inventory bổ sung (full names)
- get_visit_by_node_id, get_search_path_to_node, get_nodes_by_link_type, get_entry_point_nodes

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- search/tracer.py tạo và điền dữ liệu vào SearchTrace.

### Outbound dependencies
- pydantic BaseModel và datetime.

## Runtime implications/side effects
- Trace rất hữu ích cho debug nhưng có thể tăng kích thước payload và chi phí ghi log nếu bật liên tục.

## Failure modes
- Dữ liệu trace thiếu field bắt buộc sẽ fail validation ở Pydantic.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.trace import SearchTrace, QueryInfo, SearchSummary; print(SearchTrace.__name__)"
```

