# T7.1 - Idea Coverage Matrix (CogMem Migration Readiness)

## Scope
- Đối chiếu implementation hiện tại với ý tưởng trong `docs/CogMem-Idea.md`, tập trung phần 3.1 -> 3.5.
- Mức độ đánh giá theo 3 trạng thái:
  - `FULL`: đã có implementation và đường chạy chính.
  - `PARTIAL`: đã có implementation một phần, còn lệch/gap cần xử lý.
  - `MISSING`: chưa có implementation rõ ràng.

## Mapping Rule
- Đơn vị đối chiếu: Contribution -> module -> function/property.
- Bằng chứng phải trỏ đến symbol cụ thể trong code (`class`, `def`, thuộc tính model, hằng số config).
- Không tính phần benchmark eval diện rộng trong T7.1 (đã dời sang track sau).

## Coverage Summary

| Contribution | Idea target | Current status | Kết luận nhanh |
|---|---|---|---|
| C1 - 6 networks + 7 edge types | Có graph nhận thức đầy đủ + transition typing | `PARTIAL` | Schema/retain đã đúng hướng, nhưng còn logic legacy observation và mismatch alias link causal trong retrieval |
| C2 - Lossless metadata | Lưu và dùng `raw_snippet` end-to-end | `FULL` | Có từ schema -> retain storage -> recall -> reflect evidence |
| C3 - SUM + cycle guards | Episodic buffer SUM, có 3 guard và được áp dụng ở đường chạy retrieval chính | `PARTIAL` | SUM+guards đã có trong `BFSGraphRetriever`, nhưng default retriever hiện tại là `link_expansion` |
| C4 - Adaptive query routing | Dynamic RRF theo query type, ưu tiên đúng network theo loại câu hỏi | `PARTIAL` | Có classify + dynamic weights, nhưng chưa thấy fact-type/status filtering đầy đủ cho prospective |
| C5 - Hierarchical KG | Abstract/Basic/Specific levels | `MISSING` | Chưa có schema, migration, retrieval hooks cho hierarchy |

## Detailed Matrix

### C1 - Cognitively-Grounded Memory Graph (6 Networks + 7 Edge Types)

| Requirement | Status | Evidence (module -> function/property) | Gap |
|---|---|---|---|
| 6 fact/network types: world, experience, opinion, habit, intention, action_effect | `FULL` | `cogmem_api/models.py`: `MemoryUnit.fact_type`, `MemoryUnit.network_type`, check constraints `memory_units_fact_type_check`, `memory_units_network_type_check`; `cogmem_api/engine/retain/types.py`: `COGMEM_FACT_TYPES` | - |
| 7 edge types + typed transition | `FULL` | `cogmem_api/models.py`: `MemoryLink.link_type`, `MemoryLink.transition_type`, constraints `memory_links_link_type_check`, `memory_links_transition_type_*`; `cogmem_api/engine/retain/link_creation.py`: `create_habit_sr_links_batch`, `create_transition_links_batch`, `create_action_effect_links_batch` | - |
| Intention lifecycle transitions (`fulfilled_by`, `abandoned`, `triggered`, `enabled_by`) | `PARTIAL` | `cogmem_api/engine/retain/types.py`: `TRANSITION_EDGE_RULES`; `cogmem_api/engine/retain/link_creation.py`: bỏ qua `abandoned` đúng theo status-only rule | Chưa có cơ chế query-time riêng cho intention `status=planning` khi hỏi prospective |
| Observation/consolidation đã loại bỏ khỏi đường chạy CogMem | `PARTIAL` | `cogmem_api/engine/memory_engine.py`: recall sử dụng `COGMEM_FACT_TYPES` (không có observation) | Còn nhánh legacy observation trong `cogmem_api/engine/search/link_expansion_retrieval.py` và mô tả fact_type cũ trong một số docstring |

### C2 - Lossless Node Metadata (Raw State Snippets)

| Requirement | Status | Evidence (module -> function/property) | Gap |
|---|---|---|---|
| Có cột `raw_snippet` trong schema | `FULL` | `cogmem_api/models.py`: `MemoryUnit.raw_snippet`; `cogmem_api/alembic/versions/20260330_0001_t1_2_schema_extensions.py`: add column `raw_snippet` | - |
| Retain lưu `raw_snippet` nhất quán | `FULL` | `cogmem_api/engine/retain/types.py`: `sanitize_raw_snippet`; `cogmem_api/engine/retain/fact_storage.py`: `_prepare_fact_for_storage`, `insert_facts_batch`; `cogmem_api/engine/retain/fact_extraction.py`: gán `raw_snippet=content.content` | - |
| Recall/reflect dùng `raw_snippet` cho lazy synthesis | `FULL` | `cogmem_api/engine/memory_engine.py`: payload kết quả recall có `raw_snippet`; `cogmem_api/engine/reflect/tools.py`: `to_reflect_evidence` map `raw_snippet`; `cogmem_api/engine/reflect/agent.py`: inject raw evidence vào context | - |

### C3 - Episodic Buffer SUM + Cycle Guards

| Requirement | Status | Evidence (module -> function/property) | Gap |
|---|---|---|---|
| SUM spreading activation | `PARTIAL` | `cogmem_api/engine/search/graph_retrieval.py`: `BFSGraphRetriever._retrieve_with_conn` cộng dồn activation (không dùng MAX) và clip saturation | SUM đã có ở BFS, nhưng đường chạy default retrieval hiện tại là `link_expansion` (`cogmem_api/config.py`: `DEFAULT_GRAPH_RETRIEVER = "link_expansion"`) |
| Refractory guard | `FULL` | `cogmem_api/engine/search/graph_retrieval.py`: `refractory_steps`, `last_fired_step` | - |
| Firing quota guard | `FULL` | `cogmem_api/engine/search/graph_retrieval.py`: `firing_quota`, `firing_count` | - |
| Saturation guard (`A_max`) | `FULL` | `cogmem_api/engine/search/graph_retrieval.py`: `activation_saturation` và clip activation | - |

### C4 - Adaptive Query Routing

| Requirement | Status | Evidence (module -> function/property) | Gap |
|---|---|---|---|
| Query classification + dynamic channel weights | `FULL` | `cogmem_api/engine/query_analyzer.py`: `QueryType`, `_ADAPTIVE_RRF_WEIGHTS`, `classify_query_type`, `get_adaptive_rrf_weights` | - |
| RRF fusion áp dụng trong retrieval pipeline | `FULL` | `cogmem_api/engine/search/retrieval.py`: `resolve_query_routing`, `retrieve_all_fact_types_parallel`, `fuse_parallel_results`; `cogmem_api/engine/search/fusion.py`: `weighted_reciprocal_rank_fusion` | - |
| Prospective/Causal route có ràng buộc retrieval theo status/network đúng ý tưởng | `PARTIAL` | Đã có type `prospective`/`causal` và weights trong `query_analyzer.py` | Chưa thấy filter `intention status=planning` trên đường query prospective; chưa thấy ưu tiên trực tiếp Action-Effect/Transition ở cấp filter truy vấn |
| Đồng bộ link-type cho causal traversal | `PARTIAL` | Retain tạo `link_type='causal'` tại `create_causal_links_batch` | Một số truy vấn search vẫn lọc theo alias cũ (`causes`, `caused_by`, `enables`, `prevents`) trong `retrieval.py` và `link_expansion_retrieval.py` |

### C5 - Hierarchical Knowledge Graph (Exploratory)

| Requirement | Status | Evidence (module -> function/property) | Gap |
|---|---|---|---|
| Cấp level Abstract/Basic/Specific trong schema | `MISSING` | Chưa tìm thấy cột/enum hierarchy trong `cogmem_api/models.py` | Cần bổ sung schema + migration |
| Retrieval aware theo hierarchy | `MISSING` | Chưa tìm thấy routing/filter theo hierarchy trong `cogmem_api/engine/search/*` | Cần bổ sung retrieval hooks + ranking strategy |
| Mapping retain sang hierarchy | `MISSING` | Chưa tìm thấy parser/mapper hierarchy trong `cogmem_api/engine/retain/*` | Cần bổ sung rule map facts -> hierarchy level |

## Overall Readiness (for T7.1)
- Tổng quan: `PARTIAL`.
- Đạt được: C2 và phần lớn C1/C3/C4.
- Chưa đạt để claim migration complete theo Idea:
  1. C1/C4: dọn dẹp legacy observation branch và đồng bộ causal link traversal.
  2. C3: quyết định đường chạy graph mặc định cho SUM path (hoặc nâng cấp link_expansion tương đương).
  3. C5: chưa implement (có thể để track sau nếu giữ đúng phạm vi exploratory).

## Backlog Handover to T7.2
1. Tạo gate kiểm tra import/reference để bắt các nhánh còn dùng concept observation ngoài phạm vi CogMem.
2. Tạo gate consistency cho link type: writer (`causal`) và reader (search traversal) phải đồng bộ alias.
3. Tạo gate routing cho query prospective: có filtering intention status planning và ưu tiên transition evidence.
4. Chốt policy graph retriever mặc định: BFS (SUM guards) hoặc link_expansion có equivalent guard strategy.