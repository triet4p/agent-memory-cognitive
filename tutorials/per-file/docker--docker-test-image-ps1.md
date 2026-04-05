# S19.6 Manual Tutorial - docker/test-image.ps1

## Purpose
- Smoke test Docker image CogMem trên Windows/PowerShell.
- Xác thực chuỗi health + retain/recall smoke + guard deterministic embeddings.

## Source File
- docker/test-image.ps1

## Symbol-by-symbol explanation
### param([string]$Image)
- Bắt buộc truyền tên image để test.

### Get-EnvOrDefault
- Helper đọc env với fallback giá trị mặc định.

### Runtime config variables
- Nạp timeout, containerName, healthUrl, smoke settings, LLM/embedding/reranker knobs.

### $cleanupContainer
- Script block dọn container cũ/mới để tránh xung đột tên.

### $dockerRunArgs
- Danh sách tham số chạy container và pass ENV runtime.
- Có bổ sung tùy chọn theo điều kiện (llm base url, embeddings openai, reranker tei).

### Health polling loop
- Poll health endpoint tối đa timeout giây.
- Nếu container chết sớm thì in log và fail ngay.

### Smoke execution
- Gọi scripts/smoke-test-cogmem.ps1 để kiểm tra retain/recall.
- Nếu bật yêu cầu non-deterministic local embeddings, scan logs để chặn fallback deterministic.

### finally block
- Luôn cleanup container, kể cả khi test fail.

### Symbol inventory bổ sung (full names)
- $ErrorActionPreference, $value, $scriptDir, $repoRoot, $timeout, $containerName, $healthUrl, $smokeBaseUrl, $smokeDatabaseUrl, $smokePg0VolumeDir, $smokeRequireNonDeterministic, $llmProvider, $llmBaseUrl, $llmApiKey, $llmModel, $llmTimeout, $retainLlmTimeout, $reflectLlmTimeout, $retainMaxCompletionTokens, $retainExtractionMode, $embeddingsProvider, $embeddingsLocalModel, $embeddingsOpenAiModel, $embeddingsOpenAiBaseUrl, $embeddingsOpenAiApiKey, $rerankerProvider, $rerankerLocalModel, $rerankerTeiUrl, $rerankerTeiBatchSize, $rerankerMaxCandidates, $startTime, $healthy, $running, $duration, $containerLogs

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Người vận hành chạy trực tiếp script này để test image trên Windows.

### Outbound dependencies
- scripts/smoke-test-cogmem.ps1
- Docker CLI
- CogMem API /health

## Runtime implications/side effects
- Tạo và xóa container smoke test.
- Có thể mount volume pg0 smoke dir.
- In logs cuối để hỗ trợ debug.

## Failure modes
- Image không tồn tại hoặc pull/build lỗi.
- Health timeout/container crash.
- retain/recall smoke fail.
- Phát hiện fallback deterministic embeddings khi local embeddings được yêu cầu.

## Verify commands
```powershell
pwsh -NoProfile -Command "$null=$tokens=$null; $errors=$null; [System.Management.Automation.Language.Parser]::ParseFile('docker/test-image.ps1',[ref]$tokens,[ref]$errors) | Out-Null; if($errors.Count -gt 0){$errors | ForEach-Object { $_.ToString() }; exit 1}; 'OK'"
pwsh -NoProfile -File docker/test-image.ps1 -Image cogmem:local
```

