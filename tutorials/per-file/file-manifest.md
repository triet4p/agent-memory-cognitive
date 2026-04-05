# Phase D File Manifest (S19.0)

## Scope Lock
- Include paths: `cogmem_api/**`, `scripts/**`, `docker/**`.
- Include extensions: `.py`, `.sh`, `.ps1`.
- Exclude mandatory tutorial scope: `tests/artifacts/**`.

## Coverage Status Legend
- `not-started`: Chưa có tutorial manual cho file.
- `in-progress`: Đang viết tutorial manual cho file.
- `done`: Đã có tutorial manual theo canon và đạt quality gate.

## File Manifest

| # | File Path | Extension | Coverage Status | Tutorial Doc |
|---|---|---|---|---|
| 1 | cogmem_api/__init__.py | .py | done | tutorials/per-file/bootstrap--cogmem-api-init.md |
| 2 | cogmem_api/alembic/versions/20260330_0001_t1_2_schema_extensions.py | .py | done | tutorials/per-file/schema--cogmem-api-alembic-t1-2-schema-extensions.md |
| 3 | cogmem_api/api/__init__.py | .py | done | tutorials/per-file/api--cogmem-api-api-init.md |
| 4 | cogmem_api/api/http.py | .py | done | tutorials/per-file/api--cogmem-api-api-http.md |
| 5 | cogmem_api/config.py | .py | done | tutorials/per-file/bootstrap--cogmem-api-config.md |
| 6 | cogmem_api/engine/__init__.py | .py | done | tutorials/per-file/engine-core--cogmem-api-engine-init.md |
| 7 | cogmem_api/engine/cross_encoder.py | .py | done | tutorials/per-file/engine-core--cogmem-api-engine-cross-encoder.md |
| 8 | cogmem_api/engine/db_utils.py | .py | done | tutorials/per-file/engine-core--cogmem-api-engine-db-utils.md |
| 9 | cogmem_api/engine/embeddings.py | .py | done | tutorials/per-file/engine-core--cogmem-api-engine-embeddings.md |
| 10 | cogmem_api/engine/llm_wrapper.py | .py | done | tutorials/per-file/engine-core--cogmem-api-engine-llm-wrapper.md |
| 11 | cogmem_api/engine/memory_engine.py | .py | done | tutorials/per-file/engine-core--cogmem-api-engine-memory-engine.md |
| 12 | cogmem_api/engine/query_analyzer.py | .py | done | tutorials/per-file/search--cogmem-api-engine-query-analyzer.md |
| 13 | cogmem_api/engine/reflect/__init__.py | .py | not-started | TBD |
| 14 | cogmem_api/engine/reflect/agent.py | .py | not-started | TBD |
| 15 | cogmem_api/engine/reflect/models.py | .py | not-started | TBD |
| 16 | cogmem_api/engine/reflect/prompts.py | .py | not-started | TBD |
| 17 | cogmem_api/engine/reflect/tools.py | .py | not-started | TBD |
| 18 | cogmem_api/engine/response_models.py | .py | done | tutorials/per-file/engine-core--cogmem-api-engine-response-models.md |
| 19 | cogmem_api/engine/retain/__init__.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-init.md |
| 20 | cogmem_api/engine/retain/chunk_storage.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-chunk-storage.md |
| 21 | cogmem_api/engine/retain/embedding_processing.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-embedding-processing.md |
| 22 | cogmem_api/engine/retain/embedding_utils.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-embedding-utils.md |
| 23 | cogmem_api/engine/retain/entity_processing.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-entity-processing.md |
| 24 | cogmem_api/engine/retain/fact_extraction.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-fact-extraction.md |
| 25 | cogmem_api/engine/retain/fact_storage.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-fact-storage.md |
| 26 | cogmem_api/engine/retain/link_creation.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-link-creation.md |
| 27 | cogmem_api/engine/retain/link_utils.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-link-utils.md |
| 28 | cogmem_api/engine/retain/orchestrator.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-orchestrator.md |
| 29 | cogmem_api/engine/retain/types.py | .py | done | tutorials/per-file/retain--cogmem-api-engine-retain-types.md |
| 30 | cogmem_api/engine/search/__init__.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-init.md |
| 31 | cogmem_api/engine/search/fusion.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-fusion.md |
| 32 | cogmem_api/engine/search/graph_retrieval.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-graph-retrieval.md |
| 33 | cogmem_api/engine/search/link_expansion_retrieval.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-link-expansion-retrieval.md |
| 34 | cogmem_api/engine/search/mpfp_retrieval.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-mpfp-retrieval.md |
| 35 | cogmem_api/engine/search/reranking.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-reranking.md |
| 36 | cogmem_api/engine/search/retrieval.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-retrieval.md |
| 37 | cogmem_api/engine/search/tags.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-tags.md |
| 38 | cogmem_api/engine/search/temporal_extraction.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-temporal-extraction.md |
| 39 | cogmem_api/engine/search/think_utils.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-think-utils.md |
| 40 | cogmem_api/engine/search/trace.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-trace.md |
| 41 | cogmem_api/engine/search/tracer.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-tracer.md |
| 42 | cogmem_api/engine/search/types.py | .py | done | tutorials/per-file/search--cogmem-api-engine-search-types.md |
| 43 | cogmem_api/main.py | .py | done | tutorials/per-file/bootstrap--cogmem-api-main.md |
| 44 | cogmem_api/models.py | .py | done | tutorials/per-file/schema--cogmem-api-models.md |
| 45 | cogmem_api/pg0.py | .py | done | tutorials/per-file/bootstrap--cogmem-api-pg0.md |
| 46 | cogmem_api/server.py | .py | done | tutorials/per-file/bootstrap--cogmem-api-server.md |
| 47 | docker/standalone/start-all.sh | .sh | not-started | TBD |
| 48 | docker/test-image.ps1 | .ps1 | not-started | TBD |
| 49 | docker/test-image.sh | .sh | not-started | TBD |
| 50 | scripts/ablation_runner.py | .py | not-started | TBD |
| 51 | scripts/distill_dataset.py | .py | not-started | TBD |
| 52 | scripts/docker.ps1 | .ps1 | not-started | TBD |
| 53 | scripts/docker.sh | .sh | not-started | TBD |
| 54 | scripts/eval_cogmem.py | .py | not-started | TBD |
| 55 | scripts/run_hindsight.ps1 | .ps1 | not-started | TBD |
| 56 | scripts/smoke-test-cogmem.ps1 | .ps1 | not-started | TBD |
| 57 | scripts/smoke-test-cogmem.sh | .sh | not-started | TBD |
| 58 | scripts/test_hindsight.py | .py | not-started | TBD |