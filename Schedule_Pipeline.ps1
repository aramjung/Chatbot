# Schedule the OneNote Pipeline to run daily
# Run this script as Administrator

$taskName = "OneNote Document Pipeline"
$scriptPath = Join-Path $PSScriptRoot "Run_Pipeline.bat"
$triggerTime = "02:00AM"  # Change this to your preferred time

# Create the scheduled task
$action = New-ScheduledTaskAction -Execute $scriptPath
$trigger = New-ScheduledTaskTrigger -Daily -At $triggerTime
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register the task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Processes OneNote documents and generates embeddings daily"

Write-Host "✓ Scheduled task created successfully!" -ForegroundColor Green
Write-Host "Task: $taskName" -ForegroundColor Cyan
Write-Host "Schedule: Daily at $triggerTime" -ForegroundColor Cyan
Write-Host ""
Write-Host "To modify the schedule:" -ForegroundColor Yellow
Write-Host "1. Open Task Scheduler" -ForegroundColor Yellow
Write-Host "2. Find '$taskName' under 'Task Scheduler Library'" -ForegroundColor Yellow
