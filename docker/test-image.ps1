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
    "-e", "COGMEM_API_RETAIN_EXTRACTION_MODE=$retainExtractionMode"
)

if (-not [string]::IsNullOrWhiteSpace($llmBaseUrl)) {
    $dockerRunArgs += @("-e", "COGMEM_API_LLM_BASE_URL=$llmBaseUrl")
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

    Write-Host ""
    Write-Host "=== Container Logs (last 50 lines) ==="
    & docker logs --tail 50 $containerName
    Write-Host ""
    Write-Host "PASS: Docker smoke test"
}
finally {
    & $cleanupContainer $containerName
}
