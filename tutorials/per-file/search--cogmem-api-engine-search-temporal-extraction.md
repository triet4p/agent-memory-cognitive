# S19.5 Manual Tutorial - cogmem_api/engine/search/temporal_extraction.py

## Purpose (Mục đích)
- Trích xuất temporal constraint từ query tự nhiên.
- Cung cấp analyzer mặc định theo lazy initialization.

## Source File
- cogmem_api/engine/search/temporal_extraction.py

## Symbol-by-symbol explanation
### _default_analyzer và get_default_analyzer
- Quản lý singleton analyzer mặc định dùng DateparserQueryAnalyzer.

### extract_temporal_constraint(query, reference_date, analyzer)
- Gọi analyzer.analyze và trả tuple start_date hoặc end_date nếu có constraint.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- retrieval.py dùng logic temporal extraction thông qua query routing.

### Outbound dependencies
- query_analyzer.QueryAnalyzer và DateparserQueryAnalyzer.

## Runtime implications/side effects
- Lazy init tránh chi phí load analyzer ở import time.

## Failure modes
- Analyzer custom không đúng interface có thể gây lỗi runtime ở analyze.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.temporal_extraction import extract_temporal_constraint; print(extract_temporal_constraint('last week'))"
```
