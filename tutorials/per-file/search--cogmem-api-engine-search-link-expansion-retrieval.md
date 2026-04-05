# S19.5 Manual Tutorial - cogmem_api/engine/search/link_expansion_retrieval.py

## Purpose (Mục đích)
- Triển khai graph retrieval kiểu mở rộng liên kết từ seed nodes.
- Kết hợp bốn tín hiệu: entity, semantic, causal, transition.
- Tối ưu truy vấn bằng một roundtrip CTE cho nhiều nguồn signal.

## Source File
- cogmem_api/engine/search/link_expansion_retrieval.py

## Symbol-by-symbol explanation
### _find_semantic_seeds
- Tìm semantic seeds theo embedding threshold và tags filter.

### LinkExpansionRetriever
- Graph retriever với name là link_expansion.
- retrieve:
  - lấy seeds semantic hoặc dùng seeds có sẵn,
  - gộp với temporal seeds,
  - gọi _expand_combined để lấy bốn nhóm rows,
  - hợp nhất score theo additive evidence,
  - map về RetrievalResult và áp tag filters.

### _expand_combined
- CTE query gồm entity_expanded, semantic_expanded, causal_expanded, transition_expanded.
- Trả rows kèm source để merge theo từng loại tín hiệu.

### Symbol inventory bổ sung (full names)
- __init__

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- retrieval.py chọn retriever này khi config graph_retriever là link_expansion.

### Outbound dependencies
- graph_retrieval.GraphRetriever.
- tags.py (tag filters).
- types.py (RetrievalResult, MPFPTimings).
- memory_engine.fq_table.

## Runtime implications/side effects
- Phù hợp khi dữ liệu links đã được tiền xử lý tốt ở retain pipeline.
- Một truy vấn CTE hợp nhất giúp giảm độ trễ và số roundtrip DB.

## Failure modes
- Seed rỗng dẫn đến kết quả rỗng.
- Link graph thiếu hoặc weight thấp làm giảm khả năng mở rộng liên kết.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.link_expansion_retrieval import LinkExpansionRetriever; print(LinkExpansionRetriever().name)"
```

