# Start PaiiD Development with Chrome Auto-Launch
# Run this script to start both backend + frontend + open Chrome
# Uses ProcessManager.ps1 for proper process tracking

# Import ProcessManager module
$ProcessManagerPath = Join-Path $PSScriptRoot "scripts\ProcessManager.ps1"
if (-not (Test-Path $ProcessManagerPath)) {
    Write-Host "ERROR: ProcessManager.ps1 not found at $ProcessManagerPath" -ForegroundColor Red
    exit 1
}

Import-Module $ProcessManagerPath -Force

Write-Host "🚀 Starting PaiiD Development Environment (Managed)..." -ForegroundColor Cyan
Write-Host ""

# Initialize process manager
Initialize-ProcessManager

# Kill existing processes on ports 3000-3003 and 8001
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
$cleaned = Clear-Port -Port 3000 -MaxRetries 2
if ($cleaned) { Write-Host "  Port 3000 cleared" -ForegroundColor Green }

$cleaned = Clear-Port -Port 8001 -MaxRetries 2
if ($cleaned) { Write-Host "  Port 8001 cleared" -ForegroundColor Green }

# Clean up orphaned PID files
Clear-OrphanedPids

Write-Host "✅ Ports cleared" -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "🐍 Starting Backend (port 8001)..." -ForegroundColor Cyan
$backendPath = Join-Path $PSScriptRoot "backend"
$backendCommand = "python -m uvicorn app.main:app --reload --port 8001"

$backendPid = Start-ManagedProcess `
    -Name "backend-dev" `
    -Command $backendCommand `
    -WorkingDirectory $backendPath

if ($backendPid) {
    Write-Host "  Backend started with PID: $backendPid" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Backend failed to start" -ForegroundColor Red
    exit 1
}

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "⚛️  Starting Frontend (port 3000)..." -ForegroundColor Cyan
$frontendPath = Join-Path $PSScriptRoot "frontend"
$frontendCommand = "npm run dev"

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

Start-Sleep -Seconds 5

# Wait for frontend to be ready
Write-Host "⏳ Waiting for servers to start..." -ForegroundColor Yellow
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
        break
    } catch {
        Start-Sleep -Seconds 1
        $waited++
    }
}

# Open Chrome
Write-Host "🌐 Opening Chrome..." -ForegroundColor Cyan

$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chromePath) {
    & $chromePath --new-window "http://localhost:3000"
    Write-Host "✅ Chrome opened to http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "⚠️  Chrome not found at default location" -ForegroundColor Yellow
    Write-Host "   Opening in default browser instead..." -ForegroundColor Yellow
    Start-Process "http://localhost:3000"
}

Write-Host ""
Write-Host "✅ PaiiD Development Environment Ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Servers Running:" -ForegroundColor Cyan
Write-Host "   Backend:  http://127.0.0.1:8001" -ForegroundColor Gray
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "   Swagger:  http://127.0.0.1:8001/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "🔧 Managed Processes:" -ForegroundColor Cyan
Write-Host "   Backend:  PID $backendPid (backend-dev)" -ForegroundColor Gray
Write-Host "   Frontend: PID $frontendPid (frontend-dev)" -ForegroundColor Gray
Write-Host ""
Write-Host "🛑 To stop all services:" -ForegroundColor Yellow
Write-Host "   .\scripts\stop-all.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Tip: Close this window to keep servers running" -ForegroundColor Yellow
