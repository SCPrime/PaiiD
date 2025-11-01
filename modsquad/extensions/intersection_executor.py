"""Intersection Executor - ARMANI Squad Extension #5.

Executes integration at exact intersection points with atomic operations,
conflict resolution, and comprehensive validation.

Part of the ARMANI weaving pattern for parallel batch execution.
"""

from __future__ import annotations

import ast
import difflib
import json
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import portalocker

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "intersection_executor"
BACKUP_DIR = ARTIFACT_DIR / "backups"


class ValidationError(Exception):
    """Raised when validation fails after integration."""
    pass


class ConflictError(Exception):
    """Raised when conflicts cannot be resolved automatically."""
    pass


class IntegrationError(Exception):
    """Raised when integration execution fails."""
    pass


def execute(
    intersection: dict[str, Any],
    glue_code: dict[str, Any],
    resolutions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Execute integration at exact intersection point.

    Args:
        intersection: Intersection definition from intersection_mapper
        glue_code: Glue code snippet from glue_code_generator
        resolutions: Conflict resolutions from conflict_resolver (optional)

    Returns:
        Execution result with status, files modified, validation results

    Raises:
        ValidationError: If validation fails after integration
        ConflictError: If conflicts cannot be resolved
        IntegrationError: If integration execution fails
    """
    config = load_extension_config()
    settings = config.get("intersection_executor", {})

    if not settings.get("enabled", False):
        return {"status": "disabled", "reason": "Intersection executor not enabled"}

    intersection_id = intersection.get("id", "unknown")
    target_file = intersection.get("target_file")
    integration_pattern = glue_code.get("pattern", "handoff_function")

    execution_log = []
    files_modified = []
    backup_paths = {}

    try:
        # Phase 1: Validate intersection is ready
        execution_log.append("Phase 1: Validating intersection readiness")
        if not _validate_intersection_ready(intersection):
            return {
                "intersection_id": intersection_id,
                "status": "not_ready",
                "reason": "Dependent batches not completed",
                "execution_log": "\n".join(execution_log),
            }

        # Phase 2: Create backups for rollback capability
        execution_log.append("Phase 2: Creating file backups")
        backup_paths = _create_backups(intersection, glue_code)

        # Phase 3: Apply conflict resolutions (if any)
        if resolutions:
            execution_log.append(f"Phase 3: Applying {len(resolutions)} conflict resolutions")
            _apply_conflict_resolutions(resolutions, execution_log)
            files_modified.extend([r.get("file") for r in resolutions if r.get("file")])

        # Phase 4: Inject glue code at target location
        execution_log.append(f"Phase 4: Injecting glue code ({integration_pattern})")
        injection_result = _inject_glue_code(
            target_file,
            glue_code,
            intersection,
            integration_pattern,
            execution_log,
        )

        if target_file not in files_modified:
            files_modified.append(target_file)

        # Phase 5: Run validation
        execution_log.append("Phase 5: Running validation")
        validation_result = _run_validation(
            target_file,
            glue_code.get("validation", {}),
            execution_log,
        )

        if not validation_result.get("passed", False):
            raise ValidationError(
                f"Validation failed: {validation_result.get('error', 'Unknown error')}"
            )

        # Success - clean up backups
        execution_log.append("Phase 6: Validation passed, cleaning up backups")
        _cleanup_backups(backup_paths)

        result = {
            "intersection_id": intersection_id,
            "status": "success",
            "files_modified": files_modified,
            "validation_result": validation_result,
            "execution_log": "\n".join(execution_log),
            "injection_details": injection_result,
        }

        # Persist execution result
        dump_jsonl(
            ARTIFACT_DIR / "executions.jsonl",
            {
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "execution": result,
            },
        )

        return result

    except (ValidationError, ConflictError, IntegrationError) as e:
        # Rollback on failure
        execution_log.append(f"ERROR: {type(e).__name__}: {str(e)}")
        execution_log.append("Phase X: Rolling back changes")

        _rollback_on_failure(backup_paths, execution_log)

        result = {
            "intersection_id": intersection_id,
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__,
            "files_modified": files_modified,
            "execution_log": "\n".join(execution_log),
        }

        # Persist failure
        dump_jsonl(
            ARTIFACT_DIR / "executions.jsonl",
            {
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "execution": result,
            },
        )

        return result

    except Exception as e:
        # Unexpected error - still rollback
        execution_log.append(f"UNEXPECTED ERROR: {type(e).__name__}: {str(e)}")
        execution_log.append("Phase X: Rolling back changes")

        _rollback_on_failure(backup_paths, execution_log)

        result = {
            "intersection_id": intersection_id,
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "files_modified": files_modified,
            "execution_log": "\n".join(execution_log),
        }

        dump_jsonl(
            ARTIFACT_DIR / "executions.jsonl",
            {
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "execution": result,
            },
        )

        return result


def _write_with_lock(path: Path, content: str, max_retries: int = 3) -> None:
    """
    Write file with exclusive lock and exponential backoff.

    Prevents race conditions when multiple batches modify same file.

    Args:
        path: File path to write
        content: Content to write
        max_retries: Maximum retry attempts (default: 3)

    Raises:
        IntegrationError: If lock cannot be acquired after retries
    """
    for attempt in range(max_retries):
        try:
            # Acquire exclusive lock with 30s timeout
            with portalocker.Lock(path, mode="w", timeout=30, flags=portalocker.LOCK_EX):
                with path.open("w", encoding="utf-8") as f:
                    f.write(content)
            return  # Success
        except portalocker.LockException:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                time.sleep(wait_time)
            else:
                raise IntegrationError(
                    f"Failed to acquire lock on {path} after {max_retries} attempts"
                )
        except Exception as e:
            raise IntegrationError(f"Failed to write {path}: {e}")


def _validate_intersection_ready(intersection: dict[str, Any]) -> bool:
    """
    Check if all dependent batches have completed.

    Args:
        intersection: Intersection definition with dependencies

    Returns:
        True if ready to execute, False otherwise
    """
    # Check if dependent batches are marked complete
    dependent_batches = intersection.get("dependent_batches", [])

    if not dependent_batches:
        return True  # No dependencies, ready to execute

    # Load batch completion status from elite_strategist logs
    strategist_log = CONFIG_PATH.parent.parent / "logs" / "run-history" / "elite_strategist" / "batch_plans.jsonl"

    if not strategist_log.exists():
        return True  # No log yet, assume ready

    try:
        with strategist_log.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return True

            # Get most recent batch plan
            latest_plan = json.loads(lines[-1])
            batch_plan = latest_plan.get("batch_plan", {})
            batches = batch_plan.get("batches", [])

            # Check if all dependent batches are complete
            completed_batches = {
                b.get("id") for b in batches if b.get("status") == "completed"
            }

            for dep_batch_id in dependent_batches:
                if dep_batch_id not in completed_batches:
                    return False  # Dependent batch not complete

            return True  # All dependencies satisfied

    except Exception:
        # If we can't read status, assume ready (fail open)
        return True


def _create_backups(
    intersection: dict[str, Any], glue_code: dict[str, Any]
) -> dict[str, Path]:
    """
    Create backups of files that will be modified.

    Args:
        intersection: Intersection definition
        glue_code: Glue code with target file info

    Returns:
        Map of original_path -> backup_path
    """
    backup_paths = {}
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    # Backup target file
    target_file = glue_code.get("target_file") or intersection.get("target_file")
    if target_file:
        target_path = Path(target_file)
        if target_path.exists():
            backup_path = BACKUP_DIR / f"{target_path.name}.{timestamp}.backup"
            shutil.copy2(target_path, backup_path)
            backup_paths[str(target_path)] = backup_path

    # Backup any additional files from intersection
    additional_files = intersection.get("files", [])
    for file_path in additional_files:
        path = Path(file_path)
        if path.exists() and str(path) not in backup_paths:
            backup_path = BACKUP_DIR / f"{path.name}.{timestamp}.backup"
            shutil.copy2(path, backup_path)
            backup_paths[str(path)] = backup_path

    return backup_paths


def _apply_conflict_resolutions(
    resolutions: list[dict[str, Any]], execution_log: list[str]
) -> None:
    """
    Apply conflict resolutions before glue code injection.

    Args:
        resolutions: List of conflict resolutions from conflict_resolver
        execution_log: Execution log to append messages
    """
    for resolution in resolutions:
        file_path = resolution.get("file")
        resolution_type = resolution.get("type", "merge")
        content = resolution.get("resolved_content")

        if not file_path or not content:
            execution_log.append(f"  SKIP: Invalid resolution for {file_path}")
            continue

        try:
            path = Path(file_path)
            if not path.exists():
                execution_log.append(f"  ERROR: File not found: {file_path}")
                raise ConflictError(f"File not found: {file_path}")

            # Write resolved content
            _write_with_lock(path, content)

            execution_log.append(f"  Applied {resolution_type} resolution to {file_path}")

        except Exception as e:
            execution_log.append(f"  ERROR: Failed to apply resolution to {file_path}: {e}")
            raise ConflictError(f"Failed to apply resolution: {e}")


def _inject_glue_code(
    target_file: str,
    glue_code: dict[str, Any],
    intersection: dict[str, Any],
    integration_pattern: str,
    execution_log: list[str],
) -> dict[str, Any]:
    """
    Inject glue code at exact target location.

    Args:
        target_file: Path to target file
        glue_code: Glue code snippet with content and metadata
        intersection: Intersection definition with location info
        integration_pattern: Type of integration (handoff_function, import_injection, etc.)
        execution_log: Execution log to append messages

    Returns:
        Injection details (lines inserted, location, etc.)

    Raises:
        IntegrationError: If injection fails
    """
    target_path = Path(target_file)

    if not target_path.exists():
        raise IntegrationError(f"Target file not found: {target_file}")

    code_snippet = glue_code.get("code", "")
    if not code_snippet:
        raise IntegrationError("Glue code snippet is empty")

    try:
        # Read current file content
        with target_path.open("r", encoding="utf-8") as f:
            original_content = f.read()

        # Apply integration based on pattern
        if integration_pattern == "handoff_function":
            modified_content = _inject_handoff_function(
                original_content, code_snippet, intersection
            )
        elif integration_pattern == "import_injection":
            modified_content = _inject_import(
                original_content, code_snippet, intersection
            )
        elif integration_pattern == "parameter_passthrough":
            modified_content = _inject_parameter_passthrough(
                original_content, code_snippet, intersection
            )
        elif integration_pattern == "type_adapter":
            modified_content = _inject_type_adapter(
                original_content, code_snippet, intersection
            )
        else:
            # Generic injection at specified line
            modified_content = _inject_at_line(
                original_content, code_snippet, intersection.get("line", 0)
            )

        # Write modified content
        _write_with_lock(target_path, modified_content)

        # Calculate diff stats
        lines_added = code_snippet.count("\n") + 1
        location = intersection.get("line", "end")

        execution_log.append(
            f"  Injected {lines_added} lines at {target_file}:{location}"
        )

        return {
            "pattern": integration_pattern,
            "lines_added": lines_added,
            "location": location,
            "target_file": target_file,
        }

    except Exception as e:
        execution_log.append(f"  ERROR: Injection failed: {e}")
        raise IntegrationError(f"Failed to inject glue code: {e}")


def _inject_handoff_function(
    content: str, code_snippet: str, intersection: dict[str, Any]
) -> str:
    """
    Inject a new handoff function at intersection point.

    Uses AST manipulation for safe insertion.
    """
    try:
        tree = ast.parse(content)

        # Find insertion point (after last function or at end)
        last_function_line = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, "end_lineno") and node.end_lineno:
                    last_function_line = max(last_function_line, node.end_lineno)

        # Insert after last function
        lines = content.splitlines()
        target_line = intersection.get("line", last_function_line)

        if target_line == 0:
            target_line = len(lines)

        # Insert with proper spacing
        lines.insert(target_line, "\n")
        lines.insert(target_line + 1, code_snippet)

        return "\n".join(lines)

    except SyntaxError:
        # Fallback to simple line insertion
        return _inject_at_line(content, code_snippet, intersection.get("line", 0))


def _inject_import(
    content: str, code_snippet: str, intersection: dict[str, Any]
) -> str:
    """
    Inject import statement at top of file (after module docstring).

    Uses AST to find correct insertion point.
    """
    try:
        tree = ast.parse(content)

        # Find last import statement
        last_import_line = 0
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if hasattr(node, "end_lineno") and node.end_lineno:
                    last_import_line = node.end_lineno

        # If no imports, insert after module docstring
        if last_import_line == 0 and tree.body:
            first_node = tree.body[0]
            if isinstance(first_node, ast.Expr) and isinstance(
                first_node.value, ast.Constant
            ):
                if hasattr(first_node, "end_lineno") and first_node.end_lineno:
                    last_import_line = first_node.end_lineno

        # Insert import
        lines = content.splitlines()
        target_line = last_import_line

        lines.insert(target_line, code_snippet)

        return "\n".join(lines)

    except SyntaxError:
        # Fallback to top of file insertion
        return code_snippet + "\n\n" + content


def _inject_parameter_passthrough(
    content: str, code_snippet: str, intersection: dict[str, Any]
) -> str:
    """
    Modify function call sites to pass new parameters.

    Uses AST to find and modify function calls.
    """
    target_function = intersection.get("target_function")

    if not target_function:
        # Fallback to simple injection
        return _inject_at_line(content, code_snippet, intersection.get("line", 0))

    try:
        tree = ast.parse(content)
        modified = False

        # Find function calls matching target
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, "id") and node.func.id == target_function:
                    # Found target function call - need to modify
                    # For simplicity, we'll use line-based replacement
                    if hasattr(node, "lineno"):
                        lines = content.splitlines()
                        target_line = node.lineno - 1
                        lines[target_line] = code_snippet
                        modified = True
                        return "\n".join(lines)

        if not modified:
            # Function not found, fallback to injection
            return _inject_at_line(content, code_snippet, intersection.get("line", 0))

    except SyntaxError:
        return _inject_at_line(content, code_snippet, intersection.get("line", 0))

    return content


def _inject_type_adapter(
    content: str, code_snippet: str, intersection: dict[str, Any]
) -> str:
    """
    Add type conversion wrapper at intersection point.

    Similar to handoff_function but focuses on type adapters.
    """
    return _inject_handoff_function(content, code_snippet, intersection)


def _inject_at_line(content: str, code_snippet: str, line: int) -> str:
    """
    Generic injection at specified line number.

    Args:
        content: Original file content
        code_snippet: Code to inject
        line: Line number (0 = append to end)

    Returns:
        Modified content
    """
    lines = content.splitlines()

    if line == 0 or line > len(lines):
        # Append to end
        lines.append("")
        lines.append(code_snippet)
    else:
        # Insert at specified line
        lines.insert(line - 1, code_snippet)

    return "\n".join(lines)


def _run_validation(
    target_file: str,
    validation_config: dict[str, Any],
    execution_log: list[str],
) -> dict[str, Any]:
    """
    Run validation command to verify integration.

    Args:
        target_file: Path to modified file
        validation_config: Validation configuration with command
        execution_log: Execution log to append messages

    Returns:
        Validation result with pass/fail status

    Raises:
        ValidationError: If validation command fails
    """
    command = validation_config.get("command")

    if not command:
        # Default validation: Python syntax check
        command = f"python -m py_compile {target_file}"

    try:
        # Run validation with timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
        )

        passed = result.returncode == 0

        execution_log.append(f"  Validation command: {command}")
        execution_log.append(f"  Exit code: {result.returncode}")

        if not passed:
            execution_log.append(f"  STDERR: {result.stderr}")

        return {
            "command": command,
            "returncode": result.returncode,
            "passed": passed,
            "stdout": result.stdout[:500] if result.stdout else "",  # Limit output
            "stderr": result.stderr[:500] if result.stderr else "",
        }

    except subprocess.TimeoutExpired:
        execution_log.append(f"  ERROR: Validation timeout (60s)")
        return {
            "command": command,
            "returncode": -1,
            "passed": False,
            "error": "Validation timeout (60s)",
        }

    except Exception as e:
        execution_log.append(f"  ERROR: Validation failed: {e}")
        return {
            "command": command,
            "returncode": -1,
            "passed": False,
            "error": str(e),
        }


def _rollback_on_failure(backup_paths: dict[str, Path], execution_log: list[str]) -> None:
    """
    Rollback changes by restoring from backups.

    Args:
        backup_paths: Map of original_path -> backup_path
        execution_log: Execution log to append messages
    """
    for original_path, backup_path in backup_paths.items():
        try:
            if backup_path.exists():
                shutil.copy2(backup_path, original_path)
                execution_log.append(f"  Restored {original_path} from backup")
            else:
                execution_log.append(f"  WARNING: Backup not found for {original_path}")
        except Exception as e:
            execution_log.append(f"  ERROR: Failed to restore {original_path}: {e}")


def _cleanup_backups(backup_paths: dict[str, Path]) -> None:
    """
    Clean up backup files after successful execution.

    Args:
        backup_paths: Map of original_path -> backup_path
    """
    for backup_path in backup_paths.values():
        try:
            if backup_path.exists():
                backup_path.unlink()
        except Exception:
            pass  # Ignore cleanup errors


def run(
    intersection: dict[str, Any],
    glue_code: dict[str, Any],
    resolutions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Public API for executing intersection integration.

    Args:
        intersection: Intersection definition
        glue_code: Glue code snippet
        resolutions: Optional conflict resolutions

    Returns:
        Execution result
    """
    return execute(intersection, glue_code, resolutions or [])


def cli() -> None:
    """CLI entry point for testing."""
    print("Intersection Executor - ARMANI Squad Extension #5")
    print("Usage: Call run() with intersection and glue_code dictionaries")
