# S19.2 Manual Tutorial - [cogmem_api/models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/models.py)

## Purpose (Mục đích)
- Định nghĩa toàn bộ schema ORM cho CogMem bằng SQLAlchemy.
- Mô tả ràng buộc dữ liệu, quan hệ bảng và chỉ mục phục vụ retain/recall.
- Cung cấp lớp context dùng cho xác thực/ủy quyền theo request.

## Source File
- [cogmem_api/models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/models.py)

## Symbol-by-symbol explanation
### RequestContext (dataclass)
- Mô tả ngữ cảnh thực thi request ở tầng ứng dụng.
- Trường quan trọng:
  - api_key/api_key_id/tenant_id cho xác thực.
  - internal và user_initiated để phân biệt tác vụ nền và tác vụ do người dùng kích hoạt.
  - allowed_bank_ids để giới hạn phạm vi truy cập bank.

### Base (AsyncAttrs, DeclarativeBase)
- Base class ORM dùng cho toàn bộ model.
- Kích hoạt đặc tính async ORM và metadata chung.

### Document
- Bảng documents (PK kép: id + bank_id).
- Lưu original_text, content_hash, metadata, created_at, updated_at.
- Quan hệ ngược tới MemoryUnit qua memory_units.
- Chỉ mục bank_id và content_hash để truy vấn nhanh theo tenant/tài liệu.

### MemoryUnit
- Bảng lõi lưu từng memory unit cấp câu.
- Trường chính:
  - id UUID, bank_id, document_id, text, raw_snippet.
  - embedding (pgvector), context, event_date/occurred_start/occurred_end/mentioned_at.
  - network_type, fact_type, confidence_score, metadata.
- Ràng buộc chính:
  - fact_type và network_type giới hạn ở world/experience/opinion/habit/intention/action_effect.
  - opinion bắt buộc có confidence_score; các loại khác phải NULL.
  - confidence_score trong khoảng [0.0, 1.0].
- Chỉ mục chính:
  - theo bank/date/type/network cho recall theo thời gian và loại fact.
  - chỉ mục HNSW trên embedding cho semantic retrieval.

### Entity
- Bảng entities đã resolve theo canonical_name và bank_id.
- Lưu metadata, first_seen/last_seen, mention_count.
- Có quan hệ tới UnitEntity, MemoryLink và EntityCooccurrence.

### UnitEntity
- Bảng liên kết nhiều-nhiều giữa MemoryUnit và Entity.
- PK kép (unit_id, entity_id).

### EntityCooccurrence
- Cache vật hóa tần suất đồng xuất hiện của cặp entity.
- Ràng buộc thứ tự entity_id_1 < entity_id_2 để tránh trùng cặp đảo chiều.

### MemoryLink
- Bảng cạnh giữa memory units.
- PK gồm from_unit_id, to_unit_id, link_type, entity_id.
- Hỗ trợ transition_type cho link_type = transition.
- Ràng buộc chính:
  - link_type thuộc tập temporal/semantic/entity/causal/s_r_link/a_o_causal/transition.
  - transition_type chỉ hợp lệ cho link_type transition.
  - weight trong [0.0, 1.0].

### Bank
- Bảng profile theo bank_id.
- Lưu disposition (JSON) và background text.
- Là nguồn cấu hình nền cho phản hồi/reflect theo bank.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Tầng engine (retain/search/reflect) sử dụng model này cho CRUD và truy vấn.
- Migration Alembic đồng bộ ràng buộc với schema ORM.

### Outbound dependencies
- [cogmem_api/config.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/config.py) cung cấp EMBEDDING_DIMENSION cho Vector.
- SQLAlchemy, pgvector, PostgreSQL JSONB/TIMESTAMP/UUID là nền tảng schema.

## Runtime implications/side effects
- Chỉ mục HNSW embedding giúp recall semantic nhanh nhưng tăng chi phí build/indexing.
- Ràng buộc check ở DB layer ngăn dữ liệu sai semantic đi vào graph.
- Quan hệ cascade delete làm sạch dữ liệu liên quan khi xóa memory unit/entity.

## Failure modes
- Không cài pgvector extension sẽ lỗi khi tạo cột/vector index.
- Sai dimension embedding giữa runtime và schema có thể gây lỗi insert/query.
- Dữ liệu không thỏa check constraint sẽ fail ở commit transaction.

## Verify commands
```powershell
uv run python -c "from cogmem_api.models import MemoryUnit, MemoryLink, Bank; print(MemoryUnit.__tablename__, MemoryLink.__tablename__, Bank.__tablename__)"
uv run python -c "from cogmem_api.models import RequestContext; print(RequestContext())"
uv run python -c "from cogmem_api.models import Base; print(Base.metadata.tables.keys())"
```
