# Phase B — Sprint S12-S15: Coverage Closure C1-C4

**Trạng thái:** ✅ Done (tasks 705-708)

---

## Sprint S12 — Close C1 to FULL ✅

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

Verification:
1. `uv run python tests/artifacts/test_task705_c1_full_gate.py`
2. `rg -n "observation" cogmem_api/engine/search`
3. `rg -n "causes|caused_by|enables|prevents|\bcausal\b" cogmem_api/engine/search`

Exit gate:
1. Gate test C1 pass, có evidence đủ mức function/property trong artifact.
2. Không còn nhánh retrieval nào gọi semantics observation ngoài phạm vi.

---

## Sprint S13 — Close C3 to FULL ✅

Mục tiêu sprint:
1. Đảm bảo SUM + 3 guards không chỉ tồn tại trong code mà còn là đường chạy mặc định có hiệu lực.

Phụ thuộc:
1. S12 PASS.

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

Verification:
1. `uv run python tests/artifacts/test_task706_c3_sum_default_gate.py`
2. `rg -n "DEFAULT_GRAPH_RETRIEVER|bfs|link_expansion" cogmem_api/config.py`
3. `uv run python tests/artifacts/test_task302_sum_activation.py`

Exit gate:
1. Gate test C3 pass và có evidence hành vi SUM + guards trong artifact.
2. Đường chạy mặc định của runtime thực sự dùng SUM + guards (không chỉ tồn tại trong code).

---

## Sprint S14 — Close C4 to FULL ✅

Mục tiêu sprint:
1. Hoàn tất adaptive routing đúng semantics prospective/causal theo criteria kỹ thuật.

Phụ thuộc:
1. S13 PASS.

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

Verification:
1. `uv run python tests/artifacts/test_task707_c4_adaptive_full_gate.py`
2. `rg -n "prospective|causal|planning|rrf_weights" cogmem_api/engine`
3. `uv run python tests/artifacts/test_task303_adaptive_router.py`

Exit gate:
1. Gate test C4 pass, evidence semantics prospective/causal đầy đủ trong artifact.
2. Query prospective không còn trả về intention ngoài trạng thái planning trong bộ test contract.

---

## Sprint S15 — Full Gate trước tutorial ✅

Mục tiêu sprint:
1. Khóa cổng trước tutorial bằng bằng chứng gate pack C1-C4 đều PASS.

Phụ thuộc:
1. S12, S13, S14 đều PASS.

Atomic tasks:
1. S15.1 Re-audit evidence toàn diện (C1-C4) từ logs/tests artifacts.
2. S15.2 Xuất chứng chỉ mở tutorial.
3. S15.3 Chạy regression batch readiness + coverage.

Outputs bắt buộc:
1. `reports/pre_tutorial_full_gate.md`
2. `logs/task_708_summary.md`
3. `tests/artifacts/test_task708_pre_tutorial_full_gate.py`
4. Checklist pass/fail cho từng contribution C1-C4

Verification:
1. `uv run python tests/artifacts/test_task702_hindsight_removal_gate.py`
2. `uv run python tests/artifacts/test_task703_removal_playbook_contract.py`
3. `uv run python tests/artifacts/test_task705_c1_full_gate.py`
4. `uv run python tests/artifacts/test_task706_c3_sum_default_gate.py`
5. `uv run python tests/artifacts/test_task707_c4_adaptive_full_gate.py`
6. `uv run python tests/artifacts/test_task708_pre_tutorial_full_gate.py`

Exit gate:
1. `pre_tutorial_full_gate` xác nhận gate pack C1-C4 đều PASS.
2. Chỉ khi đó mới unlock tutorial phase.
