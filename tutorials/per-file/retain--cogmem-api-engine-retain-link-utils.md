# S19.4 Manual Tutorial - [cogmem_api/engine/retain/link_utils.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_utils.py)

## Purpose (Mục đích)
- Cung cấp hàm tiện ích để build và persist links cho retain pipeline.
- Đóng gói tính toán cosine similarity và tạo temporal/semantic links.
- Hỗ trợ insert links qua hook hoặc SQL fallback.

## Source File
- [cogmem_api/engine/retain/link_utils.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_utils.py)

## Symbol-by-symbol explanation
### LinkRecord
- Kiểu tuple chuẩn cho một link:
  - from_unit_id, to_unit_id, link_type, transition_type, entity_id, weight.

### _PLACEHOLDER_ENTITY_ID
- UUID placeholder dùng khi chèn memory_links mà entity_id không có.

### cosine_similarity(vec_a, vec_b)
- Tính cosine similarity có kiểm tra độ dài vector và norm 0.

### build_temporal_links(unit_dates, window_hours)
- Tạo temporal links hai chiều cho cặp unit có chênh lệch thời gian trong cửa sổ.
- Weight giảm dần theo độ lệch thời gian.

### build_semantic_links(unit_ids, embeddings, threshold)
- Tạo semantic links có hướng cho cặp unit vượt ngưỡng similarity.

### insert_links(conn, links)
- Nếu conn có insert_memory_links thì gọi hook.
- Nếu không, fallback SQL:
  - đảm bảo placeholder entity tồn tại,
  - insert nhiều dòng vào memory_links bằng executemany.

### fetch_event_dates(conn, unit_ids)
- Lấy event_date theo unit_ids qua hook get_unit_event_dates hoặc query SQL.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- link_creation.py dùng build_*/insert_links/fetch_event_dates.
- entity_processing.py dùng insert_links để ghi entity links.

### Outbound dependencies
- memory_engine.fq_table để qualify bảng.
- math/datetime cho tính toán similarity và cửa sổ thời gian.

## Runtime implications/side effects
- insert_links fallback sẽ tạo placeholder entity toàn cục nếu chưa có.
- build_semantic_links là O(n^2) theo số unit trong batch.

## Failure modes
- Vector không cùng kích thước làm cosine_similarity trả 0 và mất semantic links.
- DB lỗi trong executemany làm mất toàn bộ lô links nếu transaction rollback.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.retain.link_utils import cosine_similarity; print(cosine_similarity([1,0],[1,0]))"
uv run python -c "from cogmem_api.engine.retain.link_utils import build_semantic_links; print(build_semantic_links(['a','b'], [[1,0],[1,0]], threshold=0.5))"
```
