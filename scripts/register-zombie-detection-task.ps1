# Register Zombie Detection Scheduled Task
# Creates a Windows scheduled task to run zombie detection weekly
# Version: 1.0.0

param(
    [switch]$Force = $false
)

# Check if running as administrator
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script must be run as Administrator to create scheduled tasks" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
    exit 1
}

$TaskName = "PaiiD-Zombie-Detection"
$ScriptPath = Join-Path $PSScriptRoot "scheduled-zombie-detector.ps1"

Write-Host "Registering zombie detection scheduled task..." -ForegroundColor Cyan

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask -and -not $Force) {
    Write-Host "Task '$TaskName' already exists. Use -Force to overwrite." -ForegroundColor Yellow
    exit 1
}

if ($existingTask -and $Force) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create the action
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File `"$ScriptPath`" -AutoCleanup"

# Create the trigger (weekly on Sundays at 2 AM)
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2AM

# Create the settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Create the principal (run as SYSTEM)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Weekly zombie process detection for PaiiD development environment"
    
    Write-Host "✅ Scheduled task '$TaskName' created successfully" -ForegroundColor Green
    Write-Host "   Task will run every Sunday at 2:00 AM" -ForegroundColor Gray
    Write-Host "   Logs will be saved to: backend\.logs\zombie-detection.log" -ForegroundColor Gray
    
    # Test the task
    Write-Host "`nTesting the task..." -ForegroundColor Yellow
    Start-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 5
    
    $taskInfo = Get-ScheduledTask -TaskName $TaskName
    Write-Host "Task Status: $($taskInfo.State)" -ForegroundColor $(if ($taskInfo.State -eq "Running") { "Green" } else { "Yellow" })
    
} catch {
    Write-Host "❌ Failed to create scheduled task: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`nTo manage the task:" -ForegroundColor Cyan
Write-Host "  View: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "  Run:  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "  Stop: Stop-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "  Remove: Unregister-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
