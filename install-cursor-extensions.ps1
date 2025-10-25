# Install Recommended Cursor Extensions
# This script installs essential extensions for PaiiD development

Write-Host "🔧 Installing Recommended Cursor Extensions for PaiiD..." -ForegroundColor Cyan
Write-Host ""

# Essential extensions for PaiiD development
$extensions = @(
    "ms-vscode.vscode-typescript-next",      # TypeScript support
    "bradlc.vscode-tailwindcss",            # Tailwind CSS IntelliSense  
    "esbenp.prettier-vscode",               # Code formatter
    "ms-vscode.vscode-eslint",              # JavaScript/TypeScript linter
    "ms-vscode.vscode-json",                # JSON support
    "ms-vscode.vscode-python",              # Python support
    "ms-vscode.vscode-git",                 # Git integration
    "GitHub.copilot",                       # AI code completion
    "GitHub.copilot-chat",                  # AI chat
    "ms-vscode.vscode-github-actions",      # GitHub Actions support
    "ms-vscode.vscode-react-snippets",      # React snippets
    "ms-vscode.vscode-npm-scripts",         # npm scripts runner
    "ms-vscode.vscode-markdown",            # Markdown support
    "ms-vscode.vscode-yaml"                 # YAML support
)

$installed = 0
$failed = 0

foreach ($extension in $extensions) {
    Write-Host "Installing $extension..." -ForegroundColor Yellow
    
    try {
        # Try to install via Cursor CLI
        $result = cursor --install-extension $extension 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $extension installed successfully" -ForegroundColor Green
            $installed++
        } else {
            Write-Host "❌ Failed to install $extension" -ForegroundColor Red
            Write-Host "   Try installing manually from Extensions tab" -ForegroundColor Yellow
            $failed++
        }
    } catch {
        Write-Host "❌ Error installing $extension" -ForegroundColor Red
        Write-Host "   Try installing manually from Extensions tab" -ForegroundColor Yellow
        $failed++
    }
    
    Start-Sleep -Seconds 1  # Brief pause between installations
}

Write-Host ""
Write-Host "📊 Installation Summary:" -ForegroundColor Cyan
Write-Host "✅ Successfully installed: $installed extensions" -ForegroundColor Green
Write-Host "❌ Failed to install: $failed extensions" -ForegroundColor Red

if ($failed -gt 0) {
    Write-Host ""
    Write-Host "🔧 Manual Installation:" -ForegroundColor Yellow
    Write-Host "1. Open Cursor" -ForegroundColor White
    Write-Host "2. Press Ctrl+Shift+X to open Extensions" -ForegroundColor White
    Write-Host "3. Search for and install the failed extensions manually" -ForegroundColor White
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Restart Cursor to ensure all extensions are loaded" -ForegroundColor White
Write-Host "2. Open your PaiiD project" -ForegroundColor White
Write-Host "3. Use Ctrl+Shift+P to open Command Palette" -ForegroundColor White
Write-Host "4. Use Ctrl+K for AI chat" -ForegroundColor White
Write-Host "5. Check the GitHub Monitor in the radial menu!" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Your Cursor environment is now optimized for PaiiD development!" -ForegroundColor Green
