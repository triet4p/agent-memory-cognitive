# Phase D Manual Tutorial - Per-file Index

## Mục tiêu
- Tạo điểm vào chính thức cho Phase D manual tutorial.
- Chốt source-of-truth manifest để theo dõi coverage từng file code trong scope.

## Tài liệu bắt buộc
1. [file-manifest.md](file-manifest.md): danh sách đầy đủ file trong scope S19.0 và trạng thái coverage.

## Scope lock (S19.0)
- Include paths: `cogmem_api/**`, `scripts/**`, `docker/**`.
- Include extensions: `.py`, `.sh`, `.ps1`.
- Exclude mandatory tutorial scope: `tests/artifacts/**`.

## Trạng thái baseline
- Tổng file trong manifest: 58.
- Coverage status ban đầu: `not-started` cho toàn bộ file.
- Status hợp lệ cho các sprint sau: `not-started`, `in-progress`, `done`.

## Hướng dẫn cập nhật
1. Mỗi sprint S19.x chỉ cập nhật status cho file nằm trong phạm vi sprint đó.
2. Không xóa dòng khỏi manifest; chỉ đổi status và bổ sung link tài liệu manual.
3. Khi thêm file mới vào scope code, cập nhật manifest trước khi claim completion.