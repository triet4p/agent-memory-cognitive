# S19.6 Manual Tutorial - [cogmem_api/engine/reflect/__init__.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/__init__.py)

## Purpose
- Đóng vai trò barrel module cho reflect stack, gom các symbol public để import thuận tiện từ một điểm.
- Khóa public API của nhánh reflect qua __all__.

## Source File
- [cogmem_api/engine/reflect/__init__.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/__init__.py)

## Symbol-by-symbol explanation
### Module docstring
- Mô tả ngắn mục tiêu của reflect module: lazy synthesis cho CogMem.

### from .agent import synthesize_lazy_reflect
- Export hàm orchestration chính để tổng hợp câu trả lời từ evidence đã retrieve.

### from .models import ReflectEvidence, ReflectSynthesisResult
- Export hai model typed cho input/output của reflect pipeline.

### from .prompts import SYSTEM_PROMPT, build_lazy_synthesis_prompt
- Export prompt system và builder prompt theo evidence.

### from .tools import group_evidence_by_network, prepare_lazy_evidence, to_reflect_evidence
- Export bộ helper chuyển đổi dữ liệu retrieval sang evidence reflect và nhóm theo network.

### __all__
- Danh sách API công khai; giúp import * chỉ lấy đúng symbol hỗ trợ cho reflect.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py) có thể import trực tiếp từ package reflect để gọi synthesize_lazy_reflect.
- Các test hoặc script debug reflect thường import từ package-level thay vì import file con.

### Outbound dependencies
- [cogmem_api/engine/reflect/agent.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/agent.py)
- [cogmem_api/engine/reflect/models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/models.py)
- [cogmem_api/engine/reflect/prompts.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/prompts.py)
- [cogmem_api/engine/reflect/tools.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/reflect/tools.py)

## Runtime implications/side effects
- Không tạo side effect runtime đáng kể; chủ yếu định nghĩa namespace export.
- Việc khóa __all__ giúp giảm nguy cơ dùng nhầm symbol private khi tích hợp.

## Failure modes
- Nếu một symbol bên dưới bị rename/xóa mà không cập nhật __init__, import package reflect sẽ lỗi ImportError.
- Mismatch giữa __all__ và import thực tế có thể gây khó hiểu cho người dùng API reflect.

## Verify commands
```powershell
uv run python -c "import cogmem_api.engine.reflect as r; print(sorted(r.__all__))"
uv run python -c "from cogmem_api.engine.reflect import synthesize_lazy_reflect, ReflectSynthesisResult; print(callable(synthesize_lazy_reflect), ReflectSynthesisResult.__name__)"
```
