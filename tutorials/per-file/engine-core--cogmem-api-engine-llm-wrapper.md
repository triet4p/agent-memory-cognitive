# S19.3 Manual Tutorial - cogmem_api/engine/llm_wrapper.py

## Purpose (Mục đích)
- Cung cấp wrapper gọi LLM theo chuẩn OpenAI-compatible cho retain/search.
- Chuẩn hóa parse JSON output và token usage.
- Xử lý an toàn dữ liệu output khi có control characters hoặc fenced block.

## Source File
- cogmem_api/engine/llm_wrapper.py

## Symbol-by-symbol explanation
### sanitize_llm_output(text)
- Loại bỏ control/surrogate characters có thể làm hỏng JSON parsing.

### OutputTooLongError
- Exception riêng cho trường hợp finish_reason = length.

### parse_llm_json(raw)
- Parse JSON từ output text.
- Hỗ trợ markdown fenced code block.
- Nếu parse lần đầu lỗi, thay control chars bằng khoảng trắng rồi parse lại.

### LLMConfig (dataclass)
- Cấu hình caller cho endpoint chat completions.
- Trường chính: provider, model, api_key, base_url, timeout.

### LLMConfig.call(...)
- Dựng payload model/messages/temperature/max_completion_tokens.
- Nếu response_format có model_json_schema thì yêu cầu JSON schema output.
- Gọi _post_chat_completions và map usage sang TokenUsage.
- Parse choices:
  - không có choice -> trả chuỗi rỗng,
  - finish_reason=length -> raise OutputTooLongError,
  - có response_format -> parse JSON + validate (trừ khi skip_validation).
- Hỗ trợ return_usage để trả tuple (parsed, usage).

### LLMConfig._post_chat_completions(payload)
- Chuẩn hóa endpoint từ base_url:
  - .../chat/completions giữ nguyên,
  - .../v1 nối /chat/completions,
  - còn lại nối /v1/chat/completions.
- Gắn Authorization header nếu có api_key.
- Gửi POST bằng httpx.AsyncClient và trả JSON body.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- cogmem_api/engine/memory_engine.py tạo LLMConfig cho retain path.
- Các helper retain/search có thể gọi LLMConfig.call để lấy structured output.

### Outbound dependencies
- cogmem_api/engine/response_models.py: TokenUsage.
- httpx cho HTTP client, json/re cho parsing và cleanup.

## Runtime implications/side effects
- Wrapper dùng HTTP call trực tiếp mỗi lần gọi, độ trễ phụ thuộc mạng/provider.
- skip_validation=True cho phép tốc độ cao hơn nhưng tăng rủi ro payload sai schema.
- sanitize + parse fallback giúp tăng độ bền trước output nhiễu.

## Failure modes
- base_url thiếu sẽ raise ValueError trước khi gọi HTTP.
- HTTP status lỗi sẽ raise từ response.raise_for_status().
- JSON output không hợp lệ sau cleanup vẫn gây JSONDecodeError.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.llm_wrapper import parse_llm_json; print(parse_llm_json('{\"a\":1}')['a'])"
uv run python -c "from cogmem_api.engine.llm_wrapper import sanitize_llm_output; print(sanitize_llm_output('abc\x00def'))"
uv run python -c "from cogmem_api.engine.llm_wrapper import LLMConfig; print(LLMConfig(model='x').model)"
```
