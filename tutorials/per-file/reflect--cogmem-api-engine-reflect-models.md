# S19.6 Manual Tutorial - cogmem_api/engine/reflect/models.py

## Purpose
- Định nghĩa kiểu dữ liệu chuẩn cho bằng chứng reflect và kết quả tổng hợp reflect.
- Cung cấp validation dữ liệu bằng Pydantic để giữ output nhất quán.

## Source File
- cogmem_api/engine/reflect/models.py

## Symbol-by-symbol explanation
### ReflectNetwork
- Literal type cho 6 network hợp lệ: world, experience, opinion, habit, intention, action_effect.

### class ReflectEvidence(BaseModel)
- Mô hình một đơn vị bằng chứng được dùng trong synthesis.
- Trường chính: id, fact_type, text, raw_snippet, source, score, event_date.

### ReflectEvidence._validate_text
- Trim text và chặn text rỗng bằng ValueError.

### ReflectEvidence._normalize_raw_snippet
- Chuẩn hóa raw_snippet: trim, chuyển chuỗi rỗng thành None.

### class ReflectSynthesisResult(BaseModel)
- Output chuẩn của một lần reflect synthesize.
- Gồm answer, used_memory_ids, networks_covered, evidence_count và prompt (debug).

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- cogmem_api/engine/reflect/tools.py tạo ReflectEvidence.
- cogmem_api/engine/reflect/agent.py trả ReflectSynthesisResult.
- cogmem_api/engine/reflect/__init__.py export cả hai model.

### Outbound dependencies
- pydantic.BaseModel, Field, field_validator.
- datetime cho timestamp của evidence.

## Runtime implications/side effects
- Validation sớm giúp giảm lỗi data quality ở tầng reflect.
- networks_covered giới hạn bằng ReflectNetwork nên bảo toàn taxonomy network của CogMem.

## Failure modes
- fact_type ngoài ReflectNetwork gây lỗi validation khi tạo ReflectEvidence.
- text trống sau strip gây ValueError.
- Nếu caller nhét kiểu sai cho event_date có thể bị Pydantic từ chối parse.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.reflect.models import ReflectEvidence; e=ReflectEvidence(id='1', fact_type='world', text='hello'); print(e.fact_type, e.raw_snippet)"
uv run python -c "from cogmem_api.engine.reflect.models import ReflectSynthesisResult; r=ReflectSynthesisResult(answer='ok'); print(r.evidence_count, len(r.networks_covered))"
```
