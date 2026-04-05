# S19.1 Manual Tutorial - cogmem_api/__init__.py

## Purpose (Mục đích)
- Định nghĩa bề mặt package tối thiểu cho CogMem API.
- Xuất đối tượng chính là MemoryEngine để module ngoài có thể import từ package root.
- Cố định phiên bản package ở mức runtime metadata.

## Source File
- cogmem_api/__init__.py

## Symbol-by-symbol explanation
### Module docstring
- Giá trị: CogMem API package.
- Vai trò: mô tả phạm vi module khi đọc bằng tooling hoặc introspection.

### MemoryEngine
- Loại: imported symbol (từ cogmem_api.engine.memory_engine).
- Vai trò: đưa lớp lõi engine lên package root để import gọn hơn.

### __all__
- Giá trị: ["MemoryEngine"].
- Vai trò: giới hạn symbol được export khi dùng from cogmem_api import *.

### __version__
- Giá trị: 0.1.0.
- Vai trò: metadata phiên bản package phục vụ kiểm tra tương thích runtime.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- cogmem_api/server.py import MemoryEngine từ package root.

### Outbound dependencies
- cogmem_api/engine/memory_engine.py: nguồn định nghĩa lớp MemoryEngine.

## Runtime implications/side effects
- Import cogmem_api sẽ trigger import dây chuyền tới memory_engine.
- Nếu dependency trong memory_engine lỗi, import package root cũng sẽ lỗi theo.

## Failure modes
- ModuleNotFoundError/ImportError nếu memory_engine hoặc dependency của nó không khả dụng.
- Sai phiên bản __version__ có thể gây nhầm lẫn trong quá trình phát hành.

## Verify commands
```powershell
uv run python -c "import cogmem_api; print(cogmem_api.__version__); print(cogmem_api.__all__)"
uv run python -c "from cogmem_api import MemoryEngine; print(MemoryEngine.__name__)"
```
