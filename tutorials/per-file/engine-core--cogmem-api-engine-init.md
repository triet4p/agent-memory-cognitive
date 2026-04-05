# S19.3 Manual Tutorial - cogmem_api/engine/__init__.py

## Purpose (Mục đích)
- Định nghĩa public surface của package engine.
- Re-export các symbol chính để caller import tập trung từ một điểm.
- Ẩn chi tiết cấu trúc thư mục con retain/reflect/memory_engine.

## Source File
- cogmem_api/engine/__init__.py

## Symbol-by-symbol explanation
### MemoryEngine
- Re-export lớp runtime core từ memory_engine.py.

### UnqualifiedTableError
- Re-export exception dùng cho kiểm tra SQL chưa qualify schema.

### fq_table
- Re-export helper tạo tên bảng đầy đủ schema.table.

### get_current_schema
- Re-export helper đọc schema theo context hiện hành.

### set_schema_context
- Re-export context manager đổi schema tạm thời theo task context.

### retain_batch
- Re-export entrypoint retain từ package retain.

### synthesize_lazy_reflect
- Re-export entrypoint reflect lazy synthesis từ package reflect.

### __all__
- Danh sách symbol public chính thức của package engine.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Các module runtime có thể import trực tiếp từ cogmem_api.engine thay vì truy cập sâu.

### Outbound dependencies
- cogmem_api/engine/memory_engine.py
- cogmem_api/engine/retain/__init__.py
- cogmem_api/engine/reflect/__init__.py

## Runtime implications/side effects
- Import cogmem_api.engine sẽ kéo theo import chuỗi các module được re-export.
- Nếu một module con lỗi import, package init sẽ lỗi theo.

## Failure modes
- ImportError do dependency thiếu ở module con (ví dụ retain/reflect/memory_engine).
- __all__ thiếu symbol có thể làm caller import * không thấy API kỳ vọng.

## Verify commands
```powershell
uv run python -c "import cogmem_api.engine as e; print(sorted(e.__all__))"
uv run python -c "from cogmem_api.engine import MemoryEngine, fq_table; print(MemoryEngine.__name__, fq_table('memory_units'))"
```
