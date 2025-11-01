"""Quality inspector for MOD SQUAD overall quality assessment."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "quality_inspector"


def run() -> None:
    """Inspect overall quality metrics across all streams."""

    config = load_extension_config()
    settings = config.get("quality_inspector")
    if not settings or not settings.get("enabled", False):
        return

    inputs: list[str] = settings.get("inputs", [])
    logs_dir = CONFIG_PATH.parent.parent / "logs" / "run-history"

    quality_report: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "inspected_inputs": inputs,
        "quality_checks": [],
        "overall_status": "healthy",
    }

    for input_name in inputs:
        input_dir = logs_dir / input_name
        if input_dir.exists():
            check = _inspect_input(input_name, input_dir)
            quality_report["quality_checks"].append(check)

            if check.get("status") == "unhealthy":
                quality_report["overall_status"] = "degraded"

    dump_jsonl(ARTIFACT_DIR / "quality_inspector.jsonl", quality_report)


def _inspect_input(name: str, input_dir: Path) -> dict[str, Any]:
    """Inspect quality of input stream."""
    try:
        jsonl_files = list(input_dir.glob("*.jsonl"))
        if not jsonl_files:
            return {
                "input": name,
                "status": "no_data",
                "files_count": 0,
            }

        latest_file = max(jsonl_files, key=lambda p: p.stat().st_mtime)

        with latest_file.open("r", encoding="utf-8") as fh:
            lines = fh.readlines()
            if lines:
                latest_data = json.loads(lines[-1])
                # Check for failure indicators
                has_errors = any(
                    key in str(latest_data).lower()
                    for key in ["error", "failed", "unhealthy"]
                )

                return {
                    "input": name,
                    "status": "unhealthy" if has_errors else "healthy",
                    "files_count": len(jsonl_files),
                    "latest_timestamp": latest_data.get("timestamp", "unknown"),
                }

        return {
            "input": name,
            "status": "healthy",
            "files_count": len(jsonl_files),
        }
    except Exception as exc:  # pragma: no cover - file I/O safety
        return {
            "input": name,
            "status": "error",
            "error": str(exc),
        }


def cli() -> None:
    run()


__all__ = ["run"]
