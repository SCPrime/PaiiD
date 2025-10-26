# Development Environment Startup Script - Version 2.0
# Uses ProcessManager.ps1 for robust process lifecycle management
# Ensures both backend and frontend start correctly with proper configuration

param(
    [switch]$KillExisting = $false,
    [int]$BackendPort = 8002,  # Default to 8002 (8001 has unkillable zombies)
    [int]$FrontendPort = 3000
)

# Import ProcessManager module
$ProcessManagerPath = Join-Path $PSScriptRoot "scripts/ProcessManager.ps1"
if (-not (Test-Path $ProcessManagerPath)) {
    Write-Host "ERROR: ProcessManager.ps1 not found at $ProcessManagerPath" -ForegroundColor Red
    exit 1
}

Import-Module $ProcessManagerPath -Force

Write-Host "`n=== PaiiD Development Startup (Managed) ===" -ForegroundColor Cyan
Write-Host "Backend Port: $BackendPort" -ForegroundColor Gray
Write-Host "Frontend Port: $FrontendPort" -ForegroundColor Gray
Write-Host ""

# Initialize process manager
Initialize-ProcessManager

# Run zombie cleanup before starting services
Write-Host "Running zombie process cleanup..." -ForegroundColor Yellow
$zombieKillerPath = Join-Path $PSScriptRoot "scripts/zombie-killer.ps1"
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

# Kill existing processes if requested
if ($KillExisting) {
    Write-Host "Killing existing processes on ports $FrontendPort and $BackendPort..." -ForegroundColor Yellow

    $cleaned = Clear-Port -Port $FrontendPort -MaxRetries 2
    if ($cleaned) {
        Write-Host "  Port $FrontendPort cleared" -ForegroundColor Green
    }

    $cleaned = Clear-Port -Port $BackendPort -MaxRetries 2
    if ($cleaned) {
        Write-Host "  Port $BackendPort cleared" -ForegroundColor Green
    }
}

# Clean up orphaned PID files
Clear-OrphanedPids

# Check for port conflicts
Write-Host "Checking for port conflicts..." -ForegroundColor Yellow

if (Test-PortInUse -Port $FrontendPort) {
    $portProcessId = Get-ProcessOnPort -Port $FrontendPort
    Write-Host "  ERROR: Port $FrontendPort is already in use (PID: $portProcessId)" -ForegroundColor Red
    Write-Host "     Run this script with -KillExisting to kill existing processes" -ForegroundColor Gray
    exit 1
}

if (Test-PortInUse -Port $BackendPort) {
    $portProcessId = Get-ProcessOnPort -Port $BackendPort
    Write-Host "  ERROR: Port $BackendPort is already in use (PID: $portProcessId)" -ForegroundColor Red
    Write-Host "     Run this script with -KillExisting to kill existing processes" -ForegroundColor Gray
    exit 1
}

Write-Host "  Ports $FrontendPort and $BackendPort are available" -ForegroundColor Green

# Verify environment files exist
Write-Host "`nVerifying environment configuration..." -ForegroundColor Yellow

if (-not (Test-Path "backend\.env")) {
    Write-Host "  ❌ backend\.env not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "frontend\.env.local")) {
    Write-Host "  ❌ frontend\.env.local not found" -ForegroundColor Red
    exit 1
}

# Check API_TOKEN matches
$backendToken = Select-String -Path "backend\.env" -Pattern "^API_TOKEN=(.+)$" | ForEach-Object { $_.Matches.Groups[1].Value }
$frontendToken = Select-String -Path "frontend\.env.local" -Pattern "^NEXT_PUBLIC_API_TOKEN=(.+)$" | ForEach-Object { $_.Matches.Groups[1].Value }

if ($backendToken -ne $frontendToken) {
    Write-Host "  ⚠️  API_TOKEN mismatch between backend and frontend!" -ForegroundColor Red
    Write-Host "     Backend: $backendToken" -ForegroundColor Gray
    Write-Host "     Frontend: $frontendToken" -ForegroundColor Gray
    exit 1
}

Write-Host "  ✅ Environment files configured correctly" -ForegroundColor Green
Write-Host "  ✅ API_TOKEN matches: $backendToken" -ForegroundColor Green

# Start backend with managed process
Write-Host "`nStarting backend on port $BackendPort..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
$backendCommand = "cd '$backendPath'; `$env:PORT=$BackendPort; uvicorn app.main:app --reload --port $BackendPort"

$backendPid = Start-ManagedProcess `
    -Name "backend-dev" `
    -Command $backendCommand `
    -WorkingDirectory $backendPath `
    -Environment @{ "PORT" = "$BackendPort" }

if ($backendPid) {
    Write-Host "  Backend started with PID: $backendPid" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Backend failed to start" -ForegroundColor Red
    exit 1
}

# Wait for backend to be ready
Write-Host "  Waiting for backend to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Verify backend is listening
if (Test-PortInUse -Port $BackendPort) {
    Write-Host "  Backend is listening on port $BackendPort" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Backend not listening yet on port $BackendPort" -ForegroundColor Yellow
}

# Start frontend with managed process
Write-Host "`nStarting frontend on port $FrontendPort..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "frontend"
$frontendCommand = "cd '$frontendPath'; npm run dev"

$frontendPid = Start-ManagedProcess `
    -Name "frontend-dev" `
    -Command $frontendCommand `
    -WorkingDirectory $frontendPath

if ($frontendPid) {
    Write-Host "  Frontend started with PID: $frontendPid" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Frontend failed to start" -ForegroundColor Red
    Stop-ManagedProcess -Name "backend-dev"
    exit 1
}

# Wait for frontend to be ready
Write-Host "  Waiting for frontend to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Verify frontend is listening
if (Test-PortInUse -Port $FrontendPort) {
    Write-Host "  Frontend is listening on port $FrontendPort" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Frontend may still be starting..." -ForegroundColor Yellow
}

Write-Host "`n=== Startup Complete ===" -ForegroundColor Cyan
Write-Host "`nServices:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:$FrontendPort" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:$BackendPort" -ForegroundColor Green
Write-Host "  API Docs: http://localhost:$BackendPort/docs" -ForegroundColor Green
Write-Host "`nManaged Processes:" -ForegroundColor Yellow
Write-Host "  Backend:  PID $backendPid (backend-dev)" -ForegroundColor Gray
Write-Host "  Frontend: PID $frontendPid (frontend-dev)" -ForegroundColor Gray
Write-Host "`nTo stop all services:" -ForegroundColor Yellow
Write-Host "  .\scripts\stop-all.ps1" -ForegroundColor Gray
Write-Host ""
