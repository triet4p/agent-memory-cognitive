# S19.5 Manual Tutorial - [cogmem_api/engine/search/fusion.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/fusion.py)

## Purpose (Mục đích)
- Gộp kết quả từ nhiều retrieval channels bằng Reciprocal Rank Fusion.
- Hỗ trợ weighted RRF cho adaptive routing theo query type.

## Source File
- [cogmem_api/engine/search/fusion.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/fusion.py)

## Symbol-by-symbol explanation
### weighted_reciprocal_rank_fusion
- Hàm chính tính điểm RRF có trọng số theo nguồn.
- Kiểm tra type đầu vào phải là RetrievalResult.
- Trả danh sách MergedCandidate đã sort theo rrf_score.

### reciprocal_rank_fusion
- Wrapper tương thích ngược cho RRF không trọng số.

### normalize_scores_on_deltas
- Min-max normalize cho các score keys trên tập kết quả hiện tại.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- retrieval.py dùng weighted_reciprocal_rank_fusion trong fuse_parallel_results.

### Outbound dependencies
- search/types.py (RetrievalResult, MergedCandidate).

## Runtime implications/side effects
- Nếu source_weights lệch mạnh, một kênh có thể chi phối thứ hạng cuối.

## Failure modes
- Truyền tuple hoặc type sai vào result_lists sẽ raise TypeError rõ ràng.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.fusion import reciprocal_rank_fusion; print(callable(reciprocal_rank_fusion))"
```
