# Tutorials Index

## Mục tiêu
Chỉ mục này là điểm vào duy nhất cho hệ thống tài liệu tutorial top-down.

## Danh mục hiện có
1. Framework overview: tutorials/README.md
2. Manual code reading guide (ưu tiên đọc): tutorials/manual-code-reading-guide.md
3. Learning path: tutorials/learning-path.md
4. Module map (4 layers): tutorials/module-map.md
5. Flow retain-recall-reflect-response: tutorials/flows/retain-recall-reflect-response.md
6. Module dossiers index: tutorials/modules/README.md
7. Function inventory (S18.1): tutorials/functions/function-inventory.md
8. Function inventory data (machine-readable): tutorials/functions/function-inventory.json
9. Function deep-dive index (S18.2): tutorials/functions/README.md
10. Function deep-dive map data: tutorials/functions/function-doc-index.json
11. Template chuẩn: tutorials/templates/function-property-template.md

## Trình tự đọc khuyến nghị
1. tutorials/README.md
2. tutorials/manual-code-reading-guide.md
3. tutorials/module-map.md
4. tutorials/flows/retain-recall-reflect-response.md
5. tutorials/modules/README.md
6. tutorials/functions/function-inventory.md
7. tutorials/functions/README.md
8. tutorials/learning-path.md
9. tutorials/templates/function-property-template.md

## Ghi chú tiến độ Sprint S16
1. S16.1: Hoàn tất scaffold module-map và learning-path.
2. S16.2: Hoàn tất template chuẩn hóa heading và chuẩn dẫn chứng file/function.
3. S16.3: Hoàn tất contract checker fail-fast cho module-map, template và roadmap legacy labels.

## Ghi chú tiến độ Sprint S18.1
1. Đã hoàn tất inventory đầy đủ function-level (public/private) cho toàn bộ module trong `cogmem_api` (trừ migration scripts).
2. Đã bổ sung inventory machine-readable để làm nguồn sự thật cho S18.2/S18.3.

## Ghi chú tiến độ Sprint S18.2
1. Đã hoàn tất bộ deep-dive function-level theo module với đủ contract purpose/inputs/outputs/side effects/dependency/failure/pre-post/verify.
2. Đã cập nhật trạng thái `deep_dive_status` sang `documented` cho toàn bộ hàm trong inventory.

## Ghi chú chất lượng tutorial
1. Bổ sung hướng dẫn thủ công `tutorials/manual-code-reading-guide.md` để giải thích đường chạy thực và quan hệ chéo giữa modules.
2. Tài liệu machine-generated chỉ giữ vai trò inventory/checklist, không thay thế hướng dẫn đọc code theo ngữ cảnh nghiệp vụ.
