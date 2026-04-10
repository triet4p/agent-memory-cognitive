$taskName = "RunHindsightTestOnce"
$project  = "F:\ai-ml\agent-memory-cognitive"
$runAt    = (Get-Date).AddHours(1)

$logDir = Join-Path $project "logs\scheduled"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$logFile = Join-Path $logDir ("hindsight_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

$cmd = "cd /d `"$project`" && uv run python -m scripts.test_hindsight >> `"$logFile`" 2>&1"
$action  = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $cmd"
$trigger = New-ScheduledTaskTrigger -Once -At $runAt

Register-ScheduledTask `
  -TaskName $taskName `
  -Action $action `
  -Trigger $trigger `
  -Description "Run hindsight test once after 1 hour with log" `
  -Force

"Task đã tạo: $taskName"
"Thời gian chạy: $runAt"
"Log file: $logFile"