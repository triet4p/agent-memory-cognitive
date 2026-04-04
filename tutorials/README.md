# Tutorials Framework

## Mục tiêu
Bộ tài liệu trong thư mục tutorials chuẩn hóa cách đọc và viết tài liệu theo hướng top-down.
Chuẩn này được thiết lập ở Sprint S16 để làm nền cho S17 (module-level) và S18 (function-level).

## Phạm vi
1. Áp dụng cho mọi tài liệu tutorial mới từ S16 trở đi.
2. Không thay đổi runtime code trong cogmem_api.
3. Không can thiệp coverage matrix trong sprint này.

## Heading chuẩn bắt buộc
Mỗi tài liệu tutorial phải có đúng các heading cấp 2 sau (đúng tên, đúng thứ tự):
1. Purpose
2. Inputs
3. Outputs
4. Top-down level
5. Prerequisites
6. Module responsibility
7. Function inventory (public/private)
8. Failure modes
9. Verify commands

## Tiêu chuẩn dẫn chứng code theo file/function
1. Luôn dẫn chứng theo cặp file + function.
2. Mỗi claim hành vi phải chỉ rõ nơi thực thi chính.
3. Nếu có nhiều hàm liên quan, liệt kê tách dòng theo thứ tự call flow.

Mẫu ghi dẫn chứng:
- File: cogmem_api/engine/search/retrieval.py
- Function: retrieve_memories
- Evidence: Điều phối retrieval đa kênh trước fusion/reranking.

- File: cogmem_api/engine/query_analyzer.py
- Function: analyze_query_type
- Evidence: Phân loại intent để áp routing weights.

## Quy ước trình bày
1. Ưu tiên tiếng Việt có dấu.
2. Dùng thuật ngữ kỹ thuật tiếng Anh khi cần giữ đúng meaning.
3. Mỗi mục Verify commands phải chạy độc lập được.
4. Mọi tài liệu mới nên khởi tạo từ template tại tutorials/templates/function-property-template.md.
