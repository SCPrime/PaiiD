"""Documentation sync for MOD SQUAD docs consistency tracking."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "docs_sync"


def run() -> None:
    """Check documentation synchronization status."""

    config = load_extension_config()
    settings = config.get("docs_sync")
    if not settings or not settings.get("enabled", False):
        return

    watch_paths: list[str] = settings.get("watch_paths", ["docs", "modsquad"])
    results: list[dict[str, Any]] = []

    for path in watch_paths:
        result = _check_docs_path(path)
        results.append(result)

    dump_jsonl(
        ARTIFACT_DIR / "docs_sync.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "watch_paths": watch_paths,
            "results": results,
        },
    )


def _check_docs_path(path: str) -> dict[str, Any]:
    """Check if documentation path is in sync."""
    try:
        # Count markdown files
        resolved_path = Path(path).resolve()
        if not resolved_path.exists():
            return {
                "path": path,
                "status": "not_found",
                "files": 0,
            }

        md_files = list(resolved_path.rglob("*.md"))

        # Check for uncommitted changes
        cmd = ["git", "diff", "--name-only", "HEAD", "--", path]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        uncommitted = completed.stdout.strip().split("\n") if completed.stdout.strip() else []

        return {
            "path": path,
            "status": "synced" if not uncommitted else "pending",
            "markdown_files": len(md_files),
            "uncommitted_changes": len(uncommitted),
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "path": path,
            "status": "error",
            "error": str(exc),
        }


def cli() -> None:
    run()


__all__ = ["run"]
