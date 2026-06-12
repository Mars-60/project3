# Run this ONCE as Administrator to register Atlas silent autostart
# Right-click this file -> "Run with PowerShell"

$AtlasDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VbsPath  = Join-Path $AtlasDir "atlas_silent_launch.vbs"

$action   = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$VbsPath`""
$trigger  = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable $true

Register-ScheduledTask `
    -TaskName "AtlasAutoStart" `
    -Action   $action `
    -Trigger  $trigger `
    -Settings $settings `
    -RunLevel Limited `
    -Force

Write-Host ""
Write-Host "[OK] Atlas will now start silently on every login." -ForegroundColor Green
Write-Host "     No window. No prompt. Just recording in the background." -ForegroundColor Green
Write-Host ""
pause
