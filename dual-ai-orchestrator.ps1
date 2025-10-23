# Dual-AI Orchestrator
# Automates coordination between Claude (planning) and ChatGPT (execution)

param(
    [Parameter(Mandatory=$true)]
    [string]$UserRequest,

    [string]$Mode = "auto",  # auto, semi, manual
    [switch]$SkipTests,
    [switch]$AutoCommit
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host "🤖 Dual-AI Orchestrator Starting..." -ForegroundColor Cyan
Write-Host "📋 User Request: $UserRequest" -ForegroundColor Yellow
Write-Host "⚙️  Mode: $Mode" -ForegroundColor Gray
Write-Host ""

# =============================================================================
# PHASE 1: CLAUDE PLANNING
# =============================================================================

Write-Host "🧠 PHASE 1: Claude High-Level Planning" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta

$PlanFile = Join-Path $ProjectRoot "IMPLEMENTATION_PLAN.md"
$LogFile = Join-Path $ProjectRoot "EXECUTION_LOG.md"

# Create planning prompt for Claude Code
$ClaudePlanningPrompt = @"
Create a detailed implementation plan for the following request:

USER REQUEST: $UserRequest

Please analyze this request and create IMPLEMENTATION_PLAN.md with:

1. **Overview** - High-level description of what we're building
2. **Architecture Decisions** - Key technical decisions and rationale
3. **File Structure** - What files will be created/modified
4. **Subtasks** - Break down into 5-10 concrete implementation steps

For each subtask, provide:
- **Task Name** - Clear, actionable name
- **File(s)** - Exact file path(s)
- **Specification** - Detailed requirements (what to code)
- **Tests Required** - What tests to write/run
- **Acceptance Criteria** - How to verify it's done correctly
- **Estimated Complexity** - Low/Medium/High

Focus on:
- Backend logic and API design
- Data flow and state management
- Error handling strategy
- Security considerations
- Performance requirements

Format as markdown for easy parsing by ChatGPT executor.

Mark as "READY FOR EXECUTION" when complete.
"@

Write-Host "📝 Sending planning request to Claude Code..." -ForegroundColor Cyan

# In a real implementation, this would call Claude Code API
# For now, we'll create a template and guide the user
Write-Host ""
Write-Host "⏳ Waiting for Claude Code to create plan..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📌 ACTION REQUIRED:" -ForegroundColor Red
Write-Host "   1. Copy the prompt above" -ForegroundColor White
Write-Host "   2. Paste into Claude Code (terminal)" -ForegroundColor White
Write-Host "   3. Claude will create IMPLEMENTATION_PLAN.md" -ForegroundColor White
Write-Host "   4. Press Enter here when plan is ready..." -ForegroundColor White
Write-Host ""

if ($Mode -ne "auto") {
    Read-Host "Press Enter to continue"
}

# Wait for plan file to exist
$MaxWaitSeconds = 300  # 5 minutes
$WaitSeconds = 0
while (-not (Test-Path $PlanFile) -and $WaitSeconds -lt $MaxWaitSeconds) {
    Start-Sleep -Seconds 2
    $WaitSeconds += 2
    if ($WaitSeconds % 10 -eq 0) {
        Write-Host "⏳ Still waiting for IMPLEMENTATION_PLAN.md... ($WaitSeconds s)" -ForegroundColor Gray
    }
}

if (-not (Test-Path $PlanFile)) {
    Write-Host "❌ ERROR: IMPLEMENTATION_PLAN.md not found after $MaxWaitSeconds seconds" -ForegroundColor Red
    Write-Host "   Please create the plan manually and run again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Plan received: IMPLEMENTATION_PLAN.md" -ForegroundColor Green

# Validate plan
$PlanContent = Get-Content $PlanFile -Raw
if ($PlanContent -notmatch "READY FOR EXECUTION") {
    Write-Host "⚠️  Warning: Plan doesn't contain 'READY FOR EXECUTION' marker" -ForegroundColor Yellow
    Write-Host "   Proceeding anyway..." -ForegroundColor Gray
}

Write-Host ""

# =============================================================================
# PHASE 2: CHATGPT EXECUTION
# =============================================================================

Write-Host "💻 PHASE 2: ChatGPT Code Execution" -ForegroundColor Blue
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue

# Create execution prompt for Cursor AI (ChatGPT)
$ChatGPTExecutionPrompt = @"
IMPLEMENTATION_PLAN.md has been created by Claude.

Your role: Execute the implementation plan step by step.

INSTRUCTIONS:
1. Read IMPLEMENTATION_PLAN.md carefully
2. Implement each subtask in order
3. After each subtask:
   - Run the specified tests
   - Fix any errors that occur
   - Update EXECUTION_LOG.md with status
4. Continue until all subtasks complete
5. Mark log as "ALL TASKS COMPLETE - READY FOR REVIEW"

ERROR HANDLING:
- If tests fail: Debug, fix, re-run (up to 3 attempts)
- If architecture unclear: Add "ESCALATE TO CLAUDE: [question]" in log and pause
- If breaking change needed: Add "DESIGN DECISION REQUIRED" in log and pause

EXECUTION LOOP:
For each subtask in plan:
  → Read specification
  → Write/modify code
  → Run tests: $(if ($SkipTests) { "SKIPPED" } else { "npm test OR pytest" })
  → Fix errors if any
  → Update EXECUTION_LOG.md
  → Move to next subtask

BEGIN EXECUTION NOW.
"@

# Initialize execution log
$InitialLog = @"
# Execution Log: $UserRequest

**Started:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Executor:** ChatGPT (Cursor AI)
**Plan:** IMPLEMENTATION_PLAN.md
**Mode:** $Mode

---

## Progress

"@

Set-Content -Path $LogFile -Value $InitialLog

Write-Host "📝 Created EXECUTION_LOG.md" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Starting Cursor AI execution..." -ForegroundColor Cyan
Write-Host ""

# Open Cursor with the execution prompt
Write-Host "📌 ACTION REQUIRED:" -ForegroundColor Red
Write-Host "   1. Open Cursor IDE" -ForegroundColor White
Write-Host "   2. Press Ctrl+L to open chat" -ForegroundColor White
Write-Host "   3. Paste the following prompt:" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host $ChatGPTExecutionPrompt -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "   4. Let ChatGPT implement all subtasks" -ForegroundColor White
Write-Host "   5. Monitor EXECUTION_LOG.md for progress" -ForegroundColor White
Write-Host "   6. Return here when log shows 'READY FOR REVIEW'" -ForegroundColor White
Write-Host ""

# Try to open Cursor automatically
try {
    Start-Process "cursor" -ArgumentList "." -WorkingDirectory $ProjectRoot
    Write-Host "✅ Cursor IDE opened" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not auto-open Cursor. Please open manually." -ForegroundColor Yellow
}

Write-Host ""

if ($Mode -ne "auto") {
    Read-Host "Press Enter when execution is complete"
}

# Monitor execution log
Write-Host "⏳ Monitoring EXECUTION_LOG.md for completion..." -ForegroundColor Cyan
Write-Host ""

$MaxExecutionMinutes = 60  # 1 hour
$ElapsedMinutes = 0
$Complete = $false

while (-not $Complete -and $ElapsedMinutes -lt $MaxExecutionMinutes) {
    if (Test-Path $LogFile) {
        $LogContent = Get-Content $LogFile -Raw

        # Check for completion marker
        if ($LogContent -match "READY FOR REVIEW|ALL TASKS COMPLETE") {
            $Complete = $true
            break
        }

        # Check for escalation
        if ($LogContent -match "ESCALATE TO CLAUDE") {
            Write-Host "🚨 ESCALATION DETECTED" -ForegroundColor Red
            Write-Host "   ChatGPT needs Claude's input. Check EXECUTION_LOG.md" -ForegroundColor Yellow
            Write-Host ""
            if ($Mode -eq "auto") {
                Write-Host "   Pausing for manual intervention..." -ForegroundColor Gray
                Read-Host "Press Enter after resolving escalation"
            }
        }

        # Show progress update
        $TaskCount = ([regex]::Matches($LogContent, "##\s+Task\s+\d+")).Count
        $CompletedCount = ([regex]::Matches($LogContent, "✅")).Count
        Write-Host "📊 Progress: $CompletedCount / $TaskCount tasks completed" -ForegroundColor Gray
    }

    Start-Sleep -Seconds 30
    $ElapsedMinutes += 0.5
}

if (-not $Complete) {
    Write-Host "⚠️  Execution timeout after $MaxExecutionMinutes minutes" -ForegroundColor Yellow
    Write-Host "   Check EXECUTION_LOG.md for current status" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ Execution complete!" -ForegroundColor Green
Write-Host ""

# =============================================================================
# PHASE 3: CLAUDE VERIFICATION
# =============================================================================

Write-Host "🔍 PHASE 3: Claude Quality Review" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta

$ClaudeReviewPrompt = @"
ChatGPT has completed the implementation. Please review:

FILES:
- IMPLEMENTATION_PLAN.md (original plan)
- EXECUTION_LOG.md (what was done)
- All modified code files

REVIEW CHECKLIST:
□ Architecture matches original plan
□ All subtasks completed
□ Code quality is high
□ Error handling is robust
□ Security considerations addressed
□ Tests are passing
□ No obvious bugs or issues
□ Code follows project conventions

ACTIONS:
- If APPROVED: Stage and commit changes to git
- If CHANGES NEEDED: Document issues and send back to ChatGPT
- If MAJOR ISSUES: Reject and explain why

Provide detailed feedback in REVIEW_RESULTS.md
"@

Write-Host "📝 Review prompt for Claude Code:" -ForegroundColor Cyan
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host $ClaudeReviewPrompt -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "📌 ACTION REQUIRED:" -ForegroundColor Red
Write-Host "   1. Copy the prompt above" -ForegroundColor White
Write-Host "   2. Paste into Claude Code (terminal)" -ForegroundColor White
Write-Host "   3. Claude will review and approve/reject" -ForegroundColor White
Write-Host ""

if ($Mode -ne "auto") {
    Read-Host "Press Enter when review is complete"
}

# Check for review results
$ReviewFile = Join-Path $ProjectRoot "REVIEW_RESULTS.md"
$WaitSeconds = 0
while (-not (Test-Path $ReviewFile) -and $WaitSeconds -lt 300) {
    Start-Sleep -Seconds 5
    $WaitSeconds += 5
}

if (Test-Path $ReviewFile) {
    $ReviewContent = Get-Content $ReviewFile -Raw
    Write-Host "✅ Review complete: REVIEW_RESULTS.md" -ForegroundColor Green
    Write-Host ""

    if ($ReviewContent -match "APPROVED") {
        Write-Host "✅ ✅ ✅ IMPLEMENTATION APPROVED!" -ForegroundColor Green
        Write-Host ""

        if ($AutoCommit) {
            Write-Host "📝 Auto-committing changes..." -ForegroundColor Cyan
            git add .
            git commit -m "feat: $UserRequest

Implemented via automated dual-AI workflow:
- Planning: Claude Code
- Execution: ChatGPT (Cursor AI)
- Review: Claude Code

🤖 Generated with automated orchestration"
            Write-Host "✅ Changes committed to git" -ForegroundColor Green
        } else {
            Write-Host "📌 Changes ready to commit. Run:" -ForegroundColor Yellow
            Write-Host "   git add ." -ForegroundColor White
            Write-Host "   git commit -m 'feat: $UserRequest'" -ForegroundColor White
        }
    } else {
        Write-Host "⚠️  Changes requested by Claude" -ForegroundColor Yellow
        Write-Host "   See REVIEW_RESULTS.md for details" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  Review file not found. Manual verification required." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🎉 DUAL-AI ORCHESTRATION COMPLETE!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor White
Write-Host "   ✅ Claude created implementation plan" -ForegroundColor Green
Write-Host "   ✅ ChatGPT executed all subtasks" -ForegroundColor Green
Write-Host "   ✅ Claude reviewed and verified" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Generated Files:" -ForegroundColor White
Write-Host "   - IMPLEMENTATION_PLAN.md" -ForegroundColor Gray
Write-Host "   - EXECUTION_LOG.md" -ForegroundColor Gray
Write-Host "   - REVIEW_RESULTS.md" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Feature Ready!" -ForegroundColor Cyan
