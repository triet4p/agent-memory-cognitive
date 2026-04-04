# CogMem Manual Code Reading Guide

## Mục tiêu
Tài liệu này không theo kiểu liệt kê máy móc. Mục tiêu là giúp bạn đọc code theo mạch vận hành thật của hệ thống:
1. Đi vào từ runtime entrypoint.
2. Theo đường chạy retain.
3. Theo đường chạy recall.
4. Theo đường chạy reflect.
5. Hiểu rõ instance/singleton nào đang giữ state.

## Đọc từ đâu để nắm hệ thống nhanh nhất
1. Bước 1: đọc runtime bootstrap.
- [cogmem_api/main.py](cogmem_api/main.py)
- [cogmem_api/server.py](cogmem_api/server.py)
- [cogmem_api/api/__init__.py](cogmem_api/api/__init__.py)
- [cogmem_api/api/http.py](cogmem_api/api/http.py)

2. Bước 2: đọc engine core trước, vì mọi endpoint cuối cùng đều dồn về đây.
- [cogmem_api/engine/memory_engine.py](cogmem_api/engine/memory_engine.py)

3. Bước 3: đọc retain stack theo đúng call chain.
- [cogmem_api/engine/retain/orchestrator.py](cogmem_api/engine/retain/orchestrator.py)
- [cogmem_api/engine/retain/fact_extraction.py](cogmem_api/engine/retain/fact_extraction.py)
- [cogmem_api/engine/retain/fact_storage.py](cogmem_api/engine/retain/fact_storage.py)
- [cogmem_api/engine/retain/entity_processing.py](cogmem_api/engine/retain/entity_processing.py)
- [cogmem_api/engine/retain/link_creation.py](cogmem_api/engine/retain/link_creation.py)
- [cogmem_api/engine/retain/types.py](cogmem_api/engine/retain/types.py)

4. Bước 4: đọc recall stack theo call chain.
- [cogmem_api/engine/search/retrieval.py](cogmem_api/engine/search/retrieval.py)
- [cogmem_api/engine/query_analyzer.py](cogmem_api/engine/query_analyzer.py)
- [cogmem_api/engine/search/fusion.py](cogmem_api/engine/search/fusion.py)
- [cogmem_api/engine/search/graph_retrieval.py](cogmem_api/engine/search/graph_retrieval.py)
- [cogmem_api/engine/search/link_expansion_retrieval.py](cogmem_api/engine/search/link_expansion_retrieval.py)
- [cogmem_api/engine/search/mpfp_retrieval.py](cogmem_api/engine/search/mpfp_retrieval.py)
- [cogmem_api/engine/search/reranking.py](cogmem_api/engine/search/reranking.py)
- [cogmem_api/engine/search/types.py](cogmem_api/engine/search/types.py)

5. Bước 5: đọc reflect stack.
- [cogmem_api/engine/reflect/agent.py](cogmem_api/engine/reflect/agent.py)
- [cogmem_api/engine/reflect/tools.py](cogmem_api/engine/reflect/tools.py)
- [cogmem_api/engine/reflect/prompts.py](cogmem_api/engine/reflect/prompts.py)
- [cogmem_api/engine/reflect/models.py](cogmem_api/engine/reflect/models.py)

6. Bước 6: đọc schema và config để hiểu các ràng buộc cứng.
- [cogmem_api/models.py](cogmem_api/models.py)
- [cogmem_api/config.py](cogmem_api/config.py)

## Runtime call chain thật
1. CLI vào [cogmem_api/main.py](cogmem_api/main.py)
- Hàm build_parser: map CLI args sang host, port, log-level, workers.
- Hàm main: gọi uvicorn.run trỏ tới cogmem_api.server:app.

2. Server module [cogmem_api/server.py](cogmem_api/server.py)
- Instance _config: snapshot raw config lúc import module.
- Instance _memory: singleton MemoryEngine sống cùng process.
- Instance app: FastAPI app đã bind memory engine.

3. API factory [cogmem_api/api/__init__.py](cogmem_api/api/__init__.py)
- Hàm create_app: switch gateway. Hiện nhánh chính là HTTP API từ api/http.py.

4. HTTP app [cogmem_api/api/http.py](cogmem_api/api/http.py)
- Lifespan startup: await memory.initialize.
- Lifespan shutdown: await memory.close.
- Endpoint retain: gọi memory.retain_batch_async.
- Endpoint recall: gọi memory.recall_async.

## Retain call chain thật
1. [cogmem_api/api/http.py](cogmem_api/api/http.py)
- _build_retain_payload chuẩn hóa input item.
- retain_memories gửi list payload vào memory.retain_batch_async.

2. [cogmem_api/engine/memory_engine.py](cogmem_api/engine/memory_engine.py)
- retain_batch_async là cổng retain cấp engine.
- Hàm này lazy import orchestrator.retain_batch và truyền dependencies vào.

3. [cogmem_api/engine/retain/orchestrator.py](cogmem_api/engine/retain/orchestrator.py)
- retain_batch điều phối toàn pipeline.
- Trình tự chính:
  - normalize input thành RetainContent.
  - extract facts qua fact_extraction.extract_facts_from_contents.
  - generate embeddings qua embedding_processing.generate_embeddings_batch.
  - map thành ProcessedFact.
  - bắt transaction, ghi DB và tạo links.

4. [cogmem_api/engine/retain/fact_extraction.py](cogmem_api/engine/retain/fact_extraction.py)
- extract_facts_from_contents là API chính của module extraction.
- Nhánh chạy:
  - nếu có llm_config thì đi qua _extract_facts_with_llm.
  - nếu không hoặc lỗi thì fallback seeded/fallback facts.
- Ý nghĩa các hàm private quan trọng:
  - _build_prompt và _build_user_message: kiểm soát prompt parity theo mode.
  - _normalize_llm_facts: biến output LLM thành ExtractedFact chuẩn.
  - _extract_causal_relations, _extract_action_effect_relations, _extract_transition_relations: bóc quan hệ edge.

5. [cogmem_api/engine/retain/fact_storage.py](cogmem_api/engine/retain/fact_storage.py)
- ensure_bank_exists: bảo đảm bank row tồn tại trước insert.
- insert_facts_batch: ghi memory_units và trả list unit_ids.

6. [cogmem_api/engine/retain/entity_processing.py](cogmem_api/engine/retain/entity_processing.py)
- process_entities_batch: resolve entity và tạo EntityLink.
- insert_entity_links_batch: ghi bảng unit_entities/memory_links kiểu entity.

7. [cogmem_api/engine/retain/link_creation.py](cogmem_api/engine/retain/link_creation.py)
- create_temporal_links_batch
- create_semantic_links_batch
- create_causal_links_batch
- create_habit_sr_links_batch
- create_transition_links_batch
- create_action_effect_links_batch

8. Retain data contracts sống ở [cogmem_api/engine/retain/types.py](cogmem_api/engine/retain/types.py)
- RetainContent: input normalized.
- ExtractedFact: output extraction.
- ProcessedFact: payload trước khi ghi DB.
- COGMEM_FACT_TYPES, TRANSITION_EDGE_RULES: ràng buộc semantic cứng.

## Recall call chain thật
1. [cogmem_api/api/http.py](cogmem_api/api/http.py)
- _parse_query_timestamp chuyển query_timestamp thành datetime.
- recall_memories gọi memory.recall_async.

2. [cogmem_api/engine/memory_engine.py](cogmem_api/engine/memory_engine.py)
- recall_async là cổng recall chính.
- Trình tự:
  - tạo query embedding.
  - gọi retrieve_all_fact_types_parallel.
  - fuse từng fact type bằng fuse_parallel_results.
  - cross-encoder rerank và apply_combined_scoring.
  - fallback lexical scan nếu pipeline chính ném exception.

3. [cogmem_api/engine/search/retrieval.py](cogmem_api/engine/search/retrieval.py)
- resolve_query_routing: query type + temporal constraint + adaptive RRF weights.
- retrieve_all_fact_types_parallel: điều phối semantic + bm25 + graph + temporal.
- fuse_parallel_results: weighted RRF và boost theo query type.
- prospective guard:
  - _collect_intention_result_ids
  - _resolve_planning_intention_ids
  - _filter_prospective_results

4. Query analyzer ở [cogmem_api/engine/query_analyzer.py](cogmem_api/engine/query_analyzer.py)
- classify_query_type quyết định semantic/temporal/causal/prospective/preference/multi_hop.
- DateparserQueryAnalyzer: extractor mặc định cho temporal expressions.
- TransformerQueryAnalyzer: nhánh analyzer nâng cao.

5. Graph retrieval pluggable
- [cogmem_api/engine/search/graph_retrieval.py](cogmem_api/engine/search/graph_retrieval.py)
  - GraphRetriever là interface.
  - BFSGraphRetriever là default path khi config graph_retriever=bfs.
- [cogmem_api/engine/search/link_expansion_retrieval.py](cogmem_api/engine/search/link_expansion_retrieval.py)
  - LinkExpansionRetriever cho traversal kiểu mở rộng links từ semantic seeds.
- [cogmem_api/engine/search/mpfp_retrieval.py](cogmem_api/engine/search/mpfp_retrieval.py)
  - MPFPGraphRetriever cho pattern-based multi-hop.

6. Fusion + rerank
- [cogmem_api/engine/search/fusion.py](cogmem_api/engine/search/fusion.py)
  - weighted_reciprocal_rank_fusion
  - reciprocal_rank_fusion
- [cogmem_api/engine/search/reranking.py](cogmem_api/engine/search/reranking.py)
  - CrossEncoderReranker.rerank: neural rerank.
  - apply_combined_scoring: áp recency + temporal boost vào CE score.

## Reflect call chain thật
1. [cogmem_api/engine/reflect/agent.py](cogmem_api/engine/reflect/agent.py)
- synthesize_lazy_reflect là API chính.
- prepare_lazy_evidence lọc evidence từ retrieval items.
- build_lazy_synthesis_prompt tạo prompt tổng hợp.
- llm_generate có thể cắm ngoài; nếu không có thì dùng markdown answer mặc định.

2. [cogmem_api/engine/reflect/tools.py](cogmem_api/engine/reflect/tools.py)
- to_reflect_evidence: chuẩn hóa một candidate thành ReflectEvidence.
- prepare_lazy_evidence: cắt top-N evidence cho synthesis.
- group_evidence_by_network: gom theo fact/network type.

3. [cogmem_api/engine/reflect/models.py](cogmem_api/engine/reflect/models.py)
- ReflectEvidence: contract của một mảnh evidence.
- ReflectSynthesisResult: contract output của synthesize_lazy_reflect.

## Instance và singleton quan trọng (đây là nơi giữ state)
1. [cogmem_api/server.py](cogmem_api/server.py)
- _config: snapshot env config.
- _memory: singleton MemoryEngine được app dùng chung.
- app: FastAPI object export cho uvicorn.

2. [cogmem_api/engine/memory_engine.py](cogmem_api/engine/memory_engine.py)
- _current_schema: ContextVar giữ schema theo context.
- MemoryEngine._pool: asyncpg pool sống suốt vòng đời app.
- MemoryEngine._embeddings_model: embeddings provider đã init.
- MemoryEngine._cross_encoder: reranker singleton lazy-init.

3. [cogmem_api/engine/search/retrieval.py](cogmem_api/engine/search/retrieval.py)
- _default_graph_retriever: singleton graph retriever theo config.

4. [cogmem_api/config.py](cogmem_api/config.py)
- _cached_config: cache của get_config để tránh parse env nhiều lần.

## File-by-file map (mục đích + phụ thuộc + ai gọi)
1. [cogmem_api/__init__.py](cogmem_api/__init__.py)
- Vai trò: export package-level API (MemoryEngine/version).
- Ai gọi: server, API layer.

2. [cogmem_api/config.py](cogmem_api/config.py)
- Vai trò: parse/normalize toàn bộ COGMEM_API_* env.
- Phụ thuộc: os, dataclasses.
- Ai gọi: hầu hết modules engine/runtime.

3. [cogmem_api/models.py](cogmem_api/models.py)
- Vai trò: schema SQLAlchemy cho documents/memory_units/entities/links/banks.
- Ai gọi: memory_engine bootstrap + retain/search query layer.

4. [cogmem_api/pg0.py](cogmem_api/pg0.py)
- Vai trò: EmbeddedPostgres lifecycle khi database_url=pg0.
- Ai gọi: MemoryEngine.__init__/initialize/close.

5. [cogmem_api/main.py](cogmem_api/main.py)
- Vai trò: CLI entrypoint và uvicorn bootstrap.

6. [cogmem_api/server.py](cogmem_api/server.py)
- Vai trò: khởi tạo singleton engine + app object.

7. [cogmem_api/api/__init__.py](cogmem_api/api/__init__.py)
- Vai trò: chọn loại API app (hiện tại là HTTP).

8. [cogmem_api/api/http.py](cogmem_api/api/http.py)
- Vai trò: request/response models + routes health/version/retain/recall.
- Hàm quan trọng: _build_retain_payload, _parse_query_timestamp, create_app.

9. [cogmem_api/engine/db_utils.py](cogmem_api/engine/db_utils.py)
- Vai trò: retry_with_backoff + acquire_with_retry cho mọi DB operation.

10. [cogmem_api/engine/embeddings.py](cogmem_api/engine/embeddings.py)
- Vai trò: abstraction và provider embeddings.
- Class chính: Embeddings, DeterministicEmbeddings, LocalSTEmbeddings, OpenAIEmbeddings.
- Factory: create_embeddings_from_env.

11. [cogmem_api/engine/llm_wrapper.py](cogmem_api/engine/llm_wrapper.py)
- Vai trò: gọi LLM endpoint và parse JSON output.
- Class chính: LLMConfig.call.

12. [cogmem_api/engine/cross_encoder.py](cogmem_api/engine/cross_encoder.py)
- Vai trò: abstraction cross-encoder local/remote/passthrough.
- Factory: create_cross_encoder_from_env.

13. [cogmem_api/engine/response_models.py](cogmem_api/engine/response_models.py)
- Vai trò: dataclasses dùng chung cho memory facts và token usage.

14. [cogmem_api/engine/memory_engine.py](cogmem_api/engine/memory_engine.py)
- Vai trò: orchestration root cho init/health/retain/recall.
- Đây là file trung tâm của runtime behavior.

15. [cogmem_api/engine/retain/types.py](cogmem_api/engine/retain/types.py)
- Vai trò: data contracts và normalize helpers cho retain.

16. [cogmem_api/engine/retain/chunk_storage.py](cogmem_api/engine/retain/chunk_storage.py)
- Vai trò: lưu chunks vào bảng chunks, map chunk_index -> chunk_id.

17. [cogmem_api/engine/retain/embedding_processing.py](cogmem_api/engine/retain/embedding_processing.py)
- Vai trò: augment text với date và gọi embedding batch.

18. [cogmem_api/engine/retain/embedding_utils.py](cogmem_api/engine/retain/embedding_utils.py)
- Vai trò: deterministic embedding fallback path.

19. [cogmem_api/engine/retain/entity_processing.py](cogmem_api/engine/retain/entity_processing.py)
- Vai trò: resolve entities và tạo entity links.

20. [cogmem_api/engine/retain/fact_extraction.py](cogmem_api/engine/retain/fact_extraction.py)
- Vai trò: extraction layer lớn nhất, gồm LLM mode + fallback parsing.

21. [cogmem_api/engine/retain/fact_storage.py](cogmem_api/engine/retain/fact_storage.py)
- Vai trò: ghi facts vào memory_units và bảo đảm bank tồn tại.

22. [cogmem_api/engine/retain/link_creation.py](cogmem_api/engine/retain/link_creation.py)
- Vai trò: materialize temporal/semantic/entity/causal/s_r_link/a_o_causal/transition edges.

23. [cogmem_api/engine/retain/link_utils.py](cogmem_api/engine/retain/link_utils.py)
- Vai trò: helpers build links và fetch event dates.

24. [cogmem_api/engine/retain/orchestrator.py](cogmem_api/engine/retain/orchestrator.py)
- Vai trò: điều phối retain end-to-end trong một transaction.

25. [cogmem_api/engine/query_analyzer.py](cogmem_api/engine/query_analyzer.py)
- Vai trò: classify intent + extract temporal constraints + adaptive weights.

26. [cogmem_api/engine/search/types.py](cogmem_api/engine/search/types.py)
- Vai trò: RetrievalResult/MergedCandidate/ScoredResult contracts.

27. [cogmem_api/engine/search/tags.py](cogmem_api/engine/search/tags.py)
- Vai trò: parse/filter tags và boolean tag groups.

28. [cogmem_api/engine/search/fusion.py](cogmem_api/engine/search/fusion.py)
- Vai trò: RRF merge logic.

29. [cogmem_api/engine/search/graph_retrieval.py](cogmem_api/engine/search/graph_retrieval.py)
- Vai trò: GraphRetriever interface + BFS implementation.

30. [cogmem_api/engine/search/link_expansion_retrieval.py](cogmem_api/engine/search/link_expansion_retrieval.py)
- Vai trò: graph strategy kiểu link expansion.

31. [cogmem_api/engine/search/mpfp_retrieval.py](cogmem_api/engine/search/mpfp_retrieval.py)
- Vai trò: MPFP strategy cho pattern multi-hop traversal.

32. [cogmem_api/engine/search/reranking.py](cogmem_api/engine/search/reranking.py)
- Vai trò: cross-encoder rerank và combined scoring.

33. [cogmem_api/engine/search/retrieval.py](cogmem_api/engine/search/retrieval.py)
- Vai trò: trung tâm recall orchestration across all channels.

34. [cogmem_api/engine/search/temporal_extraction.py](cogmem_api/engine/search/temporal_extraction.py)
- Vai trò: wrapper gọi query analyzer cho temporal extraction.

35. [cogmem_api/engine/search/trace.py](cogmem_api/engine/search/trace.py)
- Vai trò: Pydantic schemas cho trace payload.

36. [cogmem_api/engine/search/tracer.py](cogmem_api/engine/search/tracer.py)
- Vai trò: collector ghi lại quá trình retrieval runtime.

37. [cogmem_api/engine/search/think_utils.py](cogmem_api/engine/search/think_utils.py)
- Vai trò: tiện ích build prompt/reflect style cũ (legacy-compatible utilities).

38. [cogmem_api/engine/reflect/agent.py](cogmem_api/engine/reflect/agent.py)
- Vai trò: lazy synthesis entrypoint.

39. [cogmem_api/engine/reflect/models.py](cogmem_api/engine/reflect/models.py)
- Vai trò: contracts cho evidence và synthesis result.

40. [cogmem_api/engine/reflect/prompts.py](cogmem_api/engine/reflect/prompts.py)
- Vai trò: build prompt phản hồi từ evidence.

41. [cogmem_api/engine/reflect/tools.py](cogmem_api/engine/reflect/tools.py)
- Vai trò: normalize candidates thành evidence dùng được cho reflect.

## Verify commands
1. uv run python tests/artifacts/test_task716_tutorial_framework.py
2. uv run python tests/artifacts/test_task717_tutorial_core.py
3. uv run python tests/artifacts/test_task718_function_inventory.py
4. uv run python tests/artifacts/test_task719_function_deep_dive.py
5. uv run python -c "import json;print(len(json.load(open('tutorials/functions/function-inventory.json','r',encoding='utf-8'))))"
