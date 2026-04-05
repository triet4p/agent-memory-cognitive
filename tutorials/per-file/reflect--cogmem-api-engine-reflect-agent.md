# S19.6 Manual Tutorial - cogmem_api/engine/reflect/agent.py

## Purpose
- Thực thi lazy reflect synthesis: tổng hợp câu trả lời sau retrieval, không chạy consolidation chủ động.
- Chuẩn hóa output reflect thành ReflectSynthesisResult với metadata evidence.

## Source File
- cogmem_api/engine/reflect/agent.py

## Symbol-by-symbol explanation
### _default_markdown_answer(question, evidence_lines)
- Sinh câu trả lời markdown fallback khi không có LLM generator hoặc generator trả rỗng.
- Khi không có evidence, trả thông báo thiếu dữ liệu; khi có evidence, dựng danh sách bullet từ bằng chứng.

### synthesize_lazy_reflect(...)
- Nhận question + retrieved_items, chuẩn hóa evidence qua prepare_lazy_evidence.
- Dựng prompt reflect bằng build_lazy_synthesis_prompt, có thể truyền bank_profile.
- Nếu có llm_generate: gọi LLM với prompt; nếu output rỗng thì fallback về _default_markdown_answer.
- Nếu không có llm_generate: luôn dùng fallback markdown answer.
- Thu thập networks_covered theo fact_type distinct, trả ReflectSynthesisResult gồm answer, used_memory_ids, evidence_count, prompt (optional).

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- cogmem_api/engine/reflect/__init__.py export synthesize_lazy_reflect.
- cogmem_api/engine/memory_engine.py (luồng recall/reflect) là caller chính khi cần tổng hợp phản hồi.

### Outbound dependencies
- cogmem_api/engine/reflect/tools.py: prepare_lazy_evidence.
- cogmem_api/engine/reflect/prompts.py: build_lazy_synthesis_prompt.
- cogmem_api/engine/reflect/models.py: ReflectSynthesisResult.
- Optional dependency: callback llm_generate do caller cung cấp.

## Runtime implications/side effects
- Chất lượng answer phụ thuộc chất lượng retrieval items và callback LLM.
- include_prompt=True có thể tăng payload response (hữu ích cho debug, tốn tài nguyên log/transport).
- Không ghi DB, không mutate state hệ thống.

## Failure modes
- retrieved_items có cấu trúc sai có thể bị loại hết ở bước prepare_lazy_evidence, dẫn đến answer thiếu nội dung.
- llm_generate ném exception sẽ bubble lên caller nếu không được bao ngoài.
- max_evidence quá nhỏ có thể làm mất bằng chứng quan trọng; quá lớn có thể làm prompt dài và chậm.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.reflect.agent import synthesize_lazy_reflect; r=synthesize_lazy_reflect('Q?', [], None); print(r.evidence_count, len(r.used_memory_ids))"
uv run python -c "from cogmem_api.engine.reflect.agent import synthesize_lazy_reflect; items=[{'id':'m1','fact_type':'world','text':'Alice likes Rust','rrf_score':0.9}]; r=synthesize_lazy_reflect('Alice thích gì?', items, include_prompt=True); print(r.networks_covered, r.prompt is not None)"
```
