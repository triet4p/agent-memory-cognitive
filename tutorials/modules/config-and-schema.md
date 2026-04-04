# Config And Schema Modules

## Purpose
- Tài liệu hóa nhóm module chịu trách nhiệm cấu hình runtime, embedded Postgres, và schema dữ liệu graph.
- Xác định rõ data contracts môi trường và persistence contracts cho retain/recall.

## Inputs
- Environment variables `COGMEM_API_*`.
- Database URL chuẩn Postgres hoặc URL `pg0://...`.
- SQLAlchemy metadata declarations cho entities/units/links.

## Outputs
- `CogMemRuntimeConfig` và `CogMemConfig` đã normalize.
- Embedded Postgres lifecycle khi dùng mode pg0.
- DB schema objects: `banks`, `memory_units`, `memory_links`, `entities`, `unit_entities`, ...

## Top-down level
- Module

## Prerequisites
- `tutorials/README.md`
- `tutorials/module-map.md`
- `tutorials/flows/retain-recall-reflect-response.md`

## Module responsibility
- `cogmem_api/config.py`
  - Trách nhiệm: parse env và chuyển thành config typed dataclasses.
  - Inbound: runtime boot (`main.py`, `server.py`, `memory_engine.py`).
  - Outbound: cung cấp `get_config`, `_get_raw_config` cho retain/retrieval/rerank params.
  - Data contracts: clamp min/max cho pool size, timeout, retriever mode, extraction mode.
  - Error boundary: raise `ValueError` khi env int/float/bool sai format hoặc ngoài range.
- `cogmem_api/pg0.py`
  - Trách nhiệm: wrapper quản lý binary Postgres embedded.
  - Inbound: `MemoryEngine.__init__/initialize` khi URL có prefix pg0.
  - Outbound: start/stop process và trả DB URL dùng cho asyncpg.
  - Error boundary: subprocess thất bại, URL parse không hợp lệ.
- `cogmem_api/models.py`
  - Trách nhiệm: định nghĩa SQLAlchemy models + enums/constraints cho memory graph.
  - Inbound: `memory_engine._bootstrap_schema_objects`, retain/read queries.
  - Outbound: metadata dùng cho create tables, ORM mapping.
  - Data contracts: `fact_type`, `link_type`, timestamp fields, metadata JSON, `raw_snippet`.
  - Error boundary: schema mismatch khi migrate/chạy DB cũ.

## Function inventory (public/private)
- Public functions/classes:
  - `cogmem_api/config.py`: `CogMemRuntimeConfig`, `CogMemConfig`, `_get_raw_config`, `get_config`
  - `cogmem_api/pg0.py`: `EmbeddedPostgres`, `parse_pg0_url`
  - `cogmem_api/models.py`: `Base`, `Document`, `MemoryUnit`, `Entity`, `UnitEntity`, `EntityCooccurrence`, `MemoryLink`, `Bank`, `RequestContext`
- Private/internal helpers:
  - `cogmem_api/config.py`: `_read_optional_str`, `_read_int`, `_read_float`, `_read_bool`, `_read_retain_extraction_mode`, `_read_graph_retriever`
  - `cogmem_api/pg0.py`: methods nội bộ phục vụ lifecycle process management

## Failure modes
- Cấu hình môi trường không hợp lệ gây fail-fast ngay khi import config.
- pg0 binary không khả dụng hoặc cổng bận khiến initialize không thành công.
- Schema thay đổi không tương thích có thể gây lỗi khi query/write ở retain/retrieval.

## Verify commands
- `uv run python tests/artifacts/test_task717_tutorial_core.py`
- `Select-String -Path cogmem_api/config.py,cogmem_api/pg0.py,cogmem_api/models.py -Pattern "def get_config|class EmbeddedPostgres|class MemoryUnit|class MemoryLink"`