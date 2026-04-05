# S19.2 Manual Tutorial - cogmem_api/alembic/versions/20260330_0001_t1_2_schema_extensions.py

## Purpose (Mục đích)
- Áp dụng mở rộng schema T1.2 cho CogMem theo contribution C1.
- Bổ sung network_type và raw_snippet vào memory_units.
- Mở rộng memory_links với transition_type và bộ ràng buộc transition.

## Source File
- cogmem_api/alembic/versions/20260330_0001_t1_2_schema_extensions.py

## Symbol-by-symbol explanation
### revision, down_revision, branch_labels, depends_on
- Metadata chuẩn của Alembic revision.
- down_revision = None cho thấy đây là base revision của nhánh migration hiện tại.

### upgrade()
- Bổ sung cột mới:
  - memory_units.raw_snippet (Text, nullable=True).
  - memory_units.network_type (Text, nullable=False, default world).
  - memory_links.transition_type (Text, nullable=True).
- Cập nhật check constraints:
  - memory_units_fact_type_check: mở rộng tập fact_type theo CogMem.
  - memory_units_network_type_check: ràng buộc network_type cùng tập giá trị.
  - memory_links_link_type_check: dùng link_type mới (causal, s_r_link, a_o_causal, transition).
  - memory_links_transition_type_values_check: whitelist transition_type.
  - memory_links_transition_type_usage_check: chỉ cho phép transition_type khi link_type = transition.
- Tạo index mới:
  - idx_memory_units_network_type
  - idx_memory_units_bank_network_type
  - idx_memory_units_bank_network_date
  - idx_memory_links_transition_type

### downgrade()
- Hoàn tác toàn bộ thay đổi của upgrade theo thứ tự an toàn:
  - xóa index/constraints mới,
  - khôi phục check constraint link_type cũ,
  - xóa cột transition_type,
  - xóa index network_type,
  - khôi phục fact_type cũ có observation,
  - xóa cột network_type và raw_snippet.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Alembic runtime gọi upgrade/downgrade khi migrate schema.

### Outbound dependencies
- Alembic op API: add_column, drop_constraint, create_check_constraint, create_index, drop_index.
- SQLAlchemy sa.Column/sa.Text để mô tả kiểu cột.
- Tương thích mục tiêu với ORM constraints trong cogmem_api/models.py.

## Runtime implications/side effects
- Sau upgrade, dữ liệu mới có thể lưu raw_snippet để phục vụ recall chi tiết.
- network_type và transition_type cho phép retrieval/filter theo semantics CogMem mới.
- Các index mới cải thiện truy vấn theo bank + network + event_date, đổi lại chi phí ghi/index maintenance tăng.

## Failure modes
- Nếu dữ liệu cũ vi phạm check constraints mới, migration upgrade có thể fail.
- Nếu migration chạy lại trên DB đã có cấu trúc tương tự, có thể lỗi trùng index/constraint.
- Downgrade làm mất dữ liệu ở cột mới (raw_snippet/network_type/transition_type).

## Verify commands
```powershell
uv run python -c "import cogmem_api.alembic.versions.20260330_0001_t1_2_schema_extensions as m; print(m.revision, m.down_revision)"
uv run python -c "import inspect, importlib; m=importlib.import_module('cogmem_api.alembic.versions.20260330_0001_t1_2_schema_extensions'); print([name for name, _ in inspect.getmembers(m, inspect.isfunction) if name in ('upgrade','downgrade')])"
```
