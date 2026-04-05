# S19.5 Manual Tutorial - cogmem_api/engine/search/think_utils.py

## Purpose (Mục đích)
- Cung cấp utility cho bước think hoặc reflect dựa trên facts đã recall.
- Tạo prompt có ngữ cảnh disposition, background và entity summaries.
- Cung cấp hàm reflect độc lập phục vụ test hoặc integration nhẹ.

## Source File
- cogmem_api/engine/search/think_utils.py

## Symbol-by-symbol explanation
### describe_trait_level
- Ánh xạ thang điểm trait 1-5 sang mô tả ngôn ngữ.

### build_disposition_description
- Tạo mô tả đầy đủ cho skepticism, literalism, empathy.

### format_facts_for_prompt
- Chuyển danh sách MemoryFact sang JSON string cho prompt context.

### format_entity_summaries_for_prompt
- Chuẩn hóa entity summaries cho prompt reflect.

### build_think_prompt
- Dựng prompt người dùng cuối từ các phần facts, query, disposition, background, context.

### get_system_message
- Tạo system message theo disposition để điều chỉnh phong cách phản hồi.

### reflect
- Hàm async standalone:
  - chuẩn hóa dữ liệu facts,
  - build prompt + system message,
  - gọi llm_config.call,
  - trả answer text.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Có thể được gọi trong đường think hoặc reflect khi cần tổng hợp câu trả lời từ facts.

### Outbound dependencies
- response_models.DispositionTraits và MemoryFact.

## Runtime implications/side effects
- Prompt dài hoặc dữ liệu facts lớn có thể tăng token usage và độ trễ LLM call.

## Failure modes
- llm_config không hỗ trợ interface call như kỳ vọng sẽ gây lỗi runtime.
- Dữ liệu disposition không hợp lệ có thể raise validation khi tạo DispositionTraits.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.think_utils import describe_trait_level; print(describe_trait_level(4))"
uv run python -c "from cogmem_api.engine.search.think_utils import get_system_message; from cogmem_api.engine.response_models import DispositionTraits; print(get_system_message(DispositionTraits()))"
```
