# S19.4 Manual Tutorial - cogmem_api/engine/retain/types.py

## Purpose (Mục đích)
- Định nghĩa toàn bộ kiểu dữ liệu và hàm chuẩn hóa cho retain pipeline.
- Chuẩn hóa fact_type, relation strength, intention status và metadata edge intent.
- Cung cấp dataclass cho dữ liệu trước và sau bước embedding/storage.

## Source File
- cogmem_api/engine/retain/types.py

## Symbol-by-symbol explanation
### COGMEM_FACT_TYPES
- Bộ fact_type hợp lệ: world, experience, opinion, habit, intention, action_effect.

### ALLOWED_INTENTION_STATUSES
- Bộ trạng thái intention hợp lệ: planning, fulfilled, abandoned.

### TRANSITION_EDGE_RULES
- Quy tắc transition typed edge theo cặp source_fact_type -> target_fact_type.

### coerce_fact_type(raw)
- Chuẩn hóa fact_type đầu vào về tập CogMem; map assistant -> experience, observation -> world.

### clamp_relation_strength(value, default)
- Ép relation strength vào khoảng [0.0, 1.0] với parse phòng thủ.

### normalize_intention_status(value)
- Chuẩn hóa intention status, trả None nếu không hợp lệ.

### sanitize_raw_snippet(raw_snippet, fact_text)
- Bảo đảm luôn có raw snippet không rỗng; fallback về fact_text.

### RetainFactSeed / RetainContentDict
- TypedDict mô tả payload đầu vào retain và payload facts seeded dùng cho test/smoke.

### RetainContent
- Dataclass normalize một item retain; from_dict xử lý event_date linh hoạt datetime/ISO string.

### ChunkMetadata
- Dataclass metadata cho chunk extraction trace và mapping chunk_id.

### CausalRelation / ActionEffectRelation / TransitionRelation
- Dataclass cho ba loại quan hệ link được trích xuất ở bước retain.

### normalize_fact_metadata(...)
- Chuẩn hóa metadata cuối cùng:
  - ghi edge_intent,
  - đánh dấu raw_snippet_present,
  - bảo đảm intention_status mặc định planning,
  - chuẩn hóa confidence/devalue_sensitive cho action_effect.

### ExtractedFact
- Dataclass dữ liệu sau extraction, trước embedding.

### ProcessedFact
- Dataclass dữ liệu sau embedding, sẵn sàng lưu DB.
- from_extracted_fact() chuẩn hóa fact_type, raw_snippet, relations, metadata.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- fact_extraction.py tạo ExtractedFact và relation dataclass.
- orchestrator.py tạo ProcessedFact từ ExtractedFact.
- fact_storage.py dùng normalize_fact_metadata và sanitize_raw_snippet.
- link_creation.py dùng TRANSITION_EDGE_RULES và relation list.

### Outbound dependencies
- Python dataclasses, datetime và typing.

## Runtime implications/side effects
- Chuẩn hóa dữ liệu ở đây ảnh hưởng trực tiếp chất lượng consistency của retain và retrieval downstream.
- ProcessedFact.from_extracted_fact là điểm then chốt để chống dữ liệu bẩn trước khi ghi DB.

## Failure modes
- event_date sai định dạng trong RetainContent.from_dict gây TypeError/ValueError.
- transition_type trống hoặc không hợp lệ bị lọc bỏ ở bước chuẩn hóa.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.retain.types import coerce_fact_type; print(coerce_fact_type('assistant'), coerce_fact_type('observation'))"
uv run python -c "from cogmem_api.engine.retain.types import clamp_relation_strength; print(clamp_relation_strength(1.5), clamp_relation_strength(-1))"
uv run python -c "from cogmem_api.engine.retain.types import RetainContent; print(RetainContent.from_dict({'content':'x','event_date':'2026-04-05T10:00:00Z'}).event_date)"
```
