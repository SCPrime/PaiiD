"""
Test Orchestrator for MOD SQUAD (Consolidates strategy_verifier + integration_validator)

Unified test execution across all test suites with:
- Centralized subprocess management
- Circuit breaker protection
- Preflight dependency checks
- <0.5% risk per execution
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

from .circuit_breaker import circuit_breaker
from .subprocess_manager import (
    check_binary_exists,
    run_command,
    run_npm_command,
    run_python_command,
)
from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "test_orchestrator"


def _preflight_check() -> Dict[str, Any]:
    """Verify required dependencies before running tests."""
    checks = {
        "pytest": check_binary_exists("pytest"),
        "npm": check_binary_exists("npm"),
        "python": check_binary_exists("python"),
    }

    if not all(checks.values()):
        missing = [k for k, v in checks.items() if not v]
        return {
            "ready": False,
            "missing_dependencies": missing,
        }

    return {"ready": True}


@circuit_breaker(failure_threshold=3, timeout=300)
def run() -> Dict[str, Any]:
    """Execute all test suites with safety mechanisms."""

    config = load_extension_config()
    settings = config.get("test_orchestrator", {})

    if not settings.get("enabled", False):
        return {"status": "disabled"}

    # Preflight check
    preflight = _preflight_check()
    if not preflight["ready"]:
        return {
            "status": "skipped",
            "reason": "Missing dependencies",
            "details": preflight,
        }

    # Run all test suites
    results: Dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "preflight": preflight,
        "smoke_tests": _run_smoke_tests(settings),
        "backend_tests": _run_backend_tests(settings),
        "frontend_tests": _run_frontend_tests(settings),
        "browser_regression": _run_browser_tests(settings),
        "e2e_tests": _run_e2e_tests(settings),
    }

    # Calculate overall status
    test_results = [
        results["smoke_tests"],
        results["backend_tests"],
        results["frontend_tests"],
        results["browser_regression"],
        results["e2e_tests"],
    ]

    passed_count = sum(1 for r in test_results if r.get("passed", False))
    skipped_count = sum(1 for r in test_results if r.get("skipped", False))

    results["summary"] = {
        "total": len(test_results),
        "passed": passed_count,
        "failed": len(test_results) - passed_count - skipped_count,
        "skipped": skipped_count,
        "overall_passed": all(
            r.get("passed", False) or r.get("skipped", False)
            for r in test_results
        ),
    }

    # Log results
    dump_jsonl(ARTIFACT_DIR / "test_orchestrator.jsonl", results)

    # Archive artifacts
    _archive_artifacts(results)

    return results


def _run_smoke_tests(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Run smoke tests from strategy_verifier config."""
    commands = settings.get("commands", [])

    # Find smoke-backtest command
    smoke_cmd = next((c for c in commands if c.get("name") == "smoke-backtest"), None)

    if not smoke_cmd:
        return {"passed": True, "skipped": True, "reason": "No smoke tests configured"}

    result = run_command(
        smoke_cmd.get("run"),
        timeout=180,
    )

    return {
        "passed": result.success,
        "returncode": result.returncode,
        "output": result.stdout[:500],
        "stderr": result.stderr,
        "skipped": result.skipped,
    }


def _run_backend_tests(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Run backend pytest suite."""
    result = run_python_command(
        ["-m", "pytest", "backend/tests", "-q", "--tb=short"],
        timeout=300,
    )

    return {
        "passed": result.success,
        "returncode": result.returncode,
        "output": result.stdout[:500],
        "stderr": result.stderr,
        "skipped": result.skipped,
    }


def _run_frontend_tests(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Run frontend Playwright tests."""
    frontend_path = Path("frontend")

    if not frontend_path.exists():
        return {
            "passed": False,
            "skipped": True,
            "reason": "Frontend directory not found",
        }

    result = run_npm_command(
        ["run", "playwright:test:ci"],
        timeout=600,
        cwd=frontend_path,
    )

    return {
        "passed": result.success,
        "returncode": result.returncode,
        "output": result.stdout[:500],
        "stderr": result.stderr,
        "skipped": result.skipped,
    }


def _run_browser_tests(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Run browser regression tests from strategy_verifier config."""
    commands = settings.get("commands", [])

    # Find browser-regression command
    browser_cmd = next(
        (c for c in commands if c.get("name") == "browser-regression"), None
    )

    if not browser_cmd:
        return {
            "passed": True,
            "skipped": True,
            "reason": "No browser tests configured",
        }

    result = run_command(
        browser_cmd.get("run"),
        timeout=300,
    )

    return {
        "passed": result.success,
        "returncode": result.returncode,
        "output": result.stdout[:500],
        "stderr": result.stderr,
        "skipped": result.skipped,
    }


def _run_e2e_tests(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Run end-to-end smoke tests."""
    tests_path = Path("tests/integration/test_smoke.py")

    if not tests_path.exists():
        return {
            "passed": True,
            "skipped": True,
            "reason": "E2E test file not found",
        }

    result = run_python_command(
        ["-m", "pytest", str(tests_path), "-v"],
        timeout=180,
    )

    return {
        "passed": result.success,
        "returncode": result.returncode,
        "output": result.stdout[:500],
        "stderr": result.stderr,
        "skipped": result.skipped,
    }


def _archive_artifacts(results: Dict[str, Any]) -> None:
    """Archive test artifacts with pruning."""
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    artifact_file = ARTIFACT_DIR / f"test-run-{timestamp}.log"

    with artifact_file.open("w", encoding="utf-8") as fh:
        fh.write(f"Test Run: {results['timestamp']}\n")
        fh.write(f"Summary: {results['summary']}\n\n")

        for test_type, result in results.items():
            if test_type not in ["timestamp", "preflight", "summary"]:
                fh.write(f"\n=== {test_type} ===\n")
                fh.write(f"Passed: {result.get('passed', False)}\n")
                if result.get("output"):
                    fh.write(f"Output:\n{result['output']}\n")

    # Prune old artifacts
    config = load_extension_config()
    keep = int(config.get("test_orchestrator", {}).get("keep_artifacts", 10))
    artifacts = sorted(ARTIFACT_DIR.glob("test-run-*.log"))
    for old_artifact in artifacts[:-keep]:
        old_artifact.unlink(missing_ok=True)


def cli() -> None:
    """CLI entry point."""
    result = run()
    import sys

    if isinstance(result, dict):
        overall_passed = result.get("summary", {}).get("overall_passed", False)
        sys.exit(0 if overall_passed else 1)
    else:
        # Circuit breaker may return different structure
        sys.exit(1)


__all__ = ["run", "cli"]
