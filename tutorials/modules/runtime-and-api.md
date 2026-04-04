# Runtime And API Modules

## Purpose
- Tài liệu hóa nhóm module runtime entrypoints và HTTP API boundary của CogMem.
- Làm rõ nơi nhận request, validate payload, và chuyển điều phối sang engine.

## Inputs
- CLI args từ shell: host, port, workers, reload, proxy headers.
- HTTP payload retain: `RetainRequest`.
- HTTP payload recall: `RecallRequest`.

## Outputs
- ASGI app chạy qua Uvicorn.
- HTTP responses: `HealthResponse`, `VersionResponse`, `RetainResponse`, `RecallResponse`.
- Exceptions được chuẩn hóa qua HTTP status codes (`400`, `503`).

## Top-down level
- Module

## Prerequisites
- `tutorials/README.md`
- `tutorials/flows/retain-recall-reflect-response.md`
- `tutorials/module-map.md`

## Module responsibility
- `cogmem_api/__init__.py`
  - Trách nhiệm: export `MemoryEngine` ở package root để runtime/app factories dùng trực tiếp.
  - Inbound: `server.py`, `api/http.py` import `MemoryEngine`.
  - Outbound: `cogmem_api.engine.memory_engine.MemoryEngine`.
- `cogmem_api/main.py`
  - Trách nhiệm: CLI bootstrap và chạy Uvicorn.
  - Inbound: command `cogmem-api` hoặc `python -m cogmem_api.main`.
  - Outbound: ASGI target `cogmem_api.server:app`.
- `cogmem_api/server.py`
  - Trách nhiệm: tạo singleton `MemoryEngine`, khởi tạo `app = create_app(...)`.
  - Inbound: `uvicorn` import module để lấy `app`.
  - Outbound: `cogmem_api.api.create_app` + lifecycle `memory.initialize/close`.
- `cogmem_api/api/__init__.py`
  - Trách nhiệm: export `create_app` như API factory public.
  - Inbound: `server.py`.
  - Outbound: `cogmem_api.api.http.create_app`.
- `cogmem_api/api/http.py`
  - Trách nhiệm: định nghĩa Pydantic request/response models và route handlers.
  - Inbound: HTTP requests `/health`, `/version`, `/memories`, `/memories/recall`.
  - Outbound: gọi `MemoryEngine.health_check`, `retain_batch_async`, `recall_async`.
  - Data contracts:
    - Retain path map `RetainItem` -> payload normalized (`event_date`, `entities`, `tags`).
    - Recall path map DB result -> `RecallResult` (`id`, `text`, `type`, `score`, `raw_snippet`).
  - Error boundaries:
    - `_parse_query_timestamp` raise `HTTPException(400)` nếu ISO timestamp lỗi.
    - retain/recall convert `RuntimeError` thành `HTTPException(503)`.

## Function inventory (public/private)
- Public functions:
  - `cogmem_api/main.py`: `build_parser`, `main`
  - `cogmem_api/server.py`: module-level `app` lifecycle bootstrap (entrypoint public của ASGI)
  - `cogmem_api/api/__init__.py`: `create_app`
  - `cogmem_api/api/http.py`: `create_app` (factory), route handlers `health_endpoint`, `version_endpoint`, `retain_memories`, `recall_memories`
- Private/internal helpers:
  - `cogmem_api/api/http.py`: `_parse_query_timestamp`, `_build_retain_payload`
  - `cogmem_api/server.py`: `_config`, `_memory` module-level runtime objects

## Failure modes
- CLI tham số không hợp lệ: argparse reject hoặc Uvicorn không start được.
- Engine chưa sẵn sàng: retain/recall trả `503`.
- Payload retain rỗng sau normalize: trả success với `items_count=0`.
- `async=true` ở retain path hiện chưa hỗ trợ: trả `400`.

## Verify commands
- `uv run python tests/artifacts/test_task717_tutorial_core.py`
- `Select-String -Path cogmem_api/main.py,cogmem_api/server.py,cogmem_api/api/http.py -Pattern "def main|def create_app|retain_memories|recall_memories"`