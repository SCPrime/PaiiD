# Simple Extension Installer for Dual-AI Workflow

Write-Host "Installing Dual-AI Enhanced Extensions..." -ForegroundColor Cyan
Write-Host ""

# Extensions list
$extensions = @(
    # AI Assistance
    "continue.continue",

    # Code Quality
    "sonarsource.sonarlint-vscode",

    # Testing
    "firsttris.vscode-jest-runner",

    # Git
    "donjayamanne.githistory",

    # Code Intelligence
    "visualstudioexptteam.intellicode-api-usage-examples",

    # Productivity
    "steoates.autoimport",
    "meganrogge.template-string-converter",

    # TypeScript
    "yoavbls.pretty-ts-errors",
    "mattpocock.ts-error-translator"
)

$installed = 0
$skipped = 0
$failed = 0

foreach ($ext in $extensions) {
    Write-Host "Installing: $ext" -ForegroundColor Yellow
    try {
        $result = code --install-extension $ext 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Success!" -ForegroundColor Green
            $installed++
        } else {
            if ($result -like "*already installed*") {
                Write-Host "  Already installed" -ForegroundColor Gray
                $skipped++
            } else {
                Write-Host "  Failed: $result" -ForegroundColor Red
                $failed++
            }
        }
    } catch {
        Write-Host "  Error: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Installed: $installed" -ForegroundColor Green
Write-Host "  Skipped: $skipped" -ForegroundColor Gray
Write-Host "  Failed: $failed" -ForegroundColor Red
Write-Host ""

if ($installed -gt 0) {
    Write-Host "Restart VS Code/Cursor to activate new extensions" -ForegroundColor Yellow
}

Write-Host "Next: Run configure-dual-ai-extensions.ps1" -ForegroundColor Cyan
