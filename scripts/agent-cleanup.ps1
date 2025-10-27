# PaiiD Agent Cleanup Script
# Purpose: Automatically kill all PaiiD-related zombie processes
# Called by: Claude agents, start-dev.ps1, git hooks, and manually

param(
    [switch]$Force = $false,
    [switch]$Verbose = $false
)

Write-Host ""
Write-Host "🧹 PaiiD Agent Cleanup - Zombie Process Elimination" -ForegroundColor Cyan
Write-Host ""

$projectDir = "C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD"
$killedCount = 0
$processesToKill = @()

# Find all node.exe processes running from PaiiD directory
Write-Host "🔍 Scanning for node.exe processes..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -and $_.Path -like "$projectDir*"
}
if ($nodeProcesses) {
    $processesToKill += $nodeProcesses
    Write-Host "   Found $($nodeProcesses.Count) node.exe process(es)" -ForegroundColor Gray
}

# Find all python.exe processes running from PaiiD directory
Write-Host "🔍 Scanning for python.exe processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -and $_.Path -like "$projectDir*"
}
if ($pythonProcesses) {
    $processesToKill += $pythonProcesses
    Write-Host "   Found $($pythonProcesses.Count) python.exe process(es)" -ForegroundColor Gray
}

# Find all pytest processes
Write-Host "🔍 Scanning for pytest processes..." -ForegroundColor Yellow
$pytestProcesses = Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -and $_.CommandLine -like "*pytest*" -and $_.CommandLine -like "*$projectDir*"
}
if ($pytestProcesses) {
    $processesToKill += $pytestProcesses
    Write-Host "   Found $($pytestProcesses.Count) pytest process(es)" -ForegroundColor Gray
}

# Find all bash.exe processes (WSL or Git Bash) with PaiiD in command line
Write-Host "🔍 Scanning for bash.exe processes..." -ForegroundColor Yellow
$bashProcesses = Get-Process -Name bash -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -and $_.CommandLine -like "*PaiiD*"
}
if ($bashProcesses) {
    $processesToKill += $bashProcesses
    Write-Host "   Found $($bashProcesses.Count) bash.exe process(es)" -ForegroundColor Gray
}

$totalProcesses = $processesToKill.Count

if ($totalProcesses -eq 0) {
    Write-Host ""
Write-Host "✅ No zombie processes found. All clear!" -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "📊 Total zombie processes found: $totalProcesses" -ForegroundColor Yellow

# Safety check: If more than 10 processes and not forced, ask for confirmation
if ($totalProcesses -gt 10 -and -not $Force) {
    Write-Host ""
    Write-Host "⚠️  WARNING: Found more than 10 processes!" -ForegroundColor Red
    Write-Host "   This is unusually high. Recommend manual inspection." -ForegroundColor Red
    Write-Host ""
    Write-Host "   Processes to be killed:" -ForegroundColor Yellow
    foreach ($proc in $processesToKill) {
        $cmdLine = if ($proc.CommandLine) { $proc.CommandLine.Substring(0, [Math]::Min(80, $proc.CommandLine.Length)) } else { "N/A" }
        Write-Host "     PID $($proc.Id): $($proc.ProcessName) - $cmdLine" -ForegroundColor Gray
    }

    $response = Read-Host "   Continue with cleanup? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host ""
        Write-Host "❌ Cleanup cancelled by user." -ForegroundColor Red
        exit 1
    }
}

# Kill all processes
Write-Host ""
Write-Host "💀 Terminating zombie processes..." -ForegroundColor Magenta
foreach ($proc in $processesToKill) {
    try {
        if ($Verbose) {
            $cmdLine = if ($proc.CommandLine) { $proc.CommandLine.Substring(0, [Math]::Min(60, $proc.CommandLine.Length)) } else { "N/A" }
            Write-Host "   Killing PID $($proc.Id): $($proc.ProcessName) - $cmdLine" -ForegroundColor Gray
        }
        Stop-Process -Id $proc.Id -Force -ErrorAction Stop
        $killedCount++
    }
    catch {
        Write-Host "   ⚠️  Failed to kill PID $($proc.Id): $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Cleanup complete: $killedCount/$totalProcesses processes terminated" -ForegroundColor Green

# Wait a moment for processes to fully terminate
Start-Sleep -Milliseconds 500

# Verify cleanup
$remaining = Get-Process -Name node, python, bash -ErrorAction SilentlyContinue | Where-Object {
    ($_.Path -and $_.Path -like "$projectDir*") -or ($_.CommandLine -and $_.CommandLine -like "*$projectDir*")
}

if ($remaining) {
    Write-Host "⚠️  Warning: $($remaining.Count) process(es) still running" -ForegroundColor Yellow
    if ($Verbose) {
        foreach ($proc in $remaining) {
            Write-Host "   PID $($proc.Id): $($proc.ProcessName)" -ForegroundColor Gray
        }
    }
}
else {
    Write-Host "🎉 All zombie processes eliminated!" -ForegroundColor Green
}

Write-Host ""
exit 0
