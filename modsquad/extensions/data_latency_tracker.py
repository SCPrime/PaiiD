"""Data latency tracker for MOD SQUAD live data monitoring."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "data_latency_tracker"


def run() -> None:
    """Monitor live data flows and track latency."""

    config = load_extension_config()
    settings = config.get("data_latency_tracker")
    if not settings or not settings.get("enabled", False):
        return

    script_path = settings.get("script", "scripts/live_data_flows.py")
    result = _run_latency_check(script_path)

    dump_jsonl(
        ARTIFACT_DIR / "data_latency.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "result": result,
        },
    )


def _run_latency_check(script_path: str) -> dict[str, Any]:
    """Execute live data flows check."""
    try:
        cmd = ["python", script_path]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        return {
            "script": script_path,
            "status": "passed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "output": completed.stdout[:1000],
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "script": script_path,
            "status": "error",
            "error": str(exc),
        }


def cli() -> None:
    run()


__all__ = ["run"]
