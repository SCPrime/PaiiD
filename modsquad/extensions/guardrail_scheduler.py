"""Guardrail scheduler for MOD SQUAD automated validation."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "guardrail_scheduler"


def run() -> None:
    """Execute scheduled guardrail checks."""

    config = load_extension_config()
    settings = config.get("guardrail_scheduler")
    if not settings or not settings.get("enabled", False):
        return

    runs: list[str] = settings.get("runs", [])
    results: list[dict[str, Any]] = []

    for check_name in runs:
        result = _run_check(check_name)
        results.append(result)

    dump_jsonl(
        ARTIFACT_DIR / "guardrail_scheduler.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "scheduled_checks": runs,
            "results": results,
        },
    )


def _run_check(check_name: str) -> dict[str, Any]:
    """Run individual guardrail check."""
    try:
        cmd = ["python", "-m", f"modsquad.extensions.{check_name}"]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "check": check_name,
            "status": "passed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "output": completed.stdout[:500],
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "check": check_name,
            "status": "error",
            "error": str(exc),
        }


def cli() -> None:
    run()


__all__ = ["run"]
