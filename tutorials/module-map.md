# CogMem Tutorial Module Map (Top-down)

## Mục tiêu
Tài liệu này cung cấp bản đồ top-down để đọc codebase theo thứ tự hệ thống -> luồng -> module -> hàm.
Đây là scaffold cho Sprint S16.1, các function inventory chỉ ở mức seed và sẽ được đầy đủ ở S17-S18.

## Layer 0 - System Overview
### L0.1 Hệ thống và boundary
1. Runtime API: nhận request retain/recall/health.
2. Retain pipeline: trích xuất fact, entity, link và lưu vào DB.
3. Recall pipeline: truy hồi đa kênh (semantic/BM25/graph/temporal), fusion và rerank.
4. Reflect pipeline: tổng hợp context retrieve để tạo response.
5. Persistence layer: Postgres/pg0 + schema model trong `cogmem_api/models.py`.

### L0.2 Định nghĩa dòng dữ liệu chính
1. Ingest path: conversation turns -> retain -> graph nodes/edges.
2. Query path: question -> analyzer -> retrieval -> reflect -> answer.
3. Ops path: startup/shutdown/health + config bootstrap.

## Layer 1 - End-to-end Flows
### L1.1 Flow retain ingestion
1. Entrypoint runtime: `cogmem_api/main.py` + `cogmem_api/server.py`.
2. HTTP route: `cogmem_api/api/http.py`.
3. Orchestration: `cogmem_api/engine/retain/orchestrator.py`.
4. Extraction/storage/linking: các module trong `cogmem_api/engine/retain/`.
5. DB write: `cogmem_api/engine/db_utils.py` và schema `cogmem_api/models.py`.

### L1.2 Flow recall and response
1. Query analysis: `cogmem_api/engine/query_analyzer.py`.
2. Retrieval orchestration: `cogmem_api/engine/search/retrieval.py`.
3. Graph + link expansion + fusion + rerank: `cogmem_api/engine/search/`.
4. Reflect synthesis: `cogmem_api/engine/reflect/`.

### L1.3 Flow startup and configuration
1. Config loading: `cogmem_api/config.py`.
2. App bootstrap: `cogmem_api/main.py`, `cogmem_api/server.py`.
3. Embedded DB mode: `cogmem_api/pg0.py`.

## Layer 2 - Module Catalog
| Module | Vai trò chính | Phụ thuộc nội bộ |
|---|---|---|
| `cogmem_api/config.py` | Nạp và validate cấu hình runtime | `cogmem_api` root modules |
| `cogmem_api/main.py` | Entrypoint khởi động dịch vụ | `server.py`, `config.py` |
| `cogmem_api/server.py` | Tạo app và lifecycle hooks | `api/http.py`, engine modules |
| `cogmem_api/api/http.py` | Định nghĩa API retain/recall/health | `engine/memory_engine.py`, schemas |
| `cogmem_api/models.py` | SQLAlchemy models cho memory graph | `alembic`, `engine/db_utils.py` |
| `cogmem_api/pg0.py` | Runtime hỗ trợ embedded postgres mode | `config.py` |
| `cogmem_api/engine/memory_engine.py` | Điều phối retain + retrieval + reflect | `engine/retain`, `engine/search`, `engine/reflect` |
| `cogmem_api/engine/db_utils.py` | Session/transaction và DB helpers | `models.py` |
| `cogmem_api/engine/llm_wrapper.py` | Adapter LLM provider | `config.py` |
| `cogmem_api/engine/embeddings.py` | Embedding provider và utility | `config.py` |
| `cogmem_api/engine/cross_encoder.py` | Rerank model wrapper | `config.py` |
| `cogmem_api/engine/query_analyzer.py` | Phân loại query type cho retrieval routing | `engine/search/types.py` |
| `cogmem_api/engine/retain/` | Ingestion pipeline (extract, entity, link, store) | db/embedding/llm helpers |
| `cogmem_api/engine/search/` | Retrieval stack (graph, temporal, fusion, rerank) | embeddings, cross-encoder |
| `cogmem_api/engine/reflect/` | Reflect agent và prompt/tooling | llm wrapper, response models |

### L2.1 Module dossier mapping (S17.3 gate)
| Module catalog group | Dossier tham chiếu |
|---|---|
| `cogmem_api/__init__.py`, `cogmem_api/main.py`, `cogmem_api/server.py`, `cogmem_api/api/__init__.py`, `cogmem_api/api/http.py` | `tutorials/modules/runtime-and-api.md` |
| `cogmem_api/config.py`, `cogmem_api/models.py`, `cogmem_api/pg0.py` | `tutorials/modules/config-and-schema.md` |
| `cogmem_api/engine/__init__.py`, `cogmem_api/engine/memory_engine.py`, `cogmem_api/engine/db_utils.py`, `cogmem_api/engine/response_models.py` | `tutorials/modules/engine-core-services.md` |
| `cogmem_api/engine/llm_wrapper.py`, `cogmem_api/engine/embeddings.py`, `cogmem_api/engine/cross_encoder.py` | `tutorials/modules/adapters-llm-embeddings-reranker.md` |
| `cogmem_api/engine/retain/` | `tutorials/modules/retain-pipeline.md` |
| `cogmem_api/engine/query_analyzer.py`, `cogmem_api/engine/search/` | `tutorials/modules/search-pipeline.md` |
| `cogmem_api/engine/reflect/` | `tutorials/modules/reflect-pipeline.md` |

## Layer 3 - Function Inventory Seed
Mục này là seed để Sprint S17-S18 bổ sung inventory đầy đủ public/private theo từng module.

| Nhóm module | Trạng thái seed | Hướng bổ sung ở S17-S18 |
|---|---|---|
| Runtime (`main.py`, `server.py`, `api/http.py`) | Đã xác định boundary | Liệt kê đầy đủ entrypoint public + helpers private |
| Config & Persistence (`config.py`, `models.py`, `pg0.py`, `db_utils.py`) | Đã xác định vai trò | Map function theo contract env/schema/db lifecycle |
| Retain (`engine/retain/`) | Đã xác định pipeline modules | Inventory theo stage: chunk -> extraction -> entity -> link -> storage |
| Search (`engine/search/`, `query_analyzer.py`) | Đã xác định retrieval stack | Inventory theo channel + fusion/rerank + routing policy |
| Reflect (`engine/reflect/`) | Đã xác định lazy synthesis scope | Inventory public/private cho generation path |

## Ghi chú gate cho S16.1
1. Bắt buộc giữ đủ 4 layer top-down trong tài liệu này.
2. Learning path phải đọc theo thứ tự Architecture -> Module -> Function.
3. Chưa chỉnh sửa coverage matrix trong sprint này (read-only theo governance).
