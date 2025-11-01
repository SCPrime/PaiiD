# COMPLETE DEPLOYMENT PLAN: 80% → 100%
## SUN TZU + ARMANI Seamless Injection

**Current Status:** 80% Implementation Complete
**Target:** 100% Production-Ready Seamless Supercharger
**Time Estimate:** 12 hours total (2 work days)

---

## 📊 CURRENT STATE ASSESSMENT

### ✅ COMPLETE (80%)
- [x] 11 extensions created (4,417 lines)
- [x] 2 squad files (sun_tzu.py, armani.py)
- [x] Configuration (batching_guardrails.yaml)
- [x] All imports updated (__init__.py files)
- [x] Version bumped to 2.2.0
- [x] Comprehensive documentation
- [x] Circular import fixes (elite_strategist.py, elite_weaver.py) ✅ **JUST COMPLETED**

### ❌ INCOMPLETE (20%)
- [ ] File locking (race condition protection)
- [ ] Server state detection
- [ ] Dependencies (mypy, portalocker)
- [ ] CLI activation mechanism
- [ ] Squad coordination (FOXTROT, ALPHA)
- [ ] Usage examples
- [ ] Rollback procedures
- [ ] Unit tests (0% coverage)
- [ ] Integration test
- [ ] CI/CD integration

---

## 🎯 PHASE 1: CRITICAL SAFETY (4 hours)

### Task 1.1: Add File Locking (1 hour)
**File:** `modsquad/extensions/intersection_executor.py`

**Changes:**
```python
# Add at top of file
import portalocker  # Cross-platform file locking

# Replace line 315-316 (_apply_conflict_resolutions)
with portalocker.Lock(path, mode="w", timeout=30, flags=portalocker.LOCK_EX):
    with path.open("w", encoding="utf-8") as f:
        f.write(content)

# Replace line 386-387 (_inject_glue_code)
with portalocker.Lock(target_path, mode="w", timeout=30, flags=portalocker.LOCK_EX):
    with target_path.open("w", encoding="utf-8") as f:
        f.write(modified_content)
```

**Retry Logic:**
```python
def _write_with_lock(path: Path, content: str, max_retries: int = 3) -> None:
    """Write file with exclusive lock and exponential backoff."""
    for attempt in range(max_retries):
        try:
            with portalocker.Lock(path, mode="w", timeout=30):
                with path.open("w", encoding="utf-8") as f:
                    f.write(content)
            return  # Success
        except portalocker.LockException:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
            else:
                raise IntegrationError(f"Failed to acquire lock on {path} after {max_retries} attempts")
```

---

### Task 1.2: Add Server State Detection (1.5 hours)
**File:** `modsquad/extensions/elite_strategist.py`

**Changes:**
```python
# Add at top
import requests
import os

# Add before Phase 1 in run()
def run(tasks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    # ... existing config loading ...

    # SAFETY: Block batching if server is running
    if not _is_safe_to_batch():
        return {
            "status": "blocked",
            "reason": "Backend server running - cannot batch critical files",
            "fix": "Stop backend server (Ctrl+C) or set MODSQUAD_ALLOW_LIVE_BATCHING=true"
        }

    # ... rest of function ...

def _is_safe_to_batch() -> bool:
    """Check if it's safe to execute batch modifications."""
    # Check environment override
    if os.getenv("MODSQUAD_ALLOW_LIVE_BATCHING", "false").lower() == "true":
        return True  # User explicitly allowed

    # Check if backend is running
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=1)
        if response.status_code == 200:
            return False  # Backend running, NOT safe
    except requests.exceptions.ConnectionError:
        pass  # Backend not running, safe
    except requests.exceptions.Timeout:
        pass  # Timeout, assume safe

    # Check if frontend dev server is running
    try:
        response = requests.get("http://localhost:3000", timeout=1)
        if response.status_code == 200:
            return False  # Next.js dev running, NOT safe
    except requests.exceptions.ConnectionError:
        pass  # Frontend not running, safe
    except requests.exceptions.Timeout:
        pass  # Timeout, assume safe

    return True  # Safe to proceed
```

---

### Task 1.3: Add Dependencies (30 min)
**File:** `backend/requirements.txt`

**Changes:**
```txt
# Add at end of file (after existing dependencies)

# MOD SQUAD SUN TZU + ARMANI Dependencies
mypy>=1.8.0                # Type checking for integration validation (optional)
portalocker>=2.8.2         # Cross-platform file locking for parallel batch execution
requests>=2.31.0           # Server state detection (may already exist)
```

**Verify existing:**
- Check if `requests` already in requirements.txt (likely yes for Alpaca/Tradier API calls)
- If yes, skip adding it

**Install:**
```bash
cd backend
pip install mypy>=1.8.0 portalocker>=2.8.2
```

---

### Task 1.4: Update Environment Variables (30 min)
**File:** `.modsquad_env`

**Add:**
```bash
# Safety Controls for Batch Execution
export MODSQUAD_ALLOW_LIVE_BATCHING=false  # NEVER allow batching while servers running
export MODSQUAD_SERVER_HEALTH_CHECK=true   # Check server state before batching
export MODSQUAD_FILE_LOCK_TIMEOUT=30       # File lock timeout (seconds)
export MODSQUAD_FILE_LOCK_RETRIES=3        # Max retry attempts for file locks
```

---

## 🔧 PHASE 2: ACTIVATION MECHANISM (3 hours)

### Task 2.1: Create CLI Commands (2 hours)
**File:** `modsquad/cli/batch.py` (NEW)

```python
"""CLI commands for SUN TZU + ARMANI batch execution."""

import argparse
import json
import sys
from pathlib import Path

def batch_plan_command(args):
    """Execute batch planning with SUN TZU squad."""
    from modsquad.squads import sun_tzu

    # Load tasks from file
    tasks_file = Path(args.tasks)
    if not tasks_file.exists():
        print(f"ERROR: Tasks file not found: {args.tasks}")
        sys.exit(1)

    with tasks_file.open("r") as f:
        tasks = json.load(f)

    # Execute planning
    print(f"[SUN TZU] Planning batch execution for {len(tasks)} tasks...")
    result = sun_tzu.plan(tasks)

    # Save plan if requested
    if args.output:
        output_file = Path(args.output)
        with output_file.open("w") as f:
            json.dump(result, f, indent=2)
        print(f"[SUN TZU] Batch plan saved to {args.output}")

    # Print summary
    if result.get("status") == "success":
        metadata = result["batch_plan"]["strategist_metadata"]
        print(f"  ✓ Batches: {metadata['total_batches']}")
        print(f"  ✓ Parallelization: {metadata['parallelization_factor']}%")
        print(f"  ✓ Estimated Speedup: {metadata['estimated_speedup']}")
        print(f"  ✓ Intersections: {metadata['total_intersections']}")
        sys.exit(0)
    else:
        print(f"  ✗ Planning failed: {result.get('reason')}")
        sys.exit(1)


def batch_weave_command(args):
    """Execute integration weaving with ARMANI squad."""
    from modsquad.squads import armani

    # Load batch plan
    plan_file = Path(args.plan)
    if not plan_file.exists():
        print(f"ERROR: Batch plan not found: {args.plan}")
        sys.exit(1)

    with plan_file.open("r") as f:
        batch_plan = json.load(f)

    # Load batch results
    results_file = Path(args.results)
    if not results_file.exists():
        print(f"ERROR: Batch results not found: {args.results}")
        sys.exit(1)

    with results_file.open("r") as f:
        batch_results = json.load(f)

    # Execute weaving
    print(f"[ARMANI] Weaving {len(batch_plan.get('intersections', []))} intersection points...")
    result = armani.weave(batch_plan, batch_results)

    # Print summary
    if result.get("status") == "success":
        metadata = result["weave_result"]["weaver_metadata"]
        print(f"  ✓ Intersections Executed: {metadata['intersections_executed']}")
        print(f"  ✓ Conflicts Resolved: {metadata['conflicts_resolved']}")
        print(f"  ✓ Validations Passed: {metadata['validations_passed']}")
        sys.exit(0)
    else:
        print(f"  ✗ Weaving failed: {result.get('reason')}")
        sys.exit(1)


def batch_rollback_command(args):
    """Rollback a failed batch execution."""
    from modsquad.extensions import intersection_executor

    # TODO: Implement rollback by restoring from backup directory
    backup_dir = Path("modsquad/logs/run-history/intersection_executor/backups")

    if not backup_dir.exists():
        print("ERROR: No backups found")
        sys.exit(1)

    # List available backups
    backups = sorted(backup_dir.glob("*.backup"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not backups:
        print("ERROR: No backup files found")
        sys.exit(1)

    print(f"Found {len(backups)} backup files:")
    for i, backup in enumerate(backups[:10]):
        print(f"  {i+1}. {backup.name}")

    # TODO: Implement restore logic
    print("\nRollback functionality coming soon!")
    sys.exit(0)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MOD SQUAD Batch Execution CLI (SUN TZU + ARMANI)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # batch-plan command
    plan_parser = subparsers.add_parser("plan", help="Create batch execution plan with SUN TZU")
    plan_parser.add_argument("--tasks", required=True, help="Path to tasks JSON file")
    plan_parser.add_argument("--output", help="Path to save batch plan JSON")
    plan_parser.set_defaults(func=batch_plan_command)

    # batch-weave command
    weave_parser = subparsers.add_parser("weave", help="Execute integration weaving with ARMANI")
    weave_parser.add_argument("--plan", required=True, help="Path to batch plan JSON")
    weave_parser.add_argument("--results", required=True, help="Path to batch results JSON")
    weave_parser.set_defaults(func=batch_weave_command)

    # batch-rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback failed batch execution")
    rollback_parser.add_argument("--batch-id", help="Batch ID to rollback (optional)")
    rollback_parser.set_defaults(func=batch_rollback_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
```

---

### Task 2.2: Update universal_loader.py (1 hour)
**File:** `modsquad/universal_loader.py`

**Changes:**
```python
# Around line 73 (after existing extension imports)
def _load_modsquad_extensions(self):
    from modsquad.extensions import (
        # ... existing imports ...
        runner,

        # SUN TZU Squad (conditional import)
        elite_strategist,
        task_graph_analyzer,
        risk_profiler,
        batch_optimizer,
        intersection_mapper,

        # ARMANI Squad (conditional import)
        elite_weaver,
        interface_predictor,
        glue_code_generator,
        conflict_resolver,
        intersection_executor,
        integration_validator,
    )

    # ... rest of function ...
```

**Note:** Only import if enabled in config (check `load_extension_config()`)

---

## 🤝 PHASE 3: SQUAD COORDINATION (2 hours)

### Task 3.1: Add Batch Lock to FOXTROT (1 hour)
**File:** `modsquad/squads/foxtrot.py`

**Add:**
```python
import threading

_batch_execution_lock = threading.Lock()

def acquire_batch_lock(timeout: float = 60.0) -> bool:
    """
    Acquire exclusive batch execution lock.

    Prevents simultaneous orchestration and batch execution.

    Returns:
        True if lock acquired, False if timeout
    """
    return _batch_execution_lock.acquire(timeout=timeout)

def release_batch_lock() -> None:
    """Release batch execution lock."""
    try:
        _batch_execution_lock.release()
    except RuntimeError:
        pass  # Lock not held

def is_batch_locked() -> bool:
    """Check if batch execution is currently locked."""
    acquired = _batch_execution_lock.acquire(blocking=False)
    if acquired:
        _batch_execution_lock.release()
        return False
    return True
```

**Update `elite_strategist.py`:**
```python
# In run() function, before Phase 1
from modsquad.squads import foxtrot

if not foxtrot.acquire_batch_lock(timeout=60):
    return {
        "status": "locked",
        "reason": "Another batch execution or orchestration in progress",
        "fix": "Wait for current operation to complete"
    }

try:
    # ... existing batch planning code ...
finally:
    foxtrot.release_batch_lock()
```

---

### Task 3.2: Add Pause Mechanism to ALPHA (1 hour)
**File:** `modsquad/squads/alpha.py`

**Add:**
```python
import threading

_alpha_paused = threading.Event()
_alpha_paused.set()  # Initially NOT paused (set = running)

def pause_alpha_squad() -> None:
    """Pause ALPHA squad always-on tasks during batch execution."""
    _alpha_paused.clear()
    print("[ALPHA SQUAD] Paused during batch execution")

def resume_alpha_squad() -> None:
    """Resume ALPHA squad always-on tasks after batch execution."""
    _alpha_paused.set()
    print("[ALPHA SQUAD] Resumed")

def is_alpha_paused() -> bool:
    """Check if ALPHA squad is currently paused."""
    return not _alpha_paused.is_set()

def wait_if_paused() -> None:
    """Block until ALPHA squad is resumed (used in always-on tasks)."""
    _alpha_paused.wait()
```

**Update `elite_strategist.py`:**
```python
# In run() function, after acquiring lock
from modsquad.squads import alpha

alpha.pause_alpha_squad()

try:
    # ... existing batch planning code ...
finally:
    alpha.resume_alpha_squad()
    foxtrot.release_batch_lock()
```

---

## 📚 PHASE 4: DOCUMENTATION (1.5 hours)

### Task 4.1: Create BATCHING_EXAMPLES.md (45 min)
**File:** `modsquad/docs/BATCHING_EXAMPLES.md`

**Content:** 5+ realistic task definition examples
1. Parallel router updates (health.py, orders.py, metrics.py)
2. Sequential with dependencies (models → routes → tests)
3. Frontend component additions (3 parallel components)
4. Database migration + code updates (sequential)
5. Multi-squad extension additions (BRAVO + CHARLIE)

**Format:**
```markdown
# SUN TZU + ARMANI Batching Examples

## Example 1: Parallel Router Updates

**Scenario:** Add new endpoints to 3 different routers simultaneously

**tasks.json:**
\`\`\`json
[
  {
    "id": "add_health_metrics",
    "description": "Add /metrics endpoint to health router",
    "files": ["backend/app/routers/health.py"],
    "dependencies": []
  },
  {
    "id": "add_order_validation",
    "description": "Add validation middleware to orders router",
    "files": ["backend/app/routers/orders.py"],
    "dependencies": []
  },
  {
    "id": "update_main_imports",
    "description": "Update main.py to register new endpoints",
    "files": ["backend/app/main.py"],
    "dependencies": ["add_health_metrics", "add_order_validation"]
  }
]
\`\`\`

**Execution:**
\`\`\`bash
# Step 1: Plan
modsquad batch-plan --tasks tasks.json --output plan.json

# Step 2: Review plan
cat plan.json

# Step 3: Execute batches manually or via CI
# (Batch 0: tasks 1+2 in parallel)
# (Batch 1: task 3 sequential after batch 0)

# Step 4: Weave
modsquad batch-weave --plan plan.json --results results.json
\`\`\`

**Expected Output:**
- Batches: 2
- Parallelization: 66.7%
- Estimated Speedup: 33%
- Intersections: 1 (main.py import merge)
```

---

### Task 4.2: Create ROLLBACK_PROCEDURES.md (45 min)
**File:** `modsquad/docs/ROLLBACK_PROCEDURES.md`

**Content:**
```markdown
# Rollback Procedures for Failed Batch Execution

## Automatic Rollback (Recommended)

When `integration_validator.py` detects syntax errors or validation failures, rollback is **automatic**:

1. Validation fails (syntax, imports, signatures)
2. `intersection_executor.py` detects failure
3. Backups are restored from `modsquad/logs/run-history/intersection_executor/backups/`
4. Original files are preserved

**Configuration:**
\`\`\`yaml
# modsquad/config/batching_guardrails.yaml
execution:
  rollback_on_validation_failure: true  # ✅ Enabled by default
\`\`\`

## Manual Rollback

If automatic rollback fails or you need to restore from a specific backup:

### Step 1: List Available Backups
\`\`\`bash
ls -lt modsquad/logs/run-history/intersection_executor/backups/
\`\`\`

**Example output:**
\`\`\`
main.py.20251031_143522.backup
health.py.20251031_143522.backup
orders.py.20251031_143522.backup
\`\`\`

### Step 2: Restore Files
\`\`\`bash
# Restore specific file
cp modsquad/logs/run-history/intersection_executor/backups/main.py.20251031_143522.backup backend/app/main.py

# Or restore all files from timestamp
TIMESTAMP=20251031_143522
for backup in modsquad/logs/run-history/intersection_executor/backups/*.$TIMESTAMP.backup; do
    original=$(basename $backup | sed "s/\.$TIMESTAMP\.backup//")
    # Restore to original location (adjust path as needed)
    cp $backup backend/app/$original
done
\`\`\`

### Step 3: Verify Restoration
\`\`\`bash
# Check syntax
python -m py_compile backend/app/main.py

# Run tests
pytest backend/tests/
\`\`\`

## CLI Rollback (Future)

\`\`\`bash
# Will be available in future release
modsquad batch-rollback --batch-id batch_20251031_143522
\`\`\`

## Prevention Best Practices

1. **Always run in dry-run mode first:**
   \`\`\`bash
   modsquad batch-plan --tasks tasks.json --dry-run
   \`\`\`

2. **Review batch plan before execution:**
   \`\`\`bash
   cat plan.json | jq '.intersections'
   \`\`\`

3. **Test in isolated branch:**
   \`\`\`bash
   git checkout -b test-batching
   modsquad batch-plan --tasks tasks.json
   # Review changes
   git diff
   \`\`\`

4. **Enable all validation layers:**
   \`\`\`yaml
   # batching_guardrails.yaml
   validation:
     block_on_integration_fail: true
     layers:
       syntax: { blocking: true }
       imports: { blocking: true }
       function_signatures: { blocking: true }
   \`\`\`
```

---

## 🧪 PHASE 5: TESTING (4 hours)

### Task 5.1: Create Unit Tests (2.5 hours)
**Create 11 test files** in `backend/tests/unit/modsquad/`:

1. `test_elite_strategist.py` (30 min)
2. `test_task_graph_analyzer.py` (20 min)
3. `test_risk_profiler.py` (20 min)
4. `test_batch_optimizer.py` (30 min)
5. `test_intersection_mapper.py` (20 min)
6. `test_elite_weaver.py` (15 min)
7. `test_interface_predictor.py` (15 min)
8. `test_glue_code_generator.py` (15 min)
9. `test_conflict_resolver.py` (15 min)
10. `test_intersection_executor.py` (15 min)
11. `test_integration_validator.py` (15 min)

**Example:** `test_task_graph_analyzer.py`
```python
"""Unit tests for task_graph_analyzer extension."""

import pytest
from pathlib import Path
from modsquad.extensions import task_graph_analyzer


def test_analyze_no_dependencies():
    """Test dependency analysis with no dependencies."""
    tasks = [
        {"id": "task1", "files": ["file1.py"]},
        {"id": "task2", "files": ["file2.py"]},
    ]

    graph = task_graph_analyzer.analyze(tasks)

    assert "task1" in graph
    assert "task2" in graph
    assert graph["task1"] == []  # No dependencies
    assert graph["task2"] == []


def test_analyze_explicit_dependencies():
    """Test explicit dependencies are preserved."""
    tasks = [
        {"id": "task1", "files": ["file1.py"], "dependencies": ["task2"]},
        {"id": "task2", "files": ["file2.py"]},
    ]

    graph = task_graph_analyzer.analyze(tasks)

    assert "task2" in graph["task1"]


def test_extract_imports_python_file(tmp_path):
    """Test import extraction from Python file."""
    # Create temp Python file with imports
    test_file = tmp_path / "test.py"
    test_file.write_text("""
import os
from pathlib import Path
from typing import Any
""")

    imports = task_graph_analyzer._extract_imports(str(test_file))

    assert "os" in imports
    assert "pathlib" in imports
    assert "typing" in imports


def test_analyze_circular_dependency_detection():
    """Test detection of circular dependencies."""
    # TODO: Implement circular dependency detection
    # For now, just ensure it doesn't crash
    tasks = [
        {"id": "task1", "files": ["file1.py"], "dependencies": ["task2"]},
        {"id": "task2", "files": ["file2.py"], "dependencies": ["task1"]},
    ]

    graph = task_graph_analyzer.analyze(tasks)

    # Should detect cycle (future enhancement)
    assert "task1" in graph
    assert "task2" in graph


# Run with: pytest backend/tests/unit/modsquad/test_task_graph_analyzer.py -v
```

**Target:** 80% code coverage minimum

---

### Task 5.2: Create Integration Test (1.5 hours)
**File:** `backend/tests/integration/modsquad/test_sun_tzu_armani_flow.py`

```python
"""Integration test for full SUN TZU → ARMANI flow."""

import pytest
import json
from pathlib import Path
from modsquad.squads import sun_tzu, armani


@pytest.fixture
def sample_tasks(tmp_path):
    """Create sample tasks for testing."""
    # Create temporary test files
    file1 = tmp_path / "router1.py"
    file1.write_text('"""Router 1"""\n\ndef get_data():\n    return {}\n')

    file2 = tmp_path / "router2.py"
    file2.write_text('"""Router 2"""\n\ndef get_items():\n    return []\n')

    main_file = tmp_path / "main.py"
    main_file.write_text('"""Main file"""\n\n# Imports will be added here\n')

    return [
        {
            "id": "task1",
            "description": "Update router1",
            "files": [str(file1)],
            "dependencies": [],
        },
        {
            "id": "task2",
            "description": "Update router2",
            "files": [str(file2)],
            "dependencies": [],
        },
        {
            "id": "task3",
            "description": "Update main imports",
            "files": [str(main_file)],
            "dependencies": ["task1", "task2"],
        },
    ]


def test_full_batch_execution_flow(sample_tasks):
    """Test complete SUN TZU planning → ARMANI weaving flow."""

    # Phase 1: SUN TZU Planning
    batch_plan = sun_tzu.plan(sample_tasks)

    assert batch_plan["status"] == "success"
    assert "batch_plan" in batch_plan

    metadata = batch_plan["batch_plan"]["strategist_metadata"]
    assert metadata["total_tasks"] == 3
    assert metadata["total_batches"] >= 2  # task1+task2 parallel, task3 sequential
    assert metadata["parallelization_factor"] >= 30  # At least 30%

    # Phase 2: Simulate Batch Execution
    # (In real scenario, batches would be executed in parallel)
    batch_results = {
        "batch_0": {"status": "completed", "tasks": ["task1", "task2"]},
        "batch_1": {"status": "completed", "tasks": ["task3"]},
    }

    # Phase 3: ARMANI Weaving
    weave_result = armani.weave(batch_plan["batch_plan"], batch_results)

    assert weave_result["status"] == "success"
    assert "weave_result" in weave_result

    weave_metadata = weave_result["weave_result"]["weaver_metadata"]
    assert weave_metadata["intersections_executed"] >= 1
    assert weave_metadata["validations_passed"] >= 1


def test_batch_planning_respects_dependencies(sample_tasks):
    """Test that batch optimizer respects task dependencies."""
    batch_plan = sun_tzu.plan(sample_tasks)

    batches = batch_plan["batch_plan"]["batches"]

    # task1 and task2 should be in earlier batch than task3
    task3_batch_level = None
    task1_batch_level = None

    for batch_id, batch_info in batches.items():
        if "task3" in [t["id"] for t in batch_info.get("tasks", [])]:
            task3_batch_level = batch_info["level"]
        if "task1" in [t["id"] for t in batch_info.get("tasks", [])]:
            task1_batch_level = batch_info["level"]

    assert task1_batch_level is not None
    assert task3_batch_level is not None
    assert task1_batch_level < task3_batch_level  # task1 before task3


# Run with: pytest backend/tests/integration/modsquad/test_sun_tzu_armani_flow.py -v
```

---

## 🚀 PHASE 6: FINAL INTEGRATION (1.5 hours)

### Task 6.1: Update README.md (30 min)
**File:** `README.md` (or `modsquad/README.md`)

**Add section:**
```markdown
## Parallel Batch Execution (SUN TZU + ARMANI)

MOD SQUAD v2.2.0 includes strategic batch planning and integration weaving for parallel task execution.

### Quick Start

1. **Define tasks** (`tasks.json`):
   \`\`\`json
   [
     {"id": "task1", "files": ["file1.py"], "dependencies": []},
     {"id": "task2", "files": ["file2.py"], "dependencies": []}
   ]
   \`\`\`

2. **Plan batches**:
   \`\`\`bash
   modsquad batch-plan --tasks tasks.json --output plan.json
   \`\`\`

3. **Execute batches** (manually or CI/CD)

4. **Weave results**:
   \`\`\`bash
   modsquad batch-weave --plan plan.json --results results.json
   \`\`\`

### Benefits
- **20-60% speedup** for large multi-task changes
- **Automatic conflict resolution** (imports, comments, functions)
- **5-layer validation** (syntax, types, imports, signatures, tests)
- **Atomic rollback** on validation failure

See `modsquad/docs/BATCHING_EXAMPLES.md` for detailed examples.
```

---

### Task 6.2: Update CI/CD (Optional) (1 hour)
**File:** `.github/workflows/mod-squad.yml`

**Add (opt-in with environment variable):**
```yaml
# After existing guardrail validation steps (around line 85)

- name: MOD SQUAD Batch Execution (Optional)
  if: env.MOD_SQUAD_ENABLE_BATCHING == 'true'
  run: |
    # Dry-run only in CI (don't actually modify files)
    python -m modsquad.cli.batch plan --tasks .github/workflows/batch-tasks.json --output batch-plan.json

    echo "Batch plan created (dry-run mode)"
    cat batch-plan.json | jq '.strategist_metadata'

env:
  MOD_SQUAD_ENABLE_BATCHING: false  # Disabled by default, enable manually
```

---

## ✅ COMPLETION CHECKLIST

### Critical Safety (Must Have)
- [ ] File locking implemented (race condition protection)
- [ ] Server state detection added (prevent corruption)
- [ ] Dependencies added (mypy, portalocker)
- [ ] Environment variables configured
- [ ] Circular imports fixed ✅ **DONE**

### Activation (Must Have)
- [ ] CLI commands created (`modsquad batch-plan`, `batch-weave`, `batch-rollback`)
- [ ] `universal_loader.py` updated (conditional imports)

### Coordination (Must Have)
- [ ] FOXTROT batch lock implemented
- [ ] ALPHA pause mechanism added
- [ ] Cross-squad coordination tested

### Documentation (Must Have)
- [ ] BATCHING_EXAMPLES.md created (5+ examples)
- [ ] ROLLBACK_PROCEDURES.md created
- [ ] README.md updated with quickstart

### Testing (Must Have)
- [ ] 11 unit test files created
- [ ] Integration test created
- [ ] 80% code coverage achieved

### Optional Enhancements
- [ ] CI/CD integration (opt-in flag)
- [ ] Metrics tracking (speedup, collisions)
- [ ] Architecture diagrams (Mermaid/UML)

---

## 📊 SUCCESS METRICS

| Metric | Target | Status |
|--------|--------|--------|
| Code Coverage | ≥80% | ⏳ Pending |
| Syntax Validation | 100% Pass | ✅ Pass |
| Import Validation | No Circular | ✅ Pass |
| Safety Controls | 5/5 Implemented | ⏳ 2/5 Done |
| Documentation | 3 Docs Created | ⏳ 1/3 Done |
| Tests | 12 Files Created | ⏳ 0/12 Done |
| CLI Commands | 3 Commands Working | ⏳ 0/3 Done |

---

## 🎯 FINAL DELIVERABLE

After completing all phases, SUN TZU + ARMANI will be:

✅ **Seamless** - No disruption to existing PaiiD workflows
✅ **Safe** - File locking, server detection, automatic rollback
✅ **Tested** - 80% code coverage, integration test passing
✅ **Documented** - Examples, procedures, quickstart guide
✅ **Production-Ready** - CLI commands, squad coordination, CI integration

**Total Time:** 12 hours (2 work days)
**Risk Level:** LOW - All critical issues addressed
**Deployment Strategy:** Phased rollout (dry-run → limited beta → production)

---

## 🚦 DEPLOYMENT READINESS

### Before Deployment
1. Complete all "Critical Safety" tasks
2. Complete all "Activation" tasks
3. Complete at least 5 unit tests
4. Run integration test successfully
5. Test CLI commands manually

### Deployment Gates
- ✅ All syntax validation passing
- ✅ No circular import errors
- ✅ File locking working (test with concurrent writes)
- ✅ Server detection blocking correctly
- ✅ Rollback tested and working

### Post-Deployment
1. Monitor first 5 batch executions closely
2. Collect metrics (speedup, collisions, conflicts)
3. Adjust guardrail thresholds if needed
4. Create additional examples based on user feedback

---

**Status:** Ready to implement remaining 20%
**Next Step:** Execute Phase 1 (Critical Safety) - 4 hours
