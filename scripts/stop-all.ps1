# Stop All Managed Processes
# Enumerates all PID files and stops each managed process
# Version: 1.0.0

# Import ProcessManager module
$ProcessManagerPath = Join-Path $PSScriptRoot "ProcessManager.ps1"
if (-not (Test-Path $ProcessManagerPath)) {
    Write-Host "ERROR: ProcessManager.ps1 not found at $ProcessManagerPath" -ForegroundColor Red
    exit 1
}

Import-Module $ProcessManagerPath -Force

Write-Host "`n=== Stopping All Managed Processes ===" -ForegroundColor Cyan
Write-Host ""

# Find all PID files
$projectRoot = Split-Path $PSScriptRoot -Parent
$pidDirs = @(
    (Join-Path $projectRoot "backend\.run"),
    (Join-Path $projectRoot "frontend\.run")
)

$stopped = 0
$failed = 0
$notRunning = 0

foreach ($pidDir in $pidDirs) {
    if (-not (Test-Path $pidDir)) {
        continue
    }

    $pidFiles = Get-ChildItem -Path $pidDir -Filter "*.pid" -ErrorAction SilentlyContinue

    foreach ($pidFile in $pidFiles) {
        $processName = $pidFile.BaseName
        $processId = Get-Content $pidFile.FullName -Raw -ErrorAction SilentlyContinue

        if ($processId) {
            $processId = $processId.Trim()

            Write-Host "Stopping $processName (PID: $processId)..." -ForegroundColor Gray

            # Check if process is running
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue

            if ($process) {
                try {
                    $result = Stop-ManagedProcess -Name $processName -Timeout 10

                    if ($result) {
                        Write-Host "  $processName stopped successfully" -ForegroundColor Green
                        $stopped++
                    } else {
                        Write-Host "  Failed to stop $processName" -ForegroundColor Red
                        $failed++
                    }
                }
                catch {
                    Write-Host "  Error stopping $processName : $_" -ForegroundColor Red
                    $failed++
                }
            } else {
                Write-Host "  $processName was not running (cleaning up PID file)" -ForegroundColor Yellow
                Remove-Item $pidFile.FullName -Force -ErrorAction SilentlyContinue
                $notRunning++
            }
        }
    }
}

Write-Host ""
Write-Host "=== Stop Summary ===" -ForegroundColor Cyan
Write-Host "  Stopped: $stopped" -ForegroundColor Green
Write-Host "  Not running: $notRunning" -ForegroundColor Yellow
Write-Host "  Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host ""

# Clean up orphaned PID files
Write-Host "Cleaning up orphaned PID files..." -ForegroundColor Gray
Clear-OrphanedPids

if ($failed -gt 0) {
    Write-Host "Some processes could not be stopped. Use Emergency Cleanup if needed." -ForegroundColor Yellow
    exit 1
}

Write-Host "All managed processes stopped successfully" -ForegroundColor Green
exit 0
