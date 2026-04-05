# S19.6 Manual Tutorial - [scripts/test_hindsight.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/test_hindsight.py)

## Purpose
- Script đo chi phí vận hành Hindsight baseline trên một sample LongMemEval.
- Theo dõi thời gian retain theo session và thống kê graph cuối cùng.

## Source File
- [scripts/test_hindsight.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/test_hindsight.py)

## Symbol-by-symbol explanation
### BASE_URL, BANK_ID_PREFIX
- Cấu hình endpoint Hindsight API và prefix bank id cho phiên đo.

### analyze_hindsight_cost(sample_index=0)
- Đọc [data/longmemeval_s_distilled_small.json](https://github.com/triet4p/agent-memory-cognitive/blob/master/data/longmemeval_s_distilled_small.json), lấy sample theo index.
- Reset/tạo bank trên Hindsight API.
- Lặp qua từng session, dựng transcript, gọi /memories (async=False) để retain.
- Ghi metric mỗi session: duration, total_nodes, total_links.
- Tổng hợp báo cáo cuối và ghi final_stats_<bank_id>.json.

### if __name__ == "__main__"
- Entry point mặc định gọi analyze_hindsight_cost(5).

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Thường chạy thủ công để benchmark baseline, không có module nội bộ nào import trực tiếp.

### Outbound dependencies
- [data/longmemeval_s_distilled_small.json.](https://github.com/triet4p/agent-memory-cognitive/blob/master/data/longmemeval_s_distilled_small.json)
- Hindsight API endpoints: DELETE/PUT/POST/GET trên /v1/default/banks/*.
- requests, json, pathlib, time.

## Runtime implications/side effects
- Tạo và ghi dữ liệu vào bank mới trên Hindsight server.
- Sinh file final_stats_<bank_id>.json ở thư mục gốc repo.
- Có thể chạy rất lâu nếu sessions dài và LLM timeout lớn.

## Failure modes
- Không có file distilled nhỏ sẽ dừng sớm.
- API lỗi hoặc timeout sẽ làm gián đoạn từng session hoặc fail tổng thể.
- sample_index ngoài phạm vi gây IndexError.

## Verify commands
```powershell
uv run python -c "import scripts.test_hindsight as t; print(hasattr(t, 'analyze_hindsight_cost'), t.BANK_ID_PREFIX)"
uv run python scripts/test_hindsight.py
```
