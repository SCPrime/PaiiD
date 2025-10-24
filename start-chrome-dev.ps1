# Start PaiiD Development with Chrome Auto-Launch
# Run this script to start both backend + frontend + open Chrome

function Get-PreferredShell {
    $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($pwsh) {
        return "pwsh"
    }

    return "powershell"
}

$shellExecutable = Get-PreferredShell

Write-Host "🚀 Starting PaiiD Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Kill existing processes on ports 3000-3003 and 8001
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 3000,3001,3002,3003,8001 -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "✅ Ports cleared" -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "🐍 Starting Backend (port 8001)..." -ForegroundColor Cyan
Start-Process $shellExecutable -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn app.main:app --reload --port 8001"

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "⚛️  Starting Frontend (port 3000)..." -ForegroundColor Cyan
Start-Process $shellExecutable -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

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
Write-Host "💡 Tip: Close this window to keep servers running" -ForegroundColor Yellow
Write-Host "🛑 To stop: Close the backend and frontend PowerShell windows" -ForegroundColor Yellow
