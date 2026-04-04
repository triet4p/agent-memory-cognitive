# Engine Core Services Modules

## Purpose
- Tài liệu hóa lõi điều phối runtime của engine: schema safety, DB retry, retain/recall orchestration.
- Làm rõ boundary giữa service orchestration và các pipeline con (retain/search/reflect).

## Inputs
- Runtime config đã parse.
- DB URL + schema context.
- Retain payloads và recall queries từ API layer.

## Outputs
- Kết quả retain theo từng content item.
- Kết quả recall đã rerank + trace (nếu bật).
- Health status cho runtime probes.

## Top-down level
- Module

## Prerequisites
- `tutorials/README.md`
- `tutorials/modules/runtime-and-api.md`
- `tutorials/modules/retain-pipeline.md`
- `tutorials/modules/search-pipeline.md`

## Module responsibility
- `cogmem_api/engine/__init__.py`
  - Trách nhiệm: export API public của engine package (`MemoryEngine`, `retain_batch`, `synthesize_lazy_reflect`).
- `cogmem_api/engine/memory_engine.py`
  - Trách nhiệm: lifecycle engine và cổng runtime cho retain/recall.
  - Inbound: API routes gọi `retain_batch_async`, `recall_async`, `health_check`.
  - Outbound:
    - Retain: `engine.retain.orchestrator.retain_batch`
    - Recall: `engine.search.retrieve_all_fact_types_parallel`, `fuse_parallel_results`, `CrossEncoderReranker`
    - Fallback: `_fallback_recall_from_conn`
  - Data contracts:
    - `recall_async` trả dict có `results` và `trace`.
    - `retain_batch_async` trả `unit_ids` theo content index.
  - Error boundaries:
    - Runtime chưa initialize/pool chưa có -> `RuntimeError`.
    - Retrieval lỗi bất kỳ -> fallback lexical scan.
- `cogmem_api/engine/db_utils.py`
  - Trách nhiệm: retry policy cho DB operation và pool acquire.
  - Error boundary: backoff + retry hữu hạn cho transient DB errors.
- `cogmem_api/engine/response_models.py`
  - Trách nhiệm: typed models dùng chung (`DispositionTraits`, `MemoryFact`, `TokenUsage`).
  - Outbound: retain/reflect/search helpers dùng chung model contract.

## Function inventory (public/private)
- Public functions/classes:
  - `cogmem_api/engine/memory_engine.py`: `MemoryEngine`, `UnqualifiedTableError`, `get_current_schema`, `set_schema_context`, `fq_table`, `validate_sql_schema`
  - `cogmem_api/engine/db_utils.py`: `retry_with_backoff`, `acquire_with_retry`
  - `cogmem_api/engine/response_models.py`: `DispositionTraits`, `MemoryFact`, `TokenUsage`
- Private/internal helpers:
  - `cogmem_api/engine/memory_engine.py`: `_bootstrap_schema_objects`, `_initialize_embeddings_model`, `_build_retain_llm_config`, `_format_date`, `_fallback_recall_from_conn`

## Failure modes
- SQL query không qualify schema -> `UnqualifiedTableError`.
- Pool đóng hoặc DB down -> health report `unhealthy`.
- Provider embeddings lỗi init -> fallback deterministic embeddings.
- Recall path lỗi graph/search/rerank -> degrade sang lexical fallback.

## Verify commands
- `uv run python tests/artifacts/test_task717_tutorial_core.py`
- `Select-String -Path cogmem_api/engine/memory_engine.py,cogmem_api/engine/db_utils.py -Pattern "class MemoryEngine|def recall_async|def retain_batch_async|def retry_with_backoff"`