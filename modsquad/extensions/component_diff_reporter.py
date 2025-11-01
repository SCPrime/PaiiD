"""Component diff reporter for MOD SQUAD change tracking."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "component_diff_reporter"


def run() -> None:
    """Track component changes and generate diff report."""

    config = load_extension_config()
    settings = config.get("component_diff_reporter")
    if not settings or not settings.get("enabled", False):
        return

    component_dirs = [
        "frontend/components",
        "frontend/pages",
        "backend/app/routers",
    ]

    diffs: list[dict[str, Any]] = []
    for directory in component_dirs:
        diff = _get_git_diff(directory)
        if diff:
            diffs.append(diff)

    dump_jsonl(
        ARTIFACT_DIR / "component_diff.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "scanned_directories": component_dirs,
            "changes": diffs,
        },
    )


def _get_git_diff(directory: str) -> dict[str, Any] | None:
    """Get git diff for directory."""
    try:
        cmd = ["git", "diff", "--stat", "HEAD~1", "HEAD", "--", directory]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if completed.returncode == 0 and completed.stdout.strip():
            return {
                "directory": directory,
                "stat": completed.stdout[:500],
                "files_changed": completed.stdout.count("| "),
            }
        return None
    except Exception:  # pragma: no cover - subprocess safety
        return None


def cli() -> None:
    run()


__all__ = ["run"]
