# Check Chrome Extensions for AI Development
# Lists all installed Chrome extensions

Write-Host "🔍 Checking Chrome Extensions..." -ForegroundColor Cyan
Write-Host ""

$chromeExtensionsPath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Extensions"

if (Test-Path $chromeExtensionsPath) {
    Write-Host "✅ Chrome extensions folder found" -ForegroundColor Green
    Write-Host "📁 Path: $chromeExtensionsPath" -ForegroundColor Gray
    Write-Host ""

    $extensions = Get-ChildItem $chromeExtensionsPath -Directory

    Write-Host "📊 Found $($extensions.Count) extensions installed:" -ForegroundColor Yellow
    Write-Host ""

    foreach ($ext in $extensions) {
        # Try to find manifest.json in any version subfolder
        $versions = Get-ChildItem $ext.FullName -Directory
        if ($versions) {
            $latestVersion = $versions | Sort-Object Name -Descending | Select-Object -First 1
            $manifestPath = Join-Path $latestVersion.FullName "manifest.json"

            if (Test-Path $manifestPath) {
                $manifest = Get-Content $manifestPath | ConvertFrom-Json

                Write-Host "  📦 Extension: $($manifest.name)" -ForegroundColor Cyan
                Write-Host "     ID: $($ext.Name)" -ForegroundColor Gray
                Write-Host "     Version: $($manifest.version)" -ForegroundColor Gray

                # Check if it is AI-related
                if ($manifest.name -match "AI|Claude|ChatGPT|Copilot|Assistant|Thunder|Console|Debug|DevTools") {
                    Write-Host "     ⭐ AI/Dev Tool Detected!" -ForegroundColor Green
                }
                Write-Host ""
            }
        }
    }

    Write-Host ""
    Write-Host "💡 Recommended AI Extensions for Development:" -ForegroundColor Yellow
    Write-Host "   1. Thunder Client - REST API testing"
    Write-Host "   2. React Developer Tools - Component debugging"
    Write-Host "   3. Redux DevTools - State management"
    Write-Host "   4. Console Ninja - Enhanced console logging"
    Write-Host "   5. Wappalyzer - Tech stack detector"
    Write-Host ""

} else {
    Write-Host "❌ Chrome extensions folder not found" -ForegroundColor Red
    Write-Host "   Make sure Chrome is installed and you have used it at least once" -ForegroundColor Yellow
}

# Check Edge extensions too (they can be similar)
Write-Host ""
Write-Host "🔍 Checking Edge Extensions..." -ForegroundColor Cyan
Write-Host ""

$edgeExtensionsPath = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Extensions"

if (Test-Path $edgeExtensionsPath) {
    Write-Host "✅ Edge extensions folder found" -ForegroundColor Green
    $edgeExtensions = Get-ChildItem $edgeExtensionsPath -Directory
    Write-Host "📊 Found $($edgeExtensions.Count) extensions in Edge" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Note: Edge can install Chrome Web Store extensions!" -ForegroundColor Cyan
    Write-Host "   Visit: https://chrome.google.com/webstore in Edge" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Edge extensions folder not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Extension check complete!" -ForegroundColor Green
