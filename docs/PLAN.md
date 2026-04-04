## PLAN - CogMem Migration (Unified, Full Trace)

## 1) Mục tiêu của bản PLAN này
Bản PLAN này hợp nhất hai phần trong một tài liệu duy nhất:
1. Lịch sử triển khai đã hoàn tất (Sprint 0 -> Sprint 7.3, bao gồm Backfill B1 -> B5).
2. Lộ trình còn lại theo ưu tiên mới: xóa hindsight_api trước, nâng coverage C1-C4 lên FULL, sau đó mới mở phase tutorial.

Mục tiêu điều phối:
1. Không mất dấu lịch sử triển khai trước đây.
2. Không phân mảnh phase/sprint như bản cũ.
3. Có entry gate/exit gate rõ cho từng sprint còn lại.

---

## 2) Trạng thái hiện tại (baseline)
1. Coverage matrix hiện tại tại docs/migration_idea_coverage_matrix.md:
- C1: PARTIAL
- C2: FULL
- C3: PARTIAL
- C4: PARTIAL
- C5: MISSING (deferred)
2. Readiness đã có:
- reports/hindsight_removal_readiness.md
- docs/hindsight_removal_playbook.md
3. Quyết định phạm vi đang khóa:
- Delete scope đợt tới: chỉ xóa thư mục hindsight_api.
- Full gate trước tutorial: bắt buộc C1-C4 = FULL.
- C5 để track sau, không chặn tutorial trong vòng này.

---

## 3) Lịch sử triển khai đã hoàn tất (không xóa)

### 3.1 Sprint 0 - Khởi tạo quy ước và inventory
1. T0.1: baseline + mapping module nguồn.
2. T0.2: convention artifact + test path.

Artifacts chính:
- logs/task_001_summary.md
- logs/task_002_summary.md
- tests/artifacts/test_task001_inventory.py
- tests/artifacts/test_task002_artifact_conventions.py

### 3.2 Sprint 1 - Nền tảng schema/engine
1. T1.1: fork schema lõi sang cogmem_api.
2. T1.2: mở rộng schema theo Idea (raw_snippet, 6 networks, transition typing).
3. T1.3: fork db_utils + memory_engine khung.

Artifacts chính:
- logs/task_101_summary.md -> logs/task_103_summary.md
- tests/artifacts/test_task101_schema_fork.py
- tests/artifacts/test_task102_schema_extensions.py
- tests/artifacts/test_task103_engine_bootstrap.py

### 3.3 Sprint 2 - Retain pipeline + mạng mới
1. T2.1: retain baseline (orchestrator/extraction/storage/entity/link).
2. T2.2: Habit + S-R links.
3. T2.3: Intention + lifecycle transitions.
4. T2.4: Action-Effect + A-O causal edges.

Artifacts chính:
- logs/task_201_summary.md -> logs/task_204_summary.md
- tests/artifacts/test_task201_retain_baseline.py
- tests/artifacts/test_task202_habit_network.py
- tests/artifacts/test_task203_intention_lifecycle.py
- tests/artifacts/test_task204_action_effect.py

### 3.4 Sprint 3 - Retrieval intelligence
1. T3.1: search baseline fork.
2. T3.2: SUM + cycle guards.
3. T3.3: adaptive query routing.

Artifacts chính:
- logs/task_301_summary.md -> logs/task_303_summary.md
- tests/artifacts/test_task301_search_fork.py
- tests/artifacts/test_task302_sum_activation.py
- tests/artifacts/test_task303_adaptive_router.py

### 3.5 Sprint 4 - Reflect
1. T4.1: reflect lazy synthesis theo phạm vi CogMem.

Artifacts chính:
- logs/task_401_summary.md
- tests/artifacts/test_task401_reflect_lazy_synthesis.py

### 3.6 Sprint 5 - Runtime + Docker
1. T5.1: runtime entrypoints.
2. T5.2: packaging/config contract.
3. T5.3: Docker assets (standalone + external-pg).
4. T5.4: smoke/runbook docker.

Artifacts chính:
- logs/task_501_summary.md -> logs/task_504_summary.md
- tests/artifacts/test_task501_runtime_entrypoints.py
- tests/artifacts/test_task502_packaging_config.py
- tests/artifacts/test_task503_docker_assets.py
- tests/artifacts/test_task504_docker_smoke_contract.py

### 3.7 Sprint 6 - Completeness trước track eval
1. T6.1: retain prompt parity.
2. T6.2: retain behavior parity.
3. T6.3: eval harness E1-E7 (pipeline có sẵn, chưa dùng làm gate vòng này).

Artifacts chính:
- logs/task_601_summary.md -> logs/task_603_summary.md
- tests/artifacts/test_task601_retain_prompt_parity.py
- tests/artifacts/test_task602_retain_behavior_parity.py
- tests/artifacts/test_task603_eval_harness.py

### 3.8 Backfill B1-B5 (đã triển khai)
1. B1: config contract parity.
2. B2: retain LLM path + prompt parity.
3. B3: runtime API completeness.
4. B4: retrieval quality parity.
5. B5: docker run contract parity.

Artifacts chính:
- logs/task_611_summary.md -> logs/task_615_summary.md
- tests/artifacts/test_task611_config_contract.py
- tests/artifacts/test_task612_retain_prompt_parity.py
- tests/artifacts/test_task613_runtime_api_e2e.py
- tests/artifacts/test_task614_retrieval_quality_contract.py
- tests/artifacts/test_task615_docker_runtime_contract.py

### 3.9 Sprint 7 readiness (đã hoàn tất)
1. T7.1: coverage matrix.
2. T7.2: readiness gate.
3. T7.3: removal playbook.

Artifacts chính:
- docs/migration_idea_coverage_matrix.md
- reports/hindsight_removal_readiness.md
- docs/hindsight_removal_playbook.md
- logs/task_701_summary.md, logs/task_702_summary.md, logs/task_703_summary.md
- tests/artifacts/test_task701_idea_coverage_matrix.py
- tests/artifacts/test_task702_hindsight_removal_gate.py
- tests/artifacts/test_task703_removal_playbook_contract.py

---

## 4) Lộ trình còn lại (hợp nhất, dễ theo dõi)

## Phase A - Delete-first
### Sprint S11 - Delete hindsight_api only
Entry gate:
1. T7.1/T7.2/T7.3 đã PASS.

Atomic tasks:
1. S11.1: pre-delete snapshot các điểm phụ thuộc folder cũ.
2. S11.2: xóa thư mục hindsight_api.
3. S11.3: ổn định artifact tests bị vỡ do check tồn tại hindsight_api.

Outputs bắt buộc:
1. reports/hindsight_delete_only_report.md
2. logs/task_704_summary.md
3. tests/artifacts/test_task704_delete_hindsight_only.py

Exit gate:
1. Không còn thư mục hindsight_api.
2. Runtime cogmem_api không có import hindsight_api.
3. Regression pack readiness PASS.

## Phase B - Coverage Closure (C1-C4 -> FULL)
### Sprint S12 - Close C1 to FULL
Atomic tasks:
1. S12.1: dọn legacy observation branch ở search path theo phạm vi CogMem hiện tại.
2. S12.2: đồng bộ causal link-type writer/reader trong retrieval/search.
3. S12.3: cập nhật matrix + gate test C1.

Outputs:
1. docs/migration_idea_coverage_matrix.md
2. logs/task_705_summary.md
3. tests/artifacts/test_task705_c1_full_gate.py

Exit gate:
1. C1 = FULL.

### Sprint S13 - Close C3 to FULL
Atomic tasks:
1. S13.1: chốt policy đường chạy graph mặc định cho SUM + 3 guards.
2. S13.2: đồng bộ config/runtime để policy có hiệu lực thật.
3. S13.3: bổ sung test anti-loop + multi-hop accumulation.

Outputs:
1. docs/migration_idea_coverage_matrix.md
2. logs/task_706_summary.md
3. tests/artifacts/test_task706_c3_sum_default_gate.py

Exit gate:
1. C3 = FULL.

### Sprint S14 - Close C4 to FULL
Atomic tasks:
1. S14.1: prospective filter theo intention.status=planning.
2. S14.2: ưu tiên evidence Action-Effect/Transition cho causal/prospective queries.
3. S14.3: cập nhật matrix + gate test C4.

Outputs:
1. docs/migration_idea_coverage_matrix.md
2. logs/task_707_summary.md
3. tests/artifacts/test_task707_c4_adaptive_full_gate.py

Exit gate:
1. C4 = FULL.

### Sprint S15 - Full Gate trước tutorial
Atomic tasks:
1. S15.1: re-audit matrix, xác nhận C1-C4 đều FULL.
2. S15.2: xuất chứng chỉ mở tutorial.
3. S15.3: regression batch readiness + coverage.

Outputs:
1. reports/pre_tutorial_full_gate.md
2. logs/task_708_summary.md
3. tests/artifacts/test_task708_pre_tutorial_full_gate.py

Exit gate:
1. pre_tutorial_full_gate xác nhận C1-C4 đều FULL.

## Phase C - Tutorial (unlock sau S15 PASS)
### Sprint S16 - Tutorial Framework
1. Scaffold tutorials + index + learning-path + module-map.

### Sprint S17 - Tutorial Core
1. Tutorials cho config/models/memory_engine/retain/search/reflect/api.

### Sprint S18 - Tutorial Non-core + Capstone
1. Tutorials cho providers/db-utils/scripts/docker/migrations.
2. Capstone walkthrough retain -> recall -> response.

---

## 5) Bảng tiến độ hợp nhất
| Nhóm | Sprint | Mục tiêu | Trạng thái |
|---|---|---|---|
| Historical | Sprint 0 -> Sprint 7.3 | Đã triển khai và có artifact | Done |
| Remaining | S11 | Delete-first | Planned |
| Remaining | S12 | Close C1 | Planned |
| Remaining | S13 | Close C3 | Planned |
| Remaining | S14 | Close C4 | Planned |
| Remaining | S15 | Full Gate trước tutorial | Planned |
| Tutorial | S16 | Tutorial framework | Locked |
| Tutorial | S17 | Tutorial core | Locked |
| Tutorial | S18 | Tutorial non-core + capstone | Locked |

---

## 6) Canonical execution order
Historical completed:
Sprint 0 -> Sprint 1 -> Sprint 2 -> Sprint 3 -> Sprint 4 -> Sprint 5 -> Sprint 6 -> Backfill B1-B5 -> Sprint 7

Remaining required:
S11 -> S12 -> S13 -> S14 -> S15 -> S16 -> S17 -> S18

Hard rules:
1. Không vào S16 nếu S15 chưa PASS.
2. C5 và eval mở rộng ở track sau, không chặn tutorial trong vòng hiện tại.

---

## 7) Verification standard (mọi sprint)
1. Drift Check: đối chiếu docs/CogMem-Idea.md và coverage matrix.
2. Behavioral Testing: mỗi sprint có artifact test chạy độc lập.
3. Isolation Check: không có import runtime trái phạm vi trong cogmem_api.
4. Sprint Gate: sprint sau chỉ bắt đầu khi sprint trước PASS exit gate.

---

## 8) Relevant files
1. docs/migration_idea_coverage_matrix.md
2. reports/hindsight_removal_readiness.md
3. docs/hindsight_removal_playbook.md
4. docs/CogMem-Idea.md
5. pyproject.toml
6. cogmem_api/engine/search/link_expansion_retrieval.py
7. cogmem_api/engine/search/retrieval.py
8. cogmem_api/engine/search/graph_retrieval.py
9. cogmem_api/config.py
10. cogmem_api/engine/query_analyzer.py
11. tests/artifacts/test_task701_idea_coverage_matrix.py
12. tests/artifacts/test_task702_hindsight_removal_gate.py
13. tests/artifacts/test_task703_removal_playbook_contract.py
