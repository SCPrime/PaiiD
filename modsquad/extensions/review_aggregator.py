"""Review aggregator for MOD SQUAD multi-stream reporting."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "review_aggregator"


def run() -> None:
    """Aggregate reports from multiple MOD SQUAD extensions."""

    config = load_extension_config()
    settings = config.get("review_aggregator")
    if not settings or not settings.get("enabled", False):
        return

    sources: list[str] = settings.get("sources", [])
    aggregated: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "sources": sources,
        "reports": [],
    }

    logs_dir = CONFIG_PATH.parent.parent / "logs" / "run-history"

    for source in sources:
        source_dir = logs_dir / source
        if source_dir.exists():
            latest = _get_latest_report(source_dir)
            if latest:
                aggregated["reports"].append({
                    "source": source,
                    "data": latest,
                })

    dump_jsonl(ARTIFACT_DIR / "review_aggregator.jsonl", aggregated)


def _get_latest_report(source_dir: Path) -> dict[str, Any] | None:
    """Get latest report from source directory."""
    try:
        jsonl_files = list(source_dir.glob("*.jsonl"))
        if not jsonl_files:
            return None

        latest_file = max(jsonl_files, key=lambda p: p.stat().st_mtime)

        # Read last line of JSONL
        with latest_file.open("r", encoding="utf-8") as fh:
            lines = fh.readlines()
            if lines:
                return json.loads(lines[-1])
        return None
    except Exception:  # pragma: no cover - file I/O safety
        return None


def cli() -> None:
    run()


__all__ = ["run"]
