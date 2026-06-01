# LoCoMo batch evaluation — two-phase (retain + eval) for cogmem_bench S35.
#
# LoCoMo distilled has 5 conversations and 161 QAs total. Unlike LongMemEval-S where each
# --conv-index is one full conversation, LoCoMo's --conv-index iterates per QA — multiple
# QAs share the same haystack. We therefore retain ONCE per conversation (5 banks) then
# eval all 161 QAs with --skip-retain, avoiding 32x redundant retain cost.
#
# Phases:
#   -PHASE retain : One eval_cogmem invocation per unique conv (--pipeline recall, no
#                   --skip-retain) → 5 banks populated. Cheap because recall pipeline
#                   skips answer generation.
#   -PHASE eval   : 161 eval invocations across the chosen $PROFILES, each with
#                   --skip-retain and the bank_id derived from the QA-to-conv mapping.
#   -PHASE all    : retain then eval (default).
#
# Usage:
#   .\scripts\eval_cogmem_batch_locomo.ps1                                   # all phases, E1 only
#   .\scripts\eval_cogmem_batch_locomo.ps1 -PHASE retain                     # just populate banks
#   .\scripts\eval_cogmem_batch_locomo.ps1 -PHASE eval -PROFILES @("E1","E7G")
#   .\scripts\eval_cogmem_batch_locomo.ps1 -START_INDEX 100 -END_INDEX 160   # eval a QA range

param(
    [string]$VERSION = "v20",
    # Default = E7 (Full CogMem — all 6 networks + adaptive router + SUM activation).
    # This is THE baseline number to claim against HINDSIGHT's published 89.61% LoCoMo.
    # Add "E1" to the list if you also want the strawman floor (no CogMem contributions →
    # HINDSIGHT-equivalent within CogMem code) for the "additions worth X pp" story.
    # Do NOT default to E7F or E7G here — those are diagnostic profiles for specific
    # ablations (S33 router-bias removal / S31 graph-channel isolation), not baselines.
    [string[]]$PROFILES = @("E7"),
    [ValidateSet("retain","eval","all")]
    [string]$PHASE = "all",
    [int]$TIMEOUT_MS = 120000,
    [int]$START_INDEX = 0,
    [int]$END_INDEX = 160,
    # Optional sparse QA list for targeted probes, e.g. -INDICES @(15,32,37).
    # When provided, Phase 2 eval ignores START_INDEX/END_INDEX and runs only these QAs.
    [int[]]$INDICES = @(),
    [int]$SLEEP_SECONDS = 0
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# ── QA-to-conversation mapping ────────────────────────────────────────────
# Source: data/locomo_distilled.json (frozen 2026-05-30).
# Verify with: uv run python scripts/locomo_mapping_dryrun.py
# Order matters — first range that contains $N wins.
$CONV_RANGES = @(
    @{ SampleId = "conv-30"; First = 0;   Last = 13  },
    @{ SampleId = "conv-26"; First = 14;  Last = 47  },
    @{ SampleId = "conv-43"; First = 48;  Last = 93  },
    @{ SampleId = "conv-50"; First = 94;  Last = 131 },
    @{ SampleId = "conv-47"; First = 132; Last = 160 }
)

function Get-SampleIdForQaIndex {
    param([int]$QaIdx)
    foreach ($r in $CONV_RANGES) {
        if ($QaIdx -ge $r.First -and $QaIdx -le $r.Last) {
            return $r.SampleId
        }
    }
    throw "QA index $QaIdx not in any conversation range (0..160)"
}

function Get-BankIdForSample {
    param([string]$SampleId)
    return "COGMEM_locomo_$SampleId"
}

# ── Common config (same surface as eval_cogmem_batch.ps1) ─────────────────
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

$CHECKPOINT_DIR = "experiments/${VERSION}/checkpoints/"
$OUTPUT_DIR     = "experiments/${VERSION}/"

Write-Host "=== CogMem LoCoMo Batch Eval ===" -ForegroundColor Cyan
Write-Host "  VERSION:     $VERSION"
Write-Host "  PHASE:       $PHASE"
Write-Host "  PROFILES:    $($PROFILES -join ', ')"
if ($INDICES.Count -gt 0) {
    Write-Host "  QA_INDICES:  $($INDICES -join ', ')  (sparse probe; LoCoMo total = 0..160 across 5 convs)"
} else {
    Write-Host "  QA_RANGE:    $START_INDEX .. $END_INDEX  (LoCoMo total = 0..160 across 5 convs)"
}
Write-Host "  TIMEOUT_MS:  $TIMEOUT_MS"
Write-Host "  CHECKPOINT:  $CHECKPOINT_DIR"
Write-Host "  OUTPUT:      $OUTPUT_DIR"
Write-Host ""

# ── Phase 1: Retain (one call per unique conv, no --skip-retain) ──────────
if ($PHASE -eq "retain" -or $PHASE -eq "all") {
    Write-Host "=== Phase 1: Retain (5 banks) ===" -ForegroundColor Cyan
    # Retain is profile-AGNOSTIC: retain_fixture() in eval_cogmem.py (line 548) does NOT
    # pass enabled_fact_types into the POST /memories payload, so the bank gets all 6
    # fact types extracted regardless of which profile we run with. E7, E1, E7G... all
    # share the same bank and differ only at recall (types filter, router, SUM).
    # (If you want S33-style cách B per-profile retain banks, use cogmem_bench/gates.py
    #  with enabled_fact_types in the payload — that's a different infrastructure.)
    # We use $PROFILES[0] here purely because the --profile flag is required by eval_cogmem;
    # the value doesn't change what gets retained.
    $retainProfile = $PROFILES[0]
    Write-Host "  (retain is profile-agnostic; using $retainProfile to satisfy --profile flag)" -ForegroundColor DarkGray
    foreach ($r in $CONV_RANGES) {
        $sampleId  = $r.SampleId
        $firstIdx  = $r.First
        $bankId    = Get-BankIdForSample $sampleId
        Write-Host "[retain] conv=$sampleId  first_qa_index=$firstIdx  bank=$bankId" -ForegroundColor Yellow
        try {
            uv run python -m scripts.eval_cogmem `
                --pipeline recall `
                --profile $retainProfile `
                --fixture locomo `
                --conv-index $firstIdx `
                --bank-id $bankId `
                --checkpoint-dir $CHECKPOINT_DIR `
                --output-dir $OUTPUT_DIR `
                --api-timeout $TIMEOUT_MS
            Write-Host "[retain] $sampleId DONE" -ForegroundColor Green
        }
        catch {
            Write-Host "[retain] $sampleId FAILED: $_" -ForegroundColor Red
            throw  # abort eval phase if any retain fails — incomplete banks → corrupt eval
        }
        if ($SLEEP_SECONDS -gt 0) { Start-SleepWithKeepAlive -Seconds $SLEEP_SECONDS }
        Write-Host ""
    }
    Write-Host "=== Phase 1 Complete: 5 banks populated ===" -ForegroundColor Cyan
    Write-Host ""
}

# ── Phase 2: Eval (every QA in range × every profile, --skip-retain) ──────
if ($PHASE -eq "eval" -or $PHASE -eq "all") {
    $evalIndices = if ($INDICES.Count -gt 0) { $INDICES } else { $START_INDEX..$END_INDEX }
    Write-Host "=== Phase 2: Eval ($($evalIndices.Count) QAs × $($PROFILES.Count) profile(s)) ===" -ForegroundColor Cyan
    $totalEvals = $evalIndices.Count * $PROFILES.Count
    $current = 0
    $failed = 0

    foreach ($profileId in $PROFILES) {
        foreach ($N in $evalIndices) {
            $current++
            $sampleId = Get-SampleIdForQaIndex -QaIdx $N
            $bankId   = Get-BankIdForSample $sampleId
            Write-Host "[$current/$totalEvals] profile=$profileId  qa=$N  conv=$sampleId  bank=$bankId" -ForegroundColor Yellow
            try {
                uv run python -m scripts.eval_cogmem `
                    --pipeline full `
                    --profile $profileId `
                    --fixture locomo `
                    --conv-index $N `
                    --bank-id $bankId `
                    --checkpoint-dir $CHECKPOINT_DIR `
                    --output-dir $OUTPUT_DIR `
                    --api-timeout $TIMEOUT_MS `
                    --skip-retain
                Write-Host "[$current/$totalEvals] profile=$profileId qa=$N PASSED" -ForegroundColor Green
            }
            catch {
                $failed++
                Write-Host "[$current/$totalEvals] profile=$profileId qa=$N FAILED: $_" -ForegroundColor Red
            }
            if ($SLEEP_SECONDS -gt 0) { Start-SleepWithKeepAlive -Seconds $SLEEP_SECONDS }
            Write-Host ""
        }
    }

    Write-Host "=== Phase 2 Complete ===" -ForegroundColor Cyan
    Write-Host "  Total evals: $totalEvals"
    Write-Host "  Passed:      $($totalEvals - $failed)"
    Write-Host "  Failed:      $failed"
    if ($failed -gt 0) { exit 1 }
}

exit 0
