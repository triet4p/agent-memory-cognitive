# S19.5 Manual Tutorial - [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py)

## Purpose (Mục đích)
- Điều phối retrieval 4-kênh: semantic, BM25, graph, temporal.
- Áp dụng query routing và weighted RRF theo intent.
- Gộp retrieval đa fact type với truy vấn DB tối ưu theo batch.

## Source File
- [cogmem_api/engine/search/retrieval.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/retrieval.py)

## Symbol-by-symbol explanation
### ParallelRetrievalResult, QueryRoutingDecision, MultiFactTypeRetrievalResult
- Dataclass mô tả kết quả retrieval theo fact type và toàn cục.

### _select_fact_types_for_query
- Với prospective query, chỉ giữ fact_type intention.

### _apply_query_type_evidence_priority
- Boost điểm sau RRF cho causal và prospective theo loại evidence.

### _collect_intention_result_ids, _resolve_planning_intention_ids, _filter_prospective_results
- Bộ hàm lọc prospective để chỉ giữ intention có trạng thái planning.

### resolve_query_routing
- Gọi query analyzer để lấy query_type, temporal_constraint, rrf_weights.

### fuse_parallel_results
- Gộp các list retrieval bằng weighted_reciprocal_rank_fusion rồi áp evidence priority.

### get_default_graph_retriever, set_default_graph_retriever
- Quản lý singleton graph retriever theo config.

### retrieve_semantic_bm25_combined
- Chạy semantic và BM25 cho nhiều fact types trong một truy vấn hợp nhất.

### retrieve_temporal_combined
- Truy hồi temporal theo khoảng thời gian và spreading qua temporal hoặc causal links.

### retrieve_all_fact_types_parallel
- Hàm điều phối chính cho recall:
  - query routing,
  - semantic+bm25 batch,
  - temporal batch (nếu có constraint),
  - graph retrieval song song per fact type,
  - lọc prospective planning intention.

### Symbol inventory bổ sung (full names)
- _PROSPECTIVE_ALLOWED_INTENTION_STATUS

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- memory_engine.recall_async gọi trực tiếp hàm retrieve_all_fact_types_parallel.

### Outbound dependencies
- query_analyzer.py, fusion.py, graph_retrieval.py, link_expansion_retrieval.py, mpfp_retrieval.py, tags.py.

## Runtime implications/side effects
- Thiết kế combined query giúp giảm round-trip DB đáng kể so với cách tách query per fact type.
- Prospective filter có thể loại mạnh kết quả intention không ở trạng thái planning.

## Failure modes
- Sai cấu hình graph_retriever có thể fallback BFS ngoài kỳ vọng.
- Temporal constraints quá chặt có thể trả ít hoặc rỗng kết quả temporal.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.retrieval import get_default_graph_retriever; print(get_default_graph_retriever().name)"
uv run python -c "from cogmem_api.engine.search.retrieval import resolve_query_routing; print(resolve_query_routing('what are we planning next').query_type)"
```

