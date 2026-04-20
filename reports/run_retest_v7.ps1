$ErrorActionPreference = 'Continue'

# Load env from .env exactly as configured
Get-Content .env |
  Where-Object { $_ -and ($_.Trim() -ne '') -and (-not $_.Trim().StartsWith('#')) -and ($_.Contains('=')) } |
  ForEach-Object {
    $line = $_.Trim()
    $idx = $line.IndexOf('=')
    $key = $line.Substring(0, $idx).Trim()
    $value = $line.Substring($idx + 1)
    if ($value.StartsWith('"') -and $value.EndsWith('"') -and $value.Length -ge 2) {
      $value = $value.Substring(1, $value.Length - 2)
    }
    [System.Environment]::SetEnvironmentVariable($key, $value, 'Process')
  }

$tests = Get-ChildItem tests/retain/test_*.py -File | Sort-Object Name
$date = Get-Date
$dateStamp = $date.ToString('yyyyMMdd')
$reportPath = "reports/audit_retain_${dateStamp}_v7.md"
$tmpDir = "reports/.tmp_retest_v7"
New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

$mode = if ($env:COGMEM_API_LLM_BASE_URL) {
  "real LLM ($($env:COGMEM_API_LLM_BASE_URL)); model=$($env:COGMEM_API_LLM_MODEL)"
} else {
  "offline (FakeLLM)"
}

$results = @()

foreach ($test in $tests) {
  $rel = $test.FullName.Replace((Get-Location).Path + '\\', '').Replace('\\','/')
  Write-Host "===== RUN: $rel ====="

  $safe = $test.BaseName
  $outFile = Join-Path $tmpDir ("$safe.out.txt")
  $errFile = Join-Path $tmpDir ("$safe.err.txt")
  Remove-Item $outFile, $errFile -ErrorAction SilentlyContinue

  $proc = Start-Process -FilePath "uv" -ArgumentList @("run","python",$rel) -WorkingDirectory (Get-Location).Path -PassThru -NoNewWindow -RedirectStandardOutput $outFile -RedirectStandardError $errFile

  $timedOut = $false
  try {
    Wait-Process -Id $proc.Id -Timeout 180 -ErrorAction Stop
  } catch {
    $timedOut = $true
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
  }

  $stdout = if (Test-Path $outFile) { Get-Content $outFile -Raw } else { '' }
  $stderr = if (Test-Path $errFile) { Get-Content $errFile -Raw } else { '' }
  $output = ($stdout + "`n" + $stderr).Trim()

  $exitCode = if ($timedOut) { 124 } else { $proc.ExitCode }

  $status = '[PASS]'
  if ($timedOut) {
    $status = '[ERROR]'
  } elseif ($exitCode -ne 0) {
    if ($output -match 'ModuleNotFoundError|ImportError|No module named') { $status = '[ERROR]' }
    else { $status = '[FAIL]' }
  }

  $assertionLine = ''
  if ($output -match '(?m)^AssertionError:.*$') {
    $assertionLine = [regex]::Match($output, '(?m)^AssertionError:.*$').Value
  }

  $results += [PSCustomObject]@{
    Path = $rel
    Status = $status
    ExitCode = $exitCode
    TimedOut = $timedOut
    Assertion = $assertionLine
    Output = $output
  }
}

$passCount = ($results | Where-Object { $_.Status -eq '[PASS]' }).Count
$failCount = ($results | Where-Object { $_.Status -eq '[FAIL]' }).Count
$errorCount = ($results | Where-Object { $_.Status -eq '[ERROR]' }).Count

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('# Audit Report — Retain Tests')
$lines.Add("Date: $($date.ToString('yyyy-MM-dd HH:mm'))")
$lines.Add("Mode: $mode")
$lines.Add('Runner: uv run python')
$lines.Add('')
$lines.Add('## Summary')
$lines.Add('')
$lines.Add('| Test file | Status | Note |')
$lines.Add('|-----------|--------|------|')

foreach ($r in $results) {
  $note = '—'
  if ($r.Status -eq '[ERROR]' -and $r.TimedOut) {
    $note = 'LLM timeout (180s)'
  } elseif ($r.Status -ne '[PASS]') {
    if ($r.Output -match '(?m)File ".*", line (\d+), in .*') {
      $note = "AssertionError line " + [regex]::Match($r.Output, '(?m)File ".*", line (\d+), in .*').Groups[1].Value
    } else {
      $note = "exit=$($r.ExitCode)"
    }
  }
  $lines.Add("| $($r.Path) | $($r.Status) | $note |")
}

$lines.Add('')
$lines.Add("Total: $passCount passed, $failCount failed, $errorCount errors")
$lines.Add('')
$lines.Add('## Failure Details')
$lines.Add('')

$problems = $results | Where-Object { $_.Status -ne '[PASS]' }
if ($problems.Count -eq 0) {
  $lines.Add('No failures or errors.')
} else {
  $i = 1
  foreach ($r in $problems) {
    $kind = if ($r.Status -eq '[ERROR]') { 'ERROR' } else { 'FAIL' }
    $lines.Add("### [$i] $($r.Path) — $kind")
    $lines.Add('')

    $trace = $r.Output
    if ($r.Output -match '(?s)(Traceback \(most recent call last\):.*)') {
      $trace = $Matches[1]
    }
    if ($r.TimedOut -and [string]::IsNullOrWhiteSpace($trace)) {
      $trace = 'Process timed out after 180s while waiting for LLM response.'
    }

    $lines.Add('**Traceback (nguyên văn):**')
    $lines.Add('```text')
    $lines.Add($trace.TrimEnd())
    $lines.Add('```')
    $lines.Add('')

    if (-not [string]::IsNullOrWhiteSpace($r.Assertion)) {
      $lines.Add('**Assertion thất bại:**')
      $lines.Add("- $($r.Assertion)")
      $lines.Add('')
    }

    $lines.Add('**Nguyên nhân sơ bộ (quan sát):**')
    if ($r.TimedOut) {
      $lines.Add('- Lỗi timeout kết nối/đợi phản hồi LLM vượt quá 180 giây.')
    } elseif ($r.Status -eq '[ERROR]') {
      $lines.Add('- Lỗi import/module hoặc lỗi trước khi logic test chạy.')
    } else {
      $lines.Add('- Test thất bại do assertion không thỏa với output thực tế ở lần chạy này.')
    }
    $lines.Add('')

    $i++
  }
}

$lines.Add('## Notes')
$lines.Add('')
$lines.Add('- Không có file source nào được sửa trong quá trình audit này.')
$lines.Add("- Audit chạy ở mode: $mode")

Set-Content -Path $reportPath -Value $lines -Encoding UTF8

$summaryPath = 'reports/retest_retain_latest.txt'
"REPORT_PATH=$reportPath`nSUMMARY=$passCount/$($results.Count) passed; fail=$failCount; error=$errorCount" | Set-Content -Path $summaryPath -Encoding UTF8

Write-Host "REPORT_PATH=$reportPath"
Write-Host "SUMMARY=$passCount/$($results.Count) passed; fail=$failCount; error=$errorCount"