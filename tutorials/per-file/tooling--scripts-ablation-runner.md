# S19.6 Manual Tutorial - [scripts/ablation_runner.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/ablation_runner.py)

## Purpose
- Chạy ablation suite cho CogMem bằng cách lặp profile (E1..E7) và pipeline (recall/full).
- Tổng hợp kết quả, ghi file JSON report và in summary nhanh trên console.

## Source File
- [scripts/ablation_runner.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/ablation_runner.py)

## Symbol-by-symbol explanation
### JsonDict
- Type alias cho dict[str, Any] dùng thống nhất trong file.

### run_ablation_suite(...)
- Lặp qua từng profile và pipeline để gọi pipeline_runner (mặc định là run_pipeline từ eval_cogmem).
- Tạo bank_id riêng cho từng run bằng uuid để tách dữ liệu.
- Trả object tổng gồm runs đầy đủ và summary rút gọn metric chính.

### save_suite_result(result, output_dir)
- Đảm bảo thư mục output tồn tại.
- Ghi file JSON theo tên ablation_suite_<timestamp>.json.

### parse_args()
- Parse tham số CLI: profiles, pipeline, fixture, base-url, skip-retain, timeout, output.

### main()
- Parse args, chuẩn hóa danh sách profile/pipeline.
- Chạy suite, ghi file, in kết quả từng run.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Người vận hành gọi trực tiếp qua CLI: uv run python [scripts/ablation_runner.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/ablation_runner.py) ...

### Outbound dependencies
- [scripts/eval_cogmem.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/eval_cogmem.py): ABLATION_PROFILES, resolve_api_base_url, run_pipeline.
- pathlib.Path, json, uuid, time.

## Runtime implications/side effects
- Sinh nhiều bank_id nên có thể tạo tải đáng kể lên API nếu chạy full profiles x both pipelines.
- Ghi report JSON vào [logs/eval](https://github.com/triet4p/agent-memory-cognitive/blob/master/logs/eval) (mặc định), phục vụ so sánh profile.

## Failure modes
- profile không hợp lệ sẽ raise ValueError.
- API không sẵn sàng hoặc timeout sẽ làm run fail giữa chừng.
- Nếu output dir không ghi được sẽ lỗi IO khi save_suite_result.

## Verify commands
```powershell
uv run python -c "from scripts.ablation_runner import run_ablation_suite; print(callable(run_ablation_suite))"
uv run python scripts/ablation_runner.py --profiles E1 --pipeline recall --fixture short --skip-retain --api-timeout 5 --output logs/eval
```
