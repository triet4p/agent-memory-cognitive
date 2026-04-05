# S19.5 Manual Tutorial - cogmem_api/engine/query_analyzer.py

## Purpose (Mục đích)
- Phân tích query tự nhiên để suy ra loại intent và ràng buộc thời gian.
- Cấp trọng số adaptive RRF theo query type cho pipeline retrieval.
- Cung cấp hai implementation analyzer: Dateparser và Transformer.

## Source File
- cogmem_api/engine/query_analyzer.py

## Symbol-by-symbol explanation
### QueryType
- Literal gồm semantic, temporal, causal, prospective, preference, multi_hop.

### _ADAPTIVE_RRF_WEIGHTS và _QUERY_CHANNELS
- Bảng trọng số theo intent cho 4 kênh semantic, bm25, graph, temporal.

### TemporalConstraint, QueryAnalysis
- Model Pydantic mô tả ràng buộc thời gian và kết quả phân tích query.

### get_adaptive_rrf_weights(query_type)
- Lấy trọng số theo query_type, chuẩn hóa giá trị âm về 0 và fallback semantic khi cần.

### classify_query_type(query, temporal_constraint)
- Phân loại intent dựa trên regex theo thứ tự ưu tiên: prospective -> causal -> preference -> multi_hop -> temporal -> semantic.

### build_query_analysis(query, temporal_constraint)
- Tạo QueryAnalysis đầy đủ gồm query_type và rrf_weights.

### QueryAnalyzer
- Abstract base class với hai hàm bắt buộc load và analyze.

### DateparserQueryAnalyzer
- Analyzer chính mặc định:
  - load dateparser,
  - nhận diện period expressions đa ngôn ngữ qua _extract_period,
  - fallback search_dates cho date expression tổng quát.

### TransformerQueryAnalyzer
- Analyzer dùng mô hình T5:
  - ưu tiên _extract_with_rules,
  - fallback generation model khi pattern lạ,
  - parse output qua _parse_generated_output.

### Symbol inventory bổ sung (full names)
- _PROSPECTIVE_PATTERN, _CAUSAL_PATTERN, _PREFERENCE_PATTERN, _MULTI_HOP_PATTERN, _TEMPORAL_HINT_PATTERN, __str__, __init__, _load_model, _no_grad

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- search/retrieval.py dùng resolve_query_routing với analyzer này.
- search/temporal_extraction.py gọi analyzer.analyze để lấy temporal constraint.

### Outbound dependencies
- pydantic BaseModel.
- dateparser (ở DateparserQueryAnalyzer).
- transformers và torch (ở TransformerQueryAnalyzer).

## Runtime implications/side effects
- Dateparser analyzer load nhanh và ổn định cho production default.
- Transformer analyzer tốn tài nguyên hơn nhưng bao phủ pattern temporal linh hoạt hơn.

## Failure modes
- Thiếu dependency dateparser hoặc transformers sẽ lỗi khi load analyzer tương ứng.
- Query temporal mơ hồ có thể bị phân loại sai intent và dẫn đến trọng số RRF không tối ưu.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.query_analyzer import classify_query_type; print(classify_query_type('why did this happen?'))"
uv run python -c "from cogmem_api.engine.query_analyzer import build_query_analysis; print(build_query_analysis('what is planned next week').query_type)"
```

