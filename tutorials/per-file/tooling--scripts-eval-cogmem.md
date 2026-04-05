# S19.6 Manual Tutorial - scripts/eval_cogmem.py

## Purpose
- Cung cấp harness đánh giá T6.3 cho CogMem: recall-only và full end-to-end có chấm điểm bằng judge LLM.
- Hỗ trợ ablation profiles E1..E7 để so sánh đóng góp của network và thuật toán retrieval.

## Source File
- scripts/eval_cogmem.py

## Symbol-by-symbol explanation
### EvalLLMConfig
- Dataclass cấu hình LLM cho bước generation/judge: provider, model, api_key, base_url, timeout, max_completion_tokens.

### AblationProfile
- Dataclass mô tả profile ablation: networks bật, fact_types recall, cờ adaptive router, cờ SUM activation.

### ABLATION_PROFILES
- Bảng profile E1..E7, từ baseline rebuilt tới full CogMem.

### SHORT_DIALOGUE_FIXTURE
- Fixture ngắn để smoke đánh giá nhanh gồm turns + questions + expected keywords + gold answers.

### _env_first, _to_float, _to_int
- Helper parse env và ép kiểu an toàn cho config.

### _normalize_text, _build_chat_url
- Chuẩn hóa text cho metric keyword và chuẩn hóa endpoint chat completions.

### resolve_eval_llm_config()
- Đọc config LLM từ env với fallback hợp lý.

### resolve_api_base_url(cli_value=None)
- Chọn base URL API CogMem từ CLI hoặc env.

### post_json(url, payload, timeout_seconds)
- HTTP helper POST JSON với requests.

### call_openai_chat(llm_config, messages, max_completion_tokens=None)
- Gọi endpoint chat completions theo chuẩn OpenAI-compatible.

### get_fixture(name)
- Trả fixture theo tên (hiện hỗ trợ short).

### build_recall_payload(profile, query)
- Dựng payload recall dựa trên fact types của profile.

### _keyword_recall_metrics(expected_keywords, recall_text)
- Tính coverage keyword và strict hit.

### _safe_parse_json(text)
- Parse output judge LLM về dict JSON an toàn.

### retain_fixture(...)
- Đẩy turns của fixture vào API memories để tạo dữ liệu trước recall/full.

### run_recall_only_pipeline(...)
- Chạy pipeline recall, tính metric keyword coverage/strict accuracy theo từng câu hỏi.

### _build_generation_prompt(query, recall_results)
- Dựng prompt generation từ recall evidence.

### _judge_answer(...)
- Chấm predicted answer so với gold bằng LLM judge, yêu cầu output JSON strict.

### run_full_pipeline(...)
- Chạy recall + generation + judge, trả metric recall và metric judge.

### run_pipeline(...)
- Router chọn recall hoặc full theo tham số pipeline.

### save_eval_result(result, output_dir)
- Ghi JSON output theo tên <profile>_<pipeline>_<timestamp>.json.

### parse_args(), main()
- Parse CLI, tạo bank_id nếu chưa có, chạy 1 hoặc 2 pipeline và in đường dẫn file kết quả.

### Symbol inventory bổ sung (full names)
- JsonDict

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- scripts/ablation_runner.py gọi run_pipeline, ABLATION_PROFILES và resolve_api_base_url.
- Người vận hành gọi trực tiếp script để benchmark từng profile.

### Outbound dependencies
- requests cho API calls.
- API CogMem: /v1/default/banks/{bank_id}/memories và /memories/recall.
- Endpoint OpenAI-compatible cho generation/judge.

## Runtime implications/side effects
- Có thể tạo nhiều request và tốn chi phí LLM (đặc biệt pipeline full).
- Nếu skip_retain=False, script sẽ ghi dữ liệu vào bank tương ứng.
- File kết quả eval được ghi vào logs/eval (mặc định).

## Failure modes
- API unavailable/timeout gây thất bại toàn pipeline.
- Judge output không phải JSON sẽ bị fallback score=0.
- Env config sai (base_url/model/api_key) khiến gọi LLM lỗi HTTP.

## Verify commands
```powershell
uv run python -c "from scripts.eval_cogmem import ABLATION_PROFILES, run_pipeline; print(sorted(ABLATION_PROFILES.keys()), callable(run_pipeline))"
uv run python scripts/eval_cogmem.py --pipeline recall --profile E1 --fixture short --skip-retain --api-timeout 5 --output-dir logs/eval
```

