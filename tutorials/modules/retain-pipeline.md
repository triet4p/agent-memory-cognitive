# Retain Pipeline Modules

## Purpose
- Tài liệu hóa retain pipeline theo từng stage: chunk -> extraction -> embedding -> entity -> storage -> links.
- Chỉ rõ contract dữ liệu trung gian giữa các module retain.

## Inputs
- `contents_dicts` từ API đã normalize.
- Embeddings model + optional LLM config.
- DB connection pool và schema.

## Outputs
- `unit_ids` theo content index.
- Token usage từ extraction path.
- Memory links gồm temporal/semantic/causal/s_r_link/transition/a_o_causal.

## Top-down level
- Module

## Prerequisites
- `tutorials/README.md`
- `tutorials/modules/engine-core-services.md`
- `tutorials/flows/retain-recall-reflect-response.md`

## Module responsibility
- `cogmem_api/engine/retain/__init__.py`
  - Trách nhiệm: export `retain_batch`.
- `cogmem_api/engine/retain/orchestrator.py`
  - Trách nhiệm: điều phối retain end-to-end trong transaction.
  - Inbound: `MemoryEngine.retain_batch_async`.
  - Outbound: gọi extraction, embedding, storage, entity, link creation.
- `cogmem_api/engine/retain/fact_extraction.py`
  - Trách nhiệm: trích xuất facts từ content bằng LLM hoặc fallback heuristic.
  - Data contracts: `ExtractedFact`, `ChunkMetadata`, `CausalRelation`, `ActionEffectRelation`, `TransitionRelation`.
  - Error boundary: LLM path lỗi -> fallback split-based extraction.
- `cogmem_api/engine/retain/embedding_processing.py`
  - Trách nhiệm: augment text với date rồi gọi embeddings batch.
- `cogmem_api/engine/retain/embedding_utils.py`
  - Trách nhiệm: deterministic embedding fallback utility.
- `cogmem_api/engine/retain/fact_storage.py`
  - Trách nhiệm: ensure bank và insert facts vào `memory_units`.
- `cogmem_api/engine/retain/entity_processing.py`
  - Trách nhiệm: normalize entities, resolve IDs, insert `unit_entities`.
- `cogmem_api/engine/retain/link_creation.py`
  - Trách nhiệm: tạo links cho các semantics temporal/semantic/causal/habit/action-effect/transition.
- `cogmem_api/engine/retain/link_utils.py`
  - Trách nhiệm: helper tính cosine/temporal neighborhood và insert links batch.
- `cogmem_api/engine/retain/chunk_storage.py`
  - Trách nhiệm: lưu raw chunks để phục vụ lossless evidence.
- `cogmem_api/engine/retain/types.py`
  - Trách nhiệm: typed contracts cho retain payload/facts/relations/entities.
  - Error boundary: normalize/coerce các giá trị metadata/status/relation-strength.

## Function inventory (public/private)
- Public functions/classes:
  - `cogmem_api/engine/retain/orchestrator.py`: `retain_batch`
  - `cogmem_api/engine/retain/fact_extraction.py`: `extract_facts_from_contents`
  - `cogmem_api/engine/retain/embedding_processing.py`: `augment_texts_with_dates`, `generate_embeddings_batch`
  - `cogmem_api/engine/retain/embedding_utils.py`: `generate_embeddings_batch`
  - `cogmem_api/engine/retain/fact_storage.py`: `ensure_bank_exists`, `insert_facts_batch`
  - `cogmem_api/engine/retain/entity_processing.py`: `process_entities_batch`, `insert_entity_links_batch`
  - `cogmem_api/engine/retain/link_creation.py`: `create_temporal_links_batch`, `create_semantic_links_batch`, `create_causal_links_batch`, `create_habit_sr_links_batch`, `create_transition_links_batch`, `create_action_effect_links_batch`
  - `cogmem_api/engine/retain/link_utils.py`: `build_temporal_links`, `build_semantic_links`, `insert_links`, `fetch_event_dates`
  - `cogmem_api/engine/retain/chunk_storage.py`: `store_chunks_batch`
  - `cogmem_api/engine/retain/types.py`: `coerce_fact_type`, `clamp_relation_strength`, `normalize_intention_status`, `sanitize_raw_snippet`, `normalize_fact_metadata`, models `RetainContent`, `ExtractedFact`, `ProcessedFact`, `EntityLink`
- Private/internal helpers:
  - `orchestrator.py`: `utcnow`, `parse_datetime_flexible`, `_maybe_transaction`, `_map_results_to_contents`
  - `fact_extraction.py`: toàn bộ nhóm `_extract_*`, `_normalize_*`, `_build_*`, `_call_llm_chunk`, `_fallback_*`
  - `entity_processing.py`: `_normalize_entity_name`, `_resolve_entity_id`
  - `types.py`: `_normalize_bool`, `_build_edge_intent_payload`

## Failure modes
- Payload đầu vào không hợp lệ hoặc trống -> không tạo facts.
- LLM extraction timeout/lỗi parse -> degrade sang fallback extraction.
- Transaction DB lỗi giữa chừng -> rollback toàn batch.
- Embedding generation lỗi -> retain fail hoặc fallback deterministic tùy call-site.

## Verify commands
- `uv run python tests/artifacts/test_task717_tutorial_core.py`
- `Select-String -Path cogmem_api/engine/retain/*.py -Pattern "def retain_batch|def extract_facts_from_contents|def insert_facts_batch|def create_.*_links_batch|class RetainContent|class ExtractedFact"`