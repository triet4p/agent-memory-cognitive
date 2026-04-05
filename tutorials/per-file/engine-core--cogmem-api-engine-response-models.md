# S19.3 Manual Tutorial - [cogmem_api/engine/response_models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/response_models.py)

## Purpose (Mục đích)
- Định nghĩa các dataclass cốt lõi dùng chung cho think/reflect/LLM metrics.
- Chuẩn hóa shape dữ liệu giữa các module engine.

## Source File
- [cogmem_api/engine/response_models.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/response_models.py)

## Symbol-by-symbol explanation
### DispositionTraits
- Dataclass biểu diễn bộ đặc tính disposition: skepticism, literalism, empathy.
- __post_init__ kiểm tra:
  - mọi trường phải là int,
  - giá trị nằm trong khoảng [1, 5].

### MemoryFact
- Dataclass đại diện một fact tối thiểu dùng để format evidence cho think/reflect.
- Trường chính: id, text, fact_type, context, occurred_start.

### TokenUsage
- Dataclass lưu số token input/output/total cho thao tác LLM.
- __add__ hỗ trợ cộng dồn usage giữa nhiều lần gọi LLM.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- [cogmem_api/engine/llm_wrapper.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/llm_wrapper.py) dùng TokenUsage để đóng gói metrics usage.
- Các pipeline think/reflect có thể dùng DispositionTraits và MemoryFact để chuẩn hóa dữ liệu.

### Outbound dependencies
- Chỉ phụ thuộc dataclasses và datetime từ Python standard library.

## Runtime implications/side effects
- Validation ở __post_init__ của DispositionTraits giúp fail-fast khi nhận giá trị sai kiểu/range.
- TokenUsage.__add__ cho phép tổng hợp chi phí token ở nhiều bước pipeline.

## Failure modes
- Truyền float/string vào DispositionTraits sẽ raise TypeError.
- Truyền int ngoài [1, 5] cho DispositionTraits sẽ raise ValueError.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.response_models import DispositionTraits; print(DispositionTraits(3,3,3))"
uv run python -c "from cogmem_api.engine.response_models import TokenUsage; a=TokenUsage(1,2,3); b=TokenUsage(4,5,9); print(a+b)"
uv run python -c "from cogmem_api.engine.response_models import MemoryFact; print(MemoryFact(id='1', text='x', fact_type='world'))"
```
