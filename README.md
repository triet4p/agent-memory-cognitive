# CogMem - Agent Memory Cognitive

Repository này chứa mã nguồn, tài liệu và artifact migration cho CogMem: hệ thống long-term conversational memory theo hướng cognitively grounded.

## Mục tiêu chính
1. Xây dựng và kiểm chứng kiến trúc retain/recall/reflect cho bộ nhớ hội thoại dài hạn.
2. Distill và đánh giá benchmark (LongMemEval, LoCoMo) theo các năng lực trọng tâm.
3. Duy trì bộ tutorial chuẩn hóa theo hướng top-down và per-file để onboarding/debug nhanh.

## 4 mục lớn trên GitHub Pages
Trang Pages của dự án được tổ chức thành 4 mục lớn:
1. Dự án tổng quan: README (tài liệu này)
2. Idea: `docs/CogMem-Idea.md`
3. Plan: `docs/PLAN.md`
4. Tutorials: toàn bộ tài liệu cũ trong `tutorials/`

## Tài liệu quan trọng
1. Idea: [docs/CogMem-Idea.md](docs/CogMem-Idea.md)
2. Plan: [docs/PLAN.md](docs/PLAN.md)
3. Tutorials index: [tutorials/INDEX.md](tutorials/INDEX.md)
4. Per-file reading order: [tutorials/per-file/READING-ORDER.md](tutorials/per-file/READING-ORDER.md)

## Cấu trúc repo (rút gọn)
```text
.
|- cogmem_api/
|- docs/
|- tutorials/
|- tests/artifacts/
|- scripts/
|- docker/
|- .github/workflows/
|- pyproject.toml
`- README.md
```

## Yêu cầu môi trường
1. Python >= 3.13
2. uv (khuyến nghị quản lý môi trường)

Cài dependencies:
```bash
uv sync
```

Kích hoạt môi trường ảo trên Windows:
```powershell
.\.venv\Scripts\Activate.ps1
```

## Chạy API nhanh (local)
```bash
uv run cogmem-api
```

Health check:
```bash
curl http://localhost:8888/health
```

## Docker và smoke test
1. Build image:
```bash
docker build -f docker/standalone/Dockerfile -t cogmem:local .
```

2. Chạy smoke test end-to-end:
```bash
./docker/test-image.sh cogmem:local
```

PowerShell:
```powershell
.\docker\test-image.ps1 -Image cogmem:local
```

## CI/CD cho Tutorials App
Workflow deploy Pages: [.github/workflows/tutorials-app-cicd.yml](.github/workflows/tutorials-app-cicd.yml)

Trigger chính:
1. Push vào branch `master`
2. Khi thay đổi `README.md`, `docs/**`, `tutorials/**`, `mkdocs.yml`, `requirements-docs.txt`

Build docs local:
```bash
uv run --with mkdocs --with mkdocs-material --with mkdocs-include-markdown-plugin mkdocs build --config-file mkdocs.yml --site-dir site
```

## Ghi chú governance
1. Không sửa `docs/migration_idea_coverage_matrix.md` nếu chưa có yêu cầu explicit audit/update coverage.
2. Logs task phải có đủ section: Scope, Outputs Created, Verification Strategy Applied.
3. Tutorials canonical per-file nằm ở `tutorials/per-file/`; `tutorials/functions/` là inventory/deep-dive function-level hỗ trợ.