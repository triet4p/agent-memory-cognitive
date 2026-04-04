# Search Pipeline Modules

## Purpose
- Tài liệu hóa retrieval intelligence stack: query analysis, 4-channel retrieval, fusion, reranking, tracing.
- Cung cấp module-level map cho đường chạy recall trước khi vào S18 function deep dive.

## Inputs
- Query text, query embedding, fact types, thinking budget.
- Optional temporal reference date, tags, tag groups.
- Graph retriever policy từ config.

## Outputs
- `MultiFactTypeRetrievalResult` và `ParallelRetrievalResult` theo fact type.
- Candidate list đã fuse theo weighted-RRF.
- Reranked outputs với `combined_score`.

## Top-down level
- Module

## Prerequisites
- `tutorials/README.md`
- `tutorials/modules/engine-core-services.md`
- `tutorials/modules/adapters-llm-embeddings-reranker.md`

## Module responsibility
- `cogmem_api/engine/query_analyzer.py`
  - Trách nhiệm: classify query type và build adaptive RRF weights.
  - Data contracts: `QueryType`, `TemporalConstraint`, `QueryAnalysis`.
- `cogmem_api/engine/search/__init__.py`
  - Trách nhiệm: export các data types và search APIs chính.
- `cogmem_api/engine/search/retrieval.py`
  - Trách nhiệm: orchestrator retrieval đa channel đa fact-type.
  - Inbound: `MemoryEngine.recall_async`.
  - Outbound: semantic+bm25 retrieval, graph retriever, temporal retrieval, fuse.
  - Error boundaries: prospective filter mismatch, empty fact types routing.
- `cogmem_api/engine/search/fusion.py`
  - Trách nhiệm: weighted reciprocal rank fusion và score normalization.
- `cogmem_api/engine/search/reranking.py`
  - Trách nhiệm: rerank bằng cross encoder + recency/temporal boosts.
- `cogmem_api/engine/search/graph_retrieval.py`
  - Trách nhiệm: abstract interface + BFS retriever implementation.
- `cogmem_api/engine/search/link_expansion_retrieval.py`
  - Trách nhiệm: link expansion graph traversal dựa trên semantic seeds.
- `cogmem_api/engine/search/mpfp_retrieval.py`
  - Trách nhiệm: MPFP traversal, pattern sync hops, RRF fusion nội bộ MPFP.
- `cogmem_api/engine/search/temporal_extraction.py`
  - Trách nhiệm: helper trích temporal constraints qua analyzer.
- `cogmem_api/engine/search/tags.py`
  - Trách nhiệm: parse tags expressions và build SQL clauses/filter runtime.
- `cogmem_api/engine/search/types.py`
  - Trách nhiệm: typed retrieval/rerank structures (`RetrievalResult`, `MergedCandidate`, `ScoredResult`, `MPFPTimings`).
- `cogmem_api/engine/search/trace.py`
  - Trách nhiệm: pydantic schema cho trace payload chi tiết.
- `cogmem_api/engine/search/tracer.py`
  - Trách nhiệm: tracer collector cho retrieval lifecycle.
- `cogmem_api/engine/search/think_utils.py`
  - Trách nhiệm: prompt assembly + static reflect helper cho think path legacy-compatible.

## Function inventory (public/private)
- Public functions/classes:
  - `query_analyzer.py`: `get_adaptive_rrf_weights`, `classify_query_type`, `build_query_analysis`, `QueryAnalyzer`, `DateparserQueryAnalyzer`, `TransformerQueryAnalyzer`
  - `retrieval.py`: `resolve_query_routing`, `fuse_parallel_results`, `get_default_graph_retriever`, `set_default_graph_retriever`, `retrieve_semantic_bm25_combined`, `retrieve_temporal_combined`, `retrieve_all_fact_types_parallel`
  - `fusion.py`: `weighted_reciprocal_rank_fusion`, `reciprocal_rank_fusion`, `normalize_scores_on_deltas`
  - `reranking.py`: `apply_combined_scoring`, `CrossEncoderReranker`
  - `graph_retrieval.py`: `GraphRetriever`, `BFSGraphRetriever`
  - `link_expansion_retrieval.py`: `LinkExpansionRetriever`
  - `mpfp_retrieval.py`: `MPFPGraphRetriever`, `mpfp_traverse_hop_synchronized`, `mpfp_traverse_async`, `rrf_fusion`, `fetch_memory_units_by_ids`
  - `temporal_extraction.py`: `get_default_analyzer`, `extract_temporal_constraint`
  - `tags.py`: `build_tags_where_clause`, `build_tags_where_clause_simple`, `build_tag_groups_where_clause`, `filter_results_by_tags`, `filter_results_by_tag_groups`
  - `types.py`: `MPFPTimings`, `RetrievalResult`, `MergedCandidate`, `ScoredResult`
  - `trace.py`: `SearchTrace` và toàn bộ trace schemas
  - `tracer.py`: `SearchTracer`
  - `think_utils.py`: `build_think_prompt`, `get_system_message`, `reflect`
- Private/internal helpers:
  - `retrieval.py`: `_select_fact_types_for_query`, `_apply_query_type_evidence_priority`, `_collect_intention_result_ids`, `_resolve_planning_intention_ids`, `_filter_prospective_results`
  - `tags.py`: `_parse_tags_match`, `_build_group_clause`, `_match_group`
  - `mpfp_retrieval.py`: `_init_pattern_state`, `_execute_hop`, `_finalize_pattern`
  - `think_utils.py`: format helpers (`describe_trait_level`, `format_facts_for_prompt`, ...)

## Failure modes
- Analyzer fail hoặc classifier lệch làm weights/routing chưa tối ưu.
- Graph retriever trả rỗng khi seed yếu hoặc budget thấp.
- Cross-encoder unavailable -> rerank degrade/passthrough.
- Temporal query không parse được -> fallback semantic routing.

## Verify commands
- `uv run python tests/artifacts/test_task717_tutorial_core.py`
- `Select-String -Path cogmem_api/engine/query_analyzer.py,cogmem_api/engine/search/*.py -Pattern "def retrieve_all_fact_types_parallel|def fuse_parallel_results|class GraphRetriever|class MPFPGraphRetriever|class CrossEncoderReranker|class SearchTracer"`