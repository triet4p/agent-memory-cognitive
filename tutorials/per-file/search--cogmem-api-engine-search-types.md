# S19.5 Manual Tutorial - [cogmem_api/engine/search/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/types.py)

## Purpose (Mục đích)
- Định nghĩa kiểu dữ liệu typed cho recall pipeline.
- Thay thế cấu trúc Dict tự do bằng dataclass rõ nghĩa cho retrieval, merge và rerank.

## Source File
- [cogmem_api/engine/search/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/types.py)

## Symbol-by-symbol explanation
### MPFPTimings
- Dataclass ghi chi tiết timing MPFP retrieval theo từng fact type.

### RetrievalResult
- Dataclass kết quả raw của một retrieval method.
- from_db_row chuyển đổi dữ liệu DB thành object typed.

### MergedCandidate
- Dataclass kết quả sau weighted RRF, gồm retrieval data + rrf metadata.

### ScoredResult
- Dataclass kết quả sau reranking với các thành phần điểm normalized và combined.
- to_dict hỗ trợ tương thích ngược với nhánh cũ dùng dict.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- retrieval.py, fusion.py, reranking.py, graph retrievers.

### Outbound dependencies
- dataclasses, datetime, typing Any.

## Runtime implications/side effects
- Dùng dataclass typed giúp giảm lỗi key typo và dễ kiểm soát contract giữa các bước recall.

## Failure modes
- Dữ liệu DB thiếu trường quan trọng có thể gây KeyError ở from_db_row.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.types import RetrievalResult; r=RetrievalResult(id='1', text='x', fact_type='world'); print(r.id, r.fact_type)"
uv run python -c "from cogmem_api.engine.search.types import ScoredResult; print(ScoredResult)"
```
