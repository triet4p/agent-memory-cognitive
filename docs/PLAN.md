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
Mục tiêu sprint:
1. Thiết lập nền tảng schema/engine trong `cogmem_api` theo nguyên tắc fork-isolated.
2. Giữ tương thích hạ tầng với nguồn HINDSIGHT, chỉ mở rộng phần nghiệp vụ theo Idea.

Atomic tasks đã hoàn tất:
1. T1.1 Fork schema lõi:
	- Phạm vi: sao chép `hindsight_api/models.py` sang `cogmem_api/models.py`, đổi namespace sang `cogmem_api`.
	- Output: `logs/task_101_summary.md`, `tests/artifacts/test_task101_schema_fork.py`.
	- Verification trọng tâm: Drift diff enum/fact/link; Behavioral import model + compile metadata tables; Isolation grep import chain không còn `hindsight_api`.
2. T1.2 Mở rộng schema theo Idea:
	- Phạm vi: thêm `raw_snippet`, mở rộng fact/network cho 6 mạng CogMem, thêm transition typing.
	- Output: migration trong `cogmem_api/alembic/versions/`, `logs/task_102_summary.md`, `tests/artifacts/test_task102_schema_extensions.py`.
	- Verification trọng tâm: migration upgrade/downgrade pass; assert cột/enum mới tồn tại đúng contract.
3. T1.3 Fork db_utils + memory_engine khung:
	- Phạm vi: bootstrap `cogmem_api/engine/db_utils.py`, `cogmem_api/engine/memory_engine.py`.
	- Output: `logs/task_103_summary.md`, `tests/artifacts/test_task103_engine_bootstrap.py`.
	- Verification trọng tâm: engine init ổn định, schema qualification đúng, không kéo dependency runtime từ `hindsight_api`.

Artifacts chính:
- `logs/task_101_summary.md` -> `logs/task_103_summary.md`
- `tests/artifacts/test_task101_schema_fork.py`
- `tests/artifacts/test_task102_schema_extensions.py`
- `tests/artifacts/test_task103_engine_bootstrap.py`

### 3.3 Sprint 2 - Retain pipeline + mạng mới
Mục tiêu sprint:
1. Fork và ổn định retain pipeline làm nền cho ingest dữ liệu hội thoại.
2. Hoàn tất các mạng nghiệp vụ mới: Habit, Intention, Action-Effect.

Atomic tasks đã hoàn tất:
1. T2.1 Retain baseline:
	- Phạm vi: fork orchestrator/extraction/storage/entity/link sang `cogmem_api/engine/retain`.
	- Output: `logs/task_201_summary.md`, `tests/artifacts/test_task201_retain_baseline.py`.
	- Verification trọng tâm: retain batch tạo node thuộc domain CogMem, không còn observation legacy.
2. T2.2 Habit + S-R links:
	- Phạm vi: thêm rule trích xuất habit và liên kết stimulus-response.
	- Output: `logs/task_202_summary.md`, `tests/artifacts/test_task202_habit_network.py`.
	- Verification trọng tâm: pattern lặp tạo habit node + edge `s_r_link` đúng entity.
3. T2.3 Intention lifecycle:
	- Phạm vi: thêm trạng thái planning/fulfilled/abandoned và các transition liên quan.
	- Output: `logs/task_203_summary.md`, `tests/artifacts/test_task203_intention_lifecycle.py`.
	- Verification trọng tâm: chuỗi planning -> fulfilled/abandoned cho kết quả node/link đúng semantics.
4. T2.4 Action-Effect + causal edges:
	- Phạm vi: parser precondition-action-outcome, tạo A-O causal edges.
	- Output: `logs/task_204_summary.md`, `tests/artifacts/test_task204_action_effect.py`.
	- Verification trọng tâm: causal utterance tạo action-effect node, edge, confidence flags đúng contract.

Artifacts chính:
- `logs/task_201_summary.md` -> `logs/task_204_summary.md`
- `tests/artifacts/test_task201_retain_baseline.py`
- `tests/artifacts/test_task202_habit_network.py`
- `tests/artifacts/test_task203_intention_lifecycle.py`
- `tests/artifacts/test_task204_action_effect.py`

### 3.4 Sprint 3 - Retrieval intelligence
Mục tiêu sprint:
1. Hoàn chỉnh retrieval stack từ baseline tới logic lan truyền nâng cao.
2. Đưa adaptive query routing vào đường chạy recall.

Atomic tasks đã hoàn tất:
1. T3.1 Search baseline fork:
	- Phạm vi: fork retrieval/graph_retrieval/link_expansion/fusion/reranking/types.
	- Output: `logs/task_301_summary.md`, `tests/artifacts/test_task301_search_fork.py`.
	- Verification trọng tâm: recall smoke 4-channel chạy end-to-end.
2. T3.2 SUM + 3 cycle guards:
	- Phạm vi: thay propagation MAX bằng SUM và thêm refractory, firing quota, saturation.
	- Output: `logs/task_302_summary.md`, `tests/artifacts/test_task302_sum_activation.py`.
	- Verification trọng tâm: anti-loop pass, multi-hop tích lũy evidence ổn định.
3. T3.3 Adaptive query routing:
	- Phạm vi: phân loại query type và áp trọng số RRF theo intent (gồm causal/prospective).
	- Output: `logs/task_303_summary.md`, `tests/artifacts/test_task303_adaptive_router.py`.
	- Verification trọng tâm: mapping query -> weights -> ranking đúng kỳ vọng, fallback semantic vẫn an toàn.

Artifacts chính:
- `logs/task_301_summary.md` -> `logs/task_303_summary.md`
- `tests/artifacts/test_task301_search_fork.py`
- `tests/artifacts/test_task302_sum_activation.py`
- `tests/artifacts/test_task303_adaptive_router.py`

### 3.5 Sprint 4 - Reflect
Mục tiêu sprint:
1. Triển khai reflect theo hướng lazy synthesis, bám phạm vi CogMem.

Atomic tasks đã hoàn tất:
1. T4.1 Reflect lazy synthesis:
	- Phạm vi: fork phần reflect cần thiết, bỏ consolidation chủ động ngoài phạm vi.
	- Output: `logs/task_401_summary.md`, `tests/artifacts/test_task401_reflect_lazy_synthesis.py`.
	- Verification trọng tâm: phản hồi tổng hợp được từ facts + `raw_snippet` sau retrieve, không phụ thuộc runtime `hindsight_api`.

Artifacts chính:
- `logs/task_401_summary.md`
- `tests/artifacts/test_task401_reflect_lazy_synthesis.py`

### 3.6 Sprint 5 - Runtime + Docker
Mục tiêu sprint:
1. Đưa CogMem lên trạng thái chạy dịch vụ độc lập.
2. Khóa contract đóng gói và vận hành Docker ở cả standalone và external-pg.

Atomic tasks đã hoàn tất:
1. T5.1 Runtime entrypoints:
	- Phạm vi: hoàn thiện `main.py`, `server.py`, HTTP routes lõi cho CogMem runtime.
	- Output: `logs/task_501_summary.md`, `tests/artifacts/test_task501_runtime_entrypoints.py`.
	- Verification trọng tâm: startup/shutdown flow và health endpoint hoạt động.
2. T5.2 Packaging/config contract:
	- Phạm vi: chốt entrypoint package, contract ENV runtime, tương thích mode pg0.
	- Output: `logs/task_502_summary.md`, `tests/artifacts/test_task502_packaging_config.py`.
	- Verification trọng tâm: parse env matrix và boot config không regression.
3. T5.3 Docker assets:
	- Phạm vi: chuẩn hóa Dockerfile/start-all/compose cho hai chế độ chạy.
	- Output: `logs/task_503_summary.md`, `tests/artifacts/test_task503_docker_assets.py`.
	- Verification trọng tâm: build image pass, `GET /health` pass trong container.
4. T5.4 Docker smoke/runbook:
	- Phạm vi: bổ sung script smoke và runbook vận hành.
	- Output: `logs/task_504_summary.md`, `tests/artifacts/test_task504_docker_smoke_contract.py`.
	- Verification trọng tâm: retain/recall smoke tối thiểu qua Docker pass.

Artifacts chính:
- `logs/task_501_summary.md` -> `logs/task_504_summary.md`
- `tests/artifacts/test_task501_runtime_entrypoints.py`
- `tests/artifacts/test_task502_packaging_config.py`
- `tests/artifacts/test_task503_docker_assets.py`
- `tests/artifacts/test_task504_docker_smoke_contract.py`

### 3.7 Sprint 6 - Completeness trước track eval
Mục tiêu sprint:
1. Đóng các khoảng trống completeness của retain pipeline trước khi đánh giá sâu.
2. Dựng harness E1-E7 để sẵn sàng chạy eval theo track riêng.

Atomic tasks đã hoàn tất:
1. T6.1 Retain prompt parity:
	- Phạm vi: khôi phục prompt/extraction path theo contract HINDSIGHT, giữ domain CogMem.
	- Output: `logs/task_601_summary.md`, `tests/artifacts/test_task601_retain_prompt_parity.py`.
	- Verification trọng tâm: 4 mode prompt parse đúng schema/fact types.
2. T6.2 Retain behavior parity:
	- Phạm vi: đồng bộ metadata + edge semantics (`raw_snippet`, `causal`, `transition`, `action_effect`).
	- Output: `logs/task_602_summary.md`, `tests/artifacts/test_task602_retain_behavior_parity.py`.
	- Verification trọng tâm: retain e2e nhiều phiên vẫn đúng lifecycle/link semantics.
3. T6.3 Eval harness E1-E7:
	- Phạm vi: dựng pipeline eval/ablation và artifacts thống kê cho track đánh giá.
	- Output: `logs/task_603_summary.md`, `tests/artifacts/test_task603_eval_harness.py`, `scripts/eval_cogmem.py`, `scripts/ablation_runner.py`.
	- Verification trọng tâm: harness chạy được trên split nhỏ, sinh được thống kê theo category.

Artifacts chính:
- `logs/task_601_summary.md` -> `logs/task_603_summary.md`
- `tests/artifacts/test_task601_retain_prompt_parity.py`
- `tests/artifacts/test_task602_retain_behavior_parity.py`
- `tests/artifacts/test_task603_eval_harness.py`

### 3.8 Backfill B1-B5 (đã triển khai)
Mục tiêu backfill:
1. Bù các phần baseline/minimal còn thiếu ở Sprint 1-5 trước khi mở nhánh completeness sâu.
2. Khóa lại contract cấu hình, retain path, runtime API, retrieval quality và docker runtime.

Atomic tasks đã hoàn tất:
1. B1 Config contract parity:
	- Output: `logs/task_611_summary.md`, `tests/artifacts/test_task611_config_contract.py`.
	- Verification trọng tâm: map ENV COGMEM tương thích contract cần thiết của runtime/retain/retrieval.
2. B2 Retain LLM path + prompt parity:
	- Output: `logs/task_612_summary.md`, `tests/artifacts/test_task612_retain_prompt_parity.py`.
	- Verification trọng tâm: extraction LLM-driven ổn định, không kéo lại observation/consolidation legacy.
3. B3 Runtime API completeness:
	- Output: `logs/task_613_summary.md`, `tests/artifacts/test_task613_runtime_api_e2e.py`.
	- Verification trọng tâm: retain -> DB -> recall roundtrip pass ở đường chạy API thật.
4. B4 Retrieval quality parity:
	- Output: `logs/task_614_summary.md`, `tests/artifacts/test_task614_retrieval_quality_contract.py`.
	- Verification trọng tâm: pipeline embedding/reranking đúng contract chất lượng retrieval.
5. B5 Docker run contract parity:
	- Output: `logs/task_615_summary.md`, `tests/artifacts/test_task615_docker_runtime_contract.py`.
	- Verification trọng tâm: docker run path khớp contract vận hành và namespace CogMem.

Artifacts chính:
- `logs/task_611_summary.md` -> `logs/task_615_summary.md`
- `tests/artifacts/test_task611_config_contract.py`
- `tests/artifacts/test_task612_retain_prompt_parity.py`
- `tests/artifacts/test_task613_runtime_api_e2e.py`
- `tests/artifacts/test_task614_retrieval_quality_contract.py`
- `tests/artifacts/test_task615_docker_runtime_contract.py`

### 3.9 Sprint 7 readiness (đã hoàn tất)
Mục tiêu sprint:
1. Chốt readiness tài liệu và gate trước thao tác xóa `hindsight_api`.
2. Biến kết quả audit thành plan hành động có thể thực thi và rollback.

Atomic tasks đã hoàn tất:
1. T7.1 Coverage matrix:
	- Phạm vi: lập ma trận C1-C5 theo function/property evidence.
	- Output: `docs/migration_idea_coverage_matrix.md`, `logs/task_701_summary.md`, `tests/artifacts/test_task701_idea_coverage_matrix.py`.
	- Verification trọng tâm: matrix có evidence truy vết được, không chỉ kết luận trạng thái.
2. T7.2 Readiness gate:
	- Phạm vi: đánh giá điều kiện xóa hindsight theo trạng thái dependency và script legacy.
	- Output: `reports/hindsight_removal_readiness.md`, `logs/task_702_summary.md`, `tests/artifacts/test_task702_hindsight_removal_gate.py`.
	- Verification trọng tâm: gate cho kết luận GO/NO-GO có lý do kỹ thuật rõ và kiểm chứng được.
3. T7.3 Removal playbook:
	- Phạm vi: chuẩn hóa quy trình dry-run/commit-run/rollback cho thao tác xóa.
	- Output: `docs/hindsight_removal_playbook.md`, `logs/task_703_summary.md`, `tests/artifacts/test_task703_removal_playbook_contract.py`.
	- Verification trọng tâm: playbook có checklist an toàn, ràng buộc bước rollback, không chứa thao tác phá hủy ngoài phạm vi.

Artifacts chính:
- `docs/migration_idea_coverage_matrix.md`
- `reports/hindsight_removal_readiness.md`
- `docs/hindsight_removal_playbook.md`
- `logs/task_701_summary.md`, `logs/task_702_summary.md`, `logs/task_703_summary.md`
- `tests/artifacts/test_task701_idea_coverage_matrix.py`
- `tests/artifacts/test_task702_hindsight_removal_gate.py`
- `tests/artifacts/test_task703_removal_playbook_contract.py`

---

## 4) Lộ trình còn lại (hợp nhất, có chiều sâu thi công)

## Phase A - Delete-first
### Sprint S11 - Delete hindsight_api only
Mục tiêu sprint:
1. Xóa thư mục `hindsight_api` theo đúng phạm vi đã khóa (không dọn dependency/script legacy trong sprint này).
2. Giữ runtime CogMem chạy ổn định sau xóa.

Phụ thuộc:
1. T7.1, T7.2, T7.3 đã PASS.

Inputs bắt buộc:
1. `docs/hindsight_removal_playbook.md`
2. `reports/hindsight_removal_readiness.md`
3. Kết quả test readiness hiện hành (T7.1/T7.2/T7.3)

Atomic tasks:
1. S11.1 Snapshot trước xóa:
	- Ghi nhận các test/artifact còn phụ thuộc vào sự tồn tại thư mục `hindsight_api`.
	- Lưu danh sách ảnh hưởng vào báo cáo sprint.
2. S11.2 Xóa thư mục:
	- Xóa toàn bộ `hindsight_api/`.
	- Không sửa `hindsight-client` trong `pyproject.toml` ở sprint này.
3. S11.3 Ổn định hậu xóa:
	- Sửa các artifact test vỡ vì kiểm tra file tồn tại trong `hindsight_api`.
	- Đảm bảo test không bị “false fail” do thay đổi phạm vi.

File tác động dự kiến:
1. `hindsight_api/**` (xóa)
2. `tests/artifacts/test_task001_inventory.py` (khả năng cao cần cập nhật)
3. `reports/hindsight_delete_only_report.md`
4. `tests/artifacts/test_task704_delete_hindsight_only.py`

Outputs bắt buộc:
1. `reports/hindsight_delete_only_report.md`
2. `logs/task_704_summary.md`
3. `tests/artifacts/test_task704_delete_hindsight_only.py`
4. Danh sách import reference trước/sau xóa trong báo cáo sprint

Verification (gợi ý lệnh):
1. `rg -n "from hindsight_api|import hindsight_api" cogmem_api`
2. `Get-ChildItem -Recurse hindsight_api` (kỳ vọng không còn thư mục)
2. `uv run python tests/artifacts/test_task701_idea_coverage_matrix.py`
3. `uv run python tests/artifacts/test_task702_hindsight_removal_gate.py`
4. `uv run python tests/artifacts/test_task703_removal_playbook_contract.py`
5. `uv run python tests/artifacts/test_task704_delete_hindsight_only.py`

Exit gate:
1. Không còn thư mục `hindsight_api`.
2. Runtime `cogmem_api` không import `hindsight_api`.
3. Readiness regression pack PASS.

Rủi ro và fallback:
1. Rủi ro: test lịch sử phụ thuộc file cũ.
2. Fallback: cập nhật test theo contract mới, không làm giảm ý nghĩa kiểm thử isolation.
3. Rủi ro: script/dev-tooling ngoài `cogmem_api` còn gọi package cũ.
4. Fallback: ghi nhận vào backlog kỹ thuật riêng, không mở rộng phạm vi sửa trong sprint xóa-first.

## Phase B - Coverage Closure (C1-C4 -> FULL)
### Sprint S12 - Close C1 to FULL
Mục tiêu sprint:
1. Đóng toàn bộ gap C1 ở code/runtime và gate test.

Phụ thuộc:
1. S11 PASS.

Inputs bắt buộc:
1. `docs/migration_idea_coverage_matrix.md` (read-only, chỉ dùng tham chiếu hiện trạng)
2. Báo cáo readiness và playbook xóa từ Sprint 7

Atomic tasks:
1. S12.1 Dọn legacy observation branch:
	- Loại bỏ nhánh xử lý observation không còn thuộc phạm vi CogMem hiện tại.
	- Rà soát docstring/mô tả fact types cũ.
2. S12.2 Đồng bộ causal link contract:
	- Writer đang tạo `link_type='causal'` phải khớp reader filters trong retrieval.
	- Loại alias cũ gây mismatch khi truy vấn.
3. S12.3 Gate test + evidence log:
	- Ghi bằng chứng function/property vào artifact của task.
	- Chốt C1 hoàn tất khi gate test pass theo criteria.

File tác động dự kiến:
1. `cogmem_api/engine/search/link_expansion_retrieval.py`
2. `cogmem_api/engine/search/retrieval.py`
3. `tests/artifacts/test_task705_c1_full_gate.py`

Outputs bắt buộc:
1. `logs/task_705_summary.md`
2. `tests/artifacts/test_task705_c1_full_gate.py`
3. Danh sách bằng chứng function/property cho C1 trong task summary

Verification (gợi ý lệnh):
1. `uv run python tests/artifacts/test_task705_c1_full_gate.py`
2. `rg -n "observation" cogmem_api/engine/search`
3. `rg -n "causes|caused_by|enables|prevents|\bcausal\b" cogmem_api/engine/search`

Exit gate:
1. Gate test C1 pass, có evidence đủ mức function/property trong artifact.
2. Không còn nhánh retrieval nào gọi semantics observation ngoài phạm vi.

Rủi ro và fallback:
1. Rủi ro: dọn observation làm lệch recall behavior cũ.
2. Fallback: giữ nhánh adapter tương thích ngắn hạn có test bao phủ, nhưng mặc định không đi qua observation path.

### Sprint S13 - Close C3 to FULL
Mục tiêu sprint:
1. Đảm bảo SUM + 3 guards không chỉ tồn tại trong code mà còn là đường chạy mặc định có hiệu lực.

Phụ thuộc:
1. S12 PASS.

Inputs bắt buộc:
1. `docs/migration_idea_coverage_matrix.md` (read-only, chỉ dùng tham chiếu hiện trạng)
2. Kết quả test C1 gate đã PASS

Atomic tasks:
1. S13.1 Chốt graph retriever policy:
	- Chọn và khóa mặc định phù hợp cho SUM path.
2. S13.2 Đồng bộ config/runtime factory:
	- Cập nhật cấu hình và resolver để mặc định mới thật sự được sử dụng.
3. S13.3 Bổ sung test hành vi:
	- Case anti-loop.
	- Case multi-hop có tích lũy nhiều đường bằng chứng.

File tác động dự kiến:
1. `cogmem_api/config.py`
2. `cogmem_api/engine/search/graph_retrieval.py`
3. `cogmem_api/engine/search/retrieval.py`
4. `tests/artifacts/test_task706_c3_sum_default_gate.py`

Outputs bắt buộc:
1. `logs/task_706_summary.md`
2. `tests/artifacts/test_task706_c3_sum_default_gate.py`
3. Biên bản quyết định policy mặc định và lý do kỹ thuật

Verification (gợi ý lệnh):
1. `uv run python tests/artifacts/test_task706_c3_sum_default_gate.py`
2. `rg -n "DEFAULT_GRAPH_RETRIEVER|bfs|link_expansion" cogmem_api/config.py`
3. `uv run python tests/artifacts/test_task302_sum_activation.py`

Exit gate:
1. Gate test C3 pass và có evidence hành vi SUM + guards trong artifact.
2. Đường chạy mặc định của runtime thực sự dùng SUM + guards (không chỉ tồn tại trong code).

Rủi ro và fallback:
1. Rủi ro: đổi default policy làm sai lệch latency hoặc chất lượng truy hồi.
2. Fallback: cho phép cờ cấu hình rollback policy tạm thời, nhưng test gate bắt buộc xác nhận default mới.

### Sprint S14 - Close C4 to FULL
Mục tiêu sprint:
1. Hoàn tất adaptive routing đúng semantics prospective/causal theo criteria kỹ thuật.

Phụ thuộc:
1. S13 PASS.

Inputs bắt buộc:
1. `docs/migration_idea_coverage_matrix.md` (read-only, chỉ dùng tham chiếu hiện trạng)
2. Kết quả test C3 gate PASS

Atomic tasks:
1. S14.1 Prospective status filter:
	- Query prospective phải ràng buộc `intention.status=planning`.
2. S14.2 Ưu tiên evidence theo intent:
	- Causal/prospective cần cơ chế ưu tiên Action-Effect/Transition phù hợp.
3. S14.3 Gate test + evidence log:
	- Chốt C4 hoàn tất khi pass criteria bằng test contract.

File tác động dự kiến:
1. `cogmem_api/engine/query_analyzer.py`
2. `cogmem_api/engine/search/retrieval.py`
3. `cogmem_api/engine/search/fusion.py`
4. `tests/artifacts/test_task707_c4_adaptive_full_gate.py`

Outputs bắt buộc:
1. `logs/task_707_summary.md`
2. `tests/artifacts/test_task707_c4_adaptive_full_gate.py`
3. Bộ case verify routing cho causal/prospective

Verification (gợi ý lệnh):
1. `uv run python tests/artifacts/test_task707_c4_adaptive_full_gate.py`
2. `rg -n "prospective|causal|planning|rrf_weights" cogmem_api/engine`
3. `uv run python tests/artifacts/test_task303_adaptive_router.py`

Exit gate:
1. Gate test C4 pass, evidence semantics prospective/causal đầy đủ trong artifact.
2. Query prospective không còn trả về intention ngoài trạng thái planning trong bộ test contract.

Rủi ro và fallback:
1. Rủi ro: filter planning quá chặt làm giảm recall một số query thực tế.
2. Fallback: cho phép threshold/weight theo config, nhưng semantics planning vẫn là mặc định bắt buộc.

### Sprint S15 - Full Gate trước tutorial
Mục tiêu sprint:
1. Khóa cổng trước tutorial bằng bằng chứng gate pack C1-C4 đều PASS.

Phụ thuộc:
1. S12, S13, S14 đều PASS.

Inputs bắt buộc:
1. Task summaries + gate outputs sau S12-S14
2. Kết quả gate tests 705/706/707
3. Readiness pack 701/702/703

Atomic tasks:
1. S15.1 Re-audit evidence toàn diện (C1-C4) từ logs/tests artifacts.
2. S15.2 Xuất chứng chỉ mở tutorial.
3. S15.3 Chạy regression batch readiness + coverage.

File tác động dự kiến:
1. `reports/pre_tutorial_full_gate.md`
2. `tests/artifacts/test_task708_pre_tutorial_full_gate.py`

Outputs bắt buộc:
1. `reports/pre_tutorial_full_gate.md`
2. `logs/task_708_summary.md`
3. `tests/artifacts/test_task708_pre_tutorial_full_gate.py`
4. Checklist pass/fail cho từng contribution C1-C4

Verification (gợi ý lệnh):
1. `uv run python tests/artifacts/test_task702_hindsight_removal_gate.py`
2. `uv run python tests/artifacts/test_task703_removal_playbook_contract.py`
3. `uv run python tests/artifacts/test_task705_c1_full_gate.py`
4. `uv run python tests/artifacts/test_task706_c3_sum_default_gate.py`
5. `uv run python tests/artifacts/test_task707_c4_adaptive_full_gate.py`
6. `uv run python tests/artifacts/test_task708_pre_tutorial_full_gate.py`

Exit gate:
1. `pre_tutorial_full_gate` xác nhận gate pack C1-C4 đều PASS.
2. Chỉ khi đó mới unlock tutorial phase.

Rủi ro và fallback:
1. Rủi ro: evidence gate pass nhưng truy vết chưa đủ rõ trong logs/artifacts.
2. Fallback: giữ trạng thái PARTIAL và mở sub-task bổ sung evidence, không unlock tutorial sớm.

## Phase C - Tutorial (unlock sau S15 PASS)
### Sprint S16 - Tutorial Framework
Mục tiêu sprint:
1. Tạo bộ khung tutorial có thể mở rộng theo module và theo learning path.
2. Thiết lập cơ chế kiểm tra coverage để tránh thiếu module.

Phụ thuộc:
1. S15 PASS (pre-tutorial full gate đã xác nhận C1-C4 FULL).

Inputs bắt buộc:
1. `docs/PLAN.md` (pha tutorial)
2. Cấu trúc code hiện tại của `cogmem_api/`
3. Danh mục module từ phase lịch sử và artifacts đã hoàn tất

Atomic tasks:
1. S16.1 Scaffold thư mục tutorial:
	- Tạo cấu trúc `tutorials/` theo nhóm core/non-core/capstone.
	- Tạo index điều hướng và learning path theo thứ tự học.
2. S16.2 Chuẩn hóa template tutorial:
	- Mỗi tài liệu có Purpose, Inputs, Outputs, Key functions/properties, Failure modes, Verify commands.
	- Thống nhất format heading và tiêu chuẩn dẫn chứng code.
3. S16.3 Coverage checker:
	- Tạo test artifact kiểm tra các module core và non-core đều xuất hiện trong module-map.
	- Fail nếu thiếu module hoặc thiếu section bắt buộc.

File tác động dự kiến:
1. `tutorials/README.md`
2. `tutorials/INDEX.md`
3. `tutorials/learning-path.md`
4. `tutorials/module-map.md`
5. `tutorials/templates/function-property-template.md`
6. `logs/task_716_summary.md`
7. `tests/artifacts/test_task716_tutorial_framework.py`

Outputs bắt buộc:
1. Bộ scaffold + template tutorial hoàn chỉnh
2. `logs/task_716_summary.md`
3. `tests/artifacts/test_task716_tutorial_framework.py`

Verification (gợi ý lệnh):
1. `uv run python tests/artifacts/test_task716_tutorial_framework.py`
2. `Get-ChildItem -Recurse tutorials`

Exit gate:
1. Framework tutorial tồn tại đầy đủ và coverage checker PASS.
2. Có learning path rõ cho cả core và non-core.

Rủi ro và fallback:
1. Rủi ro: thiếu module trong map do quét thủ công.
2. Fallback: dùng script checker fail-fast và cập nhật map trước khi qua S17.

### Sprint S17 - Tutorial Core
Mục tiêu sprint:
1. Viết tutorial chi tiết cho các module core, đủ để người mới có thể đọc code và chạy verify độc lập.

Phụ thuộc:
1. S16 PASS.

Inputs bắt buộc:
1. Template tutorial đã khóa ở S16
2. Danh mục module core trong `tutorials/module-map.md`

Atomic tasks:
1. S17.1 Core foundation docs:
	- Viết tutorial cho `config`, `models`, `memory_engine`.
	- Chỉ rõ function/property trọng yếu và quan hệ giữa các lớp.
2. S17.2 Core pipeline docs:
	- Viết tutorial cho `retain`, `search`, `reflect`, `api`.
	- Mô tả luồng retain -> recall -> response theo function-level.
3. S17.3 Verify contract cho core tutorial:
	- Mỗi tài liệu phải có verify commands tối thiểu.
	- Bổ sung test artifact kiểm tra section bắt buộc và độ phủ module core.

File tác động dự kiến:
1. `tutorials/core/config-and-models.md`
2. `tutorials/core/memory-engine.md`
3. `tutorials/core/retain-pipeline.md`
4. `tutorials/core/search-pipeline.md`
5. `tutorials/core/reflect-pipeline.md`
6. `tutorials/core/api-flow.md`
7. `logs/task_717_summary.md`
8. `tests/artifacts/test_task717_tutorial_core.py`

Outputs bắt buộc:
1. Bộ tutorial core hoàn chỉnh theo template
2. `logs/task_717_summary.md`
3. `tests/artifacts/test_task717_tutorial_core.py`

Verification (gợi ý lệnh):
1. `uv run python tests/artifacts/test_task717_tutorial_core.py`
2. `Select-String -Path tutorials/core/*.md -Pattern "## Verify"`

Exit gate:
1. Toàn bộ module core có tutorial riêng và PASS test contract.
2. Người đọc có thể thực hiện verify command tối thiểu cho từng tài liệu.

Rủi ro và fallback:
1. Rủi ro: mô tả sai do lệch so với code hiện tại.
2. Fallback: rà chéo với module-map + test contract; cập nhật ngay khi phát hiện drift.

### Sprint S18 - Tutorial Non-core + Capstone
Mục tiêu sprint:
1. Hoàn tất tutorial non-core để hiểu toàn diện codebase.
2. Cung cấp capstone walkthrough end-to-end và checklist tự học có tiêu chí pass/fail rõ.

Phụ thuộc:
1. S17 PASS.

Inputs bắt buộc:
1. Framework/tutorial core đã PASS
2. Danh mục module non-core (providers, db-utils, scripts, docker, migrations)

Atomic tasks:
1. S18.1 Non-core tutorial set:
	- Viết tài liệu cho providers, db-utils, scripts vận hành, docker assets, migrations.
	- Chỉ rõ trách nhiệm từng module và điểm nối với core pipeline.
2. S18.2 Capstone walkthrough:
	- Tạo hành trình retain -> recall -> response với chỉ dẫn đọc code theo thứ tự file/function.
	- Gắn verify commands cho từng checkpoint trong walkthrough.
3. S18.3 Self-checklist:
	- Tạo checklist tự học có tiêu chí pass/fail và expected outputs.
	- Bổ sung test artifact kiểm tra tính toàn vẹn tài liệu capstone.

File tác động dự kiến:
1. `tutorials/supporting/runtime-and-providers.md`
2. `tutorials/supporting/storage-and-db.md`
3. `tutorials/supporting/devops-and-migrations.md`
4. `tutorials/capstone/cogmem-codebase-walkthrough.md`
5. `tutorials/capstone/self-checklist.md`
6. `logs/task_718_summary.md`
7. `tests/artifacts/test_task718_tutorial_noncore_capstone.py`

Outputs bắt buộc:
1. Bộ tutorial non-core + capstone hoàn chỉnh
2. `logs/task_718_summary.md`
3. `tests/artifacts/test_task718_tutorial_noncore_capstone.py`

Verification (gợi ý lệnh):
1. `uv run python tests/artifacts/test_task718_tutorial_noncore_capstone.py`
2. `Select-String -Path tutorials/capstone/*.md -Pattern "pass/fail|Verify|Expected"`

Exit gate:
1. Coverage tutorial bao phủ cả core và non-core.
2. Capstone walkthrough + self-checklist đủ điều kiện dùng làm đường dẫn onboarding chính.

Rủi ro và fallback:
1. Rủi ro: tutorial dài nhưng khó thực thi vì thiếu checkpoint verify.
2. Fallback: tách walkthrough thành checkpoint nhỏ, bắt buộc mỗi checkpoint có lệnh verify và expected output.

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
