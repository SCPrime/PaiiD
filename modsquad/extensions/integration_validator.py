"""Integration validator extension for MOD SQUAD - ARMANI squad #6.

This extension validates woven integrations from intersection_executor to ensure
that code integrations succeeded and are safe to deploy. It performs smoke tests
across multiple validation layers: syntax, type checking, imports, function signatures,
and unit tests.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import py_compile
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "integration_validator"


def validate(integration_result: dict[str, Any]) -> dict[str, Any]:
    """
    Validate that integration succeeded and is safe to deploy.

    Performs 5-layer validation:
    1. Syntax validation (MUST pass - blocking)
    2. Type checking (SHOULD pass - warning)
    3. Import resolution (MUST pass - blocking)
    4. Function signature compatibility (MUST pass - blocking)
    5. Test execution (SHOULD pass - warning)

    Args:
        integration_result: Result dictionary from intersection_executor containing
                          modified files, integration metadata, and change details.

    Returns:
        Validation report with pass/fail status, layer-by-layer results,
        blocking issues, and warnings.
    """
    integration_id = integration_result.get("integration_id", "unknown")
    modified_files = integration_result.get("modified_files", [])

    validation_result: dict[str, Any] = {
        "integration_id": integration_id,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "passed",  # Assume success, update if failures occur
        "layers": {},
        "blocking_issues": [],
        "warnings": [],
    }

    # Layer 1: Syntax validation (BLOCKING)
    syntax_result = _validate_syntax(modified_files)
    validation_result["layers"]["syntax"] = syntax_result
    if syntax_result["status"] == "failed":
        validation_result["status"] = "failed"
        validation_result["blocking_issues"].append("Syntax errors detected")

    # Layer 2: Type checking (WARNING)
    types_result = _validate_types(modified_files)
    validation_result["layers"]["types"] = types_result
    if types_result["status"] == "failed":
        validation_result["warnings"].append(
            f"Type checking issues: {types_result.get('error', 'Unknown error')}"
        )

    # Layer 3: Import resolution (BLOCKING)
    imports_result = _validate_imports(modified_files)
    validation_result["layers"]["imports"] = imports_result
    if imports_result["status"] == "failed":
        validation_result["status"] = "failed"
        validation_result["blocking_issues"].append("Unresolved imports")

    # Layer 4: Function signature compatibility (BLOCKING)
    signatures_result = _validate_function_signatures(modified_files)
    validation_result["layers"]["function_signatures"] = signatures_result
    if signatures_result["status"] == "failed":
        validation_result["status"] = "failed"
        validation_result["blocking_issues"].append("Type contract violation")

    # Layer 5: Unit tests (WARNING)
    tests_result = _run_unit_tests(modified_files)
    validation_result["layers"]["unit_tests"] = tests_result
    if tests_result["status"] == "failed":
        validation_result["warnings"].append(
            f"Unit test failures: {tests_result.get('tests_passed')}/{tests_result.get('tests_run')}"
        )

    # Persist validation results
    dump_jsonl(
        ARTIFACT_DIR / "validations.jsonl",
        validation_result,
    )

    return validation_result


def _validate_syntax(modified_files: list[str]) -> dict[str, Any]:
    """
    Validate Python syntax using py_compile.

    Args:
        modified_files: List of file paths that were modified during integration.

    Returns:
        Result dict with status (passed/failed/skipped), files_checked count,
        and any syntax errors detected.
    """
    python_files = [f for f in modified_files if f.endswith(".py")]

    if not python_files:
        return {
            "status": "skipped",
            "files_checked": 0,
            "reason": "No Python files to validate",
        }

    files_checked = 0
    errors = []
    repo_root = CONFIG_PATH.parent.parent

    for file_path in python_files:
        abs_path = repo_root / file_path if not Path(file_path).is_absolute() else Path(file_path)

        if not abs_path.exists():
            errors.append(f"{file_path}: File not found")
            continue

        try:
            py_compile.compile(str(abs_path), doraise=True)
            files_checked += 1
        except py_compile.PyCompileError as exc:
            errors.append(f"{file_path}: {exc.msg}")

    status = "failed" if errors else "passed"
    result = {
        "status": status,
        "files_checked": files_checked,
    }

    if errors:
        result["errors"] = errors[:10]  # Limit to first 10 errors
        result["error_count"] = len(errors)

    return result


def _validate_types(modified_files: list[str]) -> dict[str, Any]:
    """
    Validate type hints using mypy if available.

    Args:
        modified_files: List of file paths that were modified during integration.

    Returns:
        Result dict with status (passed/failed/skipped), mypy score,
        and any type errors detected.
    """
    python_files = [f for f in modified_files if f.endswith(".py")]

    if not python_files:
        return {
            "status": "skipped",
            "files_checked": 0,
            "reason": "No Python files to validate",
        }

    # Check if mypy is available
    try:
        subprocess.run(
            ["mypy", "--version"],
            capture_output=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {
            "status": "skipped",
            "reason": "mypy not installed",
        }

    repo_root = CONFIG_PATH.parent.parent
    abs_files = []

    for file_path in python_files:
        abs_path = repo_root / file_path if not Path(file_path).is_absolute() else Path(file_path)
        if abs_path.exists():
            abs_files.append(str(abs_path))

    if not abs_files:
        return {
            "status": "skipped",
            "reason": "No valid Python files found",
        }

    try:
        cmd = ["mypy", "--no-error-summary"] + abs_files
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=repo_root,
        )

        # mypy returns 0 if no errors, 1 if errors found
        status = "passed" if completed.returncode == 0 else "failed"

        result = {
            "status": status,
            "files_checked": len(abs_files),
            "returncode": completed.returncode,
        }

        if completed.returncode != 0:
            result["error"] = completed.stdout[:1000]  # First 1000 chars
        else:
            result["mypy_score"] = "100%"

        return result

    except subprocess.TimeoutExpired:
        return {
            "status": "failed",
            "error": "mypy timed out after 60 seconds",
        }
    except Exception as exc:
        return {
            "status": "failed",
            "error": str(exc),
        }


def _validate_imports(modified_files: list[str]) -> dict[str, Any]:
    """
    Validate that all imports in modified files can be resolved.

    Uses AST parsing to extract imports and attempts to resolve each one
    using importlib to verify the module exists.

    Args:
        modified_files: List of file paths that were modified during integration.

    Returns:
        Result dict with status (passed/failed/skipped), imports_resolved count,
        and any unresolved imports.
    """
    python_files = [f for f in modified_files if f.endswith(".py")]

    if not python_files:
        return {
            "status": "skipped",
            "imports_resolved": 0,
            "reason": "No Python files to validate",
        }

    repo_root = CONFIG_PATH.parent.parent
    total_imports = 0
    unresolved = []

    # Add repo root to sys.path for local imports
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    for file_path in python_files:
        abs_path = repo_root / file_path if not Path(file_path).is_absolute() else Path(file_path)

        if not abs_path.exists():
            unresolved.append(f"{file_path}: File not found")
            continue

        try:
            with abs_path.open("r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(abs_path))
        except SyntaxError as exc:
            unresolved.append(f"{file_path}: Syntax error (line {exc.lineno})")
            continue

        # Extract all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    total_imports += 1
                    if not _can_resolve_import(alias.name):
                        unresolved.append(f"{file_path}: Cannot import '{alias.name}'")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    total_imports += 1
                    if not _can_resolve_import(node.module):
                        unresolved.append(f"{file_path}: Cannot import from '{node.module}'")

    status = "failed" if unresolved else "passed"
    result = {
        "status": status,
        "imports_resolved": total_imports - len(unresolved),
        "total_imports": total_imports,
    }

    if unresolved:
        result["unresolved"] = unresolved[:10]  # Limit to first 10
        result["unresolved_count"] = len(unresolved)

    return result


def _can_resolve_import(module_name: str) -> bool:
    """
    Check if a module can be imported.

    Args:
        module_name: The module name to check (e.g., "os", "pathlib", "app.models").

    Returns:
        True if the module can be found, False otherwise.
    """
    try:
        # Try to find the module spec
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, ModuleNotFoundError, ValueError, AttributeError):
        # ValueError can occur for relative imports
        # AttributeError can occur for namespace packages
        return False


def _validate_function_signatures(modified_files: list[str]) -> dict[str, Any]:
    """
    Validate function signature compatibility by checking type hints match call sites.

    This is a simplified version that checks:
    1. Functions with type hints are properly defined
    2. No obvious signature mismatches in the same file

    Args:
        modified_files: List of file paths that were modified during integration.

    Returns:
        Result dict with status (passed/failed/skipped), calls_validated count,
        and any signature mismatches detected.
    """
    python_files = [f for f in modified_files if f.endswith(".py")]

    if not python_files:
        return {
            "status": "skipped",
            "calls_validated": 0,
            "reason": "No Python files to validate",
        }

    repo_root = CONFIG_PATH.parent.parent
    calls_validated = 0
    mismatches = []

    for file_path in python_files:
        abs_path = repo_root / file_path if not Path(file_path).is_absolute() else Path(file_path)

        if not abs_path.exists():
            mismatches.append(f"{file_path}: File not found")
            continue

        try:
            with abs_path.open("r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(abs_path))
        except SyntaxError as exc:
            mismatches.append(f"{file_path}: Syntax error (line {exc.lineno})")
            continue

        # Extract function definitions with type hints
        functions = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count parameters (excluding self for methods)
                params = [arg for arg in node.args.args if arg.arg != "self"]
                functions[node.name] = {
                    "param_count": len(params),
                    "has_return_type": node.returns is not None,
                }

        # Check function calls against definitions in same file
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in functions:
                        calls_validated += 1
                        expected = functions[func_name]["param_count"]
                        actual = len(node.args)

                        # Simple check: does arg count match?
                        # Note: This is simplified and doesn't handle *args, **kwargs
                        if actual != expected:
                            mismatches.append(
                                f"{file_path}: {func_name}() expects {expected} args, got {actual}"
                            )

    status = "failed" if mismatches else "passed"
    result = {
        "status": status,
        "calls_validated": calls_validated,
    }

    if mismatches:
        result["mismatches"] = mismatches[:10]  # Limit to first 10
        result["mismatch_count"] = len(mismatches)

    return result


def _run_unit_tests(modified_files: list[str]) -> dict[str, Any]:
    """
    Run relevant unit tests for modified files.

    Discovers tests by looking for test_{module_name}.py files corresponding
    to modified modules. Runs only relevant tests, not the full suite.

    Args:
        modified_files: List of file paths that were modified during integration.

    Returns:
        Result dict with status (passed/failed/skipped), tests_run count,
        tests_passed count, and any test failures.
    """
    python_files = [f for f in modified_files if f.endswith(".py")]

    if not python_files:
        return {
            "status": "skipped",
            "tests_run": 0,
            "tests_passed": 0,
            "reason": "No Python files to test",
        }

    # Check if pytest is available
    try:
        subprocess.run(
            ["pytest", "--version"],
            capture_output=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {
            "status": "skipped",
            "reason": "pytest not installed",
        }

    repo_root = CONFIG_PATH.parent.parent
    test_files = _discover_relevant_tests(python_files, repo_root)

    if not test_files:
        return {
            "status": "skipped",
            "tests_run": 0,
            "tests_passed": 0,
            "reason": "No relevant test files found",
        }

    tests_run = 0
    tests_passed = 0
    failures = []

    for test_file in test_files:
        try:
            cmd = ["pytest", str(test_file), "-v", "--tb=short"]
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,  # 180 seconds per test file
                cwd=repo_root,
            )

            # Parse output for test counts (simplified)
            output = completed.stdout
            if "passed" in output or "failed" in output:
                # Extract test counts from pytest output
                # Format: "X passed" or "X failed, Y passed"
                import re
                passed_match = re.search(r"(\d+) passed", output)
                failed_match = re.search(r"(\d+) failed", output)

                if passed_match:
                    count = int(passed_match.group(1))
                    tests_passed += count
                    tests_run += count

                if failed_match:
                    count = int(failed_match.group(1))
                    tests_run += count
                    failures.append(f"{test_file.name}: {count} failed")

            if completed.returncode != 0 and not failed_match:
                failures.append(f"{test_file.name}: Test execution error")

        except subprocess.TimeoutExpired:
            failures.append(f"{test_file.name}: Timeout after 180s")
        except Exception as exc:
            failures.append(f"{test_file.name}: {str(exc)}")

    status = "failed" if failures else "passed"
    result = {
        "status": status,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }

    if failures:
        result["failures"] = failures[:10]  # Limit to first 10
        result["failure_count"] = len(failures)

    return result


def _discover_relevant_tests(python_files: list[str], repo_root: Path) -> list[Path]:
    """
    Discover test files relevant to the modified Python files.

    Looks for test_{module_name}.py files in common test directories.

    Args:
        python_files: List of modified Python file paths.
        repo_root: Root directory of the repository.

    Returns:
        List of Path objects for relevant test files that exist.
    """
    test_files = []

    for file_path in python_files:
        path = Path(file_path)
        module_name = path.stem  # filename without extension

        # Skip test files themselves
        if module_name.startswith("test_"):
            continue

        # Look for test_{module_name}.py in various locations
        test_candidates = [
            repo_root / "tests" / f"test_{module_name}.py",
            repo_root / path.parent / "tests" / f"test_{module_name}.py",
            repo_root / path.parent / f"test_{module_name}.py",
        ]

        # For files in subdirectories like backend/app/routers/orders.py
        # look in backend/tests/test_orders.py
        if "backend" in path.parts:
            test_candidates.append(repo_root / "backend" / "tests" / f"test_{module_name}.py")

        if "frontend" in path.parts:
            test_candidates.append(repo_root / "frontend" / "__tests__" / f"{module_name}.test.tsx")
            test_candidates.append(repo_root / "frontend" / "__tests__" / f"{module_name}.test.ts")

        for candidate in test_candidates:
            if candidate.exists() and candidate not in test_files:
                test_files.append(candidate)

    return test_files


def _enforce_guardrails(validation_result: dict[str, Any], config: dict[str, Any]) -> None:
    """
    Enforce guardrail policy for integration validation.

    Exits with code 1 if validation failed and block_on_integration_fail=true.

    Args:
        validation_result: The validation result from validate().
        config: Configuration dict with guardrail settings.
    """
    status = validation_result.get("status")

    if status != "failed":
        return

    # Check if block_on_integration_fail is enabled (default: True)
    block_on_fail = config.get("block_on_integration_fail", True)

    if block_on_fail:
        import sys

        print("INTEGRATION VALIDATION FAILED (block_on_integration_fail=true)")
        print(f"   Integration ID: {validation_result.get('integration_id')}")

        blocking_issues = validation_result.get("blocking_issues", [])
        if blocking_issues:
            print(f"   Blocking issues: {', '.join(blocking_issues)}")

        print("   Blocking deployment due to guardrail policy")
        sys.exit(1)


def run() -> dict[str, Any]:
    """
    Execute integration validation from MOD SQUAD configuration.

    Loads configuration, validates integrations, and enforces guardrails.

    Returns:
        Validation result dictionary.
    """
    config = load_extension_config()
    settings = config.get("integration_validator")

    if not settings or not settings.get("enabled", False):
        result = {
            "status": "skipped",
            "reason": "integration_validator not enabled in configuration",
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        dump_jsonl(ARTIFACT_DIR / "validations.jsonl", result)
        return result

    # For now, create a mock integration result since intersection_executor doesn't exist yet
    # In production, this would receive the actual integration result
    mock_integration = {
        "integration_id": "manual_validation",
        "modified_files": _get_modified_files_from_git(),
    }

    validation_result = validate(mock_integration)

    # Enforce guardrails
    _enforce_guardrails(validation_result, settings)

    return validation_result


def _get_modified_files_from_git() -> list[str]:
    """
    Get list of modified files from git status.

    Returns:
        List of modified file paths relative to repo root.
    """
    try:
        repo_root = CONFIG_PATH.parent.parent
        cmd = ["git", "diff", "--name-only", "HEAD"]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=repo_root,
        )

        if completed.returncode == 0:
            files = [f.strip() for f in completed.stdout.split("\n") if f.strip()]
            return files

        return []

    except Exception:
        return []


def cli() -> None:
    """Command-line interface for integration validator."""
    result = run()
    exit_code = 0 if result["status"] in ("passed", "skipped") else 1
    sys.exit(exit_code)


__all__ = ["validate", "run", "cli"]
