# Batch evaluation script for CogMem E7 profile across LongMemEval-S conversations
# Runs recall-only pipeline for each conversation index 0-11

param(
    [string]$VERSION = "v15",
    [string]$PROFILE_ = "E7",
    [string]$FIXTURE = "longmemeval",
    [int]$TIMEOUT_MS = 15000,
    [int]$START_INDEX = 0,
    [int]$END_INDEX = 34,
    [int]$SLEEP_SECONDS = 120
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

$LLM_BASE_URL = if ($env:COGMEM_API_LLM_BASE_URL) { $env:COGMEM_API_LLM_BASE_URL } else { "https://unvacillating-braden-worriless.ngrok-free.dev/v1" }
$LLM_MODEL    = if ($env:COGMEM_API_LLM_MODEL)    { $env:COGMEM_API_LLM_MODEL }    else { "ministral3-3b" }
$LLM_API_KEY  = if ($env:COGMEM_API_LLM_API_KEY)  { $env:COGMEM_API_LLM_API_KEY }  else { "openai" }

function Invoke-LLMKeepAlive {
    $base = $LLM_BASE_URL.TrimEnd("/")
    $endpoint = if ($base.EndsWith("/chat/completions")) { $base }
                elseif ($base.EndsWith("/v1"))           { "$base/chat/completions" }
                else                                     { "$base/v1/chat/completions" }

    $headers = @{ "Content-Type" = "application/json"; "Authorization" = "Bearer $LLM_API_KEY" }
    $body = @{
        model                 = $LLM_MODEL
        messages              = @(@{ role = "user"; content = "ping" })
        temperature           = 0.1
        max_completion_tokens = 1
    } | ConvertTo-Json -Depth 5 -Compress

    try {
        $null = Invoke-RestMethod -Method Post -Uri $endpoint -Headers $headers -Body $body -TimeoutSec 12
        Write-Host "  [keep-alive] OK" -ForegroundColor DarkGray
    } catch {
        Write-Host "  [keep-alive] WARN: $_" -ForegroundColor DarkYellow
    }
}

function Start-SleepWithKeepAlive {
    param([int]$Seconds)
    $remaining = $Seconds
    while ($remaining -gt 0) {
        Invoke-LLMKeepAlive
        $chunk = [Math]::Min(15, $remaining)
        Write-Host "  Sleeping ${chunk}s (${remaining}s remaining)..." -ForegroundColor DarkGray
        Start-Sleep -Seconds $chunk
        $remaining -= $chunk
    }
}

$CHECKPOINT_DIR = "experiments/${VERSION}/checkpoints-s29-wave2b"
$OUTPUT_DIR = "experiments/${VERSION}/"

Write-Host "=== CogMem Batch Eval ===" -ForegroundColor Cyan
Write-Host "  VERSION:     $VERSION"
Write-Host "  PROFILE:     $PROFILE_"
Write-Host "  FIXTURE:     $FIXTURE"
Write-Host "  CONV_RANGE:  $START_INDEX .. $END_INDEX"
Write-Host "  CHECKPOINT:  $CHECKPOINT_DIR"
Write-Host "  OUTPUT:      $OUTPUT_DIR"
Write-Host ""

$total = ($END_INDEX - $START_INDEX + 1)
$current = 0
$failed = 0

for ($N = $START_INDEX; $N -le $END_INDEX; $N++) {
    $current++
    if ($VERSION -eq "v14" -and $N -ge 10 -and $N -le 19) {
        $bankE567 = "COGMEM_EXP__e567_c{0:D3}" -f $N
    } else {
        $bankE567 = "COGMEM_EXP_${VERSION}_e567_c{0:D3}" -f $N
    }

    Write-Host "[$current/$total] ConvIdx=$N | Bank=$bankE567" -ForegroundColor Yellow

    try {
        uv run python -m scripts.eval_cogmem `
            --pipeline recall `
            --profile $PROFILE_ `
            --fixture $FIXTURE `
            --conv-index $N `
            --bank-id $bankE567 `
            --checkpoint-dir $CHECKPOINT_DIR `
            --output-dir $OUTPUT_DIR `
            --api-timeout $TIMEOUT_MS
            # --skip-retain

        Write-Host "[$current/$total] ConvIdx=$N PASSED" -ForegroundColor Green
    }
    catch {
        $failed++
        Write-Host "[$current/$total] ConvIdx=$N FAILED: $_" -ForegroundColor Red
    }

    if ($SLEEP_SECONDS -gt 0) {
        Start-SleepWithKeepAlive -Seconds $SLEEP_SECONDS
    }

    Write-Host ""
}

Write-Host "=== Batch Complete ===" -ForegroundColor Cyan
Write-Host "  Total:    $total"
Write-Host "  Passed:   $($total - $failed)"
Write-Host "  Failed:   $failed"

if ($failed -gt 0) {
    exit 1
}
exit 0