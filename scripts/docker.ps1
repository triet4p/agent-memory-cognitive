#!/usr/bin/env pwsh
param(
    [ValidateSet("embedded", "external")]
    [string]$Mode = "embedded"
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

$image = Get-EnvOrDefault -Name "COGMEM_DOCKER_IMAGE" -Default "cogmem:local"
$port = Get-EnvOrDefault -Name "COGMEM_API_PORT" -Default "8888"
$logLevel = Get-EnvOrDefault -Name "COGMEM_API_LOG_LEVEL" -Default "info"
$schema = Get-EnvOrDefault -Name "COGMEM_API_DATABASE_SCHEMA" -Default "public"
$pg0VolumeDir = Get-EnvOrDefault -Name "COGMEM_PG0_VOLUME_DIR" -Default (Join-Path $HOME ".cogmem-docker")
$externalDatabaseUrl = Get-EnvOrDefault -Name "COGMEM_EXTERNAL_DATABASE_URL" -Default ""

# Backfill B5: minimal LLM + retain runtime contract.
$llmProvider = Get-EnvOrDefault -Name "COGMEM_API_LLM_PROVIDER" -Default "openai"
$llmBaseUrl = Get-EnvOrDefault -Name "COGMEM_API_LLM_BASE_URL" -Default ""
$llmApiKey = Get-EnvOrDefault -Name "COGMEM_API_LLM_API_KEY" -Default "dummy"
$llmModel = Get-EnvOrDefault -Name "COGMEM_API_LLM_MODEL" -Default "gpt-4o-mini"
$llmTimeout = Get-EnvOrDefault -Name "COGMEM_API_LLM_TIMEOUT" -Default "120"
$retainLlmTimeout = Get-EnvOrDefault -Name "COGMEM_API_RETAIN_LLM_TIMEOUT" -Default "120"
$reflectLlmTimeout = Get-EnvOrDefault -Name "COGMEM_API_REFLECT_LLM_TIMEOUT" -Default "120"
$retainMaxCompletionTokens = Get-EnvOrDefault -Name "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS" -Default "64000"
$retainExtractionMode = Get-EnvOrDefault -Name "COGMEM_API_RETAIN_EXTRACTION_MODE" -Default "concise"

$dockerArgs = @(
    "--rm", "-it", "--pull", "always",
    "-p", "$port`:8888",
    "-e", "COGMEM_API_HOST=0.0.0.0",
    "-e", "COGMEM_API_PORT=8888",
    "-e", "COGMEM_API_LOG_LEVEL=$logLevel",
    "-e", "COGMEM_API_DATABASE_SCHEMA=$schema",
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
    $dockerArgs += @("-e", "COGMEM_API_LLM_BASE_URL=$llmBaseUrl")
}

switch ($Mode) {
    "embedded" {
        New-Item -ItemType Directory -Path $pg0VolumeDir -Force | Out-Null
        $dockerArgs += @("-e", "COGMEM_API_DATABASE_URL=pg0")
        $dockerArgs += @("-v", (($pg0VolumeDir) + ":/home/cogmem/.pg0"))
    }
    "external" {
        if ([string]::IsNullOrWhiteSpace($externalDatabaseUrl)) {
            throw "COGMEM_EXTERNAL_DATABASE_URL is required for external mode."
        }

        $dockerArgs += @("-e", "COGMEM_API_DATABASE_URL=$externalDatabaseUrl")
    }
}

Write-Host "Starting CogMem container"
Write-Host "  Mode: $Mode"
Write-Host "  Image: $image"
Write-Host "  Port: $port"
Write-Host "  LLM provider/model: $llmProvider/$llmModel"
if (-not [string]::IsNullOrWhiteSpace($llmBaseUrl)) {
    Write-Host "  LLM base URL: $llmBaseUrl"
}

& docker run @dockerArgs $image
