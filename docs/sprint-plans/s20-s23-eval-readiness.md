# Phase E — Sprint S20-S23: Evaluation Readiness (Early)

**Trạng thái:** ✅ Done (tasks 743-753)

Căn cứ: `docs/REPORT.md` (audit 2026-04-24) xác định các gap cụ thể cần đóng trước khi chạy experiments thực sự.

---

## Sprint S20 — Contribution Gaps Closure ✅

Mục tiêu sprint:
1. Đóng các gap còn lại giữa thiết kế và implementation mà S12-S14 chưa bao phủ.

Phụ thuộc: S15 PASS.

Atomic tasks:
1. **S20.1 Inject raw_snippet vào generation path** (task 743):
	- Gap: `eval_cogmem.py` `_build_generation_prompt()` dùng `result.get('text', '')` — bỏ qua `raw_snippet`.
	- Fix: thay bằng `result.get('raw_snippet') or result.get('text', '')` trong generation evidence block.
	- Đảm bảo reflect API cũng inject raw_snippet vào context LLM generation.
	- Output: `logs/task_743_summary.md`, `tests/artifacts/test_task743_raw_snippet_generation.py`.

2. **S20.2 Đặt BFS SUM làm default graph retriever** (task 744):
	- Gap: `.env` cấu hình `COGMEM_API_GRAPH_RETRIEVER=link_expansion` — SUM + 3 guards không được kích hoạt mặc định.
	- Fix: đổi default thành `bfs` trong `cogmem_api/config.py` và `.env`.
	- Output: `logs/task_744_summary.md`, `tests/artifacts/test_task744_bfs_default_gate.py`.

3. **S20.3 Document và gate s_r_link simplification** (task 745):
	- Gap: s_r_link được tạo bằng entity overlap thay vì behavioral reinforcement logic từ spec.
	- Viết rõ trong artifact tại sao entity-overlap là proxy hợp lý cho S-R linking.
	- Output: `logs/task_745_summary.md`, `tests/artifacts/test_task745_sr_link_contract.py`.

Exit gate:
1. raw_snippet xuất hiện trong generation context khi fact chứa chi tiết số cụ thể.
2. Default graph retriever là BFS SUM — xác nhận qua code path, không chỉ config.
3. s_r_link contract test PASS và có rationale document.

---

## Sprint S21 — Benchmark Pipeline Integration ✅

Mục tiêu sprint:
1. Integrate output của `scripts/distill_dataset.py` vào `eval_cogmem.py` thay cho `SHORT_DIALOGUE_FIXTURE` 2-question hiện tại.
2. Đảm bảo eval pipeline đọc được cả hai distilled files và xử lý đúng format.

Bối cảnh:
- `data/longmemeval_s_distilled_small.json` — 12 LongMemEval questions, stratified quota, seed=42
- `data/locomo_distilled.json` — 5 LoCoMo conversations, hard QA filtered

Phụ thuộc: S20 PASS.

Atomic tasks:
1. **S21.1 Adapter cho LongMemEval distilled format** (task 746):
	- Schema: `question_id`, `question`, `answer`, `question_type`, `haystack_sessions`.
	- Viết `_load_longmemeval_fixture(path)` — trả về đúng 12 items với category labels.
	- Output: `logs/task_746_summary.md`, `tests/artifacts/test_task746_lme_adapter.py`.

2. **S21.2 Adapter cho LoCoMo distilled format** (task 747):
	- Schema: list conversations, mỗi conversation có `conversation` turns và `qa` list.
	- Viết `_load_locomo_fixture(path)` — flatten + expand QA pairs.
	- Output: `logs/task_747_summary.md`, `tests/artifacts/test_task747_locomo_adapter.py`.

3. **S21.3 Wiring `--fixture` CLI arg** (task 748):
	- Mở rộng `parse_args()`: thêm `--fixture longmemeval|locomo|short` và `--fixture-path`.
	- `SHORT_DIALOGUE_FIXTURE` giữ nguyên như fallback/dev mode.
	- Output: `logs/task_748_summary.md`, `tests/artifacts/test_task748_fixture_dispatch.py`.

Exit gate:
1. Cả hai adapters đọc được distilled files và trả về đúng schema fixture.
2. `eval_cogmem.py --fixture longmemeval` và `--fixture locomo` chạy end-to-end không lỗi.
3. `SHORT_DIALOGUE_FIXTURE` vẫn hoạt động (không regression).

---

## Sprint S22 — Evaluation Metrics & Judge ✅

Mục tiêu sprint:
1. Nâng evaluation pipeline lên đủ chuẩn so sánh có ý nghĩa với HINDSIGHT: judge mạnh hơn, metrics chuẩn hơn, breakdown per-category.

Phụ thuộc: S21 PASS.

Atomic tasks:
1. **S22.1 Judge LLM config độc lập** (task 749):
	- Gap: `resolve_eval_llm_config()` fallback cùng model với retain LLM.
	- Fix: bắt buộc `COGMEM_EVAL_LLM_MODEL` và `COGMEM_EVAL_LLM_BASE_URL` phải set riêng; nếu thiếu raise error.
	- Judge LLM phải là model ≥ 7B (ưu tiên Qwen3-7B hoặc tương đương).
	- Output: `logs/task_749_summary.md`, `tests/artifacts/test_task749_judge_llm_config.py`.

2. **S22.2 Per-category accuracy breakdown** (task 750):
	- Gap: metrics hiện tại chỉ aggregate toàn dataset.
	- Fix: nhóm kết quả theo category, xuất `judge_accuracy_per_category` trong output JSON.
	- Output: `logs/task_750_summary.md`, `tests/artifacts/test_task750_per_category_metrics.py`.

3. **S22.3 Recall@k và Precision@k metrics** (task 751):
	- Gap: chỉ có keyword_coverage proxy.
	- Fix: thêm `recall_at_k(k=5, k=10)` và `precision_at_k` — keyword-based khi không có gold node IDs.
	- Output: `logs/task_751_summary.md`, `tests/artifacts/test_task751_recall_at_k.py`.

4. **S22.4 Cross-encoder reranker validation trong eval** (task 752):
	- Gap: reranker được configure nhưng eval không xác nhận nó đang được dùng.
	- Fix: thêm `reranker_used` flag vào eval output, log model name và latency của reranker step.
	- Output: `logs/task_752_summary.md`, `tests/artifacts/test_task752_reranker_active.py`.

Exit gate:
1. Eval script fail rõ ràng nếu judge LLM không configured riêng.
2. Output JSON có `judge_accuracy_per_category` với đầy đủ categories.
3. Recall@k (k=5, k=10) được tính và ghi vào output.
4. Reranker được xác nhận active trong eval run.

---

## Sprint S23 — Session-Level Recall@k Implementation ✅

Mục tiêu sprint:
1. Thay thế keyword-based `recall_at_k` (luôn trả về null với benchmark data) bằng session-level Recall@k sử dụng `document_id` provenance từ KG nodes.

Bối cảnh kỹ thuật:
- LongMemEval annotate gold ở cấp session: field `answer_session_ids`.
- LoCoMo annotate gold ở cấp evidence: field `evidence` (format `"D{doc_id}:{turn_id}"`).
- KG nodes có `document_id` trong search results.
- Approach: session-level match — Recall@k = 1 nếu ≥1 trong top-k results có `document_id` thuộc gold session set.

Phụ thuộc: S22 PASS.

Atomic task:
1. **S23.1 Session-Level Recall@k** (task 753):
	- Fixture loader LongMemEval: trích xuất `answer_session_ids` → lưu vào `gold_session_ids`.
	- Fixture loader LoCoMo: trích xuất `evidence` → map `"D{doc}:{turn}"` → list doc IDs.
	- Thay thế `_build_recall_at_k`: so sánh `result["document_id"]` với `gold_session_ids`.
	- Output: `logs/task_753_summary.md`, `tests/artifacts/test_task753_recall_at_k_session.py`.

Exit gate:
1. Unit test pass: Recall@k = 1.0 khi document_id match, 0.0 khi không match, None khi gold_session_ids=None.
2. Chạy eval với `--fixture longmemeval_s` trên ≥1 question: `recall_at_k` không còn null.
3. Không sửa `cogmem_api/` — chỉ thay đổi `scripts/eval_cogmem.py` và artifacts.
