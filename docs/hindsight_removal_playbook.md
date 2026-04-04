# T7.3 - Playbook Xóa hindsight_api

## Mục tiêu
Chuẩn hóa quy trình xóa thư mục hindsight_api theo hai pha:
1. Dry-run: chỉ kiểm tra, không sửa/xóa.
2. Commit-run: thực hiện thay đổi sau khi gate GO.

Playbook này bám theo kết quả T7.2 và ưu tiên an toàn rollback.

## Phạm vi áp dụng
- Runtime chính của dự án: cogmem_api.
- Packaging/CLI/Docker contract chính.
- Script legacy liên quan Hindsight cần được cô lập rõ trước khi xóa.

## Định nghĩa GO/NO-GO
- GO khi tất cả điều kiện sau đúng:
  1. Không có import trực tiếp hindsight_api trong đường chạy runtime cogmem_api.
  2. Không còn dependency hindsight-client trong pyproject.toml.
  3. Script runtime chính (docker.sh/docker.ps1) không dùng token HINDSIGHT_API_* hoặc image Hindsight.
  4. Script legacy đã được gắn nhãn/quarantine rõ (không nằm trong contract vận hành chính).
- NO-GO nếu bất kỳ điều kiện nào fail.

## Pha 1 - Dry-run (không thay đổi mã nguồn)

### Bước 1: Snapshot trạng thái hiện tại
1. Chạy lệnh:
```powershell
git status --short
```
2. Lưu ảnh chụp tham chiếu:
```powershell
git ls-files > logs/predelete_git_files_snapshot.txt
```

### Bước 2: Kiểm tra import/runtime isolation
1. Quét import trong runtime CogMem:
```powershell
rg -n "from hindsight_api|import hindsight_api" cogmem_api
```
2. Kỳ vọng: không có kết quả.

### Bước 3: Kiểm tra packaging + CLI contract
1. Kiểm tra dependency còn sót:
```powershell
rg -n "hindsight-client|hindsight_client" pyproject.toml
```
2. Kiểm tra script entrypoint chính:
```powershell
rg -n "\[project\.scripts\]|cogmem-api|hindsight-api" pyproject.toml
```
3. Kỳ vọng:
- Có entrypoint cogmem-api.
- Không còn dependency hindsight-client nếu muốn GO.

### Bước 4: Kiểm tra script và Docker contract
1. Quét contract runtime chính:
```powershell
rg -n "HINDSIGHT_API_|ghcr\.io/vectorize-io/hindsight|hindsight_api" scripts/docker.sh scripts/docker.ps1 docker
```
2. Kỳ vọng: runtime chính không chứa token/runtime Hindsight.

### Bước 5: Phân loại tham chiếu còn lại
1. Quét tham chiếu lịch sử:
```powershell
rg -n "hindsight_api|hindsight-client|run_hindsight|test_hindsight" docs logs scripts tests
```
2. Phân loại:
- Runtime-critical: bắt buộc xóa/sửa trước commit-run.
- Historical-tracing: được giữ nếu đã ghi chú rõ là tham chiếu lịch sử.

### Bước 6: Chốt Dry-run Verdict
1. Tạo verdict file:
- reports/hindsight_removal_dryrun_verdict.md
2. Nếu NO-GO, liệt kê blocker theo mã:
- B1: packaging blocker
- B2: legacy script blocker
- B3: runtime import blocker

## Pha 2 - Commit-run (chỉ chạy khi Dry-run = GO)

### Bước 1: Chuẩn bị nhánh và checkpoint
1. Tạo nhánh thao tác:
```powershell
git checkout -b chore/remove-hindsight-api
```
2. Ghi nhận checkpoint:
```powershell
git rev-parse HEAD > logs/predelete_commit_sha.txt
```

### Bước 2: Cập nhật packaging và script contract
1. Xóa hindsight-client khỏi pyproject.toml.
2. Đưa script legacy vào vùng cách ly, ví dụ:
- scripts/legacy/run_hindsight.ps1
- scripts/legacy/test_hindsight.py
3. Cập nhật README để chỉ rõ script legacy không thuộc runtime chính.

### Bước 3: Xóa thư mục hindsight_api
1. Xóa thư mục mục tiêu:
```powershell
Remove-Item -Recurse -Force hindsight_api
```
2. Kiểm tra không còn file trong chỉ mục:
```powershell
git status --short
```

### Bước 4: Chạy kiểm tra hậu xóa
1. Artifact tests trọng yếu:
```powershell
uv run python tests/artifacts/test_task701_idea_coverage_matrix.py
uv run python tests/artifacts/test_task702_hindsight_removal_gate.py
```
2. Quét import sau xóa:
```powershell
rg -n "from hindsight_api|import hindsight_api" cogmem_api tests scripts
```
3. Kỳ vọng: pass toàn bộ gate.

### Bước 5: Xuất báo cáo commit-run
1. Tạo báo cáo:
- reports/hindsight_removal_commitrun_report.md
2. Nội dung tối thiểu:
- Danh sách file đã đổi/xóa.
- Kết quả test/gate.
- Tình trạng GO sau xóa.

## Rollback Plan

### Rollback nhanh (khi chưa commit)
1. Khôi phục file từ working tree bằng thao tác thủ công theo danh sách git status.
2. Chạy lại dry-run để xác nhận trạng thái quay về NO-GO/GO mong muốn.

### Rollback sau commit
1. Tạo commit đảo ngược thay vì dùng lệnh phá hủy lịch sử:
```powershell
git revert <commit_sha>
```
2. Chạy lại gate T7.2 để xác nhận runtime an toàn.

## Tiêu chí hoàn tất T7.3
1. Có playbook đầy đủ hai pha dry-run và commit-run.
2. Có checklist GO/NO-GO rõ ràng.
3. Có rollback plan trước và sau commit.
4. Không dùng các lệnh phá hủy lịch sử Git.

## Ghi chú vận hành
- Khi chưa đạt GO, không thực hiện xóa hindsight_api.
- Ưu tiên giữ tính truy vết lịch sử trong docs/logs nhưng phải tách bạch với runtime contract.
