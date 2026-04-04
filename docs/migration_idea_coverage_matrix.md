# T7.1/T7.4 - Idea Coverage Matrix (CogMem Migration Re-audit)

## Scope
- Re-audit implementation hiện tại với ý tưởng trong `docs/CogMem-Idea.md`, tập trung phần 3.1 -> 3.5.
- Cập nhật này phản ánh trạng thái sau S12/S13/S14/S15 và được kiểm tra lại theo code/runtime hiện hành.
- Mức độ đánh giá theo 3 trạng thái:
  - `FULL`: đã có implementation và đang chạy trên đường runtime chính.
  - `PARTIAL`: có implementation nhưng còn gap hành vi/runtime hoặc thiếu bằng chứng đầy đủ.
  - `MISSING`: chưa có implementation rõ ràng.

## Mapping Rule
- Đơn vị đối chiếu: Contribution -> module -> function/property.
- Bằng chứng phải trỏ đến symbol cụ thể trong code (`class`, `def`, thuộc tính model, hằng số config).
- Không tính phần benchmark eval diện rộng trong T7.1 (đã dời sang track sau).

## Coverage Summary (Re-audit)

| Contribution | Idea target | Current status | Kết luận nhanh |
|---|---|---|---|
| C1 - 6 networks + 7 edge types | Có graph nhận thức đầy đủ + transition typing | `FULL` | Schema + retain + retrieval đã đồng bộ theo CogMem; observation network không còn ở retrieval path chính |
| C2 - Lossless metadata | Lưu và dùng `raw_snippet` end-to-end | `FULL` | Có từ schema -> retain storage -> recall -> reflect evidence |
| C3 - SUM + cycle guards | Episodic buffer SUM, có 3 guard và được áp dụng ở đường chạy retrieval chính | `FULL` | `BFSGraphRetriever` dùng SUM + 3 guards và đã được khóa làm default retriever |
| C4 - Adaptive query routing | Dynamic RRF theo query type, ưu tiên đúng network theo loại câu hỏi | `FULL` | Có classify + dynamic weights + prospective planning filter + intent-aware evidence priority |
| C5 - Hierarchical KG | Abstract/Basic/Specific levels | `MISSING` | Chưa có schema, migration, retrieval hooks cho hierarchy |

## Detailed Matrix

### C1 - Cognitively-Grounded Memory Graph (6 Networks + 7 Edge Types)

| Requirement | Status | Evidence (module -> function/property) | Gap |
|---|---|---|---|
| 6 fact/network types: world, experience, opinion, habit, intention, action_effect | `FULL` | `cogmem_api/models.py`: `MemoryUnit.fact_type`, `MemoryUnit.network_type`, check constraints `memory_units_fact_type_check`, `memory_units_network_type_check`; `cogmem_api/engine/retain/types.py`: `COGMEM_FACT_TYPES` | - |
| 7 edge types + typed transition | `FULL` | `cogmem_api/models.py`: `MemoryLink.link_type`, `MemoryLink.transition_type`, constraints `memory_links_link_type_check`, `memory_links_transition_type_*`; `cogmem_api/engine/retain/link_creation.py`: `create_habit_sr_links_batch`, `create_transition_links_batch`, `create_action_effect_links_batch` | - |
| Intention lifecycle transitions (`fulfilled_by`, `abandoned`, `triggered`, `enabled_by`) | `FULL` | `cogmem_api/engine/retain/types.py`: `TRANSITION_EDGE_RULES`, `normalize_intention_status`; `cogmem_api/engine/retain/link_creation.py`: `create_transition_links_batch` (status-only cho `abandoned`); `cogmem_api/engine/search/retrieval.py`: `_resolve_planning_intention_ids`, `_filter_prospective_results` | - |
| Observation/consolidation đã loại bỏ khỏi đường chạy CogMem | `FULL` | `cogmem_api/engine/retain/types.py`: `COGMEM_FACT_TYPES` không còn `observation`; `cogmem_api/engine/search/link_expansion_retrieval.py`: không còn branch `fact_type == "observation"`; `cogmem_api/engine/reflect/tools.py`: `_SUPPORTED_FACT_TYPES` chỉ gồm 6 network CogMem | Nợ kỹ thuật nhẹ: còn naming legacy ở `think_utils.py` và mapping adapter `coerce_fact_type('observation')->'world'` để tương thích dữ liệu cũ |

### C2 - Lossless Node Metadata (Raw State Snippets)

| Requirement | Status | Evidence (module -> function/property) | Gap |
|---|---|---|---|
| Có cột `raw_snippet` trong schema | `FULL` | `cogmem_api/models.py`: `MemoryUnit.raw_snippet`; `cogmem_api/alembic/versions/20260330_0001_t1_2_schema_extensions.py`: add column `raw_snippet` | - |
| Retain lưu `raw_snippet` nhất quán | `FULL` | `cogmem_api/engine/retain/types.py`: `sanitize_raw_snippet`; `cogmem_api/engine/retain/fact_storage.py`: `_prepare_fact_for_storage`, `insert_facts_batch`; `cogmem_api/engine/retain/fact_extraction.py`: gán `raw_snippet=content.content` | - |
| Recall/reflect dùng `raw_snippet` cho lazy synthesis | `FULL` | `cogmem_api/engine/memory_engine.py`: payload kết quả recall có `raw_snippet`; `cogmem_api/engine/reflect/tools.py`: `to_reflect_evidence` map `raw_snippet`; `cogmem_api/engine/reflect/agent.py`: inject raw evidence vào context | - |

### C3 - Episodic Buffer SUM + Cycle Guards

| Requirement | Status | Evidence (module -> function/property) | Gap |
|---|---|---|---|
| SUM spreading activation | `FULL` | `cogmem_api/engine/search/graph_retrieval.py`: `BFSGraphRetriever._retrieve_with_conn` dùng `frontier_activation` cộng dồn, không dùng MAX, và clip saturation | - |
| Refractory guard | `FULL` | `cogmem_api/engine/search/graph_retrieval.py`: `refractory_steps`, `last_fired_step` | - |
| Firing quota guard | `FULL` | `cogmem_api/engine/search/graph_retrieval.py`: `firing_quota`, `firing_count` | - |
| Saturation guard (`A_max`) | `FULL` | `cogmem_api/engine/search/graph_retrieval.py`: `activation_saturation` và clip activation | - |
| SUM + guards là default runtime path | `FULL` | `cogmem_api/config.py`: `DEFAULT_GRAPH_RETRIEVER = "bfs"`, `_read_graph_retriever`; `cogmem_api/engine/search/retrieval.py`: `get_default_graph_retriever()` khởi tạo BFS với guard config | - |

### C4 - Adaptive Query Routing

| Requirement | Status | Evidence (module -> function/property) | Gap |
|---|---|---|---|
| Query classification + dynamic channel weights | `FULL` | `cogmem_api/engine/query_analyzer.py`: `QueryType`, `_ADAPTIVE_RRF_WEIGHTS`, `classify_query_type`, `get_adaptive_rrf_weights` | - |
| RRF fusion áp dụng trong retrieval pipeline | `FULL` | `cogmem_api/engine/search/retrieval.py`: `resolve_query_routing`, `retrieve_all_fact_types_parallel`, `fuse_parallel_results`; `cogmem_api/engine/search/fusion.py`: `weighted_reciprocal_rank_fusion` | - |
| Prospective route có planning filter và network routing đúng ý tưởng | `FULL` | `cogmem_api/engine/search/retrieval.py`: `_select_fact_types_for_query` (prospective -> intention), `_resolve_planning_intention_ids` (`metadata->>'intention_status'='planning'`), `_filter_prospective_results` | - |
| Causal/prospective evidence priority theo intent | `FULL` | `cogmem_api/engine/search/retrieval.py`: `_apply_query_type_evidence_priority`; causal ưu tiên `action_effect` + graph evidence, prospective ưu tiên intention + graph/temporal evidence; `cogmem_api/engine/search/link_expansion_retrieval.py`: traversal `link_type='transition'` | - |
| Đồng bộ link-type cho causal traversal | `FULL` | `cogmem_api/engine/search/retrieval.py`: temporal spreading dùng `ml.link_type IN ('temporal', 'causal')`; `cogmem_api/engine/search/link_expansion_retrieval.py`: causal traversal dùng `ml.link_type = 'causal'` | - |

### C5 - Hierarchical Knowledge Graph (Exploratory)

| Requirement | Status | Evidence (module -> function/property) | Gap |
|---|---|---|---|
| Cấp level Abstract/Basic/Specific trong schema | `MISSING` | Chưa tìm thấy cột/enum hierarchy trong `cogmem_api/models.py` | Cần bổ sung schema + migration |
| Retrieval aware theo hierarchy | `MISSING` | Chưa tìm thấy routing/filter theo hierarchy trong `cogmem_api/engine/search/*` | Cần bổ sung retrieval hooks + ranking strategy |
| Mapping retain sang hierarchy | `MISSING` | Chưa tìm thấy parser/mapper hierarchy trong `cogmem_api/engine/retain/*` | Cần bổ sung rule map facts -> hierarchy level |

## Overall Readiness (Re-audit)
- Tổng quan coverage theo Idea: `PARTIAL` (do C5 còn `MISSING`).
- Trạng thái gate mở tutorial (S15 criterion): **`PASS`** vì C1-C4 đều `FULL`.

## Sprint 16 Readiness Decision
1. **Kết luận:** `READY` để vào Sprint 16.
2. **Cơ sở:**
   - Coverage re-audit: C1/C2/C3/C4 = `FULL`.
   - Gate pack S15 đã xác nhận PASS qua các test artifacts: 705/706/707/708.
3. **Lưu ý phạm vi:** C5 (Hierarchical KG) tiếp tục để track sau, không chặn tutorial phase theo PLAN hiện tại.

## Post-S16 Backlog (không chặn)
1. C5 schema/migration cho hierarchy levels (Abstract/Basic/Specific).
2. Retrieval hooks/ranking theo hierarchy.
3. Rule map retain -> hierarchy level.
4. Dọn nợ naming legacy liên quan observation trong utility layer (không ảnh hưởng runtime gate hiện tại).