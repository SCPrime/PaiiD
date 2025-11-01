# Rollback Procedures - PaiiD Mod Squad System

**Version:** 2.0
**Last Updated:** October 31, 2025
**Purpose:** Comprehensive rollback documentation for automatic, manual, and CLI-based restoration of files modified by Mod Squad batch operations.

---

## Table of Contents

1. [Overview](#overview)
2. [Automatic Rollback](#automatic-rollback)
3. [Manual Rollback](#manual-rollback)
4. [CLI Rollback (Future)](#cli-rollback-future)
5. [Prevention Best Practices](#prevention-best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Backup Directory Structure](#backup-directory-structure)
8. [Integration with Git Workflow](#integration-with-git-workflow)

---

## Overview

### What is Rollback?

Rollback is the process of restoring files to their pre-modification state after a batch operation fails validation or produces unexpected results. The Mod Squad system provides three levels of rollback protection:

1. **Automatic Rollback**: Triggered when validation fails (enabled by default)
2. **Manual Rollback**: User-initiated restoration of specific files or entire batches
3. **CLI Rollback**: Command-line interface for scripted rollback operations (planned)

### When Rollback Occurs

Rollback is triggered when:

- **Validation Failure**: Syntax errors, type check failures, import errors, or test failures
- **Integration Conflict**: Merge conflicts that cannot be auto-resolved
- **User Request**: Manual rollback via CLI or script
- **Circuit Breaker**: Emergency shutdown after repeated failures
- **Timeout**: Batch operation exceeds time limit

### Rollback Guarantees

- All file modifications are backed up **before** execution
- Backups are timestamped and isolated per batch run
- Atomic rollback: All-or-nothing restoration
- Git-aware: Can create rollback commits if needed
- Retention: Backups kept for 24 hours (configurable)

---

## Automatic Rollback

### How It Works

Automatic rollback is controlled by the ARMANI Squad's integration weaving system and configured in `batching_guardrails.yaml`.

**Configuration Path:**
```
C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\modsquad\config\batching_guardrails.yaml
```

**Key Settings:**

```yaml
integration_weaving:
  execution:
    create_backups: true                    # Enable backup creation
    backup_retention_hours: 24              # Retain for 24 hours
    rollback_on_validation_failure: true    # Auto-rollback on failure
    atomic_operations: true                 # All-or-nothing execution

  validation:
    enabled: true
    block_on_integration_fail: true         # Exit 1 if validation fails

    layers:
      syntax:
        enabled: true
        blocking: true                      # Must pass

      imports:
        enabled: true
        blocking: true                      # Must pass

      function_signatures:
        enabled: true
        blocking: true                      # Must pass

      unit_tests:
        enabled: true
        blocking: false                     # Warn only

execution_policies:
  failure_handling:
    rollback_on_failure: true               # Rollback on batch failure
    continue_on_batch_failure: false        # Stop all batches if one fails
    isolate_failed_tasks: true              # Remove failed tasks from plan
```

### Automatic Rollback Process

When validation fails, the following sequence executes:

1. **Detect Failure**: Validation layer reports blocking failure
2. **Stop Execution**: All pending integrations are paused
3. **Identify Affected Files**: List all modified files in failed batch
4. **Restore from Backup**: Copy backed-up files to original locations
5. **Verify Restoration**: Check file checksums match pre-modification state
6. **Log Rollback**: Record rollback event in `run-history/elite_weaver/`
7. **Report Status**: Generate rollback report with failure details

**Example Rollback Log:**

```json
{
  "timestamp": "2025-10-31T22:15:30Z",
  "event": "automatic_rollback",
  "trigger": "validation_failure",
  "batch_id": "batch_2",
  "failed_validation": "syntax",
  "files_restored": [
    "backend/app/main.py",
    "backend/app/routers/orders.py"
  ],
  "backup_source": "modsquad/logs/backups/20251031_221500/",
  "restoration_status": "success",
  "verification": {
    "checksums_match": true,
    "files_count": 2
  }
}
```

### What Triggers Automatic Rollback

| Validation Layer | Blocking | Trigger Condition |
|-----------------|----------|-------------------|
| Syntax Check | Yes | Python syntax errors via `py_compile` |
| Import Check | Yes | Circular imports or unresolved dependencies |
| Function Signatures | Yes | Type contract violations |
| Type Check (mypy) | No | Type hint errors (warning only) |
| Unit Tests | No | Test failures (warning only) |

**Critical Files** (higher risk, stricter validation):
- `main.py`
- `__init__.py`
- `config.py`
- `database.py`
- `migrations/` (any file)
- `alembic/` (any file)

---

## Manual Rollback

### Prerequisites

1. **Locate Backup Directory**:
   ```bash
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\modsquad\logs\backups
   ```

2. **Identify Backup Timestamp**:
   Backups are stored in directories named with format: `YYYYMMDD_HHMMSS`

   ```bash
   # PowerShell
   Get-ChildItem -Directory | Sort-Object LastWriteTime -Descending

   # Bash (Git Bash on Windows)
   ls -lt
   ```

   **Example Output:**
   ```
   20251031_221500/  <- Most recent
   20251031_201000/
   20251031_180000/
   ```

### Step-by-Step Manual Rollback

#### Option 1: Restore All Files from Timestamp

**PowerShell:**
```powershell
# Navigate to project root
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD

# Set backup timestamp
$BACKUP_TIMESTAMP = "20251031_221500"

# Restore all files
Get-ChildItem "modsquad\logs\backups\$BACKUP_TIMESTAMP" -Recurse -File | ForEach-Object {
    $RelativePath = $_.FullName.Replace((Get-Location).Path + "\modsquad\logs\backups\$BACKUP_TIMESTAMP\", "")
    $DestinationPath = Join-Path (Get-Location) $RelativePath

    # Create parent directory if needed
    $ParentDir = Split-Path $DestinationPath -Parent
    if (-not (Test-Path $ParentDir)) {
        New-Item -ItemType Directory -Path $ParentDir -Force
    }

    Copy-Item $_.FullName $DestinationPath -Force
    Write-Host "[RESTORED] $RelativePath"
}
```

**Bash (Git Bash on Windows):**
```bash
# Navigate to project root
cd /c/Users/SSaint-Cyr/Documents/GitHub/PaiiD

# Set backup timestamp
BACKUP_TIMESTAMP="20251031_221500"

# Restore all files
find "modsquad/logs/backups/$BACKUP_TIMESTAMP" -type f | while read backup_file; do
    # Extract relative path
    relative_path="${backup_file#modsquad/logs/backups/$BACKUP_TIMESTAMP/}"

    # Create parent directory if needed
    mkdir -p "$(dirname "$relative_path")"

    # Copy file
    cp "$backup_file" "$relative_path"
    echo "[RESTORED] $relative_path"
done
```

#### Option 2: Restore Specific Files

**PowerShell:**
```powershell
# Navigate to project root
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD

# Set backup timestamp
$BACKUP_TIMESTAMP = "20251031_221500"

# Define files to restore (relative to project root)
$FILES_TO_RESTORE = @(
    "backend\app\main.py",
    "backend\app\routers\orders.py",
    "frontend\components\RadialMenu.tsx"
)

foreach ($file in $FILES_TO_RESTORE) {
    $BackupFile = "modsquad\logs\backups\$BACKUP_TIMESTAMP\$file"

    if (Test-Path $BackupFile) {
        Copy-Item $BackupFile $file -Force
        Write-Host "[RESTORED] $file" -ForegroundColor Green
    } else {
        Write-Host "[NOT FOUND] $file in backup $BACKUP_TIMESTAMP" -ForegroundColor Red
    }
}
```

**Bash (Git Bash on Windows):**
```bash
# Navigate to project root
cd /c/Users/SSaint-Cyr/Documents/GitHub/PaiiD

# Set backup timestamp
BACKUP_TIMESTAMP="20251031_221500"

# Define files to restore
FILES_TO_RESTORE=(
    "backend/app/main.py"
    "backend/app/routers/orders.py"
    "frontend/components/RadialMenu.tsx"
)

for file in "${FILES_TO_RESTORE[@]}"; do
    backup_file="modsquad/logs/backups/$BACKUP_TIMESTAMP/$file"

    if [ -f "$backup_file" ]; then
        cp "$backup_file" "$file"
        echo "[RESTORED] $file"
    else
        echo "[NOT FOUND] $file in backup $BACKUP_TIMESTAMP"
    fi
done
```

#### Option 3: List Available Backups

**PowerShell:**
```powershell
# Navigate to backup directory
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\modsquad\logs\backups

# List all backups with file counts
Get-ChildItem -Directory | Sort-Object LastWriteTime -Descending | ForEach-Object {
    $FileCount = (Get-ChildItem $_.FullName -Recurse -File).Count
    $Timestamp = $_.Name
    $Age = (Get-Date) - $_.LastWriteTime

    Write-Host "$Timestamp | $FileCount files | $($Age.Hours)h $($Age.Minutes)m ago"
}
```

**Bash (Git Bash on Windows):**
```bash
# Navigate to backup directory
cd /c/Users/SSaint-Cyr/Documents/GitHub/PaiiD/modsquad/logs/backups

# List all backups with file counts
for backup_dir in $(ls -t); do
    file_count=$(find "$backup_dir" -type f | wc -l)
    timestamp=$(stat -c %y "$backup_dir" | cut -d' ' -f1,2)
    echo "$backup_dir | $file_count files | Modified: $timestamp"
done
```

### Verify Restoration

After manual rollback, verify file integrity:

**PowerShell:**
```powershell
# Check if backend starts without errors
cd backend
python -m uvicorn app.main:app --reload --port 8001

# In another terminal, check health endpoint
Invoke-WebRequest -Uri "http://127.0.0.1:8001/api/health" | Select-Object -Expand Content
```

**Bash (Git Bash on Windows):**
```bash
# Check if backend starts without errors
cd backend
python -m uvicorn app.main:app --reload --port 8001 &

# Wait 3 seconds for startup
sleep 3

# Check health endpoint
curl http://127.0.0.1:8001/api/health
```

**Frontend Verification:**
```bash
cd frontend
npm run build  # Verify build succeeds
npm run dev    # Start dev server
```

---

## CLI Rollback (Future)

### Planned CLI Commands

**Note:** CLI rollback is currently in planning phase. The following commands are proposed for future implementation.

```bash
# List available backups
modsquad rollback list

# Show details of specific backup
modsquad rollback inspect --timestamp 20251031_221500

# Restore all files from timestamp
modsquad rollback restore --timestamp 20251031_221500 --all

# Restore specific files
modsquad rollback restore --timestamp 20251031_221500 --files backend/app/main.py backend/app/routers/orders.py

# Verify integrity after rollback
modsquad rollback verify --timestamp 20251031_221500

# Clean up old backups (older than 24 hours)
modsquad rollback cleanup --older-than 24h

# Create manual backup before risky operation
modsquad rollback backup --label "before-major-refactor"
```

---

## Prevention Best Practices

### 1. Dry-Run Mode (Recommended First Step)

Always run batch operations in dry-run mode before actual execution.

### 2. Review Batch Plan Before Execution

Inspect the batch plan artifact before committing.

**Review Checklist:**
- [ ] Are critical files isolated in separate batches?
- [ ] Is collision probability below 10%?
- [ ] Is batch risk below 0.5% per batch?
- [ ] Are dependencies resolved correctly?
- [ ] Do file groups make logical sense?

### 3. Test in Isolated Branch

Always test batch operations in a dedicated branch:

```bash
# Create feature branch for batch testing
git checkout -b feature/modsquad-batch-test-$(date +%Y%m%d)

# Run batch operation
python -m modsquad.cli.batch execute --plan batch_plan.json

# If successful, merge to main
git checkout main
git merge feature/modsquad-batch-test-20251031

# If failed, delete branch
git checkout main
git branch -D feature/modsquad-batch-test-20251031
```

### 4. Enable All Validation Layers

Ensure all validation layers are enabled in `batching_guardrails.yaml`.

### 5. Use Circuit Breaker Protection

Enable circuit breaker to auto-disable after repeated failures.

### 6. Start Small

For first-time batch operations:

1. **Small Task Set**: Start with 3-5 tasks (not 20+)
2. **Low Risk**: Choose non-critical files (not `main.py` or `database.py`)
3. **Single Level**: Use tasks with no dependencies (parallelizable)
4. **Manual Review**: Review all generated glue code before execution

---

## Troubleshooting

### What If Automatic Rollback Fails?

**Common Causes:**

1. **File Locked by Process**

   **Solution:** Stop all running processes (backend, frontend, IDE)
   ```bash
   # Stop backend
   pkill -f uvicorn

   # Stop frontend
   pkill -f "next-router"

   # Retry manual rollback
   ```

2. **Backup Directory Corrupted**

   **Solution:** Use git to restore
   ```bash
   git checkout HEAD -- backend/app/main.py backend/app/routers/orders.py
   ```

3. **Permissions Issue (Windows)**

   **Solution:** Run rollback as Administrator

### How to Verify File Integrity After Rollback

**Method 1: Syntax Validation**

```bash
# Verify Python syntax
python -m py_compile backend/app/main.py
python -m py_compile backend/app/routers/orders.py

# If no output, syntax is valid
```

**Method 2: Run Tests**

```bash
# Backend tests
cd backend
pytest app/tests/ -v

# Frontend tests
cd frontend
npm run test:ci
```

### How to Clean Up Old Backups

**Manual Cleanup (PowerShell):**
```powershell
# Delete backups older than 24 hours
$RETENTION_HOURS = 24
$CUTOFF_TIME = (Get-Date).AddHours(-$RETENTION_HOURS)

Get-ChildItem "modsquad\logs\backups" -Directory | Where-Object {
    $_.LastWriteTime -lt $CUTOFF_TIME
} | ForEach-Object {
    Write-Host "Deleting backup: $($_.Name) (Age: $((Get-Date) - $_.LastWriteTime))"
    Remove-Item $_.FullName -Recurse -Force
}
```

---

## Backup Directory Structure

### Directory Layout

```
C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\modsquad\logs\backups\
├── 20251031_221500/          <- Backup timestamp directory
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routers/
│   │   │   │   ├── orders.py
│   │   │   │   └── portfolio.py
│   │   │   └── services/
│   │   │       └── strategy_execution_service.py
│   │   └── strategies/
│   │       └── __init__.py
│   ├── frontend/
│   │   └── components/
│   │       └── RadialMenu.tsx
│   └── .backup_metadata.json <- Metadata about backup
│
├── 20251031_220000/
│   └── ...
│
└── 20251031_215000/
    └── ...
```

---

## Integration with Git Workflow

### Pre-Rollback Git Status Check

Before rollback, check git status to understand current state:

```bash
# Check for uncommitted changes
git status

# If you have uncommitted changes you want to keep
git stash push -m "Work in progress before rollback"

# Perform rollback
# ... (manual or automatic)

# After rollback, restore your work
git stash pop
```

### Rollback with Git Commit

Create a rollback commit for audit trail:

```bash
# Perform manual rollback
# ... (restore files)

# Stage rolled-back files
git add backend/app/main.py backend/app/routers/orders.py

# Create rollback commit
git commit -m "rollback: Restore files from batch_3 failure

Reason: Validation failure (syntax error in orders.py)
Backup timestamp: 20251031_221500
Files restored:
- backend/app/main.py
- backend/app/routers/orders.py

Rolled back by [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"
```

### Emergency Git Hard Reset

If all else fails, use git to restore:

```bash
# CAUTION: This discards ALL uncommitted changes

# Show recent commits
git log --oneline -10

# Reset to commit before batch operation
git reset --hard 9aa047d

# Verify restoration
git status
git diff HEAD
```

---

## Quick Reference Card

### Common Commands

| Task | PowerShell | Bash |
|------|-----------|------|
| List backups | `Get-ChildItem modsquad\logs\backups -Directory` | `ls -lt modsquad/logs/backups` |
| Restore all files | See [Option 1](#option-1-restore-all-files-from-timestamp) | See [Option 1](#option-1-restore-all-files-from-timestamp) |
| Restore specific files | See [Option 2](#option-2-restore-specific-files) | See [Option 2](#option-2-restore-specific-files) |
| Verify syntax | `python -m py_compile <file>` | `python -m py_compile <file>` |
| Run tests | `pytest -v` | `pytest -v` |
| Clean old backups | See [Cleanup](#how-to-clean-up-old-backups) | See [Cleanup](#how-to-clean-up-old-backups) |

### Emergency Contacts

| Issue | Action |
|-------|--------|
| Automatic rollback failed | Try manual rollback → Git reset → Contact maintainer |
| Files corrupted | Check backup checksums → Restore from git → Contact maintainer |
| Backup not found | Check git history → Restore from git → Contact maintainer |
| Permission denied | Run as Administrator → Check file locks → Contact maintainer |

### Critical File Paths

```
Project Root:     C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD
Config:           modsquad\config\batching_guardrails.yaml
Backups:          modsquad\logs\backups\
Run History:      modsquad\logs\run-history\
Integration Logs: modsquad\logs\run-history\elite_weaver\
Batch Plans:      modsquad\logs\run-history\elite_strategist\
```

---

**Document Version:** 2.0
**Effective Date:** October 31, 2025
**Next Review:** November 30, 2025

**Maintainer:** PaiiD Mod Squad Team
**Contact:** See project CLAUDE.md for support channels
