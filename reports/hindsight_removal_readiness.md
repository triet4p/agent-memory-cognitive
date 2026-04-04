# T7.2 - Hindsight Removal Readiness Gate

## Mục tiêu
Đánh giá mức sẵn sàng để xóa thư mục `hindsight_api` dựa trên 4 trục:
1. Import chain trong code chạy CogMem.
2. Dependency/packaging trong `pyproject.toml`.
3. Script và Docker contract cho runtime hiện hành.
4. CLI contract và các script legacy có thể gây nhầm lẫn.

## Phạm vi quét
- `cogmem_api/**`
- `pyproject.toml`
- `scripts/**`
- `docker/**`
- `README.md` (tham chiếu vận hành)

## Gate Results

| Gate | Mô tả | Trạng thái | Bằng chứng |
|---|---|---|---|
| G1 - Runtime import isolation | Không có `import hindsight_api` trong đường chạy CogMem | `PASS` | Quét `cogmem_api/**` không thấy import trực tiếp `hindsight_api` |
| G2 - Packaging dependency | Không còn dependency/runtime package của Hindsight | `FAIL` | `pyproject.toml` còn `hindsight-client>=0.4.19` |
| G3 - Docker contract | Runtime Docker mặc định dùng namespace CogMem | `PASS` | `scripts/docker.sh`, `scripts/docker.ps1` dùng `COGMEM_API_*`, không phụ thuộc image/package Hindsight |
| G4 - CLI contract clarity | Entry point chính là CogMem, script legacy phải được cô lập rõ | `PARTIAL` | `pyproject.toml` có `cogmem-api`; tuy nhiên còn `scripts/run_hindsight.ps1` và `scripts/test_hindsight.py` |
| G5 - Deletion blast radius | Tài liệu/kịch bản đã tách rõ phần tham chiếu lịch sử | `PARTIAL` | Nhiều tham chiếu `hindsight_api` nằm trong docs/log/tests phục vụ tracing; chưa có policy phân loại rõ trước khi xóa |

## Kết luận
- **Decision: NO-GO** cho hành động xóa `hindsight_api` ngay lúc này.
- Lý do chặn chính:
  1. **Blocker B1**: còn dependency `hindsight-client` trong `pyproject.toml`.
  2. **Blocker B2**: còn script legacy liên quan Hindsight chưa được đóng nhãn/quarantine theo policy rõ ràng.

## Danh sách tham chiếu cần xử lý trước khi xóa
1. `pyproject.toml`: bỏ `hindsight-client>=0.4.19` nếu không còn dùng.
2. `scripts/run_hindsight.ps1`: chuyển vào vùng `scripts/legacy/` hoặc đánh dấu chỉ dùng baseline lịch sử.
3. `scripts/test_hindsight.py`: chuyển vào vùng legacy hoặc tách hẳn khỏi runtime contract chính.
4. Chuẩn hóa policy tài liệu: tách tham chiếu "source-of-truth/tracing" với tham chiếu runtime bắt buộc.

## Hành động đề xuất cho T7.3
1. Tạo removal playbook gồm `dry-run` và `commit-run`.
2. Thêm checklist phân loại tham chiếu:
   - Runtime-critical (phải sạch hoàn toàn)
   - Historical tracing (được phép giữ)
3. Sau khi xử lý B1/B2, chạy lại gate để chuyển NO-GO -> GO.
