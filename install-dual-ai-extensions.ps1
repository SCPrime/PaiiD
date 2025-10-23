# Dual-AI Enhanced Extensions Installer
# Installs and configures extensions for optimal Claude + ChatGPT workflow

param(
    [switch]$SkipInstalled
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Dual-AI Enhanced Extensions Installer" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# =============================================================================
# EXTENSION CATEGORIES FOR DUAL-AI WORKFLOW
# =============================================================================

$Extensions = @{
    # CATEGORY 1: AI ASSISTANCE (Critical for dual-AI)
    "AI_Assistance" = @(
        @{ id = "github.copilot"; name = "GitHub Copilot"; reason = "Code completion (ChatGPT-powered)" }
        @{ id = "github.copilot-chat"; name = "GitHub Copilot Chat"; reason = "Conversational AI assistance" }
        @{ id = "anthropic.claude-code"; name = "Claude Code"; reason = "Claude CLI integration" }
        @{ id = "continue.continue"; name = "Continue"; reason = "AI code assistant with Claude support" }
    )

    # CATEGORY 2: CODE QUALITY & ERROR DETECTION (Helps both AIs catch issues)
    "Code_Quality" = @(
        @{ id = "usernamehw.errorlens"; name = "Error Lens"; reason = "Inline error/warning display" }
        @{ id = "dbaeumer.vscode-eslint"; name = "ESLint"; reason = "JavaScript/TypeScript linting" }
        @{ id = "charliermarsh.ruff"; name = "Ruff"; reason = "Python linting and formatting" }
        @{ id = "sonarsource.sonarlint-vscode"; name = "SonarLint"; reason = "Code quality and security issues" }
        @{ id = "streetsidesoftware.code-spell-checker"; name = "Code Spell Checker"; reason = "Catch typos in code" }
    )

    # CATEGORY 3: TESTING & DEBUGGING (ChatGPT's execution phase)
    "Testing_Debugging" = @(
        @{ id = "wallabyjs.console-ninja"; name = "Console Ninja"; reason = "Inline runtime logs" }
        @{ id = "ms-playwright.playwright"; name = "Playwright"; reason = "E2E testing" }
        @{ id = "orta.vscode-jest"; name = "Jest"; reason = "JavaScript testing" }
        @{ id = "firsttris.vscode-jest-runner"; name = "Jest Runner"; reason = "Run tests inline" }
        @{ id = "ms-python.debugpy"; name = "Python Debugger"; reason = "Python debugging" }
    )

    # CATEGORY 4: GIT & COLLABORATION (Claude's review phase)
    "Git_Collaboration" = @(
        @{ id = "eamodio.gitlens"; name = "GitLens"; reason = "Git supercharged with AI" }
        @{ id = "github.vscode-pull-request-github"; name = "GitHub Pull Requests"; reason = "PR management" }
        @{ id = "mhutchie.git-graph"; name = "Git Graph"; reason = "Visual commit history" }
        @{ id = "donjayamanne.githistory"; name = "Git History"; reason = "File history viewer" }
    )

    # CATEGORY 5: CODE INTELLIGENCE (Better context for both AIs)
    "Code_Intelligence" = @(
        @{ id = "visualstudioexptteam.vscodeintellicode"; name = "IntelliCode"; reason = "AI-assisted IntelliSense" }
        @{ id = "visualstudioexptteam.intellicode-api-usage-examples"; name = "IntelliCode API Usage"; reason = "API usage examples" }
        @{ id = "christian-kohler.path-intellisense"; name = "Path Intellisense"; reason = "File path autocomplete" }
        @{ id = "christian-kohler.npm-intellisense"; name = "NPM Intellisense"; reason = "NPM module autocomplete" }
        @{ id = "wix.vscode-import-cost"; name = "Import Cost"; reason = "Bundle size awareness" }
    )

    # CATEGORY 6: PRODUCTIVITY (Faster implementation)
    "Productivity" = @(
        @{ id = "formulahendry.auto-rename-tag"; name = "Auto Rename Tag"; reason = "HTML/JSX tag sync" }
        @{ id = "steoates.autoimport"; name = "Auto Import"; reason = "Automatic imports" }
        @{ id = "dsznajder.es7-react-js-snippets"; name = "ES7+ React Snippets"; reason = "React boilerplate" }
        @{ id = "meganrogge.template-string-converter"; name = "Template String Converter"; reason = "Auto template literals" }
        @{ id = "gruntfuggly.todo-tree"; name = "TODO Tree"; reason = "Track TODOs/FIXMEs" }
        @{ id = "wayou.vscode-todo-highlight"; name = "TODO Highlight"; reason = "Highlight task comments" }
    )

    # CATEGORY 7: DOCUMENTATION (Both AIs need good docs)
    "Documentation" = @(
        @{ id = "yzhang.markdown-all-in-one"; name = "Markdown All in One"; reason = "Markdown authoring" }
        @{ id = "bierner.markdown-mermaid"; name = "Markdown Mermaid"; reason = "Diagram support" }
        @{ id = "njpwerner.autodocstring"; name = "autoDocstring"; reason = "Python docstrings" }
        @{ id = "aaron-bond.better-comments"; name = "Better Comments"; reason = "Colored comments" }
    )

    # CATEGORY 8: API & TESTING TOOLS (Critical for integration work)
    "API_Testing" = @(
        @{ id = "rangav.vscode-thunder-client"; name = "Thunder Client"; reason = "API testing in VS Code" }
        @{ id = "humao.rest-client"; name = "REST Client"; reason = "HTTP client" }
    )

    # CATEGORY 9: TYPESCRIPT EXCELLENCE (Frontend work)
    "TypeScript" = @(
        @{ id = "yoavbls.pretty-ts-errors"; name = "Pretty TypeScript Errors"; reason = "Readable TS errors" }
        @{ id = "mattpocock.ts-error-translator"; name = "TS Error Translator"; reason = "Plain English TS errors" }
    )

    # CATEGORY 10: MONITORING & PERFORMANCE (Quality assurance)
    "Performance" = @(
        @{ id = "wallabyjs.quokka-vscode"; name = "Quokka.js"; reason = "Live JavaScript scratchpad" }
        @{ id = "styled-components.vscode-styled-components"; name = "Styled Components"; reason = "CSS-in-JS support" }
    )
}

# Extensions you already have that we'll keep
$ExistingGood = @(
    "ms-azuretools.vscode-docker",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "esbenp.prettier-vscode",
    "pkief.material-icon-theme"
)

Write-Host "📦 Extension Categories:" -ForegroundColor Yellow
foreach ($category in $Extensions.Keys) {
    $count = $Extensions[$category].Count
    Write-Host "   $category`: $count extensions" -ForegroundColor Gray
}
Write-Host ""

# =============================================================================
# CHECK CURRENTLY INSTALLED
# =============================================================================

Write-Host "🔍 Checking currently installed extensions..." -ForegroundColor Cyan

$InstalledExtensions = code --list-extensions
Write-Host "   Found $($InstalledExtensions.Count) installed extensions" -ForegroundColor Gray
Write-Host ""

# =============================================================================
# INSTALL EXTENSIONS BY CATEGORY
# =============================================================================

$TotalToInstall = 0
$AlreadyInstalled = 0
$NewlyInstalled = 0
$Failed = 0

foreach ($category in $Extensions.Keys) {
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host "Category: $category" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host ""

    foreach ($ext in $Extensions[$category]) {
        $TotalToInstall++
        $extId = $ext.id
        $extName = $ext.name
        $extReason = $ext.reason

        Write-Host "  📦 $extName" -ForegroundColor White
        Write-Host "     ID: $extId" -ForegroundColor DarkGray
        Write-Host "     Purpose: $extReason" -ForegroundColor DarkGray

        if ($InstalledExtensions -contains $extId) {
            Write-Host "     ✅ Already installed" -ForegroundColor Green
            $AlreadyInstalled++
        } else {
            Write-Host "     ⏳ Installing..." -ForegroundColor Yellow
            try {
                $result = code --install-extension $extId 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "     ✅ Installed successfully" -ForegroundColor Green
                    $NewlyInstalled++
                } else {
                    Write-Host "     ❌ Installation failed: $result" -ForegroundColor Red
                    $Failed++
                }
            } catch {
                Write-Host "     ❌ Error: $_" -ForegroundColor Red
                $Failed++
            }
        }
        Write-Host ""
    }
}

# =============================================================================
# INSTALLATION SUMMARY
# =============================================================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 Installation Summary" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Total extensions processed: $TotalToInstall" -ForegroundColor White
Write-Host "   ✅ Already installed: $AlreadyInstalled" -ForegroundColor Green
Write-Host "   🆕 Newly installed: $NewlyInstalled" -ForegroundColor Cyan
Write-Host "   ❌ Failed: $Failed" -ForegroundColor Red
Write-Host ""

if ($NewlyInstalled -gt 0) {
    Write-Host "⚠️  RESTART REQUIRED" -ForegroundColor Yellow
    Write-Host "   Please restart VS Code/Cursor to activate new extensions" -ForegroundColor Gray
    Write-Host ""
}

# =============================================================================
# CONFIGURATION
# =============================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "⚙️  Configuring Extensions for Dual-AI Workflow" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "📝 Next step: Run configuration script..." -ForegroundColor Cyan
Write-Host "   .\configure-dual-ai-extensions.ps1" -ForegroundColor White
Write-Host ""

Write-Host "✅ Extension installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 See DUAL_AI_EXTENSIONS_GUIDE.md for usage instructions" -ForegroundColor Cyan
