#!/usr/bin/env pwsh
param(
    [string]$BaseUrl = "http://localhost:8888"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$bankId = "cogmem-smoke-$PID"

Write-Host "Running retain/recall smoke test against: $BaseUrl"
Write-Host "Bank: $bankId"

Write-Host ""
Write-Host "--- Retain ---"
$retainBody = @{
    items = @(
        @{
            content = "Alice is a software engineer who likes distributed systems and Python."
        }
    )
} | ConvertTo-Json -Depth 5

$retainResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/v1/default/banks/$bankId/memories" -ContentType "application/json" -Body $retainBody
$retainResponse | ConvertTo-Json -Depth 8

if ($retainResponse.success -ne $true) {
    throw "FAIL: retain did not return success=true"
}

Write-Host ""
Write-Host "--- Recall ---"
$recallBody = @{ query = "What does Alice do?" } | ConvertTo-Json -Depth 5
$recallResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/v1/default/banks/$bankId/memories/recall" -ContentType "application/json" -Body $recallBody
$recallResponse | ConvertTo-Json -Depth 8

$resultsCount = @($recallResponse.results).Count
if ($resultsCount -le 0) {
    throw "FAIL: recall returned no results"
}

Write-Host ""
Write-Host "PASS: retain/recall smoke test"
