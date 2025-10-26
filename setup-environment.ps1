# Setup Environment Variables for PaiiD Development
# This script sets up the necessary environment variables

Write-Host "🔧 Setting up PaiiD Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Environment variables for frontend
$envVars = @{
    "NEXT_PUBLIC_BACKEND_API_BASE_URL" = "https://paiid-backend.onrender.com"
    "NEXT_PUBLIC_WS_URL" = "wss://paiid-backend.onrender.com/ws"
    "NODE_ENV" = "development"
    "NEXT_TELEMETRY_DISABLED" = "1"
}

Write-Host "📝 Setting environment variables..." -ForegroundColor Yellow

foreach ($var in $envVars.GetEnumerator()) {
    [Environment]::SetEnvironmentVariable($var.Key, $var.Value, "User")
    Write-Host "✅ Set $($var.Key) = $($var.Value)" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔍 Verifying environment variables..." -ForegroundColor Yellow

foreach ($var in $envVars.GetEnumerator()) {
    $value = [Environment]::GetEnvironmentVariable($var.Key, "User")
    if ($value) {
        Write-Host "✅ $($var.Key) = $value" -ForegroundColor Green
    } else {
        Write-Host "❌ $($var.Key) not set" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📦 Checking project setup..." -ForegroundColor Yellow

# Check if we're in the right directory
if (Test-Path "package.json") {
    Write-Host "✅ Found package.json" -ForegroundColor Green
    
    # Check if node_modules exists
    if (Test-Path "node_modules") {
        Write-Host "✅ node_modules directory exists" -ForegroundColor Green
    } else {
        Write-Host "❌ node_modules not found. Run 'npm install'" -ForegroundColor Red
        Write-Host "   Running npm install..." -ForegroundColor Yellow
        npm install
    }
} else {
    Write-Host "❌ package.json not found. Make sure you're in the PaiiD directory" -ForegroundColor Red
}

# Check Python backend
if (Test-Path "backend/requirements.txt") {
    Write-Host "✅ Found backend/requirements.txt" -ForegroundColor Green
} else {
    Write-Host "❌ backend/requirements.txt not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "🧟 Setting up zombie process detection..." -ForegroundColor Yellow

# Register scheduled task for zombie detection
$zombieTaskScript = Join-Path $PSScriptRoot "scripts\register-zombie-detection-task.ps1"
if (Test-Path $zombieTaskScript) {
    try {
        Write-Host "   Registering weekly zombie detection task..." -ForegroundColor Gray
        & $zombieTaskScript
        Write-Host "✅ Zombie detection task registered" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Could not register zombie detection task (requires admin): $_" -ForegroundColor Yellow
        Write-Host "   You can run it manually later: .\scripts\register-zombie-detection-task.ps1" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  Zombie detection script not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Development Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Quick Start Commands:" -ForegroundColor Cyan
Write-Host "   Start All: .\start-dev.ps1" -ForegroundColor White
Write-Host "   Frontend: npm run dev" -ForegroundColor White
Write-Host "   Backend: cd backend && python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "   Stop All: .\scripts\stop-all.ps1" -ForegroundColor White
Write-Host "   Zombie Cleanup: .\scripts\zombie-killer.ps1 -Force" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Cursor Shortcuts:" -ForegroundColor Cyan
Write-Host "   Ctrl+Shift+P - Command Palette" -ForegroundColor White
Write-Host "   Ctrl+K - AI Chat" -ForegroundColor White
Write-Host "   Ctrl+Shift+A - Admin Bypass" -ForegroundColor White
Write-Host "   Ctrl+Shift+X - Extensions" -ForegroundColor White
