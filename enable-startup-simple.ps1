# Enable Dual-AI Auto-Startup - Simple Version

Write-Host "Enabling Dual-AI Auto-Startup..." -ForegroundColor Cyan
Write-Host ""

# Create PowerShell profile functions
$ProfilePath = $PROFILE.CurrentUserAllHosts
$ProfileDir = Split-Path $ProfilePath -Parent

# Create profile directory
if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null
}

$ProfileFunctions = @'

# ========================================
# DUAL-AI WORKFLOW COMMANDS
# ========================================

function dual-ai {
    param([string]$Request)
    if ([string]::IsNullOrEmpty($Request)) {
        Write-Host "Usage: dual-ai 'Your feature description'" -ForegroundColor Yellow
        return
    }
    $orchestrator = "C:\Users\SSaint-Cyr\Documents\dual-ai-global\dual-ai-orchestrator.ps1"
    if (Test-Path $orchestrator) {
        powershell -ExecutionPolicy Bypass -File $orchestrator -UserRequest $Request
    } elseif (Test-Path ".\dual-ai-orchestrator.ps1") {
        .\dual-ai-orchestrator.ps1 -UserRequest $Request
    } else {
        Write-Host "Run 'init-dual-ai' first" -ForegroundColor Red
    }
}

function init-dual-ai {
    $init = "C:\Users\SSaint-Cyr\Documents\dual-ai-global\templates\init-dual-ai-project.ps1"
    if (Test-Path $init) {
        powershell -ExecutionPolicy Bypass -File $init
    } else {
        Write-Host "Copying files..." -ForegroundColor Cyan
        $src = "C:\Users\SSaint-Cyr\Documents\dual-ai-global\dual-ai-orchestrator.ps1"
        if (Test-Path $src) {
            Copy-Item $src . -Force
            Write-Host "Done! Run: .\dual-ai-orchestrator.ps1 -UserRequest 'feature'" -ForegroundColor Green
        }
    }
}

function dual-ai-docs {
    explorer "C:\Users\SSaint-Cyr\Documents\dual-ai-global"
}

function dual-ai-help {
    Write-Host ""
    Write-Host "DUAL-AI COMMANDS:" -ForegroundColor Cyan
    Write-Host "  dual-ai 'feature'  - Run workflow" -ForegroundColor White
    Write-Host "  init-dual-ai       - Setup project" -ForegroundColor White
    Write-Host "  dual-ai-docs       - Open docs" -ForegroundColor White
    Write-Host ""
}

Write-Host "Dual-AI loaded. Type 'dual-ai-help'" -ForegroundColor Green

'@

# Add to profile
if (Test-Path $ProfilePath) {
    $content = Get-Content $ProfilePath -Raw
    if ($content -notmatch "DUAL-AI WORKFLOW") {
        Add-Content -Path $ProfilePath -Value $ProfileFunctions
        Write-Host "Functions added to profile" -ForegroundColor Green
    } else {
        Write-Host "Functions already in profile" -ForegroundColor Gray
    }
} else {
    Set-Content -Path $ProfilePath -Value $ProfileFunctions
    Write-Host "Profile created" -ForegroundColor Green
}

Write-Host "Profile: $ProfilePath" -ForegroundColor Gray
Write-Host ""

# Create init script
$InitScript = @'
$ProjectRoot = Get-Location
Write-Host "Initializing Dual-AI in: $ProjectRoot" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path ".vscode" | Out-Null
New-Item -ItemType Directory -Force -Path ".cursor" | Out-Null
$src = "C:\Users\SSaint-Cyr\Documents\dual-ai-global\dual-ai-orchestrator.ps1"
if (Test-Path $src) {
    Copy-Item $src . -Force
    Write-Host "Done! Run: .\dual-ai-orchestrator.ps1 -UserRequest 'feature'" -ForegroundColor Green
}
'@

$TemplateDir = "C:\Users\SSaint-Cyr\Documents\dual-ai-global\templates"
New-Item -ItemType Directory -Force -Path $TemplateDir | Out-Null
$InitFile = Join-Path $TemplateDir "init-dual-ai-project.ps1"
Set-Content -Path $InitFile -Value $InitScript
Write-Host "Init script created" -ForegroundColor Green
Write-Host ""

# Apply to current project
Write-Host "Initializing PaiiD..." -ForegroundColor Cyan
cd "C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD"
powershell -ExecutionPolicy Bypass -File $InitFile
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUCCESS! Auto-startup enabled" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commands available:" -ForegroundColor White
Write-Host "  dual-ai 'feature'" -ForegroundColor Cyan
Write-Host "  init-dual-ai" -ForegroundColor Cyan
Write-Host "  dual-ai-docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Restart PowerShell to activate" -ForegroundColor Yellow
Write-Host ""
Write-Host "Test now: dual-ai-help" -ForegroundColor Cyan

# Load in current session
. $ProfilePath
