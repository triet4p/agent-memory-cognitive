# CogMem Learning Path (Architecture -> Module -> Function)

## Mục tiêu
Tài liệu này quy định thứ tự học codebase theo top-down, tránh đọc ngẫu nhiên gây mất context.
Scope hiện tại là scaffold S16.1, sẽ tiếp tục mở rộng trong S17-S18.

## Điểm vào tài liệu
1. Chỉ mục tổng hợp: tutorials/INDEX.md
2. Framework và quy chuẩn: tutorials/README.md

## Thứ tự đọc đề xuất
1. Layer 0 - Architecture overview
   - Doc [tutorials/module-map.md](module-map.md), mục `Layer 0 - System Overview`.
   - Mục tiêu: nắm boundary hệ thống, dataflow retain/recall/reflect.

2. Layer 1 - End-to-end flow map
   - Doc [tutorials/module-map.md](module-map.md), mục `Layer 1 - End-to-end Flows`.
   - Doc [tutorials/flows/retain-recall-reflect-response.md](flows/retain-recall-reflect-response.md), flow module-level chính của hệ thống.
   - Mục tiêu: nắm đường chạy chính từ request vào đến response ra.

3. Layer 2 - Module catalog
   - Doc [tutorials/module-map.md](module-map.md), mục `Layer 2 - Module Catalog`.
   - Mục tiêu: xác định module ownership, dependency direction, và boundary sử dụng.

4. Layer 3 - Function inventory seed
   - Doc [tutorials/module-map.md](module-map.md), mục `Layer 3 - Function Inventory Seed`.
   - Mục tiêu: có checklist module để vào S17/S18 bổ sung inventory public/private.

5. Chuyển tiếp sang S17/S18
   - S17: viết tutorial module-level cho từng module trong catalog.
   - S18: viết deep-dive function-level (public/private) và capstone walkthrough.

6. Áp template chuẩn cho tài liệu mới
   - Dùng tutorials/templates/function-property-template.md làm khung mặc định.
   - Bảo đảm đủ các heading bắt buộc: Purpose, Inputs, Outputs, Top-down level, Prerequisites, Module responsibility, Function inventory (public/private), Failure modes, Verify commands.

## Checklist hoàn tất S16.1
1. Có đủ 2 tài liệu scaffold: `tutorials/module-map.md` và `tutorials/learning-path.md`.
2. Learning path thể hiện rõ trình tự Architecture -> Module -> Function.
3. Module map bao gồm đủ 4 layer top-down theo PLAN.

## Verify commands
1. `uv run python tests/artifacts/test_task716_tutorial_framework.py`
