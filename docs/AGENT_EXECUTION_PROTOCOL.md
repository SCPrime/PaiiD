# Agent Execution Protocol - PaiiD Trading Platform

**Version**: 1.0 (Post-MOD SQUAD)
**Date**: 2025-10-27
**Purpose**: Establish permanent, universal guidelines for ALL agents (Claude Code) AND developers

## CRITICAL: Gibraltar-Level Honesty Requirement

**PRIMARY DIRECTIVE**: "Do not report 100% if it's not utterly, exhaustively confirmed that 100% has been diligently checked and delivered to full purpose and execution."

### Honesty Standards

1. **NEVER claim "completed" without exhaustive verification**
2. **ALWAYS acknowledge gaps, incomplete items, or discovered issues**
3. **PREFER conservative language**: "mostly complete" over "100% complete"
4. **INCLUDE explicit "NOT INCLUDED" sections in commits when scope is limited**
5. **VERIFY immediately after changes**: Don't defer verification to later

### Examples of Honest vs Dishonest Reporting

**❌ DISHONEST (Premature Claims)**:
```
Phase 3 COMPLETED ✅
- Removed monitoring module
- All references cleaned up
```

**✅ HONEST (Accurate Status)**:
```
Phase 3 MOSTLY COMPLETED (with verification gaps)
- Removed monitoring module import at line 43 ✅
- Deleted monitoring/monitor.py file ✅
- WARNING: Router registration at line 700 NOT VERIFIED
- Next: Run pytest --collect-only to verify no import errors
```

## Phase-Based Execution Framework

### Phase 1: Analysis & Planning

**Inputs**: User request, codebase state, problem description

**Required Deliverables**:
1. **Scope Definition**: Exactly what WILL and WILL NOT be done
2. **Risk Assessment**: Potential breaking changes, side effects
3. **Verification Plan**: How will success be confirmed?
4. **Commit Strategy**: How many commits? What's in each?

**Analysis Checklist**:
- [ ] Read all relevant files BEFORE proposing changes
- [ ] Search for ALL occurrences of items being modified/removed
- [ ] Identify dependent code that might break
- [ ] Establish baseline (test status, startup behavior)
- [ ] Define "done" criteria explicitly

**Anti-Pattern**: Starting to code without completing analysis

**Example**:
```markdown
## Phase 1: Analysis Complete

**Scope**: Remove deprecated monitoring module
**Files to modify**:
- backend/app/main.py (line 43 import + line 700 router registration)
- backend/app/routers/monitoring/monitor.py (DELETE)

**Search Results**:
- `grep -r "monitoring" backend/app/` shows 2 references
- Import at main.py:43
- Router registration at main.py:700

**Verification Plan**:
1. Run `pytest --collect-only` to verify imports work
2. Run `grep -r "monitoring\.router" backend/` to confirm zero matches
3. Start backend to confirm no import errors

**Commit Strategy**: Single commit with immediate verification
```

### Phase 2: Implementation

**Before ANY code changes**:
1. Re-read files to be modified (even if read in Phase 1)
2. Copy EXACT old code that will be replaced
3. Write EXACT new code (no placeholders, no "...")
4. Predict side effects

**Implementation Checklist**:
- [ ] Make single-purpose changes (one logical change per commit)
- [ ] Use precise line numbers when editing
- [ ] Verify syntax immediately after edits
- [ ] NO placeholders or TODOs in production code
- [ ] Add explanatory comments for non-obvious changes

**Anti-Pattern**: Making multiple unrelated changes in one commit

**Example**:
```python
# ❌ BAD: Multi-purpose commit
# In one commit: Remove monitoring, add logging, refactor auth

# ✅ GOOD: Single-purpose commits
# Commit 1: Remove monitoring module (just monitoring)
# Commit 2: Add logging to health endpoint (just logging)
# Commit 3: Refactor auth (just auth)
```

### Phase 3: Verification

**Verification is MANDATORY before marking any task as complete.**

**Verification Checklist**:
- [ ] Run applicable tests (unit, integration, E2E)
- [ ] Verify imports/collection (`pytest --collect-only`)
- [ ] Check for unintended side effects (grep for removed items)
- [ ] Start application to confirm no runtime errors
- [ ] Review git diff for unintended changes

**Verification Failures Require**:
1. Document the failure honestly
2. Fix the issue
3. Re-verify
4. Update status to reflect current state

**Anti-Pattern**: Deferring verification to "later" or "after other changes"

**Example**:
```bash
# Phase 3: Verification (MANDATORY)

# Step 1: Verify imports work
cd backend && python -m pytest --collect-only -q
# Result: ❌ FAILED - NameError: name 'monitoring' is not defined
# Analysis: Router registration at line 700 still exists!

# Step 2: Fix issue
# (Edit main.py to remove router registration)

# Step 3: Re-verify
cd backend && python -m pytest --collect-only -q
# Result: ✅ SUCCESS - 250 tests collected

# Step 4: Additional verification
grep -r "monitoring\.router" backend/app/
# Result: ✅ No matches found
```

### Phase 4: Documentation & Commit

**Commit Message Standards**:

**Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Required Elements**:
1. **Type**: fix, feat, refactor, docs, test, chore
2. **Scope**: Module or feature affected
3. **Subject**: Concise summary (50 chars max)
4. **Body**:
   - What was changed (specific files/lines)
   - Why it was changed
   - Impact/side effects
   - Verification results
   - **Explicit "NOT INCLUDED" section if scope limited**
5. **Footer**:
   - Breaking changes (if any)
   - Related issues/PRs
   - Claude Code attribution

**Anti-Pattern**: Vague commit messages like "fix bugs" or "update files"

**Example**:
```
fix(main): Remove orphaned monitoring.router registration (MOD SQUAD Phase 3 cleanup)

CRITICAL BUG FIX: Phase 3 incomplete cleanup discovered
- Removed monitoring module import at line 43 ✅
- MISSED monitoring.router registration at line 700 ❌ (blocking ALL tests)
- Tests failed with: NameError: name 'monitoring' is not defined

Impact:
- Backend test suite completely blocked (conftest.py imports app.main)
- pytest --co -q fails immediately on import
- Zero tests could run until this fix

Resolution:
- backend/app/main.py lines 696-700: Removed monitoring.router registration
- Added explanatory comment documenting Phase 3 deprecation
- Verified no other monitoring references remain in main.py

Verification:
✅ pytest --collect-only succeeds (250 tests collected)
✅ grep -r "monitoring\.router" returns no matches
✅ Backend starts without import errors

Accountability Note:
This validates user's critical feedback: "please do not report 100% if its not
utterly, exhaustively confirmed that 100% has been diligently checked and
delivered to full purpose and execution"

Commit 09f189f claimed "Phase 3 COMPLETED" but missed this critical cleanup.
Gibraltar-level honesty requires exhaustive verification, not premature claims.

Lesson: Single-purpose commits with immediate test verification prevent gaps.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Search & Replace Best Practices

### Before Removing ANY Code

**Exhaustive Search Protocol**:

```bash
# 1. Search for direct references
grep -r "exact_name" backend/app/

# 2. Search for module imports
grep -r "from.*exact_name" backend/app/
grep -r "import.*exact_name" backend/app/

# 3. Search for router registrations
grep -r "exact_name\.router" backend/app/

# 4. Search for usage in configs
grep -r "exact_name" backend/ --include="*.yml" --include="*.yaml" --include="*.json"

# 5. Search in documentation
grep -r "exact_name" docs/

# 6. Search in tests
grep -r "exact_name" backend/tests/
```

**Anti-Pattern**: Only searching for imports, missing router registrations

### After Removing Code

**Verification Search Protocol**:

```bash
# Verify zero matches for all patterns
grep -r "removed_name" backend/app/
# Expected: No matches

grep -r "removed_name\.router" backend/app/
# Expected: No matches
```

## Testing Requirements

### Test Execution Hierarchy

**Level 1: Import Verification** (FASTEST - Run FIRST)
```bash
cd backend && python -m pytest --collect-only -q
# Purpose: Verify no import errors block test loading
# Time: <5 seconds
# When: After ANY import changes, module deletions, or router modifications
```

**Level 2: Quick Smoke Tests** (FAST - Run SECOND)
```bash
cd backend && python -m pytest tests/test_health.py tests/test_imports.py -v
# Purpose: Verify basic functionality
# Time: <30 seconds
# When: After configuration changes or core module modifications
```

**Level 3: Unit Tests** (MEDIUM - Run BEFORE COMMIT)
```bash
cd backend && python -m pytest tests/unit/ -v
# Purpose: Verify module-level functionality
# Time: 1-2 minutes
# When: After code changes to specific modules
```

**Level 4: Full Test Suite** (SLOW - Run in CI)
```bash
cd backend && python -m pytest tests/ -v
# Purpose: Comprehensive validation
# Time: 3-5 minutes
# When: In GitHub Actions on push/PR, or before major releases
```

**Anti-Pattern**: Only running full suite (wastes time on trivial changes)

### Test Baseline Honesty

**NEVER claim test improvements without baseline comparison**:

```markdown
# ❌ BAD (No Baseline)
All tests passing ✅

# ✅ GOOD (With Baseline)
Test Status After Changes:
- Baseline: 150/250 tests passing (60% - commit abc123)
- Current: 150/250 tests passing (60% - no change)
- New failures: 0
- Fixed failures: 0
- Conclusion: Changes DID NOT BREAK existing tests ✅
```

## Error Handling Standards

### When Things Go Wrong

1. **STOP immediately** - Don't continue with broken state
2. **Document the failure** - Exact error message, file, line
3. **Analyze root cause** - Why did it fail?
4. **Fix OR rollback** - Don't leave broken code
5. **Re-verify** - Confirm fix worked
6. **Update status** - Reflect current reality

**Anti-Pattern**: Ignoring test failures as "pre-existing issues"

### Error Reporting Template

```markdown
## Error Discovered: [Brief Description]

**When**: During [phase/action]
**Where**: [File:line or command]
**Error**:
```
[Exact error message]
```

**Root Cause**: [Analysis of why it failed]

**Impact**:
- [ ] Blocks current work
- [ ] Breaks existing functionality
- [ ] Prevents testing
- [ ] Documentation issue only

**Resolution**:
1. [Step 1]
2. [Step 2]
3. [Verification command/result]

**Status**:
- [ ] Fixed and verified
- [ ] Requires user decision
- [ ] Deferred (with reason)
```

## Multi-Agent Coordination

### When User Requests Multiple Agents

**Rule**: Each agent MUST have single, well-defined scope

**Bad Example**:
```
Agent 1: "Fix everything in Phase 3, 4, and 5"
# Problem: Too broad, unclear boundaries, high risk of conflicts
```

**Good Example**:
```
Agent 1 (Phase 3): Remove monitoring module
  - Delete monitoring/monitor.py
  - Remove import from main.py:43
  - Remove router registration from main.py:700
  - Verify: pytest --collect-only succeeds

Agent 2 (Phase 4): Add Tradier session lock
  - Add asyncio.Lock to TradierStream class
  - Wrap _create_session with lock
  - Verify: No session creation race conditions

Agent 3 (Phase 5): Create readiness registry
  - Implement ReadinessRegistry class
  - Integrate with news.py
  - Add /health/features endpoint
  - Verify: Registry tracks service availability
```

### Agent Handoff Protocol

**Before Completing**:
1. Document EXACTLY what was done
2. Document what was NOT done
3. List any discovered issues for next agent
4. Provide verification commands
5. State current system status

**Example Handoff**:
```markdown
## Agent 1 Completion Report

**Completed**:
- Phase 3: Monitoring module removed (commit abc123)
- All import references cleaned up
- Tests verified: pytest --collect-only succeeds

**NOT Completed** (Next Agent):
- Phase 4: Tradier session lock (NOT STARTED)
- Phase 5: Readiness registry (NOT STARTED)

**Discovered Issues**:
- 40+ unit test failures (PRE-EXISTING, not caused by Phase 3)
- Database connection pool warnings in logs (out of scope)

**Current System Status**:
- Backend starts without errors ✅
- Tests can be collected ✅
- Many tests fail (pre-existing) ⚠️

**Verification Commands**:
```bash
# Verify monitoring fully removed
grep -r "monitoring" backend/app/
# Expected: No matches

# Verify tests can run
cd backend && pytest --collect-only -q
# Expected: 250 tests collected
```

**Handoff to**: Agent 2 (Phase 4)
```

## Commit Hygiene

### What Belongs in Version Control

**✅ COMMIT**:
- Source code (`.py`, `.ts`, `.tsx`)
- Configuration files (`.yml`, `.json`, `.env.example`)
- Documentation (`.md`)
- Tests (`test_*.py`, `*.test.ts`)
- Lock files (`requirements.txt`, `package-lock.json`)

**❌ DO NOT COMMIT**:
- Test result files (`pytest-report.xml`, `*.log`)
- Generated files (`.pyc`, `__pycache__/`, `.next/`)
- Environment secrets (`.env`, `.env.local`)
- IDE files (`.vscode/`, `.idea/`)
- Build artifacts (`dist/`, `build/`, `htmlcov/`)

### .gitignore Compliance

**Before ANY commit**:
```bash
# Check what will be committed
git status

# Verify no ignored files are staged
git ls-files --others --ignored --exclude-standard

# If unwanted files appear:
git reset HEAD <file>
```

## Universal Applicability

**This protocol applies to**:
1. Claude Code agents (primary audience)
2. Human developers
3. Automated scripts
4. CI/CD pipelines
5. Code review processes

**Enforcement**:
- Pre-commit hooks verify protocol compliance
- GitHub Actions enforce testing requirements
- Code reviews check for Gibraltar-level honesty
- Post-mortems analyze protocol adherence

## Exceptions & Edge Cases

### When to Deviate from Protocol

**ONLY under these conditions**:
1. **Emergency hotfix** - Production down, immediate fix needed
   - Still document what was skipped
   - Still verify afterward
   - Still create post-mortem

2. **User explicitly requests deviation** - "Skip tests and just commit"
   - Document user request in commit message
   - Warn about risks
   - Still run basic verification

3. **Experimental branch** - POC or spike work
   - Mark branch as experimental
   - Still follow commit message standards
   - Don't merge to main without full protocol

**Anti-Pattern**: Assuming "it's a small change" means you can skip verification

## Accountability Measures

### Pre-Commit Checklist

Before EVERY commit, verify:
- [ ] Code changes are single-purpose
- [ ] All TODOs are resolved (or explicitly documented)
- [ ] Verification commands have been run
- [ ] Git diff shows only intended changes
- [ ] Commit message follows template
- [ ] No sensitive data in changes

### Post-Commit Checklist

After EVERY commit, verify:
- [ ] Tests still pass (or baseline maintained)
- [ ] Backend still starts (if backend changed)
- [ ] Frontend still builds (if frontend changed)
- [ ] Documentation is up to date

### Post-Phase Checklist

After completing ANY phase:
- [ ] Create honest status report
- [ ] Document gaps/issues discovered
- [ ] Update project documentation
- [ ] Verify handoff to next phase is clear

## References

- **Test Baseline**: `backend/TEST_BASELINE_MOD_SQUAD.md`
- **MOD SQUAD Commits**: 6c97cc3, 09f189f, 0b08385, d4d7d8f, 415bfc6
- **CI Workflow**: `.github/workflows/backend-tests.yml`
- **User Feedback**: "Please do not report 100% if its not utterly, exhaustively confirmed..."

---

**Remember**: This protocol exists because of discovered gaps in MOD SQUAD execution. Every guideline here addresses a real failure mode. Gibraltar-level honesty is not optional - it's the foundation of reliable software development.

**Version History**:
- 1.0 (2025-10-27): Initial version post-MOD SQUAD, based on lessons learned from monitoring.router bug
