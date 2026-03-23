# CogMem: A Cognitively-Grounded Framework for Long-Term Conversational Memory

Kho mã nguồn phục vụ nghiên cứu và thực nghiệm cho đề tài đồ án theo hướng CogMem (long-term conversational memory), tập trung vào distill benchmark và đánh giá hành vi hệ thống bộ nhớ hội thoại.

## 1. Mục tiêu

Mục tiêu của repository:

- Tạo tập dữ liệu distilled từ LongMemEval và LoCoMo theo các nhóm năng lực trọng tâm.
- Xây dựng bộ kiểm thử gọn, đủ khó để đo đóng góp của CogMem V3.
- Hỗ trợ đánh giá chi phí xử lý/ghi nhớ của baseline HINDSIGHT trên các mẫu đại diện.

Các nhóm năng lực chính đang được bao phủ:

- Knowledge Update
- Multi-session / Multi-hop reasoning
- Temporal Reasoning
- Abstention (hallucination control)
- Prospective / Intention signals
- Preference / User profile cues

## 2. Tài liệu nền tảng

Các tài liệu chính của đề tài:

- Ý tưởng hệ thống: [docs/CogMem-Idea.md](docs/CogMem-Idea.md)
- Slide đề cương: [docs/slides/DATN_Proposal.pptx](docs/slides/DATN_Proposal.pptx)
- Phiếu giao nhiệm vụ đồ án: [docs/PGNV/LeMinhTriet.PGNV-DATN-20252.xlsx](docs/PGNV/LeMinhTriet.PGNV-DATN-20252.xlsx)

## 3. Cấu trúc thư mục

```text
.
|- data/
|  |- LongMemEval/
|  |- LoCoMo/
|  |- longmemeval_s_distilled.json
|  `- locomo_distilled.json
|- docs/
|  |- CogMem-Idea.md
|  |- slides/
|  `- PGNV/
|- scripts/
|  |- distill_dataset.py
|  `- test_hindsight.py
|- src/
|- pyproject.toml
`- README.md
```

## 4. Yêu cầu môi trường

- Python >= 3.13
- uv (khuyến nghị để quản lý môi trường/phụ thuộc)

Phụ thuộc hiện tại (khai báo trong pyproject.toml):

- hindsight-client
- requests

## 5. Cài đặt

```bash
uv sync
```

Kích hoạt môi trường ảo trên Windows (nếu cần):

```powershell
.\.venv\Scripts\Activate.ps1
```

## 6. Distill dữ liệu

Chạy pipeline distill:

```bash
uv run python -m scripts.distill_dataset
```

### 6.1 LongMemEval

Heuristic chính:

- Lấy theo quota cho Knowledge Update, Temporal Reasoning, Multi-session.
- Bổ sung nhóm Abstention qua hậu tố question_id là _abs.
- Bổ sung nhóm Prospective theo từ khóa ý định tương lai.
- Giữ thêm nhóm single-session-user và single-session-preference để phủ tín hiệu habit/profile.

### 6.2 LoCoMo

Heuristic chính:

- Lọc hard QA theo khoảng cách bằng chứng và từ khóa nhân quả/thói quen.
- Giữ toàn bộ QA trong mỗi hội thoại đã lọc.
- Giảm quy mô ở mức hội thoại (conversation-level sampling), hiện tại khoảng 5 hội thoại đầy đủ.

### 6.3 Tệp đầu ra

- [data/longmemeval_s_distilled.json](data/longmemeval_s_distilled.json)
- [data/locomo_distilled.json](data/locomo_distilled.json)

## 7. Đánh giá chi phí HINDSIGHT (tùy chọn)

Script [scripts/test_hindsight.py](scripts/test_hindsight.py) dùng để đo chi phí xây dựng memory graph trên mẫu LongMemEval distilled.

Điều kiện trước khi chạy:

- HINDSIGHT API hoạt động tại http://localhost:8888/v1/default
- Script có thể tạo/xóa bank test và ghi tệp final_stats_*.json

Lệnh chạy:

```bash
uv run python -m scripts.test_hindsight
```

## 8. Ghi chú vận hành

- Dữ liệu trong thư mục data là dữ liệu thực nghiệm, nên commit có kiểm soát và backup trước khi chạy distill lại.
- Pipeline dùng random seed cố định để đảm bảo tái lập kết quả.