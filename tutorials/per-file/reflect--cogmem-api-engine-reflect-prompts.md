# S19.6 Manual Tutorial - [cogmem_api/engine/reflect/prompts.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/prompts.py)

## Purpose
- Xây prompt reflect theo hướng evidence-grounded, tránh bịa thông tin.
- Chuẩn hóa format prompt để dùng ổn định trong lazy synthesis.

## Source File
- [cogmem_api/engine/reflect/prompts.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/prompts.py)

## Symbol-by-symbol explanation
### SYSTEM_PROMPT
- Chỉ thị hệ thống cho LLM: chỉ trả lời dựa trên evidence đã retrieve, ưu tiên raw_snippet, không thêm claim không được chứng minh.

### _truncate(text, limit)
- Cắt chuỗi về giới hạn ký tự, thêm "..." khi vượt ngưỡng.
- Dùng để kiểm soát kích thước prompt.

### build_lazy_synthesis_prompt(question, evidences, bank_profile=None, max_snippet_chars=280)
- Tạo prompt hoàn chỉnh gồm metadata memory bank, câu hỏi, danh sách evidence đánh số, và instruction cuối.
- Nếu không có evidence thì thêm marker "- (no evidence)".
- Mỗi evidence gồm fact_type, id, source, score, fact text, raw_snippet (nếu có).

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- [cogmem_api/engine/reflect/agent.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/agent.py) gọi để dựng prompt trước khi gọi llm_generate.
- [cogmem_api/engine/reflect/__init__.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/__init__.py) export SYSTEM_PROMPT và builder.

### Outbound dependencies
- [cogmem_api/engine/reflect/models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/models.py): ReflectEvidence.
- typing.Any cho bank_profile.

## Runtime implications/side effects
- max_snippet_chars ảnh hưởng trực tiếp độ dài prompt và chi phí token.
- Prompt có score/source giúp tăng khả năng trace và audit chất lượng answer.

## Failure modes
- question rỗng vẫn tạo prompt nhưng chất lượng trả lời giảm.
- max_snippet_chars quá thấp làm mất ngữ cảnh; quá cao làm prompt phình to.
- Dữ liệu evidence bẩn (text quá nhiễu) sẽ đi thẳng vào prompt và làm giảm chất lượng đầu ra.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.reflect.prompts import build_lazy_synthesis_prompt; print('Retrieved Evidence:' in build_lazy_synthesis_prompt('Q', [], None))"
uv run python -c "from cogmem_api.engine.reflect.models import ReflectEvidence; from cogmem_api.engine.reflect.prompts import build_lazy_synthesis_prompt; e=ReflectEvidence(id='m1', fact_type='world', text='Alice works at X'); p=build_lazy_synthesis_prompt('Where?', [e]); print('Alice works at X' in p)"
```
