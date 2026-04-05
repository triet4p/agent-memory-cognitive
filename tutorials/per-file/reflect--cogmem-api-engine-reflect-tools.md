# S19.6 Manual Tutorial - [cogmem_api/engine/reflect/tools.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/tools.py)

## Purpose
- Chuyển đổi output retrieval/search thành ReflectEvidence hợp lệ cho reflect synthesis.
- Deduplicate, xếp hạng, và nhóm evidence theo network.

## Source File
- [cogmem_api/engine/reflect/tools.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/tools.py)

## Symbol-by-symbol explanation
### _SUPPORTED_FACT_TYPES
- Tập fact_type được phép đi vào reflect (6 network CogMem).

### _coerce_score(payload)
- Lấy score ưu tiên theo thứ tự khóa: rrf_score, similarity, activation, temporal_score, bm25_score, score.

### _coerce_datetime(payload)
- Lấy timestamp từ event_date/occurred_start/mentioned_at nếu là datetime.

### _normalize_payload(item, source)
- Chuẩn hóa item về dict thống nhất cho 3 dạng input:
  - MergedCandidate
  - RetrievalResult
  - dict bất kỳ
- Gán source mặc định tương ứng.

### to_reflect_evidence(item, source=None)
- Validate fact_type, id, text; bỏ item không hợp lệ.
- Trả ReflectEvidence hoặc None.

### prepare_lazy_evidence(items, max_items=8)
- Map toàn bộ item sang ReflectEvidence.
- Deduplicate theo id, giữ phiên bản có score cao hơn.
- Sort giảm dần theo score, rồi timestamp (nếu có).
- Cắt còn tối đa max_items, tối thiểu 1.

### group_evidence_by_network(evidences)
- Gom evidence theo fact_type để phục vụ summary theo network.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- [cogmem_api/engine/reflect/agent.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/agent.py) gọi prepare_lazy_evidence.
- [cogmem_api/engine/reflect/__init__.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/__init__.py) export toàn bộ helper chính.

### Outbound dependencies
- [cogmem_api/engine/reflect/models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/models.py): ReflectEvidence.
- [cogmem_api/engine/search/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/types.py): RetrievalResult, MergedCandidate.
- collections.defaultdict để group theo network.

## Runtime implications/side effects
- Bước deduplicate theo id làm giảm trùng lặp evidence và giảm nhiễu prompt.
- Chiến lược sort ưu tiên score giúp reflect tập trung vào bằng chứng mạnh hơn.
- Không ghi DB; chỉ xử lý dữ liệu in-memory.

## Failure modes
- Item thiếu id/text/fact_type hợp lệ sẽ bị drop toàn bộ.
- Nếu mọi item đều bị drop thì reflect agent sẽ trả fallback answer thiếu thông tin.
- Input dict có kiểu dữ liệu lạ có thể gây convert chuỗi không mong muốn cho raw_snippet/source.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.reflect.tools import to_reflect_evidence; e=to_reflect_evidence({'id':'m1','fact_type':'world','text':'hello','score':0.5}); print(e is not None, e.score if e else None)"
uv run python -c "from cogmem_api.engine.reflect.tools import prepare_lazy_evidence; items=[{'id':'m1','fact_type':'world','text':'A','score':0.1},{'id':'m1','fact_type':'world','text':'A2','score':0.9}]; out=prepare_lazy_evidence(items, max_items=8); print(len(out), out[0].score)"
```
