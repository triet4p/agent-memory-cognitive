# S19.5 Manual Tutorial - [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py)

## Purpose (Mục đích)
- Thu thập trace chi tiết cho toàn bộ vòng đời search.
- Ghi nhận retrieval outputs, RRF merge, rerank và legacy graph visits.

## Source File
- [cogmem_api/engine/search/tracer.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/tracer.py)

## Symbol-by-symbol explanation
### SearchTracer.__init__
- Khởi tạo trạng thái trace và biến đếm thống kê.

### start, record_query_embedding, record_temporal_constraint
- Nhóm hàm ghi thông tin đầu vào query và mốc thời gian.

### add_entry_point, visit_node, add_neighbor_link, prune_node
- Nhóm hàm ghi chi tiết quá trình graph traversal.

### add_phase_metric
- Ghi metrics theo phase.

### add_retrieval_results, add_rrf_merged, add_reranked
- Ghi pipeline mới 4-way retrieval -> RRF -> rerank.

### finalize
- Chốt trace:
  - tính tổng thời gian,
  - gán final rank cho visits,
  - tạo QueryInfo, SearchSummary,
  - trả SearchTrace hoàn chỉnh.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Retrieval or recall orchestration có thể dùng SearchTracer khi bật trace mode.

### Outbound dependencies
- search/trace.py (toàn bộ model classes).
- time, datetime.

## Runtime implications/side effects
- Bật tracer chi tiết giúp điều tra hành vi retrieval nhưng tăng overhead runtime và bộ nhớ.

## Failure modes
- Gọi finalize trước start sẽ raise ValueError.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.tracer import SearchTracer; t=SearchTracer('q',10,100); t.start(); print(type(t).__name__)"
```
