# Auto-Open Chrome for PaiiD Development
# This script forces Chrome to open instead of Edge

param(
    [string]$Url = "http://localhost:3003"
)

Write-Host "🌐 Opening Chrome for PaiiD Development..." -ForegroundColor Cyan

# Find Chrome executable
$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$chromePath = $chromePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($chromePath) {
    Write-Host "✅ Found Chrome at: $chromePath" -ForegroundColor Green

    # Open Chrome with development flags
    & $chromePath `
        --new-window `
        --disable-web-security `
        --disable-features=IsolateOrigins,site-per-process `
        --user-data-dir="$env:TEMP\chrome-dev-paiid" `
        $Url

    Write-Host "✅ Chrome opened to: $Url" -ForegroundColor Green
} else {
    Write-Host "❌ Chrome not found! Please install Chrome or update the path." -ForegroundColor Red
    Write-Host "   Install from: https://www.google.com/chrome/" -ForegroundColor Yellow
}
