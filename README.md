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

## 6. Chạy Docker (Sprint 5)

Backfill B5 chuẩn hóa contract chạy runtime để retain LLM hoạt động thực chiến. Các biến tối thiểu cần khai báo:

- `COGMEM_API_LLM_PROVIDER`
- `COGMEM_API_LLM_MODEL`
- `COGMEM_API_LLM_API_KEY`
- `COGMEM_API_LLM_BASE_URL` (nếu dùng OpenAI-compatible proxy/local endpoint)
- `COGMEM_API_LLM_TIMEOUT`
- `COGMEM_API_RETAIN_LLM_TIMEOUT`
- `COGMEM_API_REFLECT_LLM_TIMEOUT`
- `COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS`
- `COGMEM_API_RETAIN_EXTRACTION_MODE`

### 6.1 Standalone với embedded pg0

Build image:

```bash
docker build -f docker/standalone/Dockerfile -t cogmem:local .
```

Run container:

```bash
docker run --rm -it -p 8888:8888 \
	-e COGMEM_API_DATABASE_URL=pg0 \
	-v $HOME/.cogmem-docker:/home/cogmem/.pg0 \
	cogmem:local
```

Health check:

```bash
curl http://localhost:8888/health
```

### 6.2 Docker Compose với external PostgreSQL

```bash
cp .env.example .env
# cập nhật COGMEM_DB_PASSWORD và các biến LLM nếu cần
docker compose --env-file .env -f docker/docker-compose/external-pg/docker-compose.yaml up --build
```

### 6.3 Smoke test retain/recall qua container

Sau khi container healthy:

```bash
./scripts/smoke-test-cogmem.sh http://localhost:8888
```

PowerShell (Windows):

```powershell
.\scripts\smoke-test-cogmem.ps1 http://localhost:8888
```

Hoặc chạy end-to-end build + health + retain/recall smoke bằng script:

```bash
./docker/test-image.sh cogmem:local
```

PowerShell (Windows):

```powershell
.\docker\test-image.ps1 -Image cogmem:local
```

Script `docker/test-image.sh` và `docker/test-image.ps1` hỗ trợ cả 2 chế độ DB qua `COGMEM_SMOKE_DATABASE_URL`:

- Embedded pg0 (mặc định): `COGMEM_SMOKE_DATABASE_URL=pg0`
- External PostgreSQL: `COGMEM_SMOKE_DATABASE_URL=postgresql://user:pass@host:5432/dbname`

### 6.4 Lệnh nhanh bằng scripts/docker (B5)

Linux/WSL (`scripts/docker.sh`) - chế độ embedded pg0:

```bash
COGMEM_API_LLM_PROVIDER=openai \
COGMEM_API_LLM_BASE_URL=http://host.docker.internal:11434/v1 \
COGMEM_API_LLM_API_KEY=ollama \
COGMEM_API_LLM_MODEL=qwen3:8b \
COGMEM_API_RETAIN_EXTRACTION_MODE=concise \
./scripts/docker.sh embedded
```

Linux/WSL (`scripts/docker.sh`) - chế độ external PostgreSQL:

```bash
COGMEM_EXTERNAL_DATABASE_URL=postgresql://cogmem_user:change-me@localhost:5432/cogmem_db \
COGMEM_API_LLM_PROVIDER=openai \
COGMEM_API_LLM_BASE_URL=http://host.docker.internal:11434/v1 \
COGMEM_API_LLM_API_KEY=ollama \
COGMEM_API_LLM_MODEL=qwen3:8b \
./scripts/docker.sh external
```

PowerShell (`scripts/docker.ps1`) - chế độ embedded pg0:

```powershell
$env:COGMEM_API_LLM_PROVIDER = "openai"
$env:COGMEM_API_LLM_BASE_URL = "http://host.docker.internal:11434/v1"
$env:COGMEM_API_LLM_API_KEY = "ollama"
$env:COGMEM_API_LLM_MODEL = "qwen3:8b"
$env:COGMEM_API_RETAIN_EXTRACTION_MODE = "concise"
.\scripts\docker.ps1 -Mode embedded
```

PowerShell (`scripts/docker.ps1`) - chế độ external PostgreSQL:

```powershell
$env:COGMEM_EXTERNAL_DATABASE_URL = "postgresql://cogmem_user:change-me@localhost:5432/cogmem_db"
$env:COGMEM_API_LLM_PROVIDER = "openai"
$env:COGMEM_API_LLM_BASE_URL = "http://host.docker.internal:11434/v1"
$env:COGMEM_API_LLM_API_KEY = "ollama"
$env:COGMEM_API_LLM_MODEL = "qwen3:8b"
.\scripts\docker.ps1 -Mode external
```

## 7. Distill dữ liệu

Chạy pipeline distill:

```bash
uv run python -m scripts.distill_dataset
```

### 7.1 LongMemEval

Heuristic chính:

- Lấy theo quota cho Knowledge Update, Temporal Reasoning, Multi-session.
- Bổ sung nhóm Abstention qua hậu tố question_id là _abs.
- Bổ sung nhóm Prospective theo từ khóa ý định tương lai.
- Giữ thêm nhóm single-session-user và single-session-preference để phủ tín hiệu habit/profile.

### 7.2 LoCoMo

Heuristic chính:

- Lọc hard QA theo khoảng cách bằng chứng và từ khóa nhân quả/thói quen.
- Giữ toàn bộ QA trong mỗi hội thoại đã lọc.
- Giảm quy mô ở mức hội thoại (conversation-level sampling), hiện tại khoảng 5 hội thoại đầy đủ.

### 7.3 Tệp đầu ra

- [data/longmemeval_s_distilled.json](data/longmemeval_s_distilled.json)
- [data/locomo_distilled.json](data/locomo_distilled.json)

## 8. Đánh giá chi phí HINDSIGHT (tùy chọn)

Script [scripts/test_hindsight.py](scripts/test_hindsight.py) dùng để đo chi phí xây dựng memory graph trên mẫu LongMemEval distilled.

Điều kiện trước khi chạy:

- HINDSIGHT API hoạt động tại http://localhost:8888/v1/default
- Script có thể tạo/xóa bank test và ghi tệp final_stats_*.json

Lệnh chạy:

```bash
uv run python -m scripts.test_hindsight
```

## 9. Ghi chú vận hành

- Dữ liệu trong thư mục data là dữ liệu thực nghiệm, nên commit có kiểm soát và backup trước khi chạy distill lại.
- Pipeline dùng random seed cố định để đảm bảo tái lập kết quả.

## 10. Tiến độ Migration CogMem (đến hết Sprint 5.3)

Trạng thái hiện tại theo [docs/PLAN.md](docs/PLAN.md):

- Sprint 0 hoàn tất: T0.1, T0.2
- Sprint 1 hoàn tất: T1.1, T1.2, T1.3
- Sprint 2 hoàn tất: T2.1, T2.2, T2.3, T2.4

Các thành phần đã có trong `cogmem_api` sau Sprint 2:

- Retain baseline pipeline độc lập trong `cogmem_api/engine/retain/`
- Habit Network + `s_r_link`
- Intention lifecycle transitions (`fulfilled_by`, `triggered`, `enabled_by`, `abandoned` status-only)
- Action-Effect parsing (precondition/action/outcome) + `a_o_causal`

Artifact logs hiện có:

- [logs/task_201_summary.md](logs/task_201_summary.md)
- [logs/task_202_summary.md](logs/task_202_summary.md)
- [logs/task_203_summary.md](logs/task_203_summary.md)
- [logs/task_204_summary.md](logs/task_204_summary.md)
- [logs/task_501_summary.md](logs/task_501_summary.md)
- [logs/task_502_summary.md](logs/task_502_summary.md)
- [logs/task_503_summary.md](logs/task_503_summary.md)

Artifact tests cho Sprint 2:

- [tests/artifacts/test_task201_retain_baseline.py](tests/artifacts/test_task201_retain_baseline.py)
- [tests/artifacts/test_task202_habit_network.py](tests/artifacts/test_task202_habit_network.py)
- [tests/artifacts/test_task203_intention_lifecycle.py](tests/artifacts/test_task203_intention_lifecycle.py)
- [tests/artifacts/test_task204_action_effect.py](tests/artifacts/test_task204_action_effect.py)

Lệnh kiểm tra nhanh:

```bash
uv run python tests/artifacts/test_task201_retain_baseline.py
uv run python tests/artifacts/test_task202_habit_network.py
uv run python tests/artifacts/test_task203_intention_lifecycle.py
uv run python tests/artifacts/test_task204_action_effect.py
```