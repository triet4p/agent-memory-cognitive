# Phase D Canonical Reading Order (S19.7)

## Mục tiêu
- Xuất thứ tự đọc bao phủ 100% file code trong scope Phase D.
- Cung cấp hai lộ trình: onboarding path và debug-first path.
- Giữ một catalog ID ổn định để trao đổi nhanh theo số thứ tự.

## Scope
- Include paths: cogmem_api/**, scripts/**, docker/**.
- Include extensions: .py, .sh, .ps1.
- Tổng số file: 58.

## Canonical catalog IDs
| ID | Source file | Tutorial doc |
|---|---|---|
| 1 | cogmem_api/__init__.py | tutorials/per-file/bootstrap--cogmem-api-init.md |
| 2 | cogmem_api/alembic/versions/20260330_0001_t1_2_schema_extensions.py | tutorials/per-file/schema--cogmem-api-alembic-t1-2-schema-extensions.md |
| 3 | cogmem_api/api/__init__.py | tutorials/per-file/api--cogmem-api-api-init.md |
| 4 | cogmem_api/api/http.py | tutorials/per-file/api--cogmem-api-api-http.md |
| 5 | cogmem_api/config.py | tutorials/per-file/bootstrap--cogmem-api-config.md |
| 6 | cogmem_api/engine/__init__.py | tutorials/per-file/engine-core--cogmem-api-engine-init.md |
| 7 | cogmem_api/engine/cross_encoder.py | tutorials/per-file/engine-core--cogmem-api-engine-cross-encoder.md |
| 8 | cogmem_api/engine/db_utils.py | tutorials/per-file/engine-core--cogmem-api-engine-db-utils.md |
| 9 | cogmem_api/engine/embeddings.py | tutorials/per-file/engine-core--cogmem-api-engine-embeddings.md |
| 10 | cogmem_api/engine/llm_wrapper.py | tutorials/per-file/engine-core--cogmem-api-engine-llm-wrapper.md |
| 11 | cogmem_api/engine/memory_engine.py | tutorials/per-file/engine-core--cogmem-api-engine-memory-engine.md |
| 12 | cogmem_api/engine/query_analyzer.py | tutorials/per-file/search--cogmem-api-engine-query-analyzer.md |
| 13 | cogmem_api/engine/reflect/__init__.py | tutorials/per-file/reflect--cogmem-api-engine-reflect-init.md |
| 14 | cogmem_api/engine/reflect/agent.py | tutorials/per-file/reflect--cogmem-api-engine-reflect-agent.md |
| 15 | cogmem_api/engine/reflect/models.py | tutorials/per-file/reflect--cogmem-api-engine-reflect-models.md |
| 16 | cogmem_api/engine/reflect/prompts.py | tutorials/per-file/reflect--cogmem-api-engine-reflect-prompts.md |
| 17 | cogmem_api/engine/reflect/tools.py | tutorials/per-file/reflect--cogmem-api-engine-reflect-tools.md |
| 18 | cogmem_api/engine/response_models.py | tutorials/per-file/engine-core--cogmem-api-engine-response-models.md |
| 19 | cogmem_api/engine/retain/__init__.py | tutorials/per-file/retain--cogmem-api-engine-retain-init.md |
| 20 | cogmem_api/engine/retain/chunk_storage.py | tutorials/per-file/retain--cogmem-api-engine-retain-chunk-storage.md |
| 21 | cogmem_api/engine/retain/embedding_processing.py | tutorials/per-file/retain--cogmem-api-engine-retain-embedding-processing.md |
| 22 | cogmem_api/engine/retain/embedding_utils.py | tutorials/per-file/retain--cogmem-api-engine-retain-embedding-utils.md |
| 23 | cogmem_api/engine/retain/entity_processing.py | tutorials/per-file/retain--cogmem-api-engine-retain-entity-processing.md |
| 24 | cogmem_api/engine/retain/fact_extraction.py | tutorials/per-file/retain--cogmem-api-engine-retain-fact-extraction.md |
| 25 | cogmem_api/engine/retain/fact_storage.py | tutorials/per-file/retain--cogmem-api-engine-retain-fact-storage.md |
| 26 | cogmem_api/engine/retain/link_creation.py | tutorials/per-file/retain--cogmem-api-engine-retain-link-creation.md |
| 27 | cogmem_api/engine/retain/link_utils.py | tutorials/per-file/retain--cogmem-api-engine-retain-link-utils.md |
| 28 | cogmem_api/engine/retain/orchestrator.py | tutorials/per-file/retain--cogmem-api-engine-retain-orchestrator.md |
| 29 | cogmem_api/engine/retain/types.py | tutorials/per-file/retain--cogmem-api-engine-retain-types.md |
| 30 | cogmem_api/engine/search/__init__.py | tutorials/per-file/search--cogmem-api-engine-search-init.md |
| 31 | cogmem_api/engine/search/fusion.py | tutorials/per-file/search--cogmem-api-engine-search-fusion.md |
| 32 | cogmem_api/engine/search/graph_retrieval.py | tutorials/per-file/search--cogmem-api-engine-search-graph-retrieval.md |
| 33 | cogmem_api/engine/search/link_expansion_retrieval.py | tutorials/per-file/search--cogmem-api-engine-search-link-expansion-retrieval.md |
| 34 | cogmem_api/engine/search/mpfp_retrieval.py | tutorials/per-file/search--cogmem-api-engine-search-mpfp-retrieval.md |
| 35 | cogmem_api/engine/search/reranking.py | tutorials/per-file/search--cogmem-api-engine-search-reranking.md |
| 36 | cogmem_api/engine/search/retrieval.py | tutorials/per-file/search--cogmem-api-engine-search-retrieval.md |
| 37 | cogmem_api/engine/search/tags.py | tutorials/per-file/search--cogmem-api-engine-search-tags.md |
| 38 | cogmem_api/engine/search/temporal_extraction.py | tutorials/per-file/search--cogmem-api-engine-search-temporal-extraction.md |
| 39 | cogmem_api/engine/search/think_utils.py | tutorials/per-file/search--cogmem-api-engine-search-think-utils.md |
| 40 | cogmem_api/engine/search/trace.py | tutorials/per-file/search--cogmem-api-engine-search-trace.md |
| 41 | cogmem_api/engine/search/tracer.py | tutorials/per-file/search--cogmem-api-engine-search-tracer.md |
| 42 | cogmem_api/engine/search/types.py | tutorials/per-file/search--cogmem-api-engine-search-types.md |
| 43 | cogmem_api/main.py | tutorials/per-file/bootstrap--cogmem-api-main.md |
| 44 | cogmem_api/models.py | tutorials/per-file/schema--cogmem-api-models.md |
| 45 | cogmem_api/pg0.py | tutorials/per-file/bootstrap--cogmem-api-pg0.md |
| 46 | cogmem_api/server.py | tutorials/per-file/bootstrap--cogmem-api-server.md |
| 47 | docker/standalone/start-all.sh | tutorials/per-file/docker--docker-standalone-start-all-sh.md |
| 48 | docker/test-image.ps1 | tutorials/per-file/docker--docker-test-image-ps1.md |
| 49 | docker/test-image.sh | tutorials/per-file/docker--docker-test-image-sh.md |
| 50 | scripts/ablation_runner.py | tutorials/per-file/tooling--scripts-ablation-runner.md |
| 51 | scripts/distill_dataset.py | tutorials/per-file/tooling--scripts-distill-dataset.md |
| 52 | scripts/docker.ps1 | tutorials/per-file/tooling--scripts-docker-ps1.md |
| 53 | scripts/docker.sh | tutorials/per-file/tooling--scripts-docker-sh.md |
| 54 | scripts/eval_cogmem.py | tutorials/per-file/tooling--scripts-eval-cogmem.md |
| 55 | scripts/run_hindsight.ps1 | tutorials/per-file/tooling--scripts-run-hindsight-ps1.md |
| 56 | scripts/smoke-test-cogmem.ps1 | tutorials/per-file/tooling--scripts-smoke-test-cogmem-ps1.md |
| 57 | scripts/smoke-test-cogmem.sh | tutorials/per-file/tooling--scripts-smoke-test-cogmem-sh.md |
| 58 | scripts/test_hindsight.py | tutorials/per-file/tooling--scripts-test-hindsight.md |

## Onboarding path
- Mục tiêu: đi từ entrypoint đến các lớp lõi theo luồng nghiệp vụ chuẩn, rồi mở rộng sang tooling/runtime scripts.
- ONBOARDING_IDS: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58

## Debug-first path
- Mục tiêu: đọc theo hướng xử lý sự cố production trước, ưu tiên startup, API path, search/retain/reflect và script vận hành.
- DEBUG_FIRST_IDS: 43,46,4,11,12,30,36,31,35,42,32,33,34,37,38,40,41,39,19,28,24,25,23,26,27,21,22,20,29,13,14,15,16,17,6,8,9,7,10,18,1,5,44,2,3,45,53,52,49,48,47,56,57,50,54,51,58,55

## Gợi ý áp dụng
1. Khi onboarding thành viên mới: dùng Onboarding path theo thứ tự tuyệt đối.
2. Khi lỗi runtime/quality recall: dùng Debug-first path và dừng tại ID đầu tiên có bất thường.
3. Khi review PR: đối chiếu file thay đổi với catalog ID để chọn khối tutorial liên quan.

## Verify commands
1. uv run python tests/artifacts/test_task728_reading_order_full_scope.py
2. uv run python tests/artifacts/test_task727_manual_reflect_tooling_coverage.py
3. uv run python tests/artifacts/test_task721_file_manifest_gate.py
