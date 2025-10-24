# Test Port Cleanup Script
# Cleans up all ports used during testing
# Version: 1.0.0

param(
    [switch]$Force = $false
)

# Import ProcessManager module
$ProcessManagerPath = Join-Path $PSScriptRoot "ProcessManager.ps1"
if (Test-Path $ProcessManagerPath) {
    Import-Module $ProcessManagerPath -Force
} else {
    Write-Host "WARNING: ProcessManager.ps1 not found, using basic cleanup" -ForegroundColor Yellow
}

Write-Host "`n=== Test Port Cleanup ===" -ForegroundColor Cyan
Write-Host ""

# Test ports to clean
$testPorts = @(3000, 3001, 3002, 3003, 8000, 8001, 8002)

$cleaned = 0
$failed = 0

foreach ($port in $testPorts) {
    Write-Host "Cleaning port $port..." -ForegroundColor Gray

    try {
        if (Get-Command Clear-Port -ErrorAction SilentlyContinue) {
            # Use ProcessManager function if available
            $result = Clear-Port -Port $port -MaxRetries 2
            if ($result) {
                Write-Host "  Port $port cleaned" -ForegroundColor Green
                $cleaned++
            } else {
                Write-Host "  Port $port cleanup failed" -ForegroundColor Yellow
                $failed++
            }
        } else {
            # Fallback to basic cleanup
            $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
            if ($connection) {
                $processId = $connection.OwningProcess
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                Write-Host "  Port $port cleaned (PID: $processId)" -ForegroundColor Green
                $cleaned++
            } else {
                Write-Host "  Port $port was not in use" -ForegroundColor Gray
            }
        }
    }
    catch {
        Write-Host "  Error cleaning port $port : $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "=== Cleanup Summary ===" -ForegroundColor Cyan
Write-Host "  Ports cleaned: $cleaned" -ForegroundColor Green
Write-Host "  Ports failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Yellow" } else { "Green" })
Write-Host ""

if ($failed -gt 0 -and -not $Force) {
    Write-Host "Some ports could not be cleaned. Run with -Force for aggressive cleanup." -ForegroundColor Yellow
    exit 1
}

exit 0
