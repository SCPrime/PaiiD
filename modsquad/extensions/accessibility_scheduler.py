"""Accessibility scheduler for MOD SQUAD a11y validation."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "accessibility_scheduler"


def run() -> None:
    """Run scheduled accessibility checks."""

    config = load_extension_config()
    settings = config.get("accessibility_scheduler")
    if not settings or not settings.get("enabled", False):
        return

    targets: list[str] = settings.get("targets", ["frontend/components"])
    results: list[dict[str, Any]] = []

    for target in targets:
        result = _check_target(target)
        results.append(result)

    dump_jsonl(
        ARTIFACT_DIR / "accessibility_scheduler.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "targets": targets,
            "results": results,
        },
    )


def _check_target(target: str) -> dict[str, Any]:
    """Run accessibility checks on target directory."""
    try:
        # Run the branding a11y checks script
        cmd = ["python", "scripts/branding_a11y_checks.py"]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        return {
            "target": target,
            "status": "passed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "output": completed.stdout[:500],
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "target": target,
            "status": "error",
            "error": str(exc),
        }


def cli() -> None:
    run()


__all__ = ["run"]
