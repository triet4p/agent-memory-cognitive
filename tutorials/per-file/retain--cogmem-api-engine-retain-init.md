# S19.4 Manual Tutorial - [cogmem_api/engine/retain/__init__.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/__init__.py)

## Purpose (Mục đích)
- Định nghĩa public surface cho retain pipeline của CogMem.
- Re-export các kiểu dữ liệu cốt lõi và hàm retain_batch.
- Gom các module con để caller import theo một điểm duy nhất.

## Source File
- [cogmem_api/engine/retain/__init__.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/__init__.py)

## Symbol-by-symbol explanation
### chunk_storage, embedding_processing, entity_processing, fact_extraction, fact_storage, link_creation
- Import module-level để expose trực tiếp qua package retain.

### retain_batch
- Re-export từ orchestrator.py, là entrypoint chính cho luồng retain.

### COGMEM_FACT_TYPES và các dataclass quan trọng
- Re-export từ types.py để đồng bộ contract dữ liệu giữa các bước retain.

### __all__
- Danh sách symbol công khai được hỗ trợ chính thức của package retain.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py) gọi retain_batch qua orchestrator.

### Outbound dependencies
- Toàn bộ module con trong thư mục retain và file types.py.

## Runtime implications/side effects
- Import package retain sẽ nạp các module con, giúp caller có API tập trung nhưng tăng footprint import.

## Failure modes
- Lỗi import ở một module con sẽ làm import retain package thất bại.

## Verify commands
```powershell
uv run python -c "import cogmem_api.engine.retain as r; print('retain_batch' in r.__all__)"
uv run python -c "from cogmem_api.engine.retain import COGMEM_FACT_TYPES; print(COGMEM_FACT_TYPES)"
```
