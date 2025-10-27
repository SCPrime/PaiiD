# PaiiD Development Server Shutdown Script
# Purpose: Gracefully stop backend + frontend dev servers
# Usage: .\scripts\stop-dev.ps1

Write-Host "`n🛑 PaiiD Development Environment - Shutdown`n" -ForegroundColor Cyan

$backendPort = 8001
$frontendPort = 3001
$stoppedCount = 0

# Function to kill process by port
function Stop-ProcessByPort {
    param(
        [int]$Port,
        [string]$ServiceName
    )

    Write-Host "🔍 Stopping $ServiceName on port $Port..." -ForegroundColor Yellow

    try {
        # Find process using the port
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connection) {
            $processId = $connection.OwningProcess
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue

            if ($process) {
                Write-Host "   Found PID $processId ($($process.ProcessName))" -ForegroundColor Gray
                Stop-Process -Id $processId -Force -ErrorAction Stop
                Write-Host "   ✅ Stopped $ServiceName (PID $processId)" -ForegroundColor Green
                return $true
            }
        }
        else {
            Write-Host "   ✓ No process on port $Port" -ForegroundColor Gray
            return $false
        }
    }
    catch {
        Write-Host "   ⚠️  Error stopping $ServiceName $_" -ForegroundColor Red
        return $false
    }
}

# Stop backend
if (Stop-ProcessByPort -Port $backendPort -ServiceName "Backend") {
    $stoppedCount++
}

# Stop frontend
if (Stop-ProcessByPort -Port $frontendPort -ServiceName "Frontend") {
    $stoppedCount++
}

# Wait for processes to terminate
Start-Sleep -Milliseconds 500

Write-Host "`n📊 Summary: Stopped $stoppedCount service(s)" -ForegroundColor Cyan

# Optional: Run cleanup to kill any lingering processes
Write-Host "`n🧹 Running cleanup to remove any zombie processes..." -ForegroundColor Yellow
& "$PSScriptRoot\agent-cleanup.ps1" -Force

Write-Host "`n✅ Development environment stopped.`n" -ForegroundColor Green
