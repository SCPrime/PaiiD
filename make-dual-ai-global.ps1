# Make Dual-AI Automation Global Across All Projects

$ErrorActionPreference = "Continue"

Write-Host "Making Dual-AI Automation Global..." -ForegroundColor Cyan
Write-Host ""

# Source files in PaiiD
$SourceDir = "C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD"
$TemplateDir = "C:\Users\SSaint-Cyr\Documents\GitHub\dual-ai-template"

# Global locations
$GlobalCursorDir = "$env:USERPROFILE\.cursor"
$GlobalDocsDir = "$env:USERPROFILE\Documents\dual-ai-global"

Write-Host "Step 1: Creating global directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "$GlobalCursorDir\rules" | Out-Null
New-Item -ItemType Directory -Force -Path "$GlobalCursorDir\workflows" | Out-Null
New-Item -ItemType Directory -Force -Path $GlobalDocsDir | Out-Null
Write-Host "  Created" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Copying automation files..." -ForegroundColor Yellow

# Copy automation rules
if (Test-Path "$SourceDir\.cursor\rules\dual-ai-automation.md") {
    Copy-Item "$SourceDir\.cursor\rules\dual-ai-automation.md" "$GlobalCursorDir\rules\" -Force
    Write-Host "  dual-ai-automation.md copied" -ForegroundColor Green
}

# Copy workflow templates
if (Test-Path "$SourceDir\.cursor\workflows\planning-template.md") {
    Copy-Item "$SourceDir\.cursor\workflows\*.md" "$GlobalCursorDir\workflows\" -Force
    Write-Host "  Workflow templates copied" -ForegroundColor Green
}

# Copy orchestrator script
if (Test-Path "$SourceDir\dual-ai-orchestrator.ps1") {
    Copy-Item "$SourceDir\dual-ai-orchestrator.ps1" $GlobalDocsDir -Force
    Write-Host "  Orchestrator script copied" -ForegroundColor Green
}

# Copy extension scripts
if (Test-Path "$SourceDir\install-extensions-simple.ps1") {
    Copy-Item "$SourceDir\install-extensions-simple.ps1" $GlobalDocsDir -Force
    Copy-Item "$SourceDir\configure-extensions-simple.ps1" $GlobalDocsDir -Force
    Write-Host "  Extension scripts copied" -ForegroundColor Green
}

# Copy documentation
$Docs = @(
    "AUTOMATED_WORKFLOW_GUIDE.md",
    "DUAL_AI_EXTENSIONS_GUIDE.md",
    "QUICK_REFERENCE_AUTOMATED_WORKFLOW.md",
    "TASK_ASSIGNMENT_WORKFLOW.md"
)

foreach ($doc in $Docs) {
    if (Test-Path "$SourceDir\$doc") {
        Copy-Item "$SourceDir\$doc" $GlobalDocsDir -Force
        Write-Host "  $doc copied" -ForegroundColor Green
    }
}

Write-Host ""

Write-Host "Step 3: Creating global PATH entry..." -ForegroundColor Yellow
# Create a batch file in a common location
$BatchContent = @"
@echo off
REM Dual-AI Orchestrator Global Launcher
cd /d %CD%
powershell -ExecutionPolicy Bypass -File "$GlobalDocsDir\dual-ai-orchestrator.ps1" %*
"@

$ScriptsDir = "$env:USERPROFILE\scripts"
New-Item -ItemType Directory -Force -Path $ScriptsDir | Out-Null
Set-Content -Path "$ScriptsDir\dual-ai.bat" -Value $BatchContent -Force
Write-Host "  Global command created: dual-ai" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Success! Dual-AI is now global" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Files installed to:" -ForegroundColor White
Write-Host "  $GlobalCursorDir\rules" -ForegroundColor Gray
Write-Host "  $GlobalCursorDir\workflows" -ForegroundColor Gray
Write-Host "  $GlobalDocsDir" -ForegroundColor Gray
Write-Host ""

Write-Host "How to use in ANY project:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Navigate to any project:" -ForegroundColor White
Write-Host "   cd C:\path\to\your\project" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run orchestrator:" -ForegroundColor White
Write-Host "   powershell $GlobalDocsDir\dual-ai-orchestrator.ps1 -UserRequest 'Your feature'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. OR use shortcuts in each project:" -ForegroundColor White
Write-Host "   Copy dual-ai-orchestrator.ps1 to project root" -ForegroundColor Gray
Write-Host ""

Write-Host "Extensions are already global (installed to VS Code/Cursor)" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test in PaiiD project first" -ForegroundColor White
Write-Host "2. Then try in other projects" -ForegroundColor White
Write-Host "3. Reference: $GlobalDocsDir\AUTOMATED_WORKFLOW_GUIDE.md" -ForegroundColor White
Write-Host ""

Write-Host "Done!" -ForegroundColor Green
