# PaiiD Development Environment Status Script
# Purpose: Show all running processes and port usage for PaiiD
# Usage: .\scripts\status.ps1

Write-Host "`n📊 PaiiD Development Environment - Status Report`n" -ForegroundColor Cyan

$projectDir = "C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD"
$backendPort = 8001
$frontendPort = 3001

# Check backend port
Write-Host "🔍 Backend Status (Port $backendPort):" -ForegroundColor Yellow
try {
    $backendConn = Get-NetTCPConnection -LocalPort $backendPort -ErrorAction SilentlyContinue
    if ($backendConn) {
        $backendProc = Get-Process -Id $backendConn.OwningProcess -ErrorAction SilentlyContinue
        if ($backendProc) {
            Write-Host "   ✅ Running - PID $($backendProc.Id) ($($backendProc.ProcessName))" -ForegroundColor Green
            Write-Host "   URL: http://127.0.0.1:$backendPort" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "   ❌ Not running" -ForegroundColor Red
    }
}
catch {
    Write-Host "   ⚠️  Error checking backend: $_" -ForegroundColor Red
}

# Check frontend port
Write-Host "`n🔍 Frontend Status (Port $frontendPort):" -ForegroundColor Yellow
try {
    $frontendConn = Get-NetTCPConnection -LocalPort $frontendPort -ErrorAction SilentlyContinue
    if ($frontendConn) {
        $frontendProc = Get-Process -Id $frontendConn.OwningProcess -ErrorAction SilentlyContinue
        if ($frontendProc) {
            Write-Host "   ✅ Running - PID $($frontendProc.Id) ($($frontendProc.ProcessName))" -ForegroundColor Green
            Write-Host "   URL: http://localhost:$frontendPort" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "   ❌ Not running" -ForegroundColor Red
    }
}
catch {
    Write-Host "   ⚠️  Error checking frontend: $_" -ForegroundColor Red
}

# Find all PaiiD-related processes
Write-Host "`n🔍 All PaiiD-Related Processes:" -ForegroundColor Yellow

$allProcesses = @()

# Node.exe processes
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -and $_.Path -like "$projectDir*"
}
if ($nodeProcesses) {
    $allProcesses += $nodeProcesses | Select-Object Id, ProcessName, @{Name = "Type"; Expression = { "Node.js" } }
}

# Python processes
$pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -and $_.Path -like "$projectDir*"
}
if ($pythonProcesses) {
    $allProcesses += $pythonProcesses | Select-Object Id, ProcessName, @{Name = "Type"; Expression = { "Python" } }
}

# Bash processes
$bashProcesses = Get-Process -Name bash -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -and $_.CommandLine -like "*PaiiD*"
}
if ($bashProcesses) {
    $allProcesses += $bashProcesses | Select-Object Id, ProcessName, @{Name = "Type"; Expression = { "Bash" } }
}

if ($allProcesses.Count -gt 0) {
    Write-Host "   Found $($allProcesses.Count) process(es):`n" -ForegroundColor Gray

    foreach ($proc in $allProcesses) {
        Write-Host "   PID $($proc.Id): $($proc.Type) ($($proc.ProcessName))" -ForegroundColor Gray
    }

    if ($allProcesses.Count -gt 5) {
        Write-Host "`n   ⚠️  Warning: More than 5 processes detected!" -ForegroundColor Yellow
        Write-Host "   Consider running: .\scripts\agent-cleanup.ps1" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   ✓ No PaiiD processes found" -ForegroundColor Green
}

Write-Host "`n📋 Quick Actions:" -ForegroundColor Cyan
Write-Host "   Start:   .\scripts\start-dev.ps1" -ForegroundColor Gray
Write-Host "   Stop:    .\scripts\stop-dev.ps1" -ForegroundColor Gray
Write-Host "   Cleanup: .\scripts\agent-cleanup.ps1" -ForegroundColor Gray

Write-Host ""
