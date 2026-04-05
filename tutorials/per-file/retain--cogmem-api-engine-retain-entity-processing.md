# S19.4 Manual Tutorial - [cogmem_api/engine/retain/entity_processing.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/entity_processing.py)

## Purpose (Mục đích)
- Xử lý entity theo batch trong retain pipeline.
- Tạo ánh xạ unit -> entity và sinh entity links giữa các memory units.
- Lưu unit-entity association và memory_links kiểu entity.

## Source File
- [cogmem_api/engine/retain/entity_processing.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/entity_processing.py)

## Symbol-by-symbol explanation
### _normalize_entity_name(entity)
- Chuẩn hóa tên entity về lowercase để đồng nhất khóa định danh.

### _resolve_entity_id(bank_id, entity_name)
- Sinh deterministic UUIDv5 theo bank_id + entity_name normalized.

### process_entities_batch(...)
- Merge entities từ facts và user_entities_per_content.
- Tạo unit_entity_pairs để lưu liên kết unit-entity.
- Lập entity_index để tạo cặp link hai chiều giữa các unit có chung entity.
- Trả danh sách EntityLink để bước sau insert vào memory_links.

### insert_entity_links_batch(conn, entity_links)
- Chuyển EntityLink thành LinkRecord và gọi link_utils.insert_links.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- orchestrator.py gọi process_entities_batch và insert_entity_links_batch trong transaction retain.

### Outbound dependencies
- retain/link_utils.py để persist links.
- retain/types.py (EntityLink, ProcessedFact).

## Runtime implications/side effects
- Sinh link hai chiều cho cùng entity làm tăng số edge nhanh theo số unit trong batch.
- Dùng UUIDv5 giúp id entity ổn định giữa nhiều lần retain với cùng bank+entity.

## Failure modes
- Dữ liệu entity rỗng hoặc sai định dạng làm giảm liên kết entity-based retrieval.
- Nếu conn không hỗ trợ insert_unit_entities và không có nhánh SQL thay thế, association có thể không được lưu đầy đủ.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.retain.entity_processing import _resolve_entity_id; print(_resolve_entity_id('b1','Alice'))"
uv run python -c "import inspect; from cogmem_api.engine.retain.entity_processing import process_entities_batch; print(inspect.iscoroutinefunction(process_entities_batch))"
```
