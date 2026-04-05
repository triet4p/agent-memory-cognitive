# S19.6 Manual Tutorial - scripts/docker.ps1

## Purpose
- Wrapper PowerShell tương đương scripts/docker.sh để build/chạy CogMem Docker theo mode embedded/external.
- Chuẩn hóa cấu hình runtime qua biến môi trường trên Windows.

## Source File
- scripts/docker.ps1

## Symbol-by-symbol explanation
### param([ValidateSet("embedded", "external")] $Mode)
- Khóa mode hợp lệ, mặc định embedded.

### Get-EnvOrDefault
- Helper đọc biến môi trường với fallback mặc định.

### Các biến config runtime
- Nạp image/port/schema/compose path/LLM settings/retain knobs/embedding/reranker settings.

### $dockerArgs
- Tập tham số chung cho docker run (port + ENV runtime).

### switch ($Mode)
- embedded:
  - build image từ docker/standalone/Dockerfile
  - tạo volume pg0
  - chạy docker run.
- external:
  - có external URL => chạy docker run trực tiếp với DB ngoài.
  - không có external URL => chạy docker compose với env file.

### Symbol inventory bổ sung (full names)
- $ErrorActionPreference, $value, $image, $port, $logLevel, $schema, $pg0VolumeDir, $externalDatabaseUrl, $repoRoot, $composeFile, $composeEnvFile, $dockerIncludeLocalModels, $dockerPreloadMlModels, $llmProvider, $llmBaseUrl, $llmApiKey, $llmModel, $llmTimeout, $retainLlmTimeout, $reflectLlmTimeout, $retainMaxCompletionTokens, $retainExtractionMode

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Người vận hành local trên Windows gọi script để khởi chạy container.

### Outbound dependencies
- docker/standalone/Dockerfile
- docker/docker-compose/external-pg/docker-compose.yaml
- .env (khi chạy compose)
- Docker CLI / Docker Compose

## Runtime implications/side effects
- Build image và chạy container/stack, có thể tốn tài nguyên đáng kể.
- embedded mode mount dữ liệu pg0 vào COGMEM_PG0_VOLUME_DIR.

## Failure modes
- Docker daemon chưa chạy hoặc lệnh docker/compose không có sẵn.
- Thiếu file .env trong external compose mode.
- Lỗi permission với volume path.

## Verify commands
```powershell
pwsh -NoProfile -Command "$null=$tokens=$null; $errors=$null; [System.Management.Automation.Language.Parser]::ParseFile('scripts/docker.ps1',[ref]$tokens,[ref]$errors) | Out-Null; if($errors.Count -gt 0){$errors | ForEach-Object { $_.ToString() }; exit 1}; 'OK'"
uv run python -c "from pathlib import Path; print(Path('scripts/docker.ps1').exists())"
```

