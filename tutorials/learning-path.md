# CogMem Learning Path (Architecture -> Module -> Function)

## Mục tiêu
Tài liệu này quy định thứ tự học codebase theo top-down, tránh đọc ngẫu nhiên gây mất context.
Scope hiện tại đã hoàn tất nền S16/S17 và bổ sung inventory đầy đủ ở S18.1.

## Điểm vào tài liệu
1. Chỉ mục tổng hợp: [tutorials/INDEX.md](INDEX.md)
2. Framework và quy chuẩn: [tutorials/README.md](README.md)
3. Hướng dẫn đọc code thủ công: [tutorials/manual-code-reading-guide.md](manual-code-reading-guide.md)
4. Phase D per-file index: [tutorials/per-file/INDEX.md](per-file/INDEX.md)
5. Phase D canonical reading order: [tutorials/per-file/READING-ORDER.md](per-file/READING-ORDER.md)

## Thứ tự đọc đề xuất
1. Manual-first walkthrough
   - Doc [tutorials/manual-code-reading-guide.md](manual-code-reading-guide.md).
   - Mục tiêu: nắm ngay runtime call chain thật (main -> server -> api -> memory_engine -> retain/recall/reflect).

2. Layer 0 - Architecture overview
   - Doc [tutorials/module-map.md](module-map.md), mục `Layer 0 - System Overview`.
   - Mục tiêu: nắm boundary hệ thống, dataflow retain/recall/reflect.

3. Layer 1 - End-to-end flow map
   - Doc [tutorials/module-map.md](module-map.md), mục `Layer 1 - End-to-end Flows`.
   - Doc [tutorials/flows/retain-recall-reflect-response.md](flows/retain-recall-reflect-response.md), flow module-level chính của hệ thống.
   - Mục tiêu: nắm đường chạy chính từ request vào đến response ra.

4. Layer 2 - Module catalog
   - Doc [tutorials/module-map.md](module-map.md), mục `Layer 2 - Module Catalog`.
   - Doc [tutorials/modules/README.md](modules/README.md), danh mục module dossiers của S17.2.
   - Mục tiêu: xác định module ownership, dependency direction, và boundary sử dụng.

5. Layer 3 - Function inventory seed
   - Doc [tutorials/module-map.md](module-map.md), mục `Layer 3 - Function Inventory Seed`.
   - Doc [tutorials/functions/function-inventory.md](functions/function-inventory.md), inventory function-level đầy đủ ở S18.1.
   - Mục tiêu: dùng inventory làm baseline chống bỏ sót hàm trước khi viết deep-dive docs.

6. Chuyển tiếp sang S17/S18
   - S17: đã hoàn tất module-level dossiers và flow docs.
   - S18.2: đã hoàn tất deep-dive function-level theo inventory đã khóa ở S18.1 (xem `tutorials/functions/README.md`).
   - S18.3: tạo capstone walkthrough + self-checklist gắn function checkpoints.

7. Áp template chuẩn cho tài liệu mới
   - Dùng [tutorials/templates/function-property-template.md](templates/function-property-template.md) làm khung mặc định.
   - Bảo đảm đủ các heading bắt buộc: Purpose, Inputs, Outputs, Top-down level, Prerequisites, Module responsibility, Function inventory (public/private), Failure modes, Verify commands.

8. Phase D canonical per-file reading
   - Doc [tutorials/per-file/READING-ORDER.md](per-file/READING-ORDER.md).
   - Mục tiêu: đọc theo catalog ID để bao phủ 100% file code scope Phase D.
   - Khi onboarding: áp dụng `ONBOARDING_IDS` theo thứ tự tuyệt đối.
   - Khi debug production: áp dụng `DEBUG_FIRST_IDS` để khoanh vùng nhanh.

## Checklist hoàn tất S16.1
1. Có đủ 2 tài liệu scaffold: `tutorials/module-map.md` và `tutorials/learning-path.md`.
2. Learning path thể hiện rõ trình tự Architecture -> Module -> Function.
3. Module map bao gồm đủ 4 layer top-down theo PLAN.

## Checklist hoàn tất S18.1
1. Có `tutorials/functions/function-inventory.md` và `tutorials/functions/function-inventory.json`.
2. Inventory bao phủ toàn bộ hàm/module trong phạm vi `cogmem_api/**` (trừ `cogmem_api/alembic/versions/**`).
3. Mỗi hàm có signature + vị trí file và trạng thái coverage (`inventory_status`, `deep_dive_status`).

## Checklist hoàn tất S18.2
1. Có `tutorials/functions/README.md` và `tutorials/functions/function-doc-index.json`.
2. Có deep-dive docs theo module trong `tutorials/functions/*.md` (trừ inventory/index files).
3. Mọi hàm trong inventory đều có section deep-dive và verify command tương ứng.

## Verify commands
1. `uv run python tests/artifacts/test_task716_tutorial_framework.py`
2. `uv run python tests/artifacts/test_task718_function_inventory.py`
3. `uv run python tests/artifacts/test_task719_function_deep_dive.py`
4. `uv run python tests/artifacts/test_task728_reading_order_full_scope.py`
