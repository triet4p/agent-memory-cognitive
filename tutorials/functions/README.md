# Function-level Deep Dive Index (S18.2)

## Mục tiêu
- Chỉ mục này gom toàn bộ tài liệu deep-dive function-level của Sprint S18.2.
- Mỗi module có một file deep-dive với contract đầy đủ cho mọi hàm public/private.

## Danh mục deep-dive theo module
- cogmem_api/api/__init__.py -> tutorials/functions/cogmem_api_api___init__.md (1 functions)
- cogmem_api/api/http.py -> tutorials/functions/cogmem_api_api_http.md (3 functions)
- cogmem_api/config.py -> tutorials/functions/cogmem_api_config.md (8 functions)
- cogmem_api/engine/cross_encoder.py -> tutorials/functions/cogmem_api_engine_cross_encoder.md (17 functions)
- cogmem_api/engine/db_utils.py -> tutorials/functions/cogmem_api_engine_db_utils.md (2 functions)
- cogmem_api/engine/embeddings.py -> tutorials/functions/cogmem_api_engine_embeddings.md (21 functions)
- cogmem_api/engine/llm_wrapper.py -> tutorials/functions/cogmem_api_engine_llm_wrapper.md (4 functions)
- cogmem_api/engine/memory_engine.py -> tutorials/functions/cogmem_api_engine_memory_engine.md (19 functions)
- cogmem_api/engine/query_analyzer.py -> tutorials/functions/cogmem_api_engine_query_analyzer.md (17 functions)
- cogmem_api/engine/reflect/agent.py -> tutorials/functions/cogmem_api_engine_reflect_agent.md (2 functions)
- cogmem_api/engine/reflect/models.py -> tutorials/functions/cogmem_api_engine_reflect_models.md (2 functions)
- cogmem_api/engine/reflect/prompts.py -> tutorials/functions/cogmem_api_engine_reflect_prompts.md (2 functions)
- cogmem_api/engine/reflect/tools.py -> tutorials/functions/cogmem_api_engine_reflect_tools.md (6 functions)
- cogmem_api/engine/response_models.py -> tutorials/functions/cogmem_api_engine_response_models.md (2 functions)
- cogmem_api/engine/retain/chunk_storage.py -> tutorials/functions/cogmem_api_engine_retain_chunk_storage.md (1 functions)
- cogmem_api/engine/retain/embedding_processing.py -> tutorials/functions/cogmem_api_engine_retain_embedding_processing.md (2 functions)
- cogmem_api/engine/retain/embedding_utils.py -> tutorials/functions/cogmem_api_engine_retain_embedding_utils.md (2 functions)
- cogmem_api/engine/retain/entity_processing.py -> tutorials/functions/cogmem_api_engine_retain_entity_processing.md (4 functions)
- cogmem_api/engine/retain/fact_extraction.py -> tutorials/functions/cogmem_api_engine_retain_fact_extraction.md (21 functions)
- cogmem_api/engine/retain/fact_storage.py -> tutorials/functions/cogmem_api_engine_retain_fact_storage.md (4 functions)
- cogmem_api/engine/retain/link_creation.py -> tutorials/functions/cogmem_api_engine_retain_link_creation.md (6 functions)
- cogmem_api/engine/retain/link_utils.py -> tutorials/functions/cogmem_api_engine_retain_link_utils.md (5 functions)
- cogmem_api/engine/retain/orchestrator.py -> tutorials/functions/cogmem_api_engine_retain_orchestrator.md (5 functions)
- cogmem_api/engine/retain/types.py -> tutorials/functions/cogmem_api_engine_retain_types.md (9 functions)
- cogmem_api/engine/search/fusion.py -> tutorials/functions/cogmem_api_engine_search_fusion.md (3 functions)
- cogmem_api/engine/search/graph_retrieval.py -> tutorials/functions/cogmem_api_engine_search_graph_retrieval.md (6 functions)
- cogmem_api/engine/search/link_expansion_retrieval.py -> tutorials/functions/cogmem_api_engine_search_link_expansion_retrieval.md (5 functions)
- cogmem_api/engine/search/mpfp_retrieval.py -> tutorials/functions/cogmem_api_engine_search_mpfp_retrieval.md (18 functions)
- cogmem_api/engine/search/reranking.py -> tutorials/functions/cogmem_api_engine_search_reranking.md (4 functions)
- cogmem_api/engine/search/retrieval.py -> tutorials/functions/cogmem_api_engine_search_retrieval.md (12 functions)
- cogmem_api/engine/search/tags.py -> tutorials/functions/cogmem_api_engine_search_tags.md (8 functions)
- cogmem_api/engine/search/temporal_extraction.py -> tutorials/functions/cogmem_api_engine_search_temporal_extraction.md (2 functions)
- cogmem_api/engine/search/think_utils.py -> tutorials/functions/cogmem_api_engine_search_think_utils.md (7 functions)
- cogmem_api/engine/search/trace.py -> tutorials/functions/cogmem_api_engine_search_trace.md (6 functions)
- cogmem_api/engine/search/tracer.py -> tutorials/functions/cogmem_api_engine_search_tracer.md (13 functions)
- cogmem_api/engine/search/types.py -> tutorials/functions/cogmem_api_engine_search_types.md (5 functions)
- cogmem_api/main.py -> tutorials/functions/cogmem_api_main.md (2 functions)
- cogmem_api/pg0.py -> tutorials/functions/cogmem_api_pg0.md (8 functions)

## Verify commands
- uv run python tests/artifacts/test_task719_function_deep_dive.py
- Select-String -Path tutorials/functions/*.md -Pattern "### Function:"
