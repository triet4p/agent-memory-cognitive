# Phase C — Sprint S16-S18: Tutorial Top-Down

**Trạng thái:** ✅ Done (tasks 716-718 + S19.0-S19.8 tasks 721-729 + Audits tasks 730-742)

---

## Sprint S16 — Tutorial Top-down Architecture Baseline ✅

Mục tiêu sprint:
1. Thiết lập bộ khung tutorial top-down đi từ toàn cảnh hệ thống đến từng lớp chi tiết.
2. Khóa bản đồ phụ thuộc để toàn bộ module và hàm đều có vị trí rõ ràng trong learning path.

Top-down level: Architecture

Phụ thuộc:
1. S15 PASS (pre-tutorial full gate đã xác nhận C1-C4 FULL).

Atomic tasks:
1. S16.1 Scaffold kiến trúc tutorial top-down:
	- Tạo `tutorials/module-map.md` theo các lớp: Layer 0 (System overview), Layer 1 (End-to-end flows), Layer 2 (Module catalog), Layer 3 (Function inventory seed).
	- Tạo `tutorials/learning-path.md` thể hiện thứ tự đọc từ high-level xuống low-level.
2. S16.2 Chuẩn hóa template tutorial theo chiều sâu:
	- Mỗi tài liệu bắt buộc có: Purpose, Inputs, Outputs, Top-down level, Prerequisites, Module responsibility, Function inventory (public/private), Failure modes, Verify commands.
	- Thống nhất format heading và tiêu chuẩn dẫn chứng code theo file/function.
3. S16.3 Contract checker cấp architecture:
	- Tạo test artifact fail-fast nếu thiếu layer trong module-map hoặc thiếu section bắt buộc trong template.
	- Fail nếu tutorial roadmap còn dùng cách chia nhóm cũ theo nhãn lịch sử.

File tác động:
- `tutorials/README.md`, `tutorials/INDEX.md`, `tutorials/learning-path.md`, `tutorials/module-map.md`
- `tutorials/templates/function-property-template.md`
- `logs/task_716_summary.md`, `tests/artifacts/test_task716_tutorial_framework.py`

Exit gate:
1. Framework tutorial tồn tại đầy đủ, module-map đủ 4 layer top-down và contract checker PASS.
2. Learning path thể hiện rõ thứ tự Architecture -> Module -> Function.

---

## Sprint S17 — Tutorial Module-by-Module Decomposition ✅

Mục tiêu sprint:
1. Viết tutorial module-level theo thứ tự top-down, từ flow tổng quan xuống từng module cụ thể.
2. Đảm bảo mỗi module có bản đồ phụ thuộc và danh mục hàm public/private.

Top-down level: Module

Phụ thuộc: S16 PASS.

Atomic tasks:
1. S17.1 Viết tutorial theo flow chính của hệ thống:
	- Tài liệu hóa luồng retain -> recall -> reflect -> response với call graph theo module.
	- Mỗi bước chỉ rõ file nguồn và entry points.
2. S17.2 Viết module dossiers:
	- Mỗi module trong `cogmem_api` có mục riêng gồm trách nhiệm, inbound/outbound dependencies, data contracts, error boundaries.
	- Mỗi module bắt buộc có Function inventory (public/private) trước khi sang S18.
3. S17.3 Verify contract cho module-level tutorial:
	- Mỗi tài liệu phải có verify commands tối thiểu và section bắt buộc theo template S16.
	- Test artifact fail nếu thiếu module hoặc thiếu function inventory.

File tác động:
- `tutorials/flows/retain-recall-reflect-response.md`
- `tutorials/modules/*.md`, `tutorials/module-map.md`
- `logs/task_717_summary.md`, `tests/artifacts/test_task717_tutorial_core.py`

Exit gate:
1. Toàn bộ module trong module-map có tutorial module-level và PASS test contract.
2. Mỗi module đã có function inventory (public/private) và verify command tối thiểu.

---

## Sprint S18 — Tutorial Function-by-Function Deep Dive ✅

Mục tiêu sprint:
1. Hoàn tất tutorial function-level cho toàn bộ hàm public/private của từng module.
2. Cung cấp capstone walkthrough end-to-end bám theo function checkpoints và checklist pass/fail.

Top-down level: Function

Phụ thuộc: S17 PASS.

Atomic tasks:
1. S18.1 Function inventory hoàn chỉnh:
	- Liệt kê đầy đủ từng hàm public/private theo module, kèm signature và vị trí file.
	- Gắn trạng thái coverage để không bỏ sót hàm.
2. S18.2 Function deep-dive docs:
	- Mỗi hàm bắt buộc có: purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.
	- Bổ sung ví dụ input/output tối thiểu cho nhóm hàm quan trọng.
3. S18.3 Capstone + self-checklist function-level:
	- Tạo walkthrough retain -> recall -> response theo checkpoint gắn function IDs cụ thể.
	- Checklist pass/fail phải ánh xạ tới function checkpoints và expected outputs.

File tác động:
- `tutorials/functions/*.md`
- `tutorials/capstone/cogmem-codebase-walkthrough.md`
- `tutorials/capstone/self-checklist.md`
- `logs/task_718_summary.md`, `tests/artifacts/test_task718_tutorial_noncore_capstone.py`

Exit gate:
1. Coverage tutorial bao phủ toàn bộ module và toàn bộ hàm public/private trong phạm vi đã map.
2. Capstone walkthrough + self-checklist đủ điều kiện dùng làm đường dẫn onboarding chính.

---

## Sprint S19 — Per-file Manual Tutorial Coverage ✅

**Tasks 721-729** — Per-file reading guides cho từng module trong `cogmem_api`.

Artifacts: `tutorials/per-file/*.md`

---

## Phase E Pre-work: Audits + Retain Re-tests ✅

**Tasks 730-742** — Tutorial convention audit, CI/CD setup, retain test re-audits.

Ghi chú đánh số: Tasks 730-742 trong logs đã dùng cho tutorial convention audit, CI/CD setup, và retain test re-audits. Phase E chính thức bắt đầu từ task 743 (Sprint S20).
