# Batch evaluation script for CogMem E7 profile across LongMemEval-S conversations
# Runs recall-only pipeline for each conversation index 0-11

param(
    [string]$VERSION = "v14",
    [string]$PROFILE_ = "E7",
    [string]$FIXTURE = "longmemeval",
    [int]$TIMEOUT_MS = 15000,
    [int]$START_INDEX = 0,
    [int]$END_INDEX = 34
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

$CHECKPOINT_DIR = "experiments/${VERSION}/checkpoints_5"
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
            --pipeline full `
            --profile $PROFILE_ `
            --fixture $FIXTURE `
            --conv-index $N `
            --bank-id $bankE567 `
            --checkpoint-dir $CHECKPOINT_DIR `
            --output-dir $OUTPUT_DIR `
            --api-timeout $TIMEOUT_MS `
            --skip-retain

        Write-Host "[$current/$total] ConvIdx=$N PASSED" -ForegroundColor Green
    }
    catch {
        $failed++
        Write-Host "[$current/$total] ConvIdx=$N FAILED: $_" -ForegroundColor Red
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