# 🌐 BROWSER MOD - Browser Rendering & Issue Monitor (PowerShell)
# Windows-native version of browser_mod.py

param(
    [string]$Url = "https://paiid-frontend.onrender.com",
    [switch]$Dev,
    [switch]$QuickCheck,
    [switch]$FullAudit = $true,
    [switch]$Headed
)

# Set URL based on flags
if ($Dev) {
    $Url = "http://localhost:3000"
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🌐 BROWSER MOD v1.0" -ForegroundColor Cyan
Write-Host "  Browser Rendering & Issue Monitor" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    Write-Host "❌ Python not found. Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

# Check if browser_mod.py exists
$scriptPath = Join-Path $PSScriptRoot "browser_mod.py"

if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ browser_mod.py not found at: $scriptPath" -ForegroundColor Red
    exit 1
}

# Build Python command
$pythonArgs = @($scriptPath, "--url", $Url)

if ($QuickCheck) {
    $pythonArgs += "--check-render"
    Write-Host "🚀 Running quick render check..." -ForegroundColor Yellow
} elseif ($FullAudit) {
    $pythonArgs += "--full-audit"
    Write-Host "🔍 Running full audit..." -ForegroundColor Yellow
}

if ($Headed) {
    $pythonArgs += "--headed"
}

Write-Host ""
Write-Host "Target URL: $Url" -ForegroundColor Cyan
Write-Host ""

# Run Python script
& python $pythonArgs

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ BROWSER MOD complete - No critical issues" -ForegroundColor Green
} else {
    Write-Host "❌ BROWSER MOD complete - Critical issues found" -ForegroundColor Red
}

exit $exitCode
