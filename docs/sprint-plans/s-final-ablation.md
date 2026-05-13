# Sprint S-final: Full Ablation Dry Run Gate

**Trạng thái:** 🔄 Pending (tasks 761-763)

**Phụ thuộc:** S28 Wave 2 PASS (v15 banks ready)

---

## Mục tiêu sprint
1. Chạy toàn bộ E1-E7 trên benchmark subset thực — xác nhận pipeline hoạt động end-to-end trước khi run chính thức.
2. Phát hiện bottleneck, lỗi runtime, và kết quả bất thường trước khi đầu tư tài nguyên vào full run.

---

## Inputs bắt buộc
1. Stratified subset đã chọn từ S21 (seed cố định)
2. Judge LLM ≥ 7B đã configure
3. `scripts/ablation_runner.py` đã integrate benchmark loaders + per-category metrics

---

## Atomic tasks

### S-final.1 Dry run E1 baseline (task 761)
- Chạy E1 trên LongMemEval-S subset (~30 questions) và LoCoMo subset (~10 conversations).
- Kiểm tra: không có lỗi runtime, output JSON đúng schema, judge trả về kết quả coherent.
- Ghi lại: tổng thời gian, LLM call count, latency p50/p95.
- Output: `reports/dry_run_E1.json`, `logs/task_761_summary.md`.

### S-final.2 Dry run E2-E7 ablation (task 762)
- Chạy E2-E7 trên cùng subset.
- So sánh per-category accuracy giữa các profiles — trend phải coherent với hypothesis:
  - E2 cải thiện Preference
  - E6 cải thiện Multi-hop
- Nếu trend ngược với hypothesis: flag là anomaly, document nhưng không block sprint.
- Output: `reports/dry_run_E2_E7.json`, `logs/task_762_summary.md`.

### S-final.3 Evaluation readiness gate (task 763)
- Tạo checklist kết quả: pipeline chạy không lỗi, metrics coherent, anomalies documented.
- Nếu PASS: unlock chạy full benchmark.
- Output: `reports/eval_readiness_gate.md`, `logs/task_763_summary.md`, `tests/artifacts/test_task763_eval_readiness_gate.py`.

---

## File tác động dự kiến
1. `scripts/ablation_runner.py` (integrate với benchmark loaders)
2. `reports/dry_run_E1.json` (mới)
3. `reports/dry_run_E2_E7.json` (mới)
4. `reports/eval_readiness_gate.md` (mới)

## Outputs bắt buộc
1. `reports/dry_run_E1.json`
2. `reports/dry_run_E2_E7.json`
3. `reports/eval_readiness_gate.md`
4. `logs/task_761_summary.md` -> `logs/task_763_summary.md`
5. `tests/artifacts/test_task763_eval_readiness_gate.py`

---

## Exit gate
1. E1-E7 chạy không lỗi trên benchmark subset.
2. Per-category output đúng schema, judge accuracy coherent (không phải toàn bộ 0 hoặc toàn bộ 1).
3. `eval_readiness_gate.md` ký kết xác nhận pipeline sẵn sàng cho full benchmark run.

## Rủi ro và fallback
1. Rủi ro: subset quá nhỏ để phát hiện trend per-category.
2. Fallback: tăng subset size trước khi claim gate PASS; record anomalies thay vì block.

---

## Post-S-final

Sau khi S-final PASS, mở khoá:
- C5 (Hierarchical KG) track
- Full benchmark run (toàn bộ LongMemEval-S 500 questions + LoCoMo)
- Publication track
