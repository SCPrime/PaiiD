# PaiiD Development Server Startup Script
# Purpose: Clean startup of backend + frontend with automatic zombie cleanup
# Usage: .\scripts\start-dev.ps1

Write-Host "`n🚀 PaiiD Development Environment - Clean Startup`n" -ForegroundColor Cyan

$projectDir = "C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD"
$backendPort = 8001
$frontendPort = 3001

# Step 1: Kill all zombie processes
Write-Host "📍 Step 1/5: Cleaning up zombie processes..." -ForegroundColor Yellow
& "$projectDir\scripts\agent-cleanup.ps1" -Force
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Cleanup script returned non-zero exit code, but continuing..." -ForegroundColor Yellow
}

# Step 2: Clear Next.js build cache
Write-Host "`n📍 Step 2/5: Clearing Next.js build cache..." -ForegroundColor Yellow
$nextCacheDir = "$projectDir\frontend\.next"
if (Test-Path $nextCacheDir) {
    try {
        Remove-Item -Path $nextCacheDir -Recurse -Force -ErrorAction Stop
        Write-Host "   ✅ Cleared .next cache" -ForegroundColor Green
    }
    catch {
        Write-Host "   ⚠️  Could not clear .next cache: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "   ✓ No .next cache to clear" -ForegroundColor Gray
}

# Step 3: Start backend server
Write-Host "`n📍 Step 3/5: Starting backend server (port $backendPort)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectDir\backend'; python -m uvicorn app.main:app --reload --port $backendPort" -WindowStyle Normal
Write-Host "   🐍 Backend starting at http://127.0.0.1:$backendPort" -ForegroundColor Green

# Wait for backend to be ready
Write-Host "   ⏳ Waiting for backend health check..." -ForegroundColor Gray
$maxWait = 30
$waited = 0
$backendReady = $false
while ($waited -lt $maxWait) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$backendPort/api/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "   ✅ Backend is healthy!" -ForegroundColor Green
            break
        }
    }
    catch {
        # Still waiting...
    }
    Start-Sleep -Seconds 1
    $waited++
}

if (-not $backendReady) {
    Write-Host "   ⚠️  Backend health check timed out after ${maxWait}s" -ForegroundColor Red
    Write-Host "   Backend may still be starting. Check the backend window." -ForegroundColor Yellow
}

# Step 4: Start frontend server
Write-Host "`n📍 Step 4/5: Starting frontend server (port $frontendPort)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectDir\frontend'; npm run dev" -WindowStyle Normal
Write-Host "   ⚛️  Frontend starting at http://localhost:$frontendPort" -ForegroundColor Green

# Step 5: Display status
Write-Host "`n📍 Step 5/5: Development environment ready!" -ForegroundColor Yellow
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│  🎉 PaiiD Development Servers Running                  │" -ForegroundColor Cyan
Write-Host "├─────────────────────────────────────────────────────────┤" -ForegroundColor Cyan
Write-Host "│  Backend:  http://127.0.0.1:$backendPort                    │" -ForegroundColor White
Write-Host "│  Frontend: http://localhost:$frontendPort                    │" -ForegroundColor White
Write-Host "│                                                         │" -ForegroundColor Cyan
Write-Host "│  📝 Two new PowerShell windows opened                  │" -ForegroundColor Gray
Write-Host "│  🛑 To stop: .\scripts\stop-dev.ps1                     │" -ForegroundColor Gray
Write-Host "│  📊 Status:  .\scripts\status.ps1                       │" -ForegroundColor Gray
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Cyan

Write-Host "`n✨ Happy coding! Open http://localhost:$frontendPort in your browser.`n" -ForegroundColor Green
