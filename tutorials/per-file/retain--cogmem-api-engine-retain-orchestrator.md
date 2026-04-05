# S19.4 Manual Tutorial - [cogmem_api/engine/retain/orchestrator.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/orchestrator.py)

## Purpose (Mục đích)
- Điều phối end-to-end retain pipeline theo batch.
- Chuẩn hóa input, extraction, embedding, storage, entity/link creation trong một transaction flow.
- Trả kết quả unit_ids theo từng nội dung đầu vào.

## Source File
- [cogmem_api/engine/retain/orchestrator.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/orchestrator.py)

## Symbol-by-symbol explanation
### utcnow()
- Helper trả datetime UTC aware dùng làm fallback event_date.

### parse_datetime_flexible(value)
- Parse datetime từ datetime hoặc ISO string; đảm bảo timezone-aware.

### _maybe_transaction(conn)
- Context manager dùng transaction nếu connection có hỗ trợ.

### _map_results_to_contents(...)
- Map unit_ids phẳng thành danh sách theo content_index ban đầu.

### retain_batch(...)
- Hàm điều phối chính:
  - chuẩn hóa contents_dicts thành RetainContent,
  - gọi fact_extraction.extract_facts_from_contents,
  - áp fact_type_override nếu có,
  - tạo embeddings và ProcessedFact,
  - ghi DB trong _db_write_work qua retry_with_backoff,
  - tạo links temporal/semantic/entity/s_r/action_effect/transition/causal,
  - trả unit_ids theo từng content + TokenUsage.

### _db_write_work() (closure nội bộ)
- Nơi thực thi transaction:
  - ensure bank,
  - lưu chunk (nếu có),
  - insert facts,
  - process entities,
  - tạo links,
  - gọi outbox_callback nếu truyền vào.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- [cogmem_api/engine/memory_engine.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/memory_engine.py) gọi retain_batch trong retain_batch_async.

### Outbound dependencies
- fact_extraction, embedding_processing, fact_storage, entity_processing, link_creation, chunk_storage.
- db_utils.acquire_with_retry và retry_with_backoff.

## Runtime implications/side effects
- Một batch retain có thể tạo nhiều bản ghi và nhiều edge trong cùng transaction.
- Retry ở mức _db_write_work giúp chống lỗi DB tạm thời nhưng có thể tăng độ trễ.

## Failure modes
- Extraction rỗng dẫn đến trả danh sách rỗng theo từng content.
- Lỗi DB trong transaction làm toàn batch fail và retry.
- Sai định dạng event_date có thể ném lỗi khi chuẩn hóa.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.retain.orchestrator import parse_datetime_flexible; print(parse_datetime_flexible('2026-04-05T10:00:00Z'))"
uv run python -c "import inspect; from cogmem_api.engine.retain.orchestrator import retain_batch; print(inspect.iscoroutinefunction(retain_batch))"
```
