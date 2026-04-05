# S19.6 Manual Tutorial - scripts/run_hindsight.ps1

## Purpose
- Khởi chạy container Hindsight baseline với cấu hình LLM qua ngrok để benchmark/so sánh.
- Cung cấp command mẫu 1 bước cho môi trường Windows.

## Source File
- scripts/run_hindsight.ps1

## Symbol-by-symbol explanation
### $NGROK_URL
- Endpoint ngrok có hậu tố /v1 để tương thích API OpenAI-compatible từ backend chạy xa.

### docker run ...
- Chạy image ghcr.io/vectorize-io/hindsight:latest.
- Mapping cổng 8888 và 9999.
- Truyền ENV HINDSIGHT_API_* cho model, timeout, token limit, log level.
- Mount volume local ~/.hindsight-docker sang /home/hindsight/.pg0 để lưu state.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Người vận hành chạy trực tiếp script để dựng Hindsight baseline.

### Outbound dependencies
- Docker image: ghcr.io/vectorize-io/hindsight:latest.
- Endpoint ngrok external.

## Runtime implications/side effects
- Tạo container interactive (--rm -it), dừng container là xóa instance.
- Persist dữ liệu qua volume ~/.hindsight-docker.

## Failure modes
- NGROK_URL hết hạn/không reachable.
- Docker pull image thất bại hoặc mạng chậm.
- Cấu hình model không đúng làm Hindsight API không phản hồi như kỳ vọng.

## Verify commands
```powershell
pwsh -NoProfile -Command "$null=$tokens=$null; $errors=$null; [System.Management.Automation.Language.Parser]::ParseFile('scripts/run_hindsight.ps1',[ref]$tokens,[ref]$errors) | Out-Null; if($errors.Count -gt 0){$errors | ForEach-Object { $_.ToString() }; exit 1}; 'OK'"
uv run python -c "from pathlib import Path; print(Path('scripts/run_hindsight.ps1').exists())"
```
