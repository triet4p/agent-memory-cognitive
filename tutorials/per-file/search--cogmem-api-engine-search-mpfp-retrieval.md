# S19.5 Manual Tutorial - cogmem_api/engine/search/mpfp_retrieval.py

## Purpose (Mục đích)
- Triển khai Meta-Path Forward Push cho graph retrieval bán tuyến tính.
- Hỗ trợ lazy edge loading theo frontier để tối ưu truy vấn lớn.
- Chạy nhiều meta-path song song và hợp nhất bằng RRF.

## Source File
- cogmem_api/engine/search/mpfp_retrieval.py

## Symbol-by-symbol explanation
### EdgeTarget, EdgeCache, PatternResult, MPFPConfig, SeedNode, PatternState
- Nhóm dataclass mô tả cạnh, cache, cấu hình thuật toán và trạng thái pattern traversal.

### load_all_edges_for_frontier
- Tải top-k edges theo node và edge_type bằng LATERAL query.

### _init_pattern_state, _execute_hop, _finalize_pattern
- Nhóm hàm lõi cho từng hop của forward push.

### mpfp_traverse_hop_synchronized
- Chạy đồng bộ theo hop cho toàn bộ patterns để giảm số DB queries từ O(patterns*hops) về gần O(hops).

### mpfp_traverse_async
- Wrapper cho single-pattern hoặc use-case tương thích cũ.

### rrf_fusion
- Hợp nhất điểm từ nhiều pattern results.

### fetch_memory_units_by_ids
- Tải chi tiết memory units cho danh sách node IDs sau fusion.

### MPFPGraphRetriever
- Triển khai GraphRetriever theo MPFP:
  - chuẩn hóa seed nodes,
  - fallback semantic seeds nếu không có,
  - pre-warm edge cache,
  - chạy synchronized traversal,
  - RRF fusion,
  - fetch kết quả và gán activation.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- retrieval.py chọn retriever này khi graph_retriever là mpfp.

### Outbound dependencies
- graph_retrieval.GraphRetriever.
- tags.py.
- types.py (MPFPTimings, RetrievalResult).
- db_utils.acquire_with_retry và memory_engine.fq_table.

## Runtime implications/side effects
- MPFP hiệu quả hơn BFS trên đồ thị lớn khi threshold và top_k_neighbors được tune phù hợp.
- Cache đồng bộ theo hop giảm đáng kể tải DB ở pattern nhiều nhánh.

## Failure modes
- threshold quá cao làm lan truyền bị cắt sớm.
- top_k_neighbors quá thấp có thể bỏ mất đường quan trọng.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.mpfp_retrieval import MPFPGraphRetriever; print(MPFPGraphRetriever().name)"
uv run python -c "from cogmem_api.engine.search.mpfp_retrieval import MPFPConfig; print(MPFPConfig().top_k_neighbors)"
```
