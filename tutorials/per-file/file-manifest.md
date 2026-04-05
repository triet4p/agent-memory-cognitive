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
| 6 | cogmem_api/engine/__init__.py | .py | not-started | TBD |
| 7 | cogmem_api/engine/cross_encoder.py | .py | not-started | TBD |
| 8 | cogmem_api/engine/db_utils.py | .py | not-started | TBD |
| 9 | cogmem_api/engine/embeddings.py | .py | not-started | TBD |
| 10 | cogmem_api/engine/llm_wrapper.py | .py | not-started | TBD |
| 11 | cogmem_api/engine/memory_engine.py | .py | not-started | TBD |
| 12 | cogmem_api/engine/query_analyzer.py | .py | not-started | TBD |
| 13 | cogmem_api/engine/reflect/__init__.py | .py | not-started | TBD |
| 14 | cogmem_api/engine/reflect/agent.py | .py | not-started | TBD |
| 15 | cogmem_api/engine/reflect/models.py | .py | not-started | TBD |
| 16 | cogmem_api/engine/reflect/prompts.py | .py | not-started | TBD |
| 17 | cogmem_api/engine/reflect/tools.py | .py | not-started | TBD |
| 18 | cogmem_api/engine/response_models.py | .py | not-started | TBD |
| 19 | cogmem_api/engine/retain/__init__.py | .py | not-started | TBD |
| 20 | cogmem_api/engine/retain/chunk_storage.py | .py | not-started | TBD |
| 21 | cogmem_api/engine/retain/embedding_processing.py | .py | not-started | TBD |
| 22 | cogmem_api/engine/retain/embedding_utils.py | .py | not-started | TBD |
| 23 | cogmem_api/engine/retain/entity_processing.py | .py | not-started | TBD |
| 24 | cogmem_api/engine/retain/fact_extraction.py | .py | not-started | TBD |
| 25 | cogmem_api/engine/retain/fact_storage.py | .py | not-started | TBD |
| 26 | cogmem_api/engine/retain/link_creation.py | .py | not-started | TBD |
| 27 | cogmem_api/engine/retain/link_utils.py | .py | not-started | TBD |
| 28 | cogmem_api/engine/retain/orchestrator.py | .py | not-started | TBD |
| 29 | cogmem_api/engine/retain/types.py | .py | not-started | TBD |
| 30 | cogmem_api/engine/search/__init__.py | .py | not-started | TBD |
| 31 | cogmem_api/engine/search/fusion.py | .py | not-started | TBD |
| 32 | cogmem_api/engine/search/graph_retrieval.py | .py | not-started | TBD |
| 33 | cogmem_api/engine/search/link_expansion_retrieval.py | .py | not-started | TBD |
| 34 | cogmem_api/engine/search/mpfp_retrieval.py | .py | not-started | TBD |
| 35 | cogmem_api/engine/search/reranking.py | .py | not-started | TBD |
| 36 | cogmem_api/engine/search/retrieval.py | .py | not-started | TBD |
| 37 | cogmem_api/engine/search/tags.py | .py | not-started | TBD |
| 38 | cogmem_api/engine/search/temporal_extraction.py | .py | not-started | TBD |
| 39 | cogmem_api/engine/search/think_utils.py | .py | not-started | TBD |
| 40 | cogmem_api/engine/search/trace.py | .py | not-started | TBD |
| 41 | cogmem_api/engine/search/tracer.py | .py | not-started | TBD |
| 42 | cogmem_api/engine/search/types.py | .py | not-started | TBD |
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