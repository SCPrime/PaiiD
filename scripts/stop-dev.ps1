# Stop Development Environment
# Companion script to start-dev.ps1 - stops all managed processes
# Version: 1.0.0

param(
    [switch]$Force = $false,
    [switch]$Cleanup = $true
)

# Import ProcessManager module
$ProcessManagerPath = Join-Path $PSScriptRoot "ProcessManager.ps1"
if (-not (Test-Path $ProcessManagerPath)) {
    Write-Host "ERROR: ProcessManager.ps1 not found at $ProcessManagerPath" -ForegroundColor Red
    exit 1
}

Import-Module $ProcessManagerPath -Force

Write-Host "`n=== Stopping PaiiD Development Environment ===" -ForegroundColor Cyan
Write-Host "Force Mode: $Force" -ForegroundColor Gray
Write-Host "Cleanup Mode: $Cleanup" -ForegroundColor Gray
Write-Host ""

# Initialize process manager
Initialize-ProcessManager

# Stop all managed processes
Write-Host "Stopping managed processes..." -ForegroundColor Yellow

$stopped = 0
$failed = 0

# Common process names to stop
$processNames = @("backend-dev", "frontend-dev", "backend-server", "frontend-server")

foreach ($processName in $processNames) {
    $pid = Get-RegisteredPid -Name $processName
    
    if ($null -ne $pid) {
        Write-Host "Stopping $processName (PID: $pid)..." -ForegroundColor Gray
        
        $timeout = if ($Force) { 5 } else { 10 }
        $result = Stop-ManagedProcess -Name $processName -Timeout $timeout
        
        if ($result) {
            Write-Host "  $processName stopped successfully" -ForegroundColor Green
            $stopped++
        } else {
            Write-Host "  Failed to stop $processName" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host "  $processName not found (not running)" -ForegroundColor Yellow
    }
}

# Clean up orphaned processes if requested
if ($Cleanup) {
    Write-Host "`nCleaning up orphaned processes..." -ForegroundColor Yellow
    
    # Clean up orphaned PID files
    $cleaned = Clear-OrphanedPids
    if ($cleaned -gt 0) {
        Write-Host "  Cleaned up $cleaned orphaned PID file(s)" -ForegroundColor Green
    }
    
    # Clean up ports
    $ports = @(3000, 8001, 8002)
    foreach ($port in $ports) {
        if (Test-PortInUse -Port $port) {
            Write-Host "  Cleaning up port $port..." -ForegroundColor Gray
            $cleaned = Clear-Port -Port $port -MaxRetries 2
            if ($cleaned) {
                Write-Host "    Port $port cleared" -ForegroundColor Green
            } else {
                Write-Host "    Port $port cleanup failed" -ForegroundColor Red
            }
        }
    }
}

# Run zombie cleanup if force mode
if ($Force) {
    Write-Host "`nRunning zombie cleanup..." -ForegroundColor Yellow
    
    $zombieKillerPath = Join-Path $PSScriptRoot "zombie-killer.ps1"
    if (Test-Path $zombieKillerPath) {
        try {
            & $zombieKillerPath -SafeMode -Force
            Write-Host "  Zombie cleanup completed" -ForegroundColor Green
        }
        catch {
            Write-Host "  Zombie cleanup failed: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  Zombie killer not found at $zombieKillerPath" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n=== Stop Summary ===" -ForegroundColor Cyan
Write-Host "Processes stopped: $stopped" -ForegroundColor Green
Write-Host "Processes failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })

if ($failed -gt 0) {
    Write-Host "`nSome processes could not be stopped. Try running with -Force" -ForegroundColor Yellow
    Write-Host "Or use: .\scripts\emergency-cleanup.ps1" -ForegroundColor Gray
    exit 1
}

Write-Host "`n✅ All development processes stopped successfully" -ForegroundColor Green
exit 0
