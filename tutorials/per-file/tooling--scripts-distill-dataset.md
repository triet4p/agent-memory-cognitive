# S19.6 Manual Tutorial - [scripts/distill_dataset.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/distill_dataset.py)

## Purpose
- Chưng cất (distill) dữ liệu LongMemEval và LoCoMo thành tập khó, nhỏ hơn, phục vụ eval nhanh nhưng vẫn giữ case khó.
- Bổ sung heuristic ưu tiên prospective/abstention/knowledge-update/temporal/multi-session.

## Source File
- [scripts/distill_dataset.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/distill_dataset.py)

## Symbol-by-symbol explanation
### parse_locomo_evidence(ev_str)
- Parse định dạng evidence D<session>:<turn> thành tuple số nguyên.

### get_locomo_dist(ev_list)
- Tính khoảng cách hội thoại giữa các evidence trong LoCoMo bằng global index giả định.

### is_extremely_hard_lme(item, counts, quotas)
- Heuristic chọn mẫu LongMemEval khó theo quota: abstention, prospective, knowledge-update, temporal-reasoning, multi-session, single-session.

### flatten_session_text(session)
- Chuẩn hóa session về chuỗi text để phục vụ thống kê xung đột/entity.

### estimate_session_gap(item)
- Ước lượng độ xa timeline giữa haystack sessions và answer sessions.

### estimate_conflict_density(item)
- Đếm mật độ từ khóa thay đổi/xung đột để đo độ khó truy hồi theo thời gian.

### estimate_entity_overlap(item)
- Ước lượng mức overlap thực thể xuyên session qua regex entity đơn giản.

### small_subset_score(item)
- Tính score ưu tiên subset nhỏ dựa trên category ưu tiên + gap + conflict + overlap.

### build_lme_small_subset(lme_items, target_total=12)
- Tạo tập nhỏ ưu tiên category MS/KU/TR theo quota, sau đó lấp đầy theo score tổng.

### filter_hard_locomo_qa(sample)
- Lọc QA khó của LoCoMo bằng khoảng cách evidence và keyword causal/habit.

### main()
- Điều phối toàn bộ pipeline distill cho LongMemEval và LoCoMo.
- Ghi các file đầu ra:
  - [data/longmemeval_s_distilled.json](https://github.com/triet4p/agent-memory-cognitive/blob/master/data/longmemeval_s_distilled.json)
  - [data/longmemeval_s_distilled_small.json](https://github.com/triet4p/agent-memory-cognitive/blob/master/data/longmemeval_s_distilled_small.json)
  - [data/locomo_distilled.json](https://github.com/triet4p/agent-memory-cognitive/blob/master/data/locomo_distilled.json)

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Chạy CLI trực tiếp bởi người vận hành để tạo dataset distilled.

### Outbound dependencies
- [data/LongMemEval/longmemeval_s_cleaned.json](https://github.com/triet4p/agent-memory-cognitive/blob/master/data/LongMemEval/longmemeval_s_cleaned.json) (input)
- [data/LoCoMo/locomo10.json](https://github.com/triet4p/agent-memory-cognitive/blob/master/data/LoCoMo/locomo10.json) (input)
- random, re, json, pathlib, collections.

## Runtime implications/side effects
- Ghi đè file distilled hiện có trong thư mục data.
- random.seed(42) giúp reproducible selection.

## Failure modes
- Input file không tồn tại: phần xử lý tương ứng sẽ bị bỏ qua.
- Schema dữ liệu thay đổi (thiếu key) có thể làm heuristic giảm chất lượng chọn mẫu.
- Regex entity đơn giản có thể bỏ sót hoặc bắt dư thực thể.

## Verify commands
```powershell
uv run python -c "import scripts.distill_dataset as d; print(callable(d.main), callable(d.build_lme_small_subset))"
uv run python scripts/distill_dataset.py
```
