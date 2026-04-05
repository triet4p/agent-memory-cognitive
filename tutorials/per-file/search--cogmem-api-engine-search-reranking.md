# S19.5 Manual Tutorial - cogmem_api/engine/search/reranking.py

## Purpose (Mục đích)
- Rerank kết quả sau RRF bằng cross-encoder.
- Tính combined score dựa trên cross-encoder score và các boost recency hoặc temporal.

## Source File
- cogmem_api/engine/search/reranking.py

## Symbol-by-symbol explanation
### _RECENCY_ALPHA, _TEMPORAL_ALPHA
- Hệ số điều chỉnh độ mạnh của recency boost và temporal boost.

### apply_combined_scoring(scored_results, now, ...)
- Áp dụng scoring kết hợp:
  - recency theo số ngày so với occurred_start,
  - temporal từ temporal_proximity hoặc giá trị trung tính 0.5,
  - combined_score = ce_normalized * recency_boost * temporal_boost.

### CrossEncoderReranker
- Wrapper cho cross encoder model.
- ensure_initialized bảo đảm model được load một lần.
- rerank tạo cặp query-doc, thêm date context, gọi predict, chuẩn hóa sigmoid và trả danh sách ScoredResult.

### Symbol inventory bổ sung (full names)
- UTC, __init__

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- memory_engine.recall_async gọi CrossEncoderReranker để rerank merged candidates.

### Outbound dependencies
- cross_encoder.py (factory và provider implementation).
- search/types.py (MergedCandidate, ScoredResult).

## Runtime implications/side effects
- Rerank cải thiện chất lượng thứ hạng nhưng tăng độ trễ theo số candidates.
- Nếu provider rrf passthrough được chọn, tác động rerank gần như trung tính.

## Failure modes
- cross encoder chưa initialize hoặc provider lỗi mạng sẽ làm rerank thất bại ở recall đường chính.

## Verify commands
```powershell
uv run python -c "import inspect; from cogmem_api.engine.search.reranking import CrossEncoderReranker; print(inspect.iscoroutinefunction(CrossEncoderReranker.rerank))"
```

