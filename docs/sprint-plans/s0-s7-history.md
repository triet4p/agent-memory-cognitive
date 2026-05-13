# Sprint History: S0 → S7 + Backfill B1-B5

**Trạng thái:** ✅ Tất cả đã hoàn tất (tasks 001–703)

---

## Sprint 0 — Khởi tạo quy ước và inventory ✅

1. T0.1: baseline + mapping module nguồn.
2. T0.2: convention artifact + test path.

Artifacts chính:
- [logs/task_001_summary.md](../../logs/task_001_summary.md)
- [logs/task_002_summary.md](../../logs/task_002_summary.md)
- [tests/artifacts/test_task001_inventory.py](../../tests/artifacts/test_task001_inventory.py)
- [tests/artifacts/test_task002_artifact_conventions.py](../../tests/artifacts/test_task002_artifact_conventions.py)

---

## Sprint 1 — Nền tảng schema/engine ✅

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

---

## Sprint 2 — Retain pipeline + mạng mới ✅

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

---

## Sprint 3 — Retrieval intelligence ✅

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

---

## Sprint 4 — Reflect ✅

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

---

## Sprint 5 — Runtime + Docker ✅

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

---

## Sprint 6 — Completeness trước track eval ✅

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

---

## Backfill B1-B5 ✅

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

---

## Sprint 7 — Readiness gate trước xóa hindsight_api ✅

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
