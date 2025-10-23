# Configure Extensions for Optimal Dual-AI Workflow
# Applies global settings for Claude + ChatGPT coordination

$ErrorActionPreference = "Stop"

Write-Host "⚙️  Dual-AI Extension Configuration" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$SettingsPath = "$env:APPDATA\Code\User\settings.json"
$CursorSettingsPath = "$env:APPDATA\Cursor\User\settings.json"

# =============================================================================
# OPTIMAL SETTINGS FOR DUAL-AI WORKFLOW
# =============================================================================

$DualAISettings = @{
    # ========== AI ASSISTANCE ==========
    "github.copilot.enable" = @{
        "*" = $true
        "yaml" = $true
        "plaintext" = $false
        "markdown" = $true
    }
    "github.copilot.editor.enableAutoCompletions" = $true
    "github.copilot.advanced" = @{
        "debug.overrideEngine" = "gpt-4"
    }

    # Claude Code
    "claude-code.selectedModel" = "default"
    "claude-code.autoSuggest" = $true

    # Continue (AI assistant)
    "continue.enableTabAutocomplete" = $true
    "continue.telemetryEnabled" = $false

    # ========== ERROR DETECTION & QUALITY ==========
    "errorLens.enabled" = $true
    "errorLens.enabledDiagnosticLevels" = @("error", "warning", "info")
    "errorLens.fontSize" = "12"
    "errorLens.fontWeight" = "normal"
    "errorLens.messageMaxChars" = 200
    "errorLens.onSave" = $true
    "errorLens.followCursor" = "allLines"

    # ESLint
    "eslint.enable" = $true
    "eslint.format.enable" = $true
    "eslint.lintTask.enable" = $true
    "eslint.codeActionsOnSave.mode" = "all"

    # SonarLint
    "sonarlint.rules" = @{
        "typescript:S1186" = @{ "level" = "on" }  # Empty functions
        "typescript:S3776" = @{ "level" = "on" }  # Cognitive complexity
    }

    # ========== TESTING & DEBUGGING ==========
    "console-ninja.featureSet" = "Community"
    "console-ninja.toolsToShow" = @("console", "errors", "network")
    "console-ninja.fontSize" = 12

    # Jest
    "jest.autoRun" = "off"
    "jest.showCoverageOnLoad" = $false
    "jest.enableInlineErrorMessages" = $true

    # Playwright
    "playwright.reuseBrowser" = $true
    "playwright.showTrace" = "on"

    # Python debugging
    "python.testing.autoTestDiscoverOnSaveEnabled" = $true
    "python.testing.pytestEnabled" = $true

    # ========== GIT & COLLABORATION ==========
    "gitlens.ai.model" = "gitkraken"
    "gitlens.ai.gitkraken.model" = "gemini:gemini-2.0-flash"
    "gitlens.ai.vscode.model" = "copilot:gpt-4.1"
    "gitlens.codeLens.enabled" = $true
    "gitlens.currentLine.enabled" = $true
    "gitlens.hovers.currentLine.over" = "line"
    "gitlens.hovers.enabled" = $true

    "git.autofetch" = $true
    "git.confirmSync" = $false
    "git.enableSmartCommit" = $true
    "git.suggestSmartCommit" = $true

    # ========== CODE INTELLIGENCE ==========
    "vsintellicode.modify.editor.suggestSelection" = "automaticallyOverrodeDefaultValue"
    "typescript.suggest.autoImports" = $true
    "typescript.updateImportsOnFileMove.enabled" = "always"
    "typescript.inlayHints.parameterNames.enabled" = "all"
    "typescript.inlayHints.functionLikeReturnTypes.enabled" = $true

    "javascript.suggest.autoImports" = $true
    "javascript.updateImportsOnFileMove.enabled" = "always"

    # ========== PRODUCTIVITY ==========
    "editor.formatOnSave" = $true
    "editor.formatOnPaste" = $true
    "editor.codeActionsOnSave" = @{
        "source.fixAll" = "explicit"
        "source.organizeImports" = "explicit"
        "source.addMissingImports" = "explicit"
    }

    "editor.suggestSelection" = "first"
    "editor.inlineSuggest.enabled" = $true
    "editor.quickSuggestions" = @{
        "other" = $true
        "comments" = $false
        "strings" = $true
    }

    "files.autoSave" = "afterDelay"
    "files.autoSaveDelay" = 1000

    # Auto imports
    "typescript.preferences.importModuleSpecifier" = "relative"
    "javascript.preferences.importModuleSpecifier" = "relative"

    # ========== TODO MANAGEMENT ==========
    "todo-tree.general.tags" = @(
        "TODO",
        "FIXME",
        "CLAUDE",
        "CHATGPT",
        "ESCALATE",
        "REVIEW"
    )
    "todo-tree.highlights.customHighlight" = @{
        "CLAUDE" = @{
            "icon" = "brain"
            "iconColour" = "#9333EA"
            "foreground" = "#9333EA"
        }
        "CHATGPT" = @{
            "icon" = "robot"
            "iconColour" = "#10B981"
            "foreground" = "#10B981"
        }
        "ESCALATE" = @{
            "icon" = "alert"
            "iconColour" = "#EF4444"
            "foreground" = "#EF4444"
        }
    }

    # ========== DOCUMENTATION ==========
    "markdown.preview.fontSize" = 14
    "markdown.preview.lineHeight" = 1.6
    "markdown.extension.toc.levels" = "2..6"

    # Better comments colors
    "better-comments.tags" = @(
        @{
            "tag" = "CLAUDE:"
            "color" = "#9333EA"
            "strikethrough" = $false
            "underline" = $false
            "backgroundColor" = "transparent"
            "bold" = $true
        },
        @{
            "tag" = "CHATGPT:"
            "color" = "#10B981"
            "strikethrough" = $false
            "underline" = $false
            "backgroundColor" = "transparent"
            "bold" = $true
        },
        @{
            "tag" = "ESCALATE:"
            "color" = "#EF4444"
            "strikethrough" = $false
            "underline" = $false
            "backgroundColor" = "transparent"
            "bold" = $true
        }
    )

    # ========== PERFORMANCE ==========
    "files.exclude" = @{
        "**/.git" = $true
        "**/.DS_Store" = $true
        "**/node_modules" = $true
        "**/__pycache__" = $true
        "**/.pytest_cache" = $true
        "**/.next" = $true
        "**/dist" = $true
        "**/build" = $true
    }

    "search.exclude" = @{
        "**/node_modules" = $true
        "**/dist" = $true
        "**/.next" = $true
        "**/build" = $true
        "**/__pycache__" = $true
    }

    # ========== TERMINAL ==========
    "terminal.integrated.enableMultiLinePasteWarning" = "never"
    "terminal.integrated.fontFamily" = "Cascadia Code, Consolas, monospace"
    "terminal.integrated.fontSize" = 14

    # ========== WORKSPACE ==========
    "workbench.startupEditor" = "none"
    "workbench.colorTheme" = "Material Theme Darker"
    "workbench.iconTheme" = "material-icon-theme"
    "workbench.tree.indent" = 20
}

# =============================================================================
# LANGUAGE-SPECIFIC SETTINGS
# =============================================================================

$LanguageSettings = @{
    "[typescript]" = @{
        "editor.defaultFormatter" = "esbenp.prettier-vscode"
        "editor.codeActionsOnSave" = @{
            "source.fixAll.eslint" = "explicit"
            "source.organizeImports" = "explicit"
        }
    }
    "[typescriptreact]" = @{
        "editor.defaultFormatter" = "esbenp.prettier-vscode"
        "editor.codeActionsOnSave" = @{
            "source.fixAll.eslint" = "explicit"
            "source.organizeImports" = "explicit"
        }
    }
    "[javascript]" = @{
        "editor.defaultFormatter" = "esbenp.prettier-vscode"
    }
    "[python]" = @{
        "editor.defaultFormatter" = "charliermarsh.ruff"
        "editor.formatOnSave" = $true
        "editor.codeActionsOnSave" = @{
            "source.fixAll" = "explicit"
            "source.organizeImports" = "explicit"
        }
    }
    "[json]" = @{
        "editor.defaultFormatter" = "esbenp.prettier-vscode"
    }
    "[jsonc]" = @{
        "editor.defaultFormatter" = "esbenp.prettier-vscode"
    }
    "[markdown]" = @{
        "editor.defaultFormatter" = "yzhang.markdown-all-in-one"
        "editor.wordWrap" = "on"
    }
}

# =============================================================================
# MERGE SETTINGS
# =============================================================================

function Merge-Settings {
    param(
        [string]$TargetPath,
        [hashtable]$NewSettings
    )

    Write-Host "  📝 Merging settings into: $TargetPath" -ForegroundColor Cyan

    # Read existing settings
    $existingSettings = @{}
    if (Test-Path $TargetPath) {
        try {
            $content = Get-Content $TargetPath -Raw | ConvertFrom-Json -AsHashtable
            $existingSettings = $content
            Write-Host "     ✅ Loaded existing settings" -ForegroundColor Green
        } catch {
            Write-Host "     ⚠️  Could not parse existing settings, creating new" -ForegroundColor Yellow
        }
    } else {
        Write-Host "     ℹ️  No existing settings file, creating new" -ForegroundColor Gray
    }

    # Merge new settings
    foreach ($key in $NewSettings.Keys) {
        $existingSettings[$key] = $NewSettings[$key]
    }

    # Write back
    try {
        $json = $existingSettings | ConvertTo-Json -Depth 10
        Set-Content -Path $TargetPath -Value $json -Force
        Write-Host "     ✅ Settings updated successfully" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "     ❌ Failed to write settings: $_" -ForegroundColor Red
        return $false
    }
}

# =============================================================================
# APPLY SETTINGS
# =============================================================================

Write-Host "🔧 Applying settings to VS Code..." -ForegroundColor Cyan
$vsCodeSuccess = Merge-Settings -TargetPath $SettingsPath -NewSettings ($DualAISettings + $LanguageSettings)
Write-Host ""

Write-Host "🔧 Applying settings to Cursor..." -ForegroundColor Cyan
$cursorSuccess = Merge-Settings -TargetPath $CursorSettingsPath -NewSettings ($DualAISettings + $LanguageSettings)
Write-Host ""

# =============================================================================
# CREATE SNIPPETS FOR DUAL-AI MARKERS
# =============================================================================

Write-Host "📝 Creating code snippets for dual-AI markers..." -ForegroundColor Cyan

$SnippetsDir = "$env:APPDATA\Code\User\snippets"
if (-not (Test-Path $SnippetsDir)) {
    New-Item -ItemType Directory -Path $SnippetsDir -Force | Out-Null
}

$TypeScriptSnippets = @{
    "Claude Territory Marker" = @{
        "prefix" = "claude-territory"
        "body" = @(
            "// ===== CLAUDE TERRITORY =====",
            "// CRITICAL: $1",
            "// This code requires Claude's architectural oversight",
            "// DO NOT MODIFY without Claude Code review",
            "//",
            "// Contact: Claude Code (terminal) or claude.ai",
            "// Last Review: ${CURRENT_YEAR}-${CURRENT_MONTH}-${CURRENT_DATE}",
            "// ============================",
            "",
            "$0"
        )
        "description" = "Mark file/section as Claude-owned (critical code)"
    }
    "ChatGPT Safe Zone Marker" = @{
        "prefix" = "chatgpt-safe"
        "body" = @(
            "// ===== CHATGPT SAFE ZONE =====",
            "// $1",
            "// This code is safe for ChatGPT modifications",
            "// Low risk, high iteration speed preferred",
            "// =============================",
            "",
            "$0"
        )
        "description" = "Mark file/section as ChatGPT-safe (non-critical)"
    }
    "Escalate to Claude" = @{
        "prefix" = "escalate-claude"
        "body" = @(
            "// 🚨 ESCALATE TO CLAUDE:",
            "// Issue: $1",
            "// Question: $2",
            "// Context: $3",
            "// Urgency: ${4|High,Medium,Low|}",
            "$0"
        )
        "description" = "Escalation marker for ChatGPT to Claude"
    }
    "Review Required" = @{
        "prefix" = "review-required"
        "body" = @(
            "// ✅ REVIEW REQUIRED (Claude)",
            "// Component: $1",
            "// Concern: $2",
            "// Tests: ${3|Passing,Failing,Not Written|}",
            "$0"
        )
        "description" = "Mark code for Claude review"
    }
}

$SnippetsFile = Join-Path $SnippetsDir "typescriptreact.json"
try {
    $existingSnippets = @{}
    if (Test-Path $SnippetsFile) {
        $existingSnippets = Get-Content $SnippetsFile -Raw | ConvertFrom-Json -AsHashtable
    }

    foreach ($name in $TypeScriptSnippets.Keys) {
        $existingSnippets[$name] = $TypeScriptSnippets[$name]
    }

    $json = $existingSnippets | ConvertTo-Json -Depth 10
    Set-Content -Path $SnippetsFile -Value $json -Force
    Write-Host "  ✅ TypeScript/React snippets created" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Could not create snippets: $_" -ForegroundColor Yellow
}

Write-Host ""

# =============================================================================
# SUMMARY
# =============================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Configuration Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 What Was Configured:" -ForegroundColor White
Write-Host "   ✅ AI assistance (Copilot, Claude, Continue)" -ForegroundColor Green
Write-Host "   ✅ Error detection (Error Lens, ESLint, SonarLint)" -ForegroundColor Green
Write-Host "   ✅ Testing & debugging (Console Ninja, Jest, Playwright)" -ForegroundColor Green
Write-Host "   ✅ Git & collaboration (GitLens AI-powered)" -ForegroundColor Green
Write-Host "   ✅ Code intelligence (IntelliCode, auto-imports)" -ForegroundColor Green
Write-Host "   ✅ Productivity (auto-formatting, snippets)" -ForegroundColor Green
Write-Host "   ✅ TODO management (custom CLAUDE/CHATGPT tags)" -ForegroundColor Green
Write-Host "   ✅ Documentation (Markdown, Better Comments)" -ForegroundColor Green
Write-Host ""

Write-Host "📁 Settings Applied To:" -ForegroundColor White
if ($vsCodeSuccess) {
    Write-Host "   ✅ VS Code: $SettingsPath" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  VS Code: Failed to apply" -ForegroundColor Yellow
}

if ($cursorSuccess) {
    Write-Host "   ✅ Cursor: $CursorSettingsPath" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Cursor: Failed to apply" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "📝 Code Snippets Created:" -ForegroundColor White
Write-Host "   • claude-territory - Mark Claude-owned code" -ForegroundColor Gray
Write-Host "   • chatgpt-safe - Mark ChatGPT-safe code" -ForegroundColor Gray
Write-Host "   • escalate-claude - Escalation marker" -ForegroundColor Gray
Write-Host "   • review-required - Review request marker" -ForegroundColor Gray
Write-Host ""

Write-Host "⚠️  RESTART REQUIRED" -ForegroundColor Yellow
Write-Host "   Please restart VS Code and Cursor for all changes to take effect" -ForegroundColor Gray
Write-Host ""

Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Restart VS Code/Cursor" -ForegroundColor White
Write-Host "   2. Open any TypeScript file" -ForegroundColor White
Write-Host "   3. Type 'claude-territory' and press Tab" -ForegroundColor White
Write-Host "   4. Test the dual-AI workflow!" -ForegroundColor White
Write-Host ""

Write-Host "✅ Your dual-AI workflow is now fully configured!" -ForegroundColor Green
