# PaiiD Agent Protocol
# Permanent Zombie Process Elimination Protocol

This document defines **permanent behavioral rules** for AI agents (Claude Code) and users when working with the PaiiD codebase.

**Purpose**: Eliminate zombie processes forever through multi-layer automation and protocol enforcement.

---

## 🤖 AGENT (CLAUDE) PERMANENT RULES

These rules are **MANDATORY** for all AI agents working with this codebase. They apply automatically across all sessions.

### Rule 1: Pre-Work Cleanup

**BEFORE starting ANY background process**, agents MUST run cleanup:

```powershell
.\scripts\agent-cleanup.ps1 -Force
```

**When to apply**:
- Before `npm run dev` (frontend)
- Before `python -m uvicorn` (backend)
- Before `pytest` (tests)
- Before ANY long-running bash command
- After detecting zombie process warnings

**Why**: Prevents accumulation of stale processes that cause port conflicts and stale code.

### Rule 2: Process Termination

When starting a **temporary background process** for diagnostics:

1. Use `run_in_background=true` parameter in Bash tool
2. Monitor with `BashOutput` tool
3. Kill with `KillShell` tool when done
4. **NEVER** let diagnostic processes run indefinitely

**Example**:
```python
# ✅ CORRECT
Bash(command="curl http://localhost:8001/health", run_in_background=true)
# ... check output ...
KillShell(shell_id="abc123")

# ❌ INCORRECT - leaves zombie
Bash(command="curl http://localhost:8001/health", run_in_background=true)
# ... never killed
```

### Rule 3: Status Checks

Before claiming "servers are running", agents MUST verify using status script:

```powershell
.\scripts\status.ps1
```

**NEVER assume** processes are running. Always verify.

### Rule 4: Error Detection

If encountering ANY of these symptoms:
- Port already in use (3000, 3001, 8001, 8002)
- `EADDRINUSE` errors
- Stale dev server (started hours ago)
- More than 5 PaiiD-related processes

**IMMEDIATELY** run cleanup:
```powershell
.\scripts\agent-cleanup.ps1 -Verbose
```

### Rule 5: Session Handoff

At the end of EVERY session, agents SHOULD recommend:

```
"Run `.\scripts\status.ps1` to check process status"
"Use `.\scripts\stop-dev.ps1` to cleanly stop servers"
```

---

## 👤 USER WORKFLOW (RECOMMENDED)

### Daily Startup

```powershell
# Clean start every time
.\scripts\start-dev.ps1
```

This script:
1. Kills all zombie processes
2. Clears Next.js cache
3. Starts backend on port 8001
4. Starts frontend on port 3001
5. Waits for health checks

### Daily Shutdown

```powershell
# Clean stop
.\scripts\stop-dev.ps1
```

### Check Status

```powershell
# See what's running
.\scripts\status.ps1
```

### Emergency Cleanup

```powershell
# Nuclear option - kill everything
.\scripts\agent-cleanup.ps1 -Verbose
```

---

## 🔧 VS CODE INTEGRATION

Four keyboard-accessible tasks:

- **🧹 Kill All Zombies** - Run cleanup script
- **🚀 Start Dev (Clean)** - Clean startup
- **🛑 Stop Dev Servers** - Graceful shutdown
- **📊 Show Status** - Diagnostic report

Access via:
1. `Ctrl+Shift+P` → "Tasks: Run Task"
2. Select task from list

---

## 🪝 GIT HOOKS (AUTOMATIC)

### Pre-Commit Hook

**Triggers**: Before `git commit`

**Action**: Runs `agent-cleanup.ps1 -Force`

**Why**: Ensures no zombie processes are committed alongside code changes.

### Post-Checkout Hook

**Triggers**: After `git checkout` (branch switch)

**Action**: Runs `agent-cleanup.ps1 -Force`

**Why**: Provides clean slate when switching branches (prevents cross-branch contamination).

---

## 📊 DIAGNOSTICS

### Identifying Zombies

**Symptoms**:
- Port conflicts (`EADDRINUSE`)
- Stale code running (recent changes not reflected)
- Dev server started hours ago
- 10+ node.exe or python.exe processes

**Diagnosis**:
```powershell
# See ALL PaiiD processes
.\scripts\status.ps1

# Detailed process list
Get-Process | Where-Object { $_.Path -like "*PaiiD*" }
```

### Root Cause

**Why zombies form**:
1. Background bash shells created during debugging
2. `Ctrl+C` doesn't kill child processes in PowerShell
3. Multiple frontend dev servers on different ports
4. pytest runners left hanging
5. curl health checks running in background

**Solution**: Permanent protocol (this document)

---

## 🚨 EMERGENCY PROCEDURES

### Scenario 1: Port 8001 In Use

```powershell
# Find process
Get-NetTCPConnection -LocalPort 8001 | Select-Object OwningProcess

# Kill it
Stop-Process -Id <PID> -Force

# Or use cleanup script
.\scripts\agent-cleanup.ps1 -Force
```

### Scenario 2: Frontend Won't Start

```powershell
# Clear Next.js cache
Remove-Item -Recurse -Force frontend\.next

# Kill all node processes
.\scripts\agent-cleanup.ps1 -Force

# Start fresh
.\scripts\start-dev.ps1
```

### Scenario 3: 20+ Zombie Processes

```powershell
# Nuclear cleanup
.\scripts\agent-cleanup.ps1 -Verbose -Force

# Verify
.\scripts\status.ps1
```

---

## 📝 FILE REFERENCE

### Automation Scripts

| File | Purpose | Usage |
|------|---------|-------|
| `scripts/agent-cleanup.ps1` | Kill all PaiiD zombie processes | `.\scripts\agent-cleanup.ps1 -Force` |
| `scripts/start-dev.ps1` | Clean startup (backend + frontend) | `.\scripts\start-dev.ps1` |
| `scripts/stop-dev.ps1` | Graceful shutdown | `.\scripts\stop-dev.ps1` |
| `scripts/status.ps1` | Diagnostic report | `.\scripts\status.ps1` |

### VS Code Tasks

| Task | Shortcut | Function |
|------|----------|----------|
| 🧹 Kill All Zombies | Ctrl+Shift+P → Run Task | Run cleanup |
| 🚀 Start Dev (Clean) | Ctrl+Shift+P → Run Task | Clean startup |
| 🛑 Stop Dev Servers | Ctrl+Shift+P → Run Task | Stop servers |
| 📊 Show Status | Ctrl+Shift+P → Run Task | Show diagnostics |

### Git Hooks

| Hook | Trigger | Action |
|------|---------|--------|
| `.git/hooks/pre-commit` | Before commit | Run cleanup |
| `.git/hooks/post-checkout` | After branch switch | Run cleanup |

---

## ✅ SUCCESS CRITERIA

**Protocol is working when**:

1. **Zero zombie processes** between coding sessions
2. **Clean startup every time** - no port conflicts
3. **Fresh code always running** - no stale dev servers
4. **Predictable state** - status.ps1 shows 0-2 processes
5. **No manual process killing** - automation handles it

---

## 🔄 VERSION HISTORY

- **v1.0** (2025-10-27): Initial protocol established
  - Created 4 automation scripts
  - Added 4 VS Code tasks
  - Installed 2 git hooks
  - Documented agent rules

---

## 📖 REFERENCES

- **Scripts**: `scripts/` directory
- **VS Code Config**: `.vscode/tasks.json`
- **Git Hooks**: `.git/hooks/` directory
- **Project Docs**: `CLAUDE.md`, `README.md`

---

**END OF PERMANENT PROTOCOL**

This document is the source of truth for zombie process management. All agents and users should follow this protocol automatically.
