# S19.4 Manual Tutorial - cogmem_api/engine/retain/fact_extraction.py

## Purpose (Mục đích)
- Trích xuất facts từ nội dung đầu vào cho retain pipeline.
- Hỗ trợ 3 đường: seeded facts, LLM extraction theo prompt mode, heuristic fallback.
- Chuẩn hóa entities, relations (causal/action_effect/transition) và metadata liên quan.

## Source File
- cogmem_api/engine/retain/fact_extraction.py

## Symbol-by-symbol explanation
### _HABIT_PATTERNS, _ACTION_EFFECT_PATTERNS
- Regex heuristic để suy luận habit/action_effect khi thiếu nhãn rõ ràng.

### _SUPPORTED_TRANSITION_TYPES, _ALLOWED_MODES
- Bộ transition type hợp lệ và extraction mode hợp lệ.

### _BASE_PROMPT + _CONCISE_MODE/_CUSTOM_MODE/_VERBATIM_MODE/_VERBOSE_MODE
- Template prompt phục vụ LLM extraction path.

### _parse_datetime, _safe_datetime
- Chuẩn hóa datetime phòng thủ cho các trường thời gian.

### _extract_entities / _extract_entities_from_text
- Trích xuất entities từ payload hoặc heuristic theo chữ viết hoa.

### _infer_fact_type(segment)
- Suy luận fact_type heuristic khi payload không cung cấp.

### _extract_causal_relations/_extract_action_effect_relations/_extract_transition_relations
- Parse và chuẩn hóa relation list từ output LLM/seeded payload.

### _parse_action_effect_triplet(text)
- Tách precondition/action/outcome từ câu tự nhiên bằng regex.

### _chunk_content(text, max_chars)
- Chia nội dung thành nhiều chunk theo giới hạn ký tự để gọi LLM an toàn.

### _build_prompt(config)
- Dựng prompt theo retain_extraction_mode + mission/custom instructions.

### _build_user_message(...)
- Dựng user message cho từng chunk, kèm event date/context/metadata.

### _call_llm_chunk(...)
- Gọi llm_config.call cho một chunk; parse response thành list facts + TokenUsage.
- Xử lý OutputTooLongError và fallback cho fake llm caller.

### _normalize_llm_facts(...)
- Chuẩn hóa raw facts từ LLM thành ExtractedFact.
- Bổ sung metadata action_effect/intention và relations.

### _extract_seeded_facts(...)
- Đường seeded facts dùng cho test/smoke: không gọi LLM.

### _extract_fallback_facts(...)
- Heuristic fallback khi LLM không trả facts.

### _extract_facts_with_llm(...)
- Điều phối extraction theo từng chunk và cộng dồn usage.

### extract_facts_from_contents(...)
- Hàm public chính:
  - ưu tiên seeded,
  - rồi LLM extraction,
  - cuối cùng fallback heuristic.

### Symbol inventory bổ sung (full names)
- _first_non_empty, _normalized_optional_text, _fallback_fact_splits

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- orchestrator.py gọi extract_facts_from_contents cho mọi batch retain.

### Outbound dependencies
- llm_wrapper.py (OutputTooLongError, parse_llm_json).
- response_models.py (TokenUsage).
- types.py (dataclass và helper chuẩn hóa).

## Runtime implications/side effects
- Lựa chọn mode ảnh hưởng trực tiếp chất lượng và khối lượng facts.
- Fallback heuristic đảm bảo pipeline không chết khi LLM lỗi nhưng chất lượng có thể thấp hơn.

## Failure modes
- JSON output từ LLM không parse được -> rơi về fallback.
- chunk_size hoặc max_completion_tokens cấu hình không hợp lý có thể giảm chất lượng extraction.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.retain.fact_extraction import _infer_fact_type; print(_infer_fact_type('I always check email before standup'))"
uv run python -c "from cogmem_api.engine.retain.fact_extraction import _parse_action_effect_triplet; print(_parse_action_effect_triplet('If latency is high, switch to int8 so response gets faster'))"
```

