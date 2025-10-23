# Automated Dual-AI Workflow Rules
## Claude = Planning | ChatGPT (Cursor AI) = Execution

**Last Updated:** October 22, 2025
**Status:** ACTIVE - Automatic Task Routing Enabled

---

## 🎯 AUTOMATIC LABOR DIVISION

### Claude Code (CLI) - High-Level Planner
**Responsibilities:**
- Architecture design and planning
- Breaking down complex tasks into subtasks
- Technical decision making
- Security and quality reviews
- Git operations and deployment
- Final integration verification

**Never does:**
- Direct code implementation (delegates to ChatGPT)
- Repetitive coding tasks
- UI component creation

### ChatGPT (Cursor AI) - Code Executor
**Responsibilities:**
- Code implementation from plans
- Logic checking and validation
- Error correction and debugging
- Running tests and builds
- Refactoring and optimization
- Documentation generation

**Never does:**
- High-level architecture decisions (asks Claude)
- Breaking down complex tasks (receives from Claude)
- Final security reviews (delegates to Claude)

---

## 🔄 AUTOMATIC WORKFLOW

### Phase 1: Planning (Claude)
1. User describes high-level goal
2. Claude analyzes and creates plan
3. Claude breaks into implementation subtasks
4. Claude generates detailed specs for each subtask
5. Claude outputs `IMPLEMENTATION_PLAN.md`

### Phase 2: Execution (ChatGPT via Cursor)
1. Cursor AI reads `IMPLEMENTATION_PLAN.md`
2. Implements each subtask sequentially
3. Runs tests after each implementation
4. Fixes errors automatically
5. Updates `EXECUTION_LOG.md` with progress

### Phase 3: Verification (Claude)
1. Claude reviews all implemented code
2. Checks for security issues
3. Validates architecture compliance
4. Approves or requests changes
5. Commits to git if approved

---

## 📋 TASK ROUTING TABLE

| Task Type | Handler | Auto-Route Rule |
|-----------|---------|-----------------|
| "Design..." | Claude | Keyword: design, architecture, plan |
| "Implement..." | ChatGPT | Keyword: implement, create, build |
| "Fix error..." | ChatGPT | Keyword: fix, debug, error |
| "Review..." | Claude | Keyword: review, verify, check |
| "Refactor..." | ChatGPT | Keyword: refactor, optimize |
| "Deploy..." | Claude | Keyword: deploy, release |

---

## 🤖 CURSOR AI INSTRUCTIONS

When you (Cursor AI / ChatGPT) receive a task:

### Check for Planning Phase:
```
IF IMPLEMENTATION_PLAN.md exists:
  → Read plan
  → Follow specs exactly
  → Implement step by step

ELSE IF task is complex:
  → Stop
  → Respond: "This requires Claude's planning first. Please ask Claude Code to create an implementation plan."

ELSE IF task is simple (< 50 lines):
  → Implement directly
  → Run tests
  → Fix errors
```

### Your Implementation Loop:
```
1. Read next subtask from IMPLEMENTATION_PLAN.md
2. Implement the code
3. Run relevant tests (npm test or pytest)
4. IF tests fail:
   → Analyze error
   → Fix code
   → Re-run tests
   → Repeat until passing
5. Update EXECUTION_LOG.md
6. Move to next subtask
```

### When to Escalate to Claude:
```
ESCALATE IF:
- Architecture decision needed
- Security concern discovered
- Plan is unclear or incomplete
- Breaking change required
- Multiple approaches possible (need design decision)

DO NOT ESCALATE FOR:
- Syntax errors (fix them)
- Test failures (debug and fix)
- Import/dependency issues (resolve them)
- Typing errors (correct them)
```

---

## 📁 AUTOMATION FILES

### IMPLEMENTATION_PLAN.md (Created by Claude)
```markdown
# Implementation Plan: [Feature Name]

## Overview
[High-level description]

## Architecture Decisions
- [Decision 1]
- [Decision 2]

## Subtasks
### Task 1: [Name]
**File:** path/to/file.ts
**Spec:**
- [Detailed requirement 1]
- [Detailed requirement 2]

**Tests Required:**
- [Test description]

**Acceptance Criteria:**
- [Criteria 1]
- [Criteria 2]

### Task 2: [Name]
...
```

### EXECUTION_LOG.md (Updated by ChatGPT)
```markdown
# Execution Log: [Feature Name]

## Task 1: [Name]
**Status:** ✅ Complete
**Time:** 10:30 AM - 10:45 AM (15 min)
**Tests:** All passing
**Issues:** None
**Code:** `frontend/components/Feature.tsx`

## Task 2: [Name]
**Status:** 🟡 In Progress
**Started:** 10:45 AM
**Current Step:** Implementing logic
...
```

---

## 🎯 EXAMPLE AUTOMATED WORKFLOW

### User Request:
```
"Add real-time Greeks calculation to the options chain display"
```

### Phase 1: Claude Planning (Automatic)
```markdown
Claude analyzes and creates IMPLEMENTATION_PLAN.md:

# Implementation Plan: Real-Time Greeks Display

## Architecture
- Backend: New `/api/greeks/{symbol}` endpoint
- Frontend: Update OptionsChain component
- Uses Black-Scholes model for calculations

## Subtasks

### Task 1: Backend API Endpoint
**File:** backend/app/routers/market.py
**Spec:**
- Add GET endpoint `/api/greeks/{symbol}`
- Calculate delta, gamma, theta, vega
- Use Black-Scholes model
- Return JSON with Greeks data
**Tests:** Test with AAPL symbol
**Acceptance:** Returns valid Greeks in < 500ms

### Task 2: Frontend API Client
**File:** frontend/lib/apiClient.ts
**Spec:**
- Add `fetchGreeks(symbol: string)` function
- Use proxy route `/api/proxy/greeks`
- Type return value as GreeksData
**Tests:** Mock API call test
**Acceptance:** TypeScript compiles, test passes

### Task 3: Update OptionsChain Component
**File:** frontend/components/trading/OptionsChain.tsx
**Spec:**
- Add Greeks columns (delta, gamma, theta, vega)
- Fetch Greeks on symbol load
- Display with 4 decimal precision
- Show loading state
**Tests:** Component renders with Greeks
**Acceptance:** Visual QA confirms display

### Task 4: Add TypeScript Types
**File:** frontend/types/greeks.ts
**Spec:**
- Define GreeksData interface
- Export from types/index.ts
**Tests:** TypeScript compilation
**Acceptance:** No type errors
```

### Phase 2: ChatGPT Execution (Automatic)

**Cursor AI receives notification:**
```
"IMPLEMENTATION_PLAN.md created. Beginning execution..."
```

**Cursor AI implements Task 1:**
```python
# backend/app/routers/market.py
# (ChatGPT writes code)

@router.get("/greeks/{symbol}")
async def get_greeks(symbol: str):
    # ... implementation
```

**Cursor AI runs tests:**
```bash
pytest backend/tests/test_market.py::test_greeks
# If fails: Fix and re-run
# If passes: Continue
```

**Updates EXECUTION_LOG.md:**
```markdown
## Task 1: Backend API Endpoint
✅ Complete (15 min)
Tests: All passing
Code: backend/app/routers/market.py (lines 45-78)
```

**Continues through Task 2, 3, 4...**

### Phase 3: Claude Verification (Automatic)

**Claude reviews when EXECUTION_LOG shows "All Complete":**
```bash
# Claude Code runs:
- Security review of new endpoint
- Validates Black-Scholes implementation
- Checks error handling
- Reviews TypeScript types
- Tests integration manually

# If approved:
git add .
git commit -m "feat: add real-time Greeks calculation..."
```

---

## 🚀 ENABLING AUTOMATION

### Step 1: Create Automation Files

Create these in project root:
- `.cursor/rules/dual-ai-automation.md` (this file)
- `.cursor/workflows/planning-template.md`
- `.cursor/workflows/execution-template.md`

### Step 2: Configure Cursor AI

Add to `.cursor/settings.json`:
```json
{
  "cursor.ai.rules": [
    ".cursor/rules/dual-ai-automation.md"
  ],
  "cursor.ai.autoExecute": true,
  "cursor.ai.watchFiles": [
    "IMPLEMENTATION_PLAN.md"
  ]
}
```

### Step 3: Configure Claude Code

Claude Code will automatically:
- Create IMPLEMENTATION_PLAN.md for complex tasks
- Monitor EXECUTION_LOG.md for completion
- Review code when execution finishes

---

## 📊 AUTOMATION TRIGGERS

### Cursor AI Auto-Starts When:
- `IMPLEMENTATION_PLAN.md` is created/updated
- File contains "READY FOR EXECUTION"
- All subtasks have specs

### Cursor AI Auto-Pauses When:
- Encounters "ESCALATE TO CLAUDE" marker
- Subtask marked "REQUIRES DESIGN DECISION"
- Tests fail 3 times consecutively

### Claude Code Auto-Reviews When:
- `EXECUTION_LOG.md` shows "ALL TASKS COMPLETE"
- File contains "READY FOR REVIEW"
- All tests passing

---

## 🎓 TRAINING THE WORKFLOW

### Week 1: Semi-Automatic
- Claude creates plans manually
- ChatGPT implements with reminders
- Manual handoffs

### Week 2: Mostly Automatic
- Plans trigger execution automatically
- ChatGPT runs full implementation loop
- Claude reviews on completion signal

### Week 3: Fully Automatic
- Single user request triggers full pipeline
- Minimal human intervention
- Human only for approvals

---

## 🔧 CUSTOMIZATION

### Adjust Automation Level

**Conservative (Safe):**
```json
{
  "cursor.ai.autoExecute": false,  // Manual start
  "cursor.ai.requireApproval": true  // Confirm each step
}
```

**Aggressive (Fast):**
```json
{
  "cursor.ai.autoExecute": true,  // Auto start
  "cursor.ai.requireApproval": false,  // No confirmations
  "cursor.ai.autoDeploy": false  // Still manual deploy
}
```

---

## ✅ SUCCESS METRICS

### Workflow is Working When:
- ✅ Plans complete in < 5 minutes
- ✅ 80%+ of implementations succeed without escalation
- ✅ Tests pass on first or second try
- ✅ Minimal manual intervention
- ✅ Code quality maintained
- ✅ Development speed 2-3x faster

---

## 🚨 SAFETY GUARDRAILS

### Always Manual (Never Automate):
- ❌ Git push to main branch
- ❌ Production deployments
- ❌ Database migrations
- ❌ Breaking API changes
- ❌ Security-sensitive code
- ❌ Billing/payment logic

### Require Claude Review:
- ⚠️ Authentication/authorization
- ⚠️ Data validation
- ⚠️ API integrations
- ⚠️ State management
- ⚠️ Error handling

---

**This rule file enables automatic coordination between Claude (planner) and ChatGPT (executor). Cursor AI will follow these rules when processing tasks.**
