#!/usr/bin/env pwsh
param(
    [Parameter(Mandatory = $true)]
    [string]$Image
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-EnvOrDefault {
    param(
        [string]$Name,
        [string]$Default
    )

    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) {
        return $Default
    }

    return $value
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

$timeout = [int](Get-EnvOrDefault -Name "SMOKE_TEST_TIMEOUT" -Default "120")
$containerName = Get-EnvOrDefault -Name "SMOKE_TEST_CONTAINER_NAME" -Default "cogmem-smoke-test"
$healthUrl = Get-EnvOrDefault -Name "COGMEM_API_HEALTH_URL" -Default "http://localhost:8888/health"
$smokeBaseUrl = Get-EnvOrDefault -Name "COGMEM_SMOKE_BASE_URL" -Default "http://localhost:8888"
$smokeDatabaseUrl = Get-EnvOrDefault -Name "COGMEM_SMOKE_DATABASE_URL" -Default "pg0"
$smokePg0VolumeDir = Get-EnvOrDefault -Name "COGMEM_SMOKE_PG0_VOLUME_DIR" -Default (Join-Path $HOME ".cogmem-docker-smoke")
$smokeRequireNonDeterministic = Get-EnvOrDefault -Name "COGMEM_SMOKE_REQUIRE_NON_DETERMINISTIC" -Default "true"

# Backfill B5: pass through LLM + retain knobs for real retain runtime.
$llmProvider = Get-EnvOrDefault -Name "COGMEM_API_LLM_PROVIDER" -Default "openai"
$llmBaseUrl = Get-EnvOrDefault -Name "COGMEM_API_LLM_BASE_URL" -Default ""
$llmApiKey = Get-EnvOrDefault -Name "COGMEM_API_LLM_API_KEY" -Default "dummy"
$llmModel = Get-EnvOrDefault -Name "COGMEM_API_LLM_MODEL" -Default "gpt-4o-mini"
$llmTimeout = Get-EnvOrDefault -Name "COGMEM_API_LLM_TIMEOUT" -Default "120"
$retainLlmTimeout = Get-EnvOrDefault -Name "COGMEM_API_RETAIN_LLM_TIMEOUT" -Default "120"
$reflectLlmTimeout = Get-EnvOrDefault -Name "COGMEM_API_REFLECT_LLM_TIMEOUT" -Default "120"
$retainMaxCompletionTokens = Get-EnvOrDefault -Name "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS" -Default "64000"
$retainExtractionMode = Get-EnvOrDefault -Name "COGMEM_API_RETAIN_EXTRACTION_MODE" -Default "concise"
$embeddingsProvider = Get-EnvOrDefault -Name "COGMEM_API_EMBEDDINGS_PROVIDER" -Default "local"
$embeddingsLocalModel = Get-EnvOrDefault -Name "COGMEM_API_EMBEDDINGS_LOCAL_MODEL" -Default "BAAI/bge-small-en-v1.5"
$embeddingsOpenAiModel = Get-EnvOrDefault -Name "COGMEM_API_EMBEDDINGS_OPENAI_MODEL" -Default "text-embedding-3-small"
$embeddingsOpenAiBaseUrl = Get-EnvOrDefault -Name "COGMEM_API_EMBEDDINGS_OPENAI_BASE_URL" -Default ""
$embeddingsOpenAiApiKey = Get-EnvOrDefault -Name "COGMEM_API_EMBEDDINGS_OPENAI_API_KEY" -Default ""
$rerankerProvider = Get-EnvOrDefault -Name "COGMEM_API_RERANKER_PROVIDER" -Default "rrf"
$rerankerLocalModel = Get-EnvOrDefault -Name "COGMEM_API_RERANKER_LOCAL_MODEL" -Default "cross-encoder/ms-marco-MiniLM-L-6-v2"
$rerankerTeiUrl = Get-EnvOrDefault -Name "COGMEM_API_RERANKER_TEI_URL" -Default ""
$rerankerTeiBatchSize = Get-EnvOrDefault -Name "COGMEM_API_RERANKER_TEI_BATCH_SIZE" -Default "128"
$rerankerMaxCandidates = Get-EnvOrDefault -Name "COGMEM_API_RERANKER_MAX_CANDIDATES" -Default "300"

$cleanupContainer = {
    param([string]$Name)
    & docker stop $Name | Out-Null 2>$null
    & docker rm $Name | Out-Null 2>$null
}

& $cleanupContainer $containerName

Write-Host "Starting CogMem Docker smoke test"
Write-Host "  Image: $Image"
Write-Host "  Health URL: $healthUrl"
Write-Host "  Timeout: ${timeout}s"
Write-Host "  Database mode: $smokeDatabaseUrl"
Write-Host "  LLM provider/model: $llmProvider/$llmModel"
Write-Host "  Embeddings provider: $embeddingsProvider"
if (-not [string]::IsNullOrWhiteSpace($llmBaseUrl)) {
    Write-Host "  LLM base URL: $llmBaseUrl"
}

$dockerRunArgs = @(
    "-d",
    "--name", $containerName,
    "-p", "8888:8888",
    "-e", "COGMEM_API_DATABASE_URL=$smokeDatabaseUrl",
    "-e", "COGMEM_API_LLM_PROVIDER=$llmProvider",
    "-e", "COGMEM_API_LLM_API_KEY=$llmApiKey",
    "-e", "COGMEM_API_LLM_MODEL=$llmModel",
    "-e", "COGMEM_API_LLM_TIMEOUT=$llmTimeout",
    "-e", "COGMEM_API_RETAIN_LLM_TIMEOUT=$retainLlmTimeout",
    "-e", "COGMEM_API_REFLECT_LLM_TIMEOUT=$reflectLlmTimeout",
    "-e", "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS=$retainMaxCompletionTokens",
    "-e", "COGMEM_API_RETAIN_EXTRACTION_MODE=$retainExtractionMode",
    "-e", "COGMEM_API_EMBEDDINGS_PROVIDER=$embeddingsProvider",
    "-e", "COGMEM_API_EMBEDDINGS_LOCAL_MODEL=$embeddingsLocalModel",
    "-e", "COGMEM_API_EMBEDDINGS_OPENAI_MODEL=$embeddingsOpenAiModel",
    "-e", "COGMEM_API_RERANKER_PROVIDER=$rerankerProvider",
    "-e", "COGMEM_API_RERANKER_LOCAL_MODEL=$rerankerLocalModel",
    "-e", "COGMEM_API_RERANKER_TEI_BATCH_SIZE=$rerankerTeiBatchSize",
    "-e", "COGMEM_API_RERANKER_MAX_CANDIDATES=$rerankerMaxCandidates"
)

if (-not [string]::IsNullOrWhiteSpace($llmBaseUrl)) {
    $dockerRunArgs += @("-e", "COGMEM_API_LLM_BASE_URL=$llmBaseUrl")
}

if (-not [string]::IsNullOrWhiteSpace($embeddingsOpenAiBaseUrl)) {
    $dockerRunArgs += @("-e", "COGMEM_API_EMBEDDINGS_OPENAI_BASE_URL=$embeddingsOpenAiBaseUrl")
}

if (-not [string]::IsNullOrWhiteSpace($embeddingsOpenAiApiKey)) {
    $dockerRunArgs += @("-e", "COGMEM_API_EMBEDDINGS_OPENAI_API_KEY=$embeddingsOpenAiApiKey")
}

if (-not [string]::IsNullOrWhiteSpace($rerankerTeiUrl)) {
    $dockerRunArgs += @("-e", "COGMEM_API_RERANKER_TEI_URL=$rerankerTeiUrl")
}

if ($smokeDatabaseUrl.StartsWith("pg0")) {
    New-Item -ItemType Directory -Path $smokePg0VolumeDir -Force | Out-Null
    $dockerRunArgs += @("-v", (($smokePg0VolumeDir) + ":/home/cogmem/.pg0"))
}

& docker run @dockerRunArgs $Image | Out-Null

try {
    $startTime = Get-Date
    $healthy = $false

    for ($i = 1; $i -le $timeout; $i++) {
        try {
            Invoke-WebRequest -Uri $healthUrl -Method Get -TimeoutSec 3 | Out-Null
            $healthy = $true
            break
        }
        catch {
            $running = (& docker ps -q -f "name=$containerName").Trim()
            if ([string]::IsNullOrWhiteSpace($running)) {
                Write-Host "Container exited unexpectedly"
                & docker logs $containerName
                exit 1
            }

            if ($i % 10 -eq 0) {
                Write-Host "  Still waiting for health... (${i}s)"
            }

            Start-Sleep -Seconds 1
        }
    }

    if (-not $healthy) {
        Write-Host "Timed out waiting for health endpoint"
        & docker logs $containerName
        exit 1
    }

    $duration = [int]((Get-Date) - $startTime).TotalSeconds
    Write-Host "Health check passed after ${duration}s"

    Write-Host "Running retain/recall smoke checks..."
    & (Join-Path $repoRoot "scripts/smoke-test-cogmem.ps1") $smokeBaseUrl

    if ($smokeRequireNonDeterministic -eq "true" -and $embeddingsProvider -eq "local") {
        $containerLogs = (& docker logs $containerName 2>&1 | Out-String)
        if ($containerLogs -match "Falling back to deterministic embeddings") {
            throw "FAIL: local embeddings requested but runtime fell back to deterministic embeddings"
        }
    }

    Write-Host ""
    Write-Host "=== Container Logs (last 50 lines) ==="
    & docker logs --tail 50 $containerName
    Write-Host ""
    Write-Host "PASS: Docker smoke test"
}
finally {
    & $cleanupContainer $containerName
}
