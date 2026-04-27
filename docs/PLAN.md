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
1. Coverage matrix hiện tại tại [docs/migration_idea_coverage_matrix.md](migration_idea_coverage_matrix.md):
- C1: FULL ✅
- C2: FULL ✅
- C3: FULL ✅
- C4: FULL ✅
- C5: MISSING (deferred)
2. Readiness đã có:
- [reports/hindsight_removal_readiness.md](../reports/hindsight_removal_readiness.md)
- [docs/hindsight_removal_playbook.md](hindsight_removal_playbook.md)
3. Quyết định phạm vi đang khóa:
- Delete scope đã hoàn tất ✅
- C1-C4 coverage FULL ✅
- Tutorial (S16-S19) hoàn tất ✅
- C5 để track sau, không chặn eval trong vòng này.

---

## 2.5) 🔄 NEXT IMMEDIATE STEPS — Phase E Eval Readiness (S20-S23)

**Tóm tắt hiện trạng:** S20-S22 đã hoàn tất:
- ✅ Sprint 0 → Sprint 7 + Backfill B1-B5 (tasks 001-703)
- ✅ Phase A — Delete hindsight_api (S11, task 704)
- ✅ Phase B — Coverage Closure C1-C4 (S12-S15, tasks 705-708)
- ✅ Phase C — Tutorial top-down (S16-S18, tasks 716-718)
- ✅ Phase D — Per-file manual tutorial (S19.0-S19.8, tasks 721-729)
- ✅ Phase E — Audits + retain re-tests (tasks 730-742)
- ✅ Phase E — S20 contribution gaps closure (tasks 743-745)
- ✅ Phase E — S21 benchmark integration (tasks 746-748)
- ✅ Phase E — S22 eval metrics & judge LLM (tasks 749-752)

**Tại sao Phase E cần thiết?** [docs/REPORT.md](REPORT.md) (audit 2026-04-24) xác định gaps cụ thể giữa thiết kế và eval implementation:
1. raw_snippet không được inject vào generation context (eval chỉ dùng text field)
2. SUM activation không phải default graph retriever (link_expansion là default)
3. Benchmark integration: hiện tại eval_cogmem.py chỉ có 2-question hardcoded fixture
4. Eval metrics: không có per-category breakdown, không có Recall@k, judge LLM cùng model với retain LLM

**Next 4 sprints (S20-S23), task numbers bắt đầu từ 743:**
1. **S20 (tasks 743-745)** — Fix contribution gaps: raw_snippet injection, BFS as default, s_r_link contract
2. **S21 (tasks 746-748)** — Integrate distilled benchmark into eval pipeline (LongMemEval-S + LoCoMo adapters)
3. **S22 (tasks 749-752)** — Add proper eval metrics: per-category accuracy, Recall@k, separate judge LLM config
4. **S23 (tasks 753-755)** — Dry run E1-E7 on benchmark subset để verify pipeline hoạt động trước full run

**Entry gate S20:** C1-C4 FULL coverage verified ✅ → Ready to start now

**Ghi chú đánh số:** Tasks 730-742 trong logs đã dùng cho tutorial convention audit, CI/CD setup, và retain test re-audits (không phải S20-S23). Phase E sẽ bắt đầu từ task 743.

---

## 3) Lịch sử triển khai đã hoàn tất (không xóa)

### 3.1 Sprint 0 - Khởi tạo quy ước và inventory
1. T0.1: baseline + mapping module nguồn.
2. T0.2: convention artifact + test path.

Artifacts chính:
- [logs/task_001_summary.md](../logs/task_001_summary.md)
- [logs/task_002_summary.md](../logs/task_002_summary.md)
- [tests/artifacts/test_task001_inventory.py](../tests/artifacts/test_task001_inventory.py)
- [tests/artifacts/test_task002_artifact_conventions.py](../tests/artifacts/test_task002_artifact_conventions.py)

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

## ✅ Phase A - Delete-first (DONE)
### Sprint S11 - Delete hindsight_api only ✅
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

## ✅ Phase B - Coverage Closure (C1-C4 -> FULL) (DONE)
### Sprint S12 - Close C1 to FULL ✅
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

### Sprint S13 - Close C3 to FULL ✅
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

### Sprint S14 - Close C4 to FULL ✅
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

### Sprint S15 - Full Gate trước tutorial ✅
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

## ✅ Phase C - Tutorial (DONE)
### Sprint S16 - Tutorial Top-down Architecture Baseline ✅
Mục tiêu sprint:
1. Thiết lập bộ khung tutorial top-down đi từ toàn cảnh hệ thống đến từng lớp chi tiết.
2. Khóa bản đồ phụ thuộc để toàn bộ module và hàm đều có vị trí rõ ràng trong learning path.

Top-down level:
1. Architecture

Phụ thuộc:
1. S15 PASS (pre-tutorial full gate đã xác nhận C1-C4 FULL).

Inputs bắt buộc:
1. `docs/PLAN.md` (pha tutorial)
2. Cấu trúc code hiện tại của `cogmem_api/`
3. Danh mục module từ phase lịch sử và artifacts đã hoàn tất

Atomic tasks:
1. S16.1 Scaffold kiến trúc tutorial top-down:
	- Tạo `tutorials/module-map.md` theo các lớp: Layer 0 (System overview), Layer 1 (End-to-end flows), Layer 2 (Module catalog), Layer 3 (Function inventory seed).
	- Tạo `tutorials/learning-path.md` thể hiện thứ tự đọc từ high-level xuống low-level.
2. S16.2 Chuẩn hóa template tutorial theo chiều sâu:
	- Mỗi tài liệu bắt buộc có: Purpose, Inputs, Outputs, Top-down level, Prerequisites, Module responsibility, Function inventory (public/private), Failure modes, Verify commands.
	- Thống nhất format heading và tiêu chuẩn dẫn chứng code theo file/function.
3. S16.3 Contract checker cấp architecture:
	- Tạo test artifact fail-fast nếu thiếu layer trong module-map hoặc thiếu section bắt buộc trong template.
	- Fail nếu tutorial roadmap còn dùng cách chia nhóm cũ theo nhãn lịch sử.

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
1. Framework tutorial tồn tại đầy đủ, module-map đủ 4 layer top-down và contract checker PASS.
2. Learning path thể hiện rõ thứ tự Architecture -> Module -> Function.

Rủi ro và fallback:
1. Rủi ro: thiếu module trong map do quét thủ công.
2. Fallback: dùng script checker fail-fast và cập nhật map trước khi qua S17.

### Sprint S17 - Tutorial Module-by-Module Decomposition ✅
Mục tiêu sprint:
1. Viết tutorial module-level theo thứ tự top-down, từ flow tổng quan xuống từng module cụ thể.
2. Đảm bảo mỗi module có bản đồ phụ thuộc và danh mục hàm public/private để chuẩn bị cho deep dive function-level.

Top-down level:
1. Module

Phụ thuộc:
1. S16 PASS.

Inputs bắt buộc:
1. Template tutorial đã khóa ở S16
2. Danh mục module trong `tutorials/module-map.md`

Atomic tasks:
1. S17.1 Viết tutorial theo flow chính của hệ thống:
	- Tài liệu hóa luồng retain -> recall -> reflect -> response với call graph theo module.
	- Mỗi bước chỉ rõ file nguồn và entry points.
2. S17.2 Viết module dossiers:
	- Mỗi module trong `cogmem_api` có mục riêng gồm trách nhiệm, inbound/outbound dependencies, data contracts, error boundaries.
	- Mỗi module bắt buộc có Function inventory (public/private) trước khi sang S18.
3. S17.3 Verify contract cho module-level tutorial:
	- Mỗi tài liệu phải có verify commands tối thiểu và section bắt buộc theo template S16.
	- Test artifact fail nếu thiếu module hoặc thiếu function inventory.

File tác động dự kiến:
1. `tutorials/flows/retain-recall-reflect-response.md`
2. `tutorials/modules/*.md`
3. `tutorials/module-map.md`
7. `logs/task_717_summary.md`
8. `tests/artifacts/test_task717_tutorial_core.py`

Outputs bắt buộc:
1. Bộ tutorial module-level hoàn chỉnh theo template top-down
2. `logs/task_717_summary.md`
3. `tests/artifacts/test_task717_tutorial_core.py`

Verification (gợi ý lệnh):
1. `uv run python tests/artifacts/test_task717_tutorial_core.py`
2. `Select-String -Path tutorials/modules/*.md -Pattern "## Verify|Function inventory \(public/private\)"`

Exit gate:
1. Toàn bộ module trong module-map có tutorial module-level và PASS test contract.
2. Mỗi module đã có function inventory (public/private) và verify command tối thiểu.

Rủi ro và fallback:
1. Rủi ro: mô tả sai do lệch so với code hiện tại.
2. Fallback: rà chéo với module-map + test contract; cập nhật ngay khi phát hiện drift.

### Sprint S18 - Tutorial Function-by-Function Deep Dive ✅
Mục tiêu sprint:
1. Hoàn tất tutorial function-level cho toàn bộ hàm public/private của từng module.
2. Cung cấp capstone walkthrough end-to-end bám theo function checkpoints và checklist pass/fail có expected outputs.

Top-down level:
1. Function

Phụ thuộc:
1. S17 PASS.

Inputs bắt buộc:
1. Framework tutorial top-down đã PASS
2. Module dossiers + function inventory từ S17

Atomic tasks:
1. S18.1 Function inventory hoàn chỉnh:
	- Liệt kê đầy đủ từng hàm public/private theo module, kèm signature và vị trí file.
	- Gắn trạng thái coverage để không bỏ sót hàm.
2. S18.2 Function deep-dive docs:
	- Mỗi hàm bắt buộc có: purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.
	- Bổ sung ví dụ input/output tối thiểu cho nhóm hàm quan trọng.
3. S18.3 Capstone + self-checklist function-level:
	- Tạo walkthrough retain -> recall -> response theo checkpoint gắn function IDs cụ thể.
	- Checklist pass/fail phải ánh xạ tới function checkpoints và expected outputs.

File tác động dự kiến:
1. `tutorials/functions/*.md`
4. `tutorials/capstone/cogmem-codebase-walkthrough.md`
5. `tutorials/capstone/self-checklist.md`
6. `logs/task_718_summary.md`
7. `tests/artifacts/test_task718_tutorial_noncore_capstone.py`

Outputs bắt buộc:
1. Bộ tutorial function-level + capstone hoàn chỉnh
2. `logs/task_718_summary.md`
3. `tests/artifacts/test_task718_tutorial_noncore_capstone.py`

Verification (gợi ý lệnh):
1. `uv run python tests/artifacts/test_task718_tutorial_noncore_capstone.py`
2. `Select-String -Path tutorials/functions/*.md -Pattern "public/private|Failure modes|Verify"`
3. `Select-String -Path tutorials/capstone/*.md -Pattern "pass/fail|Verify|Expected|checkpoint"`

Exit gate:
1. Coverage tutorial bao phủ toàn bộ module và toàn bộ hàm public/private trong phạm vi codebase đã map.
2. Capstone walkthrough + self-checklist đủ điều kiện dùng làm đường dẫn onboarding chính ở mức function-level.

Rủi ro và fallback:
1. Rủi ro: tutorial dài nhưng khó thực thi vì thiếu checkpoint verify.
2. Fallback: tách walkthrough thành checkpoint nhỏ, bắt buộc mỗi checkpoint có lệnh verify và expected output.

---

## 🔄 Phase E - Evaluation Readiness (NEXT — unlock sau S15 PASS)

Mục tiêu phase:
1. Đảm bảo mọi contribution kỹ thuật (C1-C4) thực sự hoạt động đúng trong đường chạy runtime — không chỉ tồn tại trong code.
2. Xây dựng evaluation pipeline đủ chuẩn để so sánh kết quả với HINDSIGHT published numbers một cách có ý nghĩa.

Căn cứ: [docs/REPORT.md](REPORT.md) (audit 2026-04-24) xác định các gap cụ thể cần đóng trước khi chạy experiments thực sự.

### Sprint S20 - Contribution Gaps Closure ✅

Mục tiêu sprint:
1. Đóng các gap còn lại giữa thiết kế và implementation mà S12-S14 chưa bao phủ.

Phụ thuộc:
1. S15 PASS.

Inputs bắt buộc:
1. `docs/REPORT.md` — danh sách gap cụ thể từ audit
2. Coverage matrix C1-C4 FULL từ S15

Atomic tasks:
1. S20.1 Inject raw_snippet vào generation path:
	- Gap: `eval_cogmem.py` `_build_generation_prompt()` dùng `result.get('text', '')` — bỏ qua `raw_snippet`.
	- Fix: thay bằng `result.get('raw_snippet') or result.get('text', '')` trong generation evidence block.
	- Đảm bảo reflect API cũng inject raw_snippet vào context LLM generation, không chỉ text/narrative_fact.
	- Output: `logs/task_743_summary.md`, `tests/artifacts/test_task743_raw_snippet_generation.py`.
	- Verification: fact có số cụ thể (ví dụ "40%", "45ms") phải xuất hiện trong generated answer sau recall.

2. S20.2 Đặt BFS SUM làm default graph retriever:
	- Gap: `.env` cấu hình `COGMEM_API_GRAPH_RETRIEVER=link_expansion` — SUM + 3 guards không được kích hoạt mặc định.
	- Fix: đổi default thành `bfs` trong `cogmem_api/config.py` và `.env`.
	- Ghi rõ lý do kỹ thuật: contribution C3 phải là đường chạy mặc định trong mọi experiment E1-E7, trừ E1 (baseline) tắt explicit.
	- Output: `logs/task_744_summary.md`, `tests/artifacts/test_task744_bfs_default_gate.py`.
	- Verification: `get_default_graph_retriever()` trả về `BFSGraphRetriever` khi không có override config.

3. S20.3 Document và gate s_r_link simplification:
	- Gap: s_r_link được tạo bằng entity overlap thay vì behavioral reinforcement logic từ spec.
	- Không rewrite toàn bộ — viết rõ trong artifact tại sao entity-overlap là proxy hợp lý cho S-R linking ở cấp NL dialogue.
	- Thêm gate test kiểm tra s_r_link edge thực sự được tạo giữa habit node và fact node chia sẻ entity.
	- Output: `logs/task_745_summary.md`, `tests/artifacts/test_task745_sr_link_contract.py`.

File tác động dự kiến:
1. `scripts/eval_cogmem.py` (raw_snippet injection)
2. `cogmem_api/engine/reflect/agent.py` (raw_snippet injection)
3. `cogmem_api/config.py` (default graph retriever)
4. `.env` (COGMEM_API_GRAPH_RETRIEVER=bfs)

Outputs bắt buộc:
1. `logs/task_743_summary.md`, `logs/task_744_summary.md`, `logs/task_745_summary.md`
2. `tests/artifacts/test_task743_raw_snippet_generation.py`
3. `tests/artifacts/test_task744_bfs_default_gate.py`
4. `tests/artifacts/test_task745_sr_link_contract.py`

Exit gate:
1. raw_snippet xuất hiện trong generation context khi fact chứa chi tiết số cụ thể.
2. Default graph retriever là BFS SUM — xác nhận qua code path, không chỉ config.
3. s_r_link contract test PASS và có rationale document.

Rủi ro và fallback:
1. Rủi ro: đổi default BFS làm tăng latency.
2. Fallback: benchmark latency trước/sau, nếu quá cao cho phép cờ config opt-in/opt-out nhưng ablation E1-E7 bắt buộc dùng BFS.

---

### Sprint S21 - Benchmark Pipeline Integration ✅

Mục tiêu sprint:
1. Integrate output của `scripts/distill_dataset.py` vào `eval_cogmem.py` thay cho `SHORT_DIALOGUE_FIXTURE` 2-question hiện tại.
2. Đảm bảo eval pipeline đọc được cả hai distilled files và xử lý đúng format của từng benchmark.

Bối cảnh:
- `scripts/distill_dataset.py` đã tồn tại và đã tạo ra:
  - `data/longmemeval_s_distilled_small.json` — 12 LongMemEval questions, stratified quota, seed=42
  - `data/locomo_distilled.json` — 5 LoCoMo conversations, hard QA filtered (multi-hop dist>100, causal keywords)
- Phần selection và distillation đã xong — việc còn lại là wiring vào eval pipeline.

Phụ thuộc:
1. S20 PASS.

Inputs bắt buộc:
1. `data/longmemeval_s_distilled_small.json` (đã có)
2. `data/locomo_distilled.json` (đã có)
3. `scripts/eval_cogmem.py` đã có S20 updates

Atomic tasks:
1. S21.1 Adapter cho LongMemEval distilled format:
	- Schema của distilled file: `question_id`, `question`, `answer`, `question_type`, `haystack_sessions`.
	- Viết `_load_longmemeval_fixture(path)` trong `eval_cogmem.py`: đọc file → trả về list fixture items theo cùng schema `{"id", "query", "gold_answer", "category", "turns"}`.
	- Map `question_type` → `category` field cho per-category metrics.
	- Output: `logs/task_746_summary.md`, `tests/artifacts/test_task746_lme_adapter.py`.
	- Verification: adapter đọc được `longmemeval_s_distilled_small.json`, trả về đúng 12 items với category labels.

2. S21.2 Adapter cho LoCoMo distilled format:
	- Schema của distilled file: list conversations, mỗi conversation có `conversation` turns và `qa` list.
	- Viết `_load_locomo_fixture(path)` trong `eval_cogmem.py`: flatten conversation turns thành `turns`, expand QA pairs thành individual fixture items.
	- Map LoCoMo category integers sang string labels (1=single-hop, 2=multi-hop, v.v. theo dataset spec).
	- Output: `logs/task_747_summary.md`, `tests/artifacts/test_task747_locomo_adapter.py`.
	- Verification: adapter đọc được `locomo_distilled.json`, expand đúng số QA items.

3. S21.3 Wiring `--fixture` CLI arg vào benchmark files:
	- Mở rộng `parse_args()`: thêm `--fixture longmemeval|locomo|short` và `--fixture-path` cho custom path.
	- `get_fixture()` dispatch sang đúng loader theo fixture name.
	- `SHORT_DIALOGUE_FIXTURE` giữ nguyên như fallback/dev mode (`--fixture short`).
	- Output: `logs/task_748_summary.md`, `tests/artifacts/test_task748_fixture_dispatch.py`.
	- Verification: `python scripts/eval_cogmem.py --fixture longmemeval --pipeline recall --profile E1 --skip-retain` chạy không lỗi.

File tác động dự kiến:
1. `scripts/eval_cogmem.py` — thêm `_load_longmemeval_fixture`, `_load_locomo_fixture`, mở rộng `get_fixture()` và `parse_args()`

Outputs bắt buộc:
1. `logs/task_746_summary.md` -> `logs/task_748_summary.md`
2. `tests/artifacts/test_task746_lme_adapter.py`
3. `tests/artifacts/test_task747_locomo_adapter.py`
4. `tests/artifacts/test_task748_fixture_dispatch.py`

Exit gate:
1. Cả hai adapters đọc được distilled files và trả về đúng schema fixture.
2. `eval_cogmem.py --fixture longmemeval` và `--fixture locomo` chạy được end-to-end (dù kết quả chưa chính xác — pipeline không lỗi là đủ cho sprint này).
3. `SHORT_DIALOGUE_FIXTURE` vẫn hoạt động (không regression).

Rủi ro và fallback:
1. Rủi ro: schema distilled file thay đổi nếu `distill_dataset.py` được chỉnh sửa.
2. Fallback: adapter đọc flexible field names, log warning nếu field thiếu thay vì crash.

---

### Sprint S22 - Evaluation Metrics & Judge ✅

Mục tiêu sprint:
1. Nâng evaluation pipeline lên đủ chuẩn so sánh có ý nghĩa với HINDSIGHT: judge mạnh hơn, metrics chuẩn hơn, breakdown per-category.

Phụ thuộc:
1. S21 PASS.

Inputs bắt buộc:
1. `scripts/eval_cogmem.py` đã tích hợp benchmark loaders
2. Cấu hình judge LLM (model mạnh hơn Ministral-3B)

Atomic tasks:
1. S22.1 Judge LLM config độc lập:
	- Gap: `resolve_eval_llm_config()` fallback cùng model với retain LLM — judge và retain dùng chung Ministral-3B.
	- Fix: bắt buộc `COGMEM_EVAL_LLM_MODEL` và `COGMEM_EVAL_LLM_BASE_URL` phải set riêng; nếu thiếu thì raise error thay vì fallback im lặng.
	- Ghi rõ trong docs: judge LLM phải là model ≥ 7B (ưu tiên Qwen3-7B hoặc tương đương), không dùng 3B.
	- Output: `logs/task_749_summary.md`, `tests/artifacts/test_task749_judge_llm_config.py`.
	- Verification: eval script fail rõ ràng nếu judge LLM không được config riêng.

2. S22.2 Per-category accuracy breakdown:
	- Gap: metrics hiện tại chỉ aggregate toàn dataset, không có breakdown theo category.
	- Fix: `run_full_pipeline()` nhận `category` field từ benchmark loader, nhóm kết quả theo category, xuất `judge_accuracy_per_category` trong output JSON.
	- Categories: single-session, multi-session, temporal, knowledge-update, preference (LongMemEval-S); multi-hop, temporal (LoCoMo).
	- Output: `logs/task_750_summary.md`, `tests/artifacts/test_task750_per_category_metrics.py`.

3. S22.3 Recall@k và Precision@k metrics:
	- Gap: chỉ có keyword_coverage proxy — không có IR metric chuẩn.
	- Fix: thêm `recall_at_k(k=5, k=10)` và `precision_at_k` dựa trên gold node IDs nếu available, hoặc keyword overlap per-k.
	- Nếu benchmark không có gold node IDs: implement keyword-based Recall@k (% gold keywords present trong top-k results).
	- Output: `logs/task_751_summary.md`, `tests/artifacts/test_task751_recall_at_k.py`.

4. S22.4 Cross-encoder reranker validation trong eval:
	- Gap: reranker được configure nhưng eval không xác nhận nó đang được dùng.
	- Fix: thêm `reranker_used` flag vào eval output, log model name và latency của reranker step.
	- Output: `logs/task_752_summary.md`, `tests/artifacts/test_task752_reranker_active.py`.

File tác động dự kiến:
1. `scripts/eval_cogmem.py` (judge config gate, per-category breakdown, recall@k, reranker log)
2. `cogmem_api/engine/search/reranking.py` (expose reranker metadata)

Outputs bắt buộc:
1. `logs/task_749_summary.md` -> `logs/task_752_summary.md`
2. `tests/artifacts/test_task749_judge_llm_config.py`
3. `tests/artifacts/test_task750_per_category_metrics.py`
4. `tests/artifacts/test_task751_recall_at_k.py`
5. `tests/artifacts/test_task752_reranker_active.py`

Exit gate:
1. Eval script fail rõ ràng nếu judge LLM không configured riêng.
2. Output JSON có `judge_accuracy_per_category` với đầy đủ categories của từng benchmark.
3. Recall@k (k=5, k=10) được tính và ghi vào output.
4. Reranker được xác nhận active trong eval run.

Rủi ro và fallback:
1. Rủi ro: không có model judge đủ mạnh trong môi trường hiện tại.
2. Fallback: dùng Qwen3-7B hoặc model ≥ 7B có sẵn; ghi rõ model ID trong báo cáo để đảm bảo reproducibility.

---

### Sprint S23 - Session-Level Recall@k Implementation 🔄

Mục tiêu sprint:
1. Thay thế keyword-based `recall_at_k` (luôn trả về null với benchmark data) bằng session-level Recall@k sử dụng `document_id` provenance từ KG nodes.
2. Đảm bảo S24 dry run có metric Recall@k có ý nghĩa thực sự.

Bối cảnh kỹ thuật:
- LongMemEval annotate gold ở cấp session: field `answer_session_ids` — chưa được fixture loader trích xuất.
- LoCoMo annotate gold ở cấp evidence: field `evidence` (format `"D{doc_id}:{turn_id}"`) — chưa được trích xuất.
- KG nodes hiện có `document_id` trong search results nhưng không có `session_id` (không stored).
- Approach: session-level match — Recall@k = 1 nếu ≥1 trong top-k results có `document_id` thuộc gold session set.

Phụ thuộc:
1. S22 PASS.

Inputs bắt buộc:
1. `scripts/eval_cogmem.py` (fixture loaders + `_build_recall_at_k`)
2. `data/longmemeval_s_distilled_small.json` (field `answer_session_ids`)
3. `data/locomo_distilled.json` (field `evidence`)

Atomic tasks:
1. S23.1 (task 753) — Session-Level Recall@k:
	- Đọc `eval_cogmem.py` lines 460-540 để xác nhận `document_id` được dùng khi retain (nếu chưa dùng session_id thì thêm).
	- Fixture loader LongMemEval: trích xuất `answer_session_ids` → lưu vào `gold_session_ids`.
	- Fixture loader LoCoMo: trích xuất `evidence` → map `"D{doc}:{turn}"` → list doc IDs → lưu vào `gold_session_ids`.
	- Thay thế `_build_recall_at_k`: so sánh `result["document_id"]` với `gold_session_ids` thay vì keyword matching.
	- Wire `gold_session_ids` qua `compute_metrics` thay cho `expected_keywords`.
	- Output: `logs/task_753_summary.md`, `tests/artifacts/test_task753_recall_at_k_session.py`.

File tác động dự kiến:
1. `scripts/eval_cogmem.py` (fixture loaders + recall@k logic)

Outputs bắt buộc:
1. `logs/task_753_summary.md`
2. `tests/artifacts/test_task753_recall_at_k_session.py`

Exit gate:
1. Unit test pass: Recall@k = 1.0 khi document_id match, 0.0 khi không match, None khi gold_session_ids=None.
2. Chạy eval với `--fixture longmemeval_s` trên ≥1 question: `recall_at_k` không còn null.
3. Không sửa `cogmem_api/` — chỉ thay đổi `scripts/eval_cogmem.py` và artifacts.

---

### Sprint S24-hotfix - Pipeline Bug Fixes Before Dry Run ✅

Mục tiêu: đóng các bug phát hiện trong quá trình chạy S24 trước khi tiếp tục dry run.

Bug đã fix (task 756 + hotfixes 2026-04-26):

1. **7.1 FK violation** (`cogmem_api/engine/retain/fact_storage.py`): `insert_facts_batch` thiếu upsert `documents` record trước khi INSERT `memory_units` → `asyncpg.ForeignKeyViolationError` với mọi LongMemEval retain. Fix: executemany upsert `(doc_id, bank_id)` vào `documents` trước vòng lặp INSERT.

2. **7.2 Judge bool coercion** (`scripts/eval_cogmem.py`): `bool("false") == True` — minimax-m2.7 đôi khi trả về `"false"` dạng string. Fix: guard `isinstance(str)` trước `bool()`.

3. **7.3 Keyword recall = 0.0** (`scripts/eval_cogmem.py`): LongMemEval không có `expected_keywords` → `_keyword_recall_metrics` trả về `0.0` gây misleading. Fix: trả về `None` khi không có keywords; tất cả 4 aggregation points dùng list-based accumulation.

4. **URL conflict** (`scripts/eval_cogmem.py`): `resolve_api_base_url` fallback đọc nhầm `COGMEM_API_EVAL_LLM_BASE_URL` (minimax) → CogMem API request bị gửi đến minimax. Fix: đổi fallback sang `COGMEM_API_BASE_URL`; thêm `COGMEM_API_BASE_URL=http://localhost:8888` vào `.env`.

5. **Bank ID double-suffix** (`scripts/eval_cogmem.py`): script luôn append `_c{idx:03d}` kể cả khi `--bank-id` đã đủ → `e567_c000_c000`. Fix: chỉ append khi `--bank-id` không được truyền.

6. **API timeout** (`scripts/eval_cogmem.py`): default `--api-timeout 120s` quá thấp cho retain ~160 chunks (~800s). Fix: tăng default lên 3600s.

7. **Per-turn chunking** (`scripts/eval_cogmem.py`): `retain_fixture` gửi từng turn riêng lẻ → mỗi turn ~100 chars → LLM không có cross-turn context → `{"facts": []}`. Fix: concatenate toàn bộ turns trong session thành 1 content item (join `"\n\n"`); backend chunk theo `COGMEM_API_RETAIN_CHUNK_SIZE=3000` → LLM nhận nhiều turns per chunk. Thêm `COGMEM_API_RETAIN_CHUNK_SIZE=3000` vào `.env`.

Artifacts: `logs/task_756_summary.md`, `tests/artifacts/test_task756_fixes.py` (9/9 passed).

### S24-hotfix task 757 — Session Recall + CE Fallback (2026-04-26) ✅

Phát hiện sau dry run E7 conv-0 (`experiments/v1/checkpoints/E7_full_c000.json`, 47 sessions, ~500 nodes):

1. **8.1 TypeError line 1087** (`scripts/eval_cogmem.py`): `recall_keyword_accuracy=None` formatted với `:.3f` → crash. Fix: `kw_str = "null" if kw is None else f"{kw:.3f}"`.

2. **8.2 Missing `dateparser` dependency (PRIMARY)**: Root cause thực sự xác nhận qua server log: `"Recall main path failed, using lexical fallback: No module named 'dateparser'"`. `dateparser` không có trong `pyproject.toml` → `DateparserQueryAnalyzer.load()` raise `ModuleNotFoundError` → outer try-except bắt silently → lexical fallback không có `document_id` → `session_recall@k = 0.0`. Fix: `uv add dateparser` (installs dateparser==1.4.0 + pytz, regex, tzdata, tzlocal).

3. **8.3 Cross-encoder silent fallback** (`cogmem_api/engine/memory_engine.py`): Phòng thủ thêm: inner try-except quanh CE block; nếu CE fail → dùng trực tiếp RRF-ordered candidates (có `document_id`).

4. **8.4 Fallback includes document_id** (`cogmem_api/engine/memory_engine.py`): `_fallback_recall_from_conn` SELECT thiếu `document_id`. Fix: thêm `document_id` vào SELECT và result dict.

5. **8.5 Warning log on fallback** (`cogmem_api/engine/memory_engine.py`): Thêm `logger.warning` khi main path và CE fail để dễ debug.

6. **8.6 Remove non-existent columns chunk_id/tags from SQL SELECTs**: `memory_units` không có cột `chunk_id` hay `tags` (không có trong `models.py` hay migration). Tất cả 4 retrieval files đều SELECT chúng → `column "chunk_id" does not exist` → fallback. Fix: remove khỏi SELECT trong `retrieval.py` (4 nơi), `graph_retrieval.py` (2 nơi), `link_expansion_retrieval.py` (5 nơi), `mpfp_retrieval.py` (1 nơi).

7. **8.7 search_vector column không tồn tại** (`cogmem_api/engine/search/retrieval.py`): Native BM25 path (`DEFAULT_TEXT_SEARCH_EXTENSION = "native"`) dùng `ts_rank_cd(search_vector, ...)` và `search_vector @@ to_tsquery(...)` — column không có trong schema. Fix tạm: thay bằng `to_tsvector('english', text)` inline. Fix vĩnh viễn: tạo stored generated column trong migration S24 (task 758).

Artifacts: `logs/task_757_summary.md`, `tests/artifacts/test_task757_recall_fixes.py` (8/8 passed).

---

### Sprint S24 — Retrieval Stack Quality Hardening 🔄

Mục tiêu sprint:
1. Tạo Alembic migration bổ sung đầy đủ schema/index còn thiếu mà retrieval code đã assume tồn tại.
2. Đồng bộ code để dùng đúng schema mới — không còn workaround inline.
3. Fix ef_search chưa được set thực tế — đây là accuracy gap quan trọng nhất.
4. Wire document_tags vào retain pipeline để tags thực sự được lưu và có thể dùng cho filtering.

**Lý do kỹ thuật (theo từng vấn đề):**
- **BM25 no-index**: `to_tsvector('english', text) @@ to_tsquery(...)` không có GIN index → full sequential scan toàn bộ memory_units cho mọi BM25 query. Với stored generated column + GIN index, PostgreSQL dùng index scan → chỉ touch matching rows.
- **search_vector stored vs inline**: `ts_rank_cd(search_vector, ...)` nhanh hơn `ts_rank_cd(to_tsvector('english', text), ...)` cho matched rows vì tsvector đã được tính trước. Không ảnh hưởng accuracy nhưng tốt hơn về hiệu năng.
- **ef_search=40 vs 200**: HNSW default ef_search=40 có accuracy thấp hơn nhiều so với ef_search=200. ef_search kiểm soát beam width khi search — cao hơn → nhiều candidate được explore → recall cao hơn. Đây là **accuracy impact trực tiếp và quan trọng nhất** của sprint này.
- **Partial HNSW indexes**: Thay vì một global HNSW index, mỗi fact_type có partial index riêng → HNSW graph được build trên tập nhỏ hơn → approximate nearest neighbor chính xác hơn trong partition. Quan trọng khi fact types phân bố không đều.
- **Tags column**: API hiện tại nhận `tags` từ client nhưng không lưu vào DB → tags filtering luôn crash/no-op. Phải fix để tags feature có thể dùng.

Phụ thuộc:
1. S23 PASS.
2. Task 757 hotfixes PASS.

---

#### Task 758 — Alembic migration: Retrieval Quality Schema

**File tạo mới**: `cogmem_api/alembic/versions/20260426_0002_retrieval_quality.py`

Header migration:
```python
"""Retrieval quality schema: search_vector, tags, partial HNSW, links indexes.

Revision ID: 20260426_0002
Revises: 20260330_0001
Create Date: 2026-04-26
"""
revision = "20260426_0002"
down_revision = "20260330_0001"
branch_labels = None
depends_on = None
```

**Nội dung `upgrade()` — thứ tự thực hiện quan trọng:**

**Step 1 — search_vector stored generated column + GIN index:**
```python
op.execute("""
    ALTER TABLE memory_units
    ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(text, '') || ' ' || coalesce(raw_snippet, ''))
    ) STORED
""")
op.execute(
    "CREATE INDEX idx_memory_units_search_vector "
    "ON memory_units USING gin(search_vector)"
)
```

Lý do dùng `op.execute()` raw SQL thay vì `op.add_column()`: SQLAlchemy Alembic chưa hỗ trợ GENERATED ALWAYS AS STORED trực tiếp qua API. Raw SQL là cách đúng chuẩn.

Lý do include `raw_snippet` trong tsvector: `raw_snippet` là đoạn hội thoại gốc chứa nhiều keyword quan trọng không xuất hiện trong `text` (extracted fact). Kết hợp cả hai tăng BM25 recall đáng kể.

**Step 2 — tags column + GIN index:**
```python
op.add_column("memory_units", sa.Column("tags", sa.ARRAY(sa.Text()), nullable=True))
op.execute(
    "CREATE INDEX idx_memory_units_tags "
    "ON memory_units USING gin(tags) "
    "WHERE tags IS NOT NULL"
)
```

GIN index with WHERE clause: chỉ index rows có tags ≠ NULL → nhỏ hơn, nhanh hơn khi hầu hết rows không có tags.

**Step 3 — 6 partial HNSW indexes per fact_type:**
```python
FACT_TYPES = ["world", "experience", "opinion", "habit", "intention", "action_effect"]
for ft in FACT_TYPES:
    op.execute(
        f"CREATE INDEX idx_mu_emb_{ft} "
        f"ON memory_units USING hnsw (embedding vector_cosine_ops) "
        f"WHERE fact_type = '{ft}'"
    )
```

Lưu ý: Alembic `op.execute()` chạy trong transaction. Với pgvector HNSW, index creation trong transaction là OK. PostgreSQL sẽ TỰ ĐỘNG dùng partial index khi query có `WHERE fact_type = '...'` — không cần thay đổi code.

**Step 4 — memory_links covering/composite indexes:**
```python
# Covering index cho entity expansion: index-only scan, không cần heap fetch
op.execute(
    "CREATE INDEX idx_memory_links_entity_covering "
    "ON memory_links (from_unit_id) "
    "INCLUDE (to_unit_id, entity_id) "
    "WHERE link_type = 'entity'"
)
# Composite index cho incoming semantic links (cả hai hướng trong LinkExpansion)
op.execute(
    "CREATE INDEX idx_memory_links_to_type_weight "
    "ON memory_links (to_unit_id, link_type, weight DESC)"
)
```

**Nội dung `downgrade()`:**
```python
def downgrade():
    op.drop_index("idx_memory_links_to_type_weight", table_name="memory_links")
    op.drop_index("idx_memory_links_entity_covering", table_name="memory_links")
    for ft in ["world", "experience", "opinion", "habit", "intention", "action_effect"]:
        op.drop_index(f"idx_mu_emb_{ft}", table_name="memory_units")
    op.drop_index("idx_memory_units_tags", table_name="memory_units")
    op.drop_column("memory_units", "tags")
    op.drop_index("idx_memory_units_search_vector", table_name="memory_units")
    op.execute("ALTER TABLE memory_units DROP COLUMN search_vector")
```

**Output task 758:**
- `cogmem_api/alembic/versions/20260426_0002_retrieval_quality.py`
- `logs/task_758_summary.md`

---

#### Task 759 — Code adaptations to match new schema

**759.1 — Revert fix 8.7 trong retrieval.py, dùng search_vector column**

File: `cogmem_api/engine/search/retrieval.py` (native BM25 branch)

Thay:
```python
else:  # native — no stored search_vector column; compute tsvector inline
    query_tsquery = " | ".join(tokens)
    bm25_score_expr = "ts_rank_cd(to_tsvector('english', text), to_tsquery('english', $4))"
    bm25_order_by = f"{bm25_score_expr} DESC"
    bm25_where_filter = "AND to_tsvector('english', text) @@ to_tsquery('english', $4)"
    bm25_text_param = query_tsquery
```

Thành:
```python
else:  # native — stored generated column search_vector (migration 20260426_0002)
    query_tsquery = " | ".join(tokens)
    bm25_score_expr = "ts_rank_cd(search_vector, to_tsquery('english', $4))"
    bm25_order_by = f"{bm25_score_expr} DESC"
    bm25_where_filter = "AND search_vector @@ to_tsquery('english', $4)"
    bm25_text_param = query_tsquery
```

**759.2 — Set ef_search=200 trong pool init**

File: `cogmem_api/engine/memory_engine.py`

Thêm callback trước `asyncpg.create_pool(...)` (line ~169):
```python
async def _init_pool_connection(conn: asyncpg.Connection) -> None:
    """Set per-connection HNSW search parameters for accuracy."""
    await conn.execute("SET hnsw.ef_search = 200")
```

Truyền `init=_init_pool_connection` vào `asyncpg.create_pool(...)`.

**Lưu ý quan trọng**: Không dùng `SET LOCAL` — chỉ có hiệu lực trong transaction. Dùng `SET` (session-level) để ef_search áp dụng cho toàn bộ connection lifetime.

**759.3 — Wire document_tags vào fact_storage INSERT**

File: `cogmem_api/engine/retain/fact_storage.py`

Sửa signature `insert_facts_batch` — thêm parameter:
```python
async def insert_facts_batch(
    conn,
    bank_id: str,
    facts: list[ProcessedFact],
    document_id: str | None = None,
    document_tags: list[str] | None = None,  # ← THÊM
) -> list[str]:
```

Sửa INSERT SQL — thêm `tags` vào column list, thêm `$15::text[]` vào VALUES. Thêm `document_tags or None` vào params list cho mỗi fact trong batch (document-level tags, cùng value cho toàn bộ facts trong batch).

File: `cogmem_api/engine/retain/orchestrator.py` (dòng gọi `insert_facts_batch`)

Thêm keyword argument:
```python
document_tags=document_tags,
```

**759.4 — Xóa dead code trong FlatQueryAnalyzer**

File: `cogmem_api/engine/query_analyzer.py`

Xóa dòng `return None` unreachable sau `return QueryAnalysis(...)` trong `FlatQueryAnalyzer.analyze()`. Dòng này không bao giờ được thực thi nhưng gây nhầm lẫn khi đọc code.

---

#### Task 760 — Artifact tests + summary log

**File tạo mới**: `tests/artifacts/test_task758_retrieval_quality.py`

Tests bắt buộc (không cần live DB):

1. `test_migration_exists_with_correct_chain` — Migration `20260426_0002` tồn tại, `revision = "20260426_0002"`, `down_revision = "20260330_0001"`.
2. `test_migration_has_all_required_indexes` — Migration tạo đủ: `idx_memory_units_search_vector`, `idx_memory_units_tags`, `idx_mu_emb_{ft}` cho 6 fact_types, `idx_memory_links_entity_covering`, `idx_memory_links_to_type_weight`.
3. `test_migration_search_vector_includes_raw_snippet` — `search_vector` generated column dùng cả `text` và `raw_snippet` trong `to_tsvector(...)`.
4. `test_bm25_native_path_uses_search_vector_column` — `retrieval.py` native BM25 path dùng `ts_rank_cd(search_vector,` và `search_vector @@ to_tsquery`; không dùng `to_tsvector('english', text)` inline.
5. `test_ef_search_set_in_pool_init` — `memory_engine.py` có code `SET hnsw.ef_search = 200` (không chỉ trong comment).
6. `test_insert_facts_batch_accepts_document_tags` — `insert_facts_batch` có parameter `document_tags` trong signature.
7. `test_orchestrator_passes_document_tags` — `orchestrator.py` pass `document_tags` vào `insert_facts_batch`.
8. `test_flat_query_analyzer_no_dead_code` — `FlatQueryAnalyzer.analyze()` không có unreachable `return None` sau `return QueryAnalysis(...)`.

**File tạo mới**: `logs/task_758_summary.md`

**Exit gate S24:**
1. `uv run python tests/artifacts/test_task758_retrieval_quality.py` — 8/8 tests PASS.
2. `alembic upgrade head` từ clean DB chạy không lỗi, tạo đủ indexes/columns.
3. BM25 native path dùng `search_vector` column (verified by test 4).
4. `ef_search=200` được set trong pool init, không chỉ trong comment (verified by test 5).
5. Retain request với `tags=["tag1"]` → tags được lưu vào DB (smoke test thủ công).
6. `FlatQueryAnalyzer.analyze()` không còn dead code (verified by test 8).

**Outputs bắt buộc:**
- `cogmem_api/alembic/versions/20260426_0002_retrieval_quality.py` (task 758)
- `cogmem_api/engine/search/retrieval.py` — revert fix 8.7 (task 759.1)
- `cogmem_api/engine/memory_engine.py` — ef_search pool init (task 759.2)
- `cogmem_api/engine/retain/fact_storage.py` — document_tags param + tags INSERT (task 759.3)
- `cogmem_api/engine/retain/orchestrator.py` — pass document_tags (task 759.3)
- `cogmem_api/engine/query_analyzer.py` — remove dead code (task 759.4)
- `tests/artifacts/test_task758_retrieval_quality.py` (task 760)
- `logs/task_758_summary.md` (task 760)

---

### Sprint S24.5 — Eval Pipeline Correctness Fix 🔄

Mục tiêu sprint:
1. Recall API: thêm hai boundary đúng nghĩa (`top_k` + `snippet_budget` trên char thực tế của raw_snippet).
2. Tách generation và judge ra khỏi eval_cogmem.py — đưa vào cogmem_api như các endpoint độc lập.
3. eval_cogmem.py chỉ còn là script ghép nối thuần túy, không chứa LLM logic.

**Vấn đề cốt lõi phát hiện khi chạy eval:**
- Recall `max_tokens` tính trên word count của `text` (fact ngắn ~10-15 words) → 800+ facts được trả về, 50-100% toàn bộ DB. Token budget sai đơn vị, cần tính trên char thực tế của `raw_snippet`.
- `eval_cogmem.py` nhét LLM logic (prompt building, HTTP calls) trực tiếp — vi phạm separation of concerns. Generation và judge phải là pipeline endpoints trong server, eval script chỉ gọi HTTP.
- `raw_snippet` cho tất cả 800+ results → 4.3M chars input, vượt context window. Với two-tier recall (top_k facts, snippet_budget chars), raw_snippet chỉ được populate cho top-L facts nằm trong budget.

Phụ thuộc: S24 PASS.

---

#### Task 764 — Two-tier recall: `top_k` + `snippet_budget`

**Thiết kế hai boundary:**
- `top_k: int | None`: hard limit số facts trả về sau rerank (primary filter). Default: None (không giới hạn).
- `snippet_budget: int | None`: budget chars cho raw_snippet, tính trên `len(raw_snippet)` thực tế, cấp phát greedy từ score cao xuống thấp. Fact nằm trong budget → `raw_snippet` populated; fact vượt budget → `raw_snippet=None` (text vẫn trả về). Default: None (không giới hạn).
- `max_tokens` hiện tại: giữ nguyên làm secondary guard trên text word count (backward compat), nhưng không còn là boundary chính.

**764.1 — `cogmem_api/api/http.py` (RecallRequest)**

```python
class RecallRequest(BaseModel):
    query: str
    types: list[str] | None = None
    budget: Literal["low", "mid", "high"] = "mid"
    max_tokens: int = 4096
    top_k: int | None = None          # ← MỚI: hard limit facts returned
    snippet_budget: int | None = None  # ← MỚI: char budget for raw_snippet
    trace: bool = False
    query_timestamp: str | None = None
    adaptive_router: bool = True
    graph_retriever: str | None = None
```

Pass cả hai vào `recall_async()`.

**764.2 — `cogmem_api/engine/memory_engine.py` (recall_async)**

Sau token budget loop (line ~625), thay thế bằng logic 2-tier:
```python
# Tier 1: hard limit on number of facts
if top_k is not None:
    reranked_results = reranked_results[:top_k]

# Tier 2: snippet_budget — populate raw_snippet greedily by score (already sorted)
if snippet_budget is not None:
    used_chars = 0
    for item in reranked_results:
        snippet = item.get("raw_snippet") or ""
        if used_chars + len(snippet) <= snippet_budget:
            used_chars += len(snippet)
        else:
            item["raw_snippet"] = None  # exceed budget → strip snippet
```

Output: `logs/task_764_summary.md`

---

#### Task 765 — Generation + Judge endpoints trong cogmem_api

**Kiến trúc:** Generation dùng retain LLM (`_build_retain_llm_config()` đã có); Judge dùng judge LLM riêng (env vars mới `COGMEM_API_JUDGE_LLM_*`).

**765.1 — Schemas mới trong `cogmem_api/api/http.py`:**

```python
class GenerateRequest(BaseModel):
    query: str
    evidence: list[dict]          # list of recall result dicts (text, raw_snippet, score, ...)
    max_tokens: int = 2048

class GenerateResponse(BaseModel):
    answer: str

class JudgeRequest(BaseModel):
    question: str
    gold_answer: str
    predicted_answer: str
    category: str | None = None

class JudgeResponse(BaseModel):
    correct: bool
    score: float
    reason: str
    raw: str
```

**765.2 — Hai endpoint mới trong `cogmem_api/api/http.py`:**

```
POST /v1/{agent_name}/banks/{bank_id}/memories/generate
POST /v1/{agent_name}/judge
```

- `/generate`: build generation prompt từ evidence, call retain LLM (`app.state.memory._build_retain_llm_config()`), trả về answer.
- `/judge`: build judge prompt (category-aware system prompt), call judge LLM (config mới), parse JSON, trả về `JudgeResponse`.

Logic prompt building được move vào `cogmem_api/engine/eval_helpers.py` (module mới):
- `build_generation_prompt(query: str, evidence: list[dict]) -> str`
- `build_judge_system_prompt(category: str | None) -> str`
- `parse_judge_response(raw: str) -> dict` — reuse `parse_llm_json` từ `llm_wrapper.py`

**765.3 — Judge LLM config trong MemoryEngine:**

Thêm `_build_judge_llm_config()` đọc:
```
COGMEM_API_JUDGE_LLM_BASE_URL
COGMEM_API_JUDGE_LLM_MODEL
COGMEM_API_JUDGE_LLM_API_KEY
COGMEM_API_JUDGE_LLM_TIMEOUT  (default 600s)
```

Env vars mới cần thêm vào `.env` và `.env.example`:
```bash
COGMEM_API_JUDGE_LLM_BASE_URL=https://api.minimax.io/v1
COGMEM_API_JUDGE_LLM_MODEL=minimax-m2.7
COGMEM_API_JUDGE_LLM_API_KEY=<key>
COGMEM_API_JUDGE_LLM_TIMEOUT=600
```

Output: `logs/task_765_summary.md`

---

#### Task 766 — Simplify eval_cogmem.py

eval_cogmem.py sau khi sửa: không còn `call_openai_chat`, `resolve_eval_llm_config`, `EvalLLMConfig`, `_build_generation_prompt`, `_judge_answer`, `_judge_system_prompt`.

**766.1 — Xóa LLM logic khỏi eval_cogmem.py:**
- Xóa: `call_openai_chat`, `resolve_eval_llm_config`, `EvalLLMConfig` dataclass
- Xóa: `_build_generation_prompt`, `_judge_answer`, `_judge_system_prompt`
- Xóa: `_build_chat_url`, `resolve_gen_llm_config` (không cần nữa)
- Xóa: debug prints `print(response.text)` và `print(f"[LLM] input chars=...")`

**766.2 — Sửa `run_full_pipeline`:**
```python
# Generation → gọi /generate endpoint
gen_resp = post_json_fn(
    f"{api_base_url}/v1/default/banks/{bank_id}/memories/generate",
    {"query": question["query"], "evidence": results, "max_tokens": 2048},
    timeout_seconds,
)
generated_answer = gen_resp.get("answer", "")

# Judge → gọi /judge endpoint
judge_resp = post_json_fn(
    f"{api_base_url}/v1/default/judge",
    {"question": question["query"], "gold_answer": question["gold_answer"],
     "predicted_answer": generated_answer, "category": question.get("category")},
    timeout_seconds,
)
judge = judge_resp  # {correct, score, reason, raw}
```

Signature `run_full_pipeline` bỏ `llm_config` và `llm_call_fn` — không còn cần thiết.

**766.3 — Fix `build_recall_payload`:**
```python
def build_recall_payload(profile: AblationProfile, query: str) -> JsonDict:
    top_k = _to_int(_env_first("COGMEM_API_EVAL_RECALL_TOP_K", default="10"), default=10)
    snippet_budget = _to_int(_env_first("COGMEM_API_EVAL_RECALL_SNIPPET_BUDGET", default="30000"), default=30000)
    return {
        "query": query,
        "types": list(profile.recall_fact_types),
        "budget": "mid",
        "top_k": top_k,
        "snippet_budget": snippet_budget,
        "trace": True,
        "adaptive_router": profile.adaptive_router_enabled,
        "graph_retriever": "bfs" if profile.sum_activation_enabled else "link_expansion",
    }
```

Env vars mới trong `.env`:
```bash
COGMEM_API_EVAL_RECALL_TOP_K=10
COGMEM_API_EVAL_RECALL_SNIPPET_BUDGET=30000
```

Output: `logs/task_766_summary.md`

---

#### Task 767 — Artifacts

**`tests/artifacts/test_task764_recall_top_k.py`** (3 tests):
- `RecallRequest` có `top_k` và `snippet_budget` fields với default None
- `recall_async` source có logic `reranked_results[:top_k]`
- `recall_async` source có logic snippet_budget strip (kiểm tra `item["raw_snippet"] = None`)

**`tests/artifacts/test_task765_generate_judge_endpoints.py`** (3 tests):
- `GenerateRequest`, `GenerateResponse` schemas tồn tại trong `http.py`
- `JudgeRequest`, `JudgeResponse` schemas tồn tại trong `http.py`
- `cogmem_api/engine/eval_helpers.py` có `build_generation_prompt` và `build_judge_system_prompt`

**`tests/artifacts/test_task766_eval_script_simplified.py`** (4 tests):
- `eval_cogmem.py` không còn `call_openai_chat`
- `eval_cogmem.py` không còn `EvalLLMConfig`
- `build_recall_payload` có `top_k` và `snippet_budget`
- `run_full_pipeline` không có `llm_config` parameter

Exit gate:
1. `uv run python tests/artifacts/test_task764_recall_top_k.py` → 3/3 PASS
2. `uv run python tests/artifacts/test_task765_generate_judge_endpoints.py` → 3/3 PASS
3. `uv run python tests/artifacts/test_task766_eval_script_simplified.py` → 4/4 PASS

---

### Sprint S25 - Full Ablation Dry Run Gate 🔄

Mục tiêu sprint:
1. Chạy toàn bộ E1-E7 trên benchmark subset thực — xác nhận pipeline hoạt động end-to-end trước khi run chính thức.
2. Phát hiện bottleneck, lỗi runtime, và kết quả bất thường trước khi đầu tư tài nguyên vào full run.

Phụ thuộc:
1. S23 PASS.

Inputs bắt buộc:
1. Stratified subset đã chọn từ S21 (seed cố định)
2. Judge LLM ≥ 7B đã configure
3. `scripts/ablation_runner.py` đã integrate benchmark loaders + per-category metrics

Atomic tasks:
1. S24.1 Dry run E1 baseline:
	- Chạy E1 trên LongMemEval-S subset (~30 questions) và LoCoMo subset (~10 conversations).
	- Kiểm tra: không có lỗi runtime, output JSON đúng schema, judge trả về kết quả coherent.
	- Ghi lại: tổng thời gian, LLM call count, latency p50/p95.
	- Output: `reports/dry_run_E1.json`, `logs/task_761_summary.md`.

2. S24.2 Dry run E2-E7 ablation:
	- Chạy E2-E7 trên cùng subset.
	- So sánh per-category accuracy giữa các profiles — trend phải coherent với hypothesis trong spec (E2 cải thiện Preference, E6 cải thiện Multi-hop, v.v.).
	- Nếu trend ngược với hypothesis: flag là anomaly, không block sprint nhưng phải document.
	- Output: `reports/dry_run_E2_E7.json`, `logs/task_762_summary.md`.

3. S24.3 Evaluation readiness gate:
	- Tạo checklist kết quả: pipeline chạy không lỗi, metrics coherent, anomalies documented.
	- Nếu PASS: unlock chạy full benchmark.
	- Output: `reports/eval_readiness_gate.md`, `logs/task_763_summary.md`, `tests/artifacts/test_task763_eval_readiness_gate.py`.

File tác động dự kiến:
1. `scripts/ablation_runner.py` (integrate với benchmark loaders)
2. `reports/dry_run_E1.json`, `reports/dry_run_E2_E7.json` (mới)
3. `reports/eval_readiness_gate.md` (mới)

Outputs bắt buộc:
1. `reports/dry_run_E1.json`
2. `reports/dry_run_E2_E7.json`
3. `reports/eval_readiness_gate.md`
4. `logs/task_761_summary.md` -> `logs/task_763_summary.md`
5. `tests/artifacts/test_task763_eval_readiness_gate.py`

Exit gate:
1. E1-E7 chạy không lỗi trên benchmark subset.
2. Per-category output đúng schema, judge accuracy coherent (không phải toàn bộ 0 hoặc toàn bộ 1).
3. `eval_readiness_gate.md` ký kết xác nhận pipeline sẵn sàng cho full benchmark run.

Rủi ro và fallback:
1. Rủi ro: subset quá nhỏ để phát hiện trend per-category.
2. Fallback: tăng subset size trước khi claim gate PASS; record anomalies thay vì block.

---

## 5) Bảng tiến độ hợp nhất

### Completed ✅
| Nhóm | Sprint | Mục tiêu | Trạng thái | Tasks |
|---|---|---|---|---|
| Historical | Sprint 0 -> Sprint 7.3 | Đã triển khai và có artifact | ✅ Done | 001-703 |
| Delete | S11 | Delete hindsight_api folder | ✅ Done | 704 |
| Coverage | S12-S15 | Close C1-C4 to FULL | ✅ Done | 705-708 |
| Tutorial | S16 | Tutorial top-down architecture baseline | ✅ Done | 716 |
| Tutorial | S17 | Tutorial module-by-module decomposition | ✅ Done | 717 |
| Tutorial | S18 | Tutorial function-by-function deep dive | ✅ Done | 718 |
| Manual Tutorial | S19.0-S19.8 | Per-file manual tutorial coverage | ✅ Done | 721-729 |
| Audits | - | Tutorial convention + retain re-tests | ✅ Done | 730-742 |

### Next Immediate (Ready to Execute)
| Nhóm | Sprint | Mục tiêu | Trạng thái | Tasks |
|---|---|---|---|---|
| Eval Readiness | S20 | Contribution gaps closure (raw_snippet, BFS default, s_r_link) | ✅ Done | 743-745 |
| Eval Readiness | S21 | Benchmark adapter integration (LongMemEval-S, LoCoMo) | ✅ Done | 746-748 |
| Eval Readiness | S22 | Evaluation metrics & judge LLM (per-category, Recall@k) | ✅ Done | 749-752 |
| Eval Readiness | S23 | Session-level Recall@k implementation | ✅ Done | 753 |
| Eval Readiness | S24-hotfix | Pipeline bug fixes (FK, bool, URL, timeout, chunking) | ✅ Done | 756 |
| Eval Readiness | S24 | Retrieval stack quality hardening (schema/index/ef_search/tags) | ✅ Done | 758-760 |
| Eval Readiness | S24.5 | Eval pipeline correctness (two-tier recall, gen/judge endpoints) | 🔄 Next | 764-767 |
| Eval Readiness | S25 | Full ablation dry run gate (E1-E7) | 🔄 Pending S24.5 | 761-763 |

---

## 6) Canonical execution order

### ✅ COMPLETED EXECUTION PATH
Sprint 0 -> S1 -> S2 -> S3 -> S4 -> S5 -> S6 -> Backfill B1-B5 -> S7 (tasks 001-703)
→ S11 (task 704)
→ S12-S15 (tasks 705-708)
→ S16-S18 (tasks 716-718)
→ S19.0-S19.8 (tasks 721-729)
→ Audits (tasks 730-742)

### 🔄 NEXT EXECUTION PATH (Currently Ready)
**S20 (tasks 743-745):** Contribution gaps closure ✅ DONE
**S21 (tasks 746-748):** Benchmark adapter integration ✅ DONE
**S22 (tasks 749-752):** Eval metrics & judge LLM ✅ DONE
→ **S23 (task 753):** Session-level Recall@k implementation
→ **S24 (tasks 758-760):** Retrieval stack quality hardening
→ **S25 (tasks 761-763):** Full ablation dry run gate

### Future (Dependent on S25 PASS)
Post-S25: C5 (Hierarchical KG) track, full benchmark run, publication track

Hard rules:
1. S20 entry gate: S15 FULL coverage confirmed ✅
2. S21 dependency: S20 PASS ✅
3. S22 dependency: S21 PASS ✅
4. S23 dependency: S22 PASS ✅
5. S24 dependency: S23 PASS + task 757 hotfixes PASS
6. S25 dependency: S24 PASS
7. C5 deferred: không chặn eval trong vòng này

---

## 7) Verification standard (mọi sprint)
1. Drift Check: đối chiếu [docs/CogMem-Idea.md](CogMem-Idea.md) và coverage matrix.
2. Behavioral Testing: mỗi sprint có artifact test chạy độc lập.
3. Isolation Check: không có import runtime trái phạm vi trong cogmem_api.
4. Sprint Gate: sprint sau chỉ bắt đầu khi sprint trước PASS exit gate.

---

## 8) Relevant files
1. [docs/migration_idea_coverage_matrix.md](migration_idea_coverage_matrix.md)
2. [reports/hindsight_removal_readiness.md](../reports/hindsight_removal_readiness.md)
3. [docs/hindsight_removal_playbook.md](hindsight_removal_playbook.md)
4. [docs/CogMem-Idea.md](CogMem-Idea.md)
5. [docs/REPORT.md](REPORT.md)
6. pyproject.toml
7. [cogmem_api/engine/search/link_expansion_retrieval.py](../cogmem_api/engine/search/link_expansion_retrieval.py)
8. [cogmem_api/engine/search/retrieval.py](../cogmem_api/engine/search/retrieval.py)
9. [cogmem_api/engine/search/graph_retrieval.py](../cogmem_api/engine/search/graph_retrieval.py)
10. [cogmem_api/config.py](../cogmem_api/config.py)
11. [cogmem_api/engine/query_analyzer.py](../cogmem_api/engine/query_analyzer.py)
12. [cogmem_api/engine/reflect/agent.py](../cogmem_api/engine/reflect/agent.py)
13. [scripts/eval_cogmem.py](../scripts/eval_cogmem.py)
14. [scripts/ablation_runner.py](../scripts/ablation_runner.py)
15. [tests/artifacts/test_task701_idea_coverage_matrix.py](../tests/artifacts/test_task701_idea_coverage_matrix.py)
16. [tests/artifacts/test_task702_hindsight_removal_gate.py](../tests/artifacts/test_task702_hindsight_removal_gate.py)
17. [tests/artifacts/test_task703_removal_playbook_contract.py](../tests/artifacts/test_task703_removal_playbook_contract.py)

---

## 9) ✅ Addendum - Phase D Manual Tutorial Full-Coverage (post S18) (DONE)

Mục tiêu addendum:
1. Chuyển tutorial từ machine-generated sang manual-first cho toàn bộ file code trong scope runtime + tooling.
2. Mỗi file code phải có tài liệu giải thích thủ công ở mức symbol-by-symbol (biến, thuộc tính, hàm, class).
3. Mỗi tài liệu file phải có phần quan hệ chéo: inbound callers, outbound dependencies, side effects runtime.
4. Có thứ tự đọc bao phủ toàn bộ file trong scope, không bỏ sót.

Phạm vi khóa cho Phase D:
1. Bao gồm: `cogmem_api/**`, `scripts/**`, `docker/**`.
2. Bao gồm extension: `.py`, `.sh`, `.ps1`.
3. Không bao gồm `tests/artifacts/**` trong mandatory tutorial scope (tests vẫn là gate/verification artifacts).
4. Bộ docs auto hiện có trong `tutorials/functions/` giữ vai trò checklist/inventory, không phải canonical explanation.

### Sprint S19.0 - Scope lock + manifest gate ✅
Mục tiêu sprint:
1. Tạo source-of-truth manifest liệt kê toàn bộ file code trong scope Phase D.
2. Khóa rule include/exclude để không có file bị bỏ sót âm thầm.

Outputs bắt buộc:
1. `tutorials/per-file/INDEX.md`
2. `tutorials/per-file/file-manifest.md`
3. `logs/task_721_summary.md`
4. `tests/artifacts/test_task721_file_manifest_gate.py`

Exit gate:
1. Manifest có đầy đủ tất cả file `.py/.sh/.ps1` trong scope.
2. Mỗi file có trạng thái coverage (`not-started|in-progress|done`).

### Sprint S19.1 - Bootstrap/runtime/manual docs ✅
Mục tiêu sprint:
1. Hoàn tất manual docs cho bootstrap/runtime group để làm điểm tựa dependency cho các sprint sau.

File scope bắt buộc:
1. `cogmem_api/__init__.py`
2. `cogmem_api/main.py`
3. `cogmem_api/server.py`
4. `cogmem_api/config.py`
5. `cogmem_api/pg0.py`

Outputs bắt buộc:
1. `tutorials/per-file/bootstrap--*.md` (1 file tutorial cho mỗi file code trong scope sprint)
2. `logs/task_722_summary.md`
3. `tests/artifacts/test_task722_manual_bootstrap_coverage.py`

### Sprint S19.2 - API/schema/manual docs ✅
Mục tiêu sprint:
1. Hoàn tất manual docs cho lớp API + schema + migration.

File scope bắt buộc:
1. `cogmem_api/api/__init__.py`
2. `cogmem_api/api/http.py`
3. `cogmem_api/models.py`
4. `cogmem_api/alembic/versions/20260330_0001_t1_2_schema_extensions.py`

Outputs bắt buộc:
1. `tutorials/per-file/api--*.md`
2. `tutorials/per-file/schema--*.md`
3. `logs/task_723_summary.md`
4. `tests/artifacts/test_task723_manual_api_schema_coverage.py`

### Sprint S19.3 - Engine core/manual docs ✅
Mục tiêu sprint:
1. Hoàn tất manual docs cho engine core services và runtime state management.

File scope bắt buộc:
1. `cogmem_api/engine/__init__.py`
2. `cogmem_api/engine/memory_engine.py`
3. `cogmem_api/engine/db_utils.py`
4. `cogmem_api/engine/embeddings.py`
5. `cogmem_api/engine/cross_encoder.py`
6. `cogmem_api/engine/llm_wrapper.py`
7. `cogmem_api/engine/response_models.py`

Outputs bắt buộc:
1. `tutorials/per-file/engine-core--*.md`
2. `logs/task_724_summary.md`
3. `tests/artifacts/test_task724_manual_engine_core_coverage.py`

### Sprint S19.4 - Retain stack/manual docs ✅
Mục tiêu sprint:
1. Hoàn tất manual docs cho toàn bộ retain stack.

File scope bắt buộc:
1. `cogmem_api/engine/retain/__init__.py`
2. `cogmem_api/engine/retain/types.py`
3. `cogmem_api/engine/retain/orchestrator.py`
4. `cogmem_api/engine/retain/fact_extraction.py`
5. `cogmem_api/engine/retain/fact_storage.py`
6. `cogmem_api/engine/retain/entity_processing.py`
7. `cogmem_api/engine/retain/link_creation.py`
8. `cogmem_api/engine/retain/link_utils.py`
9. `cogmem_api/engine/retain/embedding_processing.py`
10. `cogmem_api/engine/retain/embedding_utils.py`
11. `cogmem_api/engine/retain/chunk_storage.py`

Outputs bắt buộc:
1. `tutorials/per-file/retain--*.md`
2. `logs/task_725_summary.md`
3. `tests/artifacts/test_task725_manual_retain_coverage.py`

### Sprint S19.5 - Search/query/manual docs ✅
Mục tiêu sprint:
1. Hoàn tất manual docs cho query analyzer + toàn bộ search stack.

File scope bắt buộc:
1. `cogmem_api/engine/query_analyzer.py`
2. `cogmem_api/engine/search/__init__.py`
3. `cogmem_api/engine/search/types.py`
4. `cogmem_api/engine/search/retrieval.py`
5. `cogmem_api/engine/search/fusion.py`
6. `cogmem_api/engine/search/reranking.py`
7. `cogmem_api/engine/search/graph_retrieval.py`
8. `cogmem_api/engine/search/link_expansion_retrieval.py`
9. `cogmem_api/engine/search/mpfp_retrieval.py`
10. `cogmem_api/engine/search/tags.py`
11. `cogmem_api/engine/search/temporal_extraction.py`
12. `cogmem_api/engine/search/trace.py`
13. `cogmem_api/engine/search/tracer.py`
14. `cogmem_api/engine/search/think_utils.py`

Outputs bắt buộc:
1. `tutorials/per-file/search--*.md`
2. `logs/task_726_summary.md`
3. `tests/artifacts/test_task726_manual_search_coverage.py`

### Sprint S19.6 - Reflect + scripts + docker/manual docs ✅
Mục tiêu sprint:
1. Hoàn tất manual docs cho reflect stack và toàn bộ scripts/docker code files trong scope.

File scope bắt buộc:
1. `cogmem_api/engine/reflect/__init__.py`
2. `cogmem_api/engine/reflect/agent.py`
3. `cogmem_api/engine/reflect/models.py`
4. `cogmem_api/engine/reflect/prompts.py`
5. `cogmem_api/engine/reflect/tools.py`
6. `scripts/**/*.py`
7. `scripts/**/*.sh`
8. `scripts/**/*.ps1`
9. `docker/**/*.sh`
10. `docker/**/*.ps1`

Outputs bắt buộc:
1. `tutorials/per-file/reflect--*.md`
2. `tutorials/per-file/tooling--*.md`
3. `tutorials/per-file/docker--*.md`
4. `logs/task_727_summary.md`
5. `tests/artifacts/test_task727_manual_reflect_tooling_coverage.py`

### Sprint S19.7 - Canonical reading order all files ✅
Mục tiêu sprint:
1. Xuất thứ tự đọc bao phủ 100% file code scope Phase D.
2. Có hai lộ trình: onboarding path và debug-first path.

Outputs bắt buộc:
1. `tutorials/per-file/READING-ORDER.md`
2. Cập nhật `tutorials/INDEX.md`
3. Cập nhật `tutorials/learning-path.md`
4. `logs/task_728_summary.md`
5. `tests/artifacts/test_task728_reading_order_full_scope.py`

### Sprint S19.8 - Final gate manual tutorial completeness ✅
Mục tiêu sprint:
1. Đóng cổng chất lượng manual docs cho toàn bộ scope.

Gate checklist bắt buộc:
1. Mỗi file code trong manifest có đúng 1 tutorial manual tương ứng.
2. Mỗi tutorial file có đủ các section:
	- Purpose
	- Symbol-by-symbol explanation
	- Cross-file dependencies (inbound/outbound)
	- Runtime implications/side effects
	- Failure modes
	- Verify commands
3. `tutorials/functions/` chỉ đóng vai trò inventory/checklist, không là canonical explanation.

Outputs bắt buộc:
1. `reports/manual_tutorial_full_gate.md`
2. `logs/task_729_summary.md`
3. `tests/artifacts/test_task729_manual_full_gate.py`

Exit gate Phase D:
1. Manual tutorial coverage 100% file scope (`cogmem_api + scripts + docker`, `.py/.sh/.ps1`).
2. Reading order full-scope được publish và pass gate tests.
3. Regression tutorial pack (716/717/718/719/720 + 721-729) PASS.

---

## 10) Canonical execution order extension (post S18)
Sau khi hoàn tất S18:
S19.0 -> S19.1 -> S19.2 -> S19.3 -> S19.4 -> S19.5 -> S19.6 -> S19.7 -> S19.8

Hard rules extension:
1. Không được claim xong Phase D nếu còn bất kỳ file code nào trong manifest chưa có manual tutorial.
2. Không dùng auto-generation để thay thế giải thích thủ công cho canonical docs.
