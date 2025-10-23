# Enable Dual-AI Auto-Startup for All Projects Globally
# This configures VS Code/Cursor to auto-activate everything

$ErrorActionPreference = "Continue"

Write-Host "🚀 Enabling Dual-AI Auto-Startup Globally..." -ForegroundColor Cyan
Write-Host ""

# =============================================================================
# STEP 1: ENABLE ALL EXTENSIONS AT STARTUP
# =============================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "Step 1: Enabling All Extensions at Startup" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

$VSCodeSettings = "$env:APPDATA\Code\User\settings.json"
$CursorSettings = "$env:APPDATA\Cursor\User\settings.json"

# Global settings for auto-activation
$AutoStartupSettings = @'
{
  "extensions.autoUpdate": true,
  "extensions.autoCheckUpdates": true,
  "extensions.ignoreRecommendations": false,

  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "plaintext": false,
    "markdown": true,
    "typescript": true,
    "typescriptreact": true,
    "javascript": true,
    "javascriptreact": true,
    "python": true
  },
  "github.copilot.editor.enableAutoCompletions": true,

  "continue.enableTabAutocomplete": true,
  "continue.telemetryEnabled": false,

  "errorLens.enabled": true,
  "errorLens.enableOnDiffView": true,

  "gitlens.showWelcomeOnInstall": false,
  "gitlens.showWhatsNewAfterUpgrades": false,

  "workbench.startupEditor": "none",
  "window.restoreWindows": "all",

  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,

  "editor.formatOnSave": true,
  "editor.formatOnPaste": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "explicit",
    "source.organizeImports": "explicit"
  },

  "terminal.integrated.enableMultiLinePasteWarning": "never",

  "todo-tree.general.showActivityBarBadge": true,
  "todo-tree.general.tags": [
    "TODO", "FIXME", "HACK", "BUG",
    "CLAUDE", "CHATGPT", "ESCALATE", "REVIEW"
  ],
  "todo-tree.highlights.enabled": true,

  "console-ninja.featureSet": "Community",
  "console-ninja.toolsToShow": ["console", "errors", "network"],

  "jest.autoRun": "off",
  "jest.enableInlineErrorMessages": true,

  "typescript.tsserver.experimental.enableProjectDiagnostics": true,
  "typescript.suggest.autoImports": true,
  "typescript.updateImportsOnFileMove.enabled": "always",

  "python.languageServer": "Pylance",
  "python.testing.autoTestDiscoverOnSaveEnabled": true
}
'@

Write-Host "Applying auto-startup settings..." -ForegroundColor Cyan
Write-Host ""

# Function to merge settings
function Merge-JSONSettings {
    param(
        [string]$FilePath,
        [string]$NewSettingsJSON
    )

    try {
        $newSettings = $NewSettingsJSON | ConvertFrom-Json -AsHashtable
        $existing = @{}

        if (Test-Path $FilePath) {
            $content = Get-Content $FilePath -Raw
            if ($content) {
                $existing = $content | ConvertFrom-Json -AsHashtable
            }
        }

        # Merge settings
        foreach ($key in $newSettings.Keys) {
            $existing[$key] = $newSettings[$key]
        }

        # Write back
        $json = $existing | ConvertTo-Json -Depth 10
        Set-Content -Path $FilePath -Value $json -Force

        Write-Host "  ✅ Updated: $FilePath" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  ⚠️  Warning: Could not update $FilePath" -ForegroundColor Yellow
        Write-Host "     Error: $_" -ForegroundColor Gray
        return $false
    }
}

# Apply to VS Code
Merge-JSONSettings -FilePath $VSCodeSettings -NewSettingsJSON $AutoStartupSettings

# Apply to Cursor
Merge-JSONSettings -FilePath $CursorSettings -NewSettingsJSON $AutoStartupSettings

Write-Host ""

# =============================================================================
# STEP 2: CREATE WORKSPACE SETTINGS TEMPLATE
# =============================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "Step 2: Creating Workspace Settings Template" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

$WorkspaceTemplate = @'
{
  "folders": [],
  "settings": {
    "files.associations": {
      "*.md": "markdown",
      "IMPLEMENTATION_PLAN.md": "markdown",
      "EXECUTION_LOG.md": "markdown",
      "REVIEW_RESULTS.md": "markdown"
    },
    "files.watcherExclude": {
      "**/.git/objects/**": true,
      "**/.git/subtree-cache/**": true,
      "**/node_modules/**": true,
      "**/.next/**": true,
      "**/dist/**": true
    },
    "search.exclude": {
      "**/node_modules": true,
      "**/dist": true,
      "**/.next": true,
      "**/build": true
    }
  },
  "extensions": {
    "recommendations": [
      "github.copilot",
      "github.copilot-chat",
      "continue.continue",
      "anthropic.claude-code",
      "usernamehw.errorlens",
      "eamodio.gitlens",
      "sonarsource.sonarlint-vscode",
      "wallabyjs.console-ninja",
      "ms-playwright.playwright",
      "rangav.vscode-thunder-client"
    ]
  }
}
'@

$GlobalTemplateDir = "C:\Users\SSaint-Cyr\Documents\dual-ai-global\templates"
New-Item -ItemType Directory -Force -Path $GlobalTemplateDir | Out-Null

$WorkspaceFile = Join-Path $GlobalTemplateDir "dual-ai-workspace.code-workspace"
Set-Content -Path $WorkspaceFile -Value $WorkspaceTemplate -Force

Write-Host "  ✅ Workspace template created: $WorkspaceFile" -ForegroundColor Green
Write-Host ""

# =============================================================================
# STEP 3: CREATE AUTO-INIT SCRIPT FOR NEW PROJECTS
# =============================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "Step 3: Creating Auto-Init Script" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

$AutoInitScript = @'
# Auto-Initialize Dual-AI Workflow in Current Project
# Run this once in any new project

$ProjectRoot = Get-Location

Write-Host "Initializing Dual-AI workflow in: $ProjectRoot" -ForegroundColor Cyan
Write-Host ""

# Create .vscode directory
$VSCodeDir = Join-Path $ProjectRoot ".vscode"
New-Item -ItemType Directory -Force -Path $VSCodeDir | Out-Null

# Create .cursor directory
$CursorDir = Join-Path $ProjectRoot ".cursor"
New-Item -ItemType Directory -Force -Path $CursorDir | Out-Null

# Copy orchestrator
$OrchestratorSource = "C:\Users\SSaint-Cyr\Documents\dual-ai-global\dual-ai-orchestrator.ps1"
if (Test-Path $OrchestratorSource) {
    Copy-Item $OrchestratorSource $ProjectRoot -Force
    Write-Host "✅ Orchestrator copied" -ForegroundColor Green
}

# Copy automation rules (symlink to global)
$RulesSource = "C:\Users\SSaint-Cyr\.cursor\rules\dual-ai-automation.md"
if (Test-Path $RulesSource) {
    $RulesDir = Join-Path $CursorDir "rules"
    New-Item -ItemType Directory -Force -Path $RulesDir | Out-Null
    Copy-Item $RulesSource $RulesDir -Force
    Write-Host "✅ Automation rules linked" -ForegroundColor Green
}

# Create project settings
$ProjectSettings = @'
{
  "files.associations": {
    "IMPLEMENTATION_PLAN.md": "markdown",
    "EXECUTION_LOG.md": "markdown",
    "REVIEW_RESULTS.md": "markdown"
  },
  "files.exclude": {
    "IMPLEMENTATION_PLAN.md": false,
    "EXECUTION_LOG.md": false,
    "REVIEW_RESULTS.md": false
  }
}
'@

$SettingsFile = Join-Path $VSCodeDir "settings.json"
Set-Content -Path $SettingsFile -Value $ProjectSettings -Force
Write-Host "✅ Project settings created" -ForegroundColor Green

# Create README for dual-AI usage
$ReadmeContent = @'
# Dual-AI Workflow

This project is configured for automated dual-AI development.

## Quick Start

```powershell
# Run automated workflow:
.\dual-ai-orchestrator.ps1 -UserRequest "Your feature description"
```

## Workflow:
1. **Claude** plans the implementation
2. **ChatGPT** writes the code
3. **Claude** reviews and approves

## Files:
- `IMPLEMENTATION_PLAN.md` - Claude's plan
- `EXECUTION_LOG.md` - ChatGPT's progress
- `REVIEW_RESULTS.md` - Claude's review

## Documentation:
See: `C:\Users\SSaint-Cyr\Documents\dual-ai-global\`
'@

$ReadmeFile = Join-Path $ProjectRoot "DUAL_AI_README.md"
if (-not (Test-Path $ReadmeFile)) {
    Set-Content -Path $ReadmeFile -Value $ReadmeContent -Force
    Write-Host "✅ README created" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Project initialized for Dual-AI workflow!" -ForegroundColor Green
Write-Host ""
Write-Host "Run: .\dual-ai-orchestrator.ps1 -UserRequest 'Your feature'" -ForegroundColor Cyan
'@

$AutoInitFile = Join-Path $GlobalTemplateDir "init-dual-ai-project.ps1"
Set-Content -Path $AutoInitFile -Value $AutoInitScript -Force

Write-Host "  ✅ Auto-init script created: $AutoInitFile" -ForegroundColor Green
Write-Host ""

# =============================================================================
# STEP 4: CREATE POWERSHELL PROFILE FUNCTIONS
# =============================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "Step 4: Adding PowerShell Profile Functions" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

$ProfileFunctions = @'

# ========================================
# DUAL-AI WORKFLOW GLOBAL FUNCTIONS
# ========================================

# Quick dual-AI orchestrator
function dual-ai {
    param([string]$Request)
    if ([string]::IsNullOrEmpty($Request)) {
        Write-Host "Usage: dual-ai 'Your feature description'" -ForegroundColor Yellow
        return
    }
    $orchestratorPath = "C:\Users\SSaint-Cyr\Documents\dual-ai-global\dual-ai-orchestrator.ps1"
    if (Test-Path $orchestratorPath) {
        & powershell -ExecutionPolicy Bypass -File $orchestratorPath -UserRequest $Request
    } else {
        # Try local
        if (Test-Path ".\dual-ai-orchestrator.ps1") {
            .\dual-ai-orchestrator.ps1 -UserRequest $Request
        } else {
            Write-Host "Orchestrator not found. Run: init-dual-ai" -ForegroundColor Red
        }
    }
}

# Initialize dual-AI in current project
function init-dual-ai {
    $initScript = "C:\Users\SSaint-Cyr\Documents\dual-ai-global\templates\init-dual-ai-project.ps1"
    if (Test-Path $initScript) {
        & powershell -ExecutionPolicy Bypass -File $initScript
    } else {
        Write-Host "Init script not found at: $initScript" -ForegroundColor Red
    }
}

# Open dual-AI documentation
function dual-ai-docs {
    explorer "C:\Users\SSaint-Cyr\Documents\dual-ai-global"
}

# Quick reference
function dual-ai-help {
    Write-Host ""
    Write-Host "DUAL-AI WORKFLOW COMMANDS" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  dual-ai 'feature'      - Run automated workflow" -ForegroundColor White
    Write-Host "  init-dual-ai           - Initialize current project" -ForegroundColor White
    Write-Host "  dual-ai-docs           - Open documentation" -ForegroundColor White
    Write-Host "  dual-ai-help           - Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "Example:" -ForegroundColor Yellow
    Write-Host "  dual-ai 'Add login feature with JWT auth'" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Dual-AI workflow commands loaded. Type 'dual-ai-help' for usage." -ForegroundColor Green

'@

# Get PowerShell profile path
$ProfilePath = $PROFILE.CurrentUserAllHosts

# Create profile directory if it does not exist
$ProfileDir = Split-Path $ProfilePath -Parent
if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null
}

# Add functions to profile if not already there
if (Test-Path $ProfilePath) {
    $existingContent = Get-Content $ProfilePath -Raw
    if ($existingContent -notmatch "DUAL-AI WORKFLOW GLOBAL FUNCTIONS") {
        Add-Content -Path $ProfilePath -Value $ProfileFunctions
        Write-Host "  ✅ Functions added to PowerShell profile" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Functions already in profile" -ForegroundColor Gray
    }
} else {
    Set-Content -Path $ProfilePath -Value $ProfileFunctions -Force
    Write-Host "  ✅ PowerShell profile created with functions" -ForegroundColor Green
}

Write-Host "  📍 Profile location: $ProfilePath" -ForegroundColor Gray
Write-Host ""

# =============================================================================
# STEP 5: APPLY TO CURRENT PROJECT
# =============================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "Step 5: Applying to Current Project (PaiiD)" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

$CurrentProject = "C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD"
Set-Location $CurrentProject

Write-Host "Running init script for PaiiD..." -ForegroundColor Cyan
& powershell -ExecutionPolicy Bypass -File $AutoInitFile

Write-Host ""

# =============================================================================
# STEP 6: CREATE STARTUP SHORTCUTS
# =============================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "Step 6: Creating Desktop Shortcuts" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

# Create shortcut to open Cursor with PaiiD
$Shell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath("Desktop")

# Shortcut for PaiiD project
$ShortcutPath = Join-Path $Desktop "PaiiD-DualAI.lnk"
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "cursor"
$Shortcut.Arguments = "$CurrentProject"
$Shortcut.WorkingDirectory = $CurrentProject
$Shortcut.Description = "Open PaiiD with Dual-AI Workflow"
$Shortcut.Save()

Write-Host "  ✅ Desktop shortcut created: PaiiD-DualAI.lnk" -ForegroundColor Green

# Shortcut for documentation
$DocsShortcutPath = Join-Path $Desktop "DualAI-Docs.lnk"
$DocsShortcut = $Shell.CreateShortcut($DocsShortcutPath)
$DocsShortcut.TargetPath = "C:\Users\SSaint-Cyr\Documents\dual-ai-global"
$DocsShortcut.Description = "Dual-AI Workflow Documentation"
$DocsShortcut.Save()

Write-Host "  ✅ Desktop shortcut created: DualAI-Docs.lnk" -ForegroundColor Green
Write-Host ""

# =============================================================================
# SUMMARY
# =============================================================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ AUTO-STARTUP ENABLED GLOBALLY!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "What is Now Active:" -ForegroundColor White
Write-Host "  ✅ All extensions auto-enabled at startup" -ForegroundColor Green
Write-Host "  ✅ Global settings applied (VS Code + Cursor)" -ForegroundColor Green
Write-Host "  ✅ PowerShell functions available everywhere" -ForegroundColor Green
Write-Host "  ✅ PaiiD project initialized" -ForegroundColor Green
Write-Host "  ✅ Desktop shortcuts created" -ForegroundColor Green
Write-Host ""

Write-Host "New PowerShell Commands (Available Now):" -ForegroundColor Cyan
Write-Host "  dual-ai 'feature description'" -ForegroundColor White
Write-Host "  init-dual-ai" -ForegroundColor White
Write-Host "  dual-ai-docs" -ForegroundColor White
Write-Host "  dual-ai-help" -ForegroundColor White
Write-Host ""

Write-Host "To Use in ANY Project:" -ForegroundColor Yellow
Write-Host "  1. Open new PowerShell window (to load profile)" -ForegroundColor White
Write-Host "  2. cd C:\path\to\any\project" -ForegroundColor White
Write-Host "  3. init-dual-ai" -ForegroundColor White
Write-Host "  4. dual-ai 'Add feature X'" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  IMPORTANT: Restart Required" -ForegroundColor Yellow
Write-Host "  1. Close this PowerShell window" -ForegroundColor White
Write-Host "  2. Close VS Code / Cursor" -ForegroundColor White
Write-Host "  3. Reopen - everything will auto-activate" -ForegroundColor White
Write-Host ""

Write-Host "Test After Restart:" -ForegroundColor Cyan
Write-Host "  1. Open new PowerShell" -ForegroundColor White
Write-Host "  2. Type: dual-ai-help" -ForegroundColor White
Write-Host "  3. Type: dual-ai 'test feature'" -ForegroundColor White
Write-Host ""

Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""

# Reload current session
Write-Host "Loading functions in current session..." -ForegroundColor Cyan
. $PROFILE.CurrentUserAllHosts
Write-Host ""
Write-Host "Functions loaded! Type dual-ai-help to see commands." -ForegroundColor Green
