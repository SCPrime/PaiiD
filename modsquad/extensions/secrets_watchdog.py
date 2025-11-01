"""Secrets watchdog extension for MOD SQUAD."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

WATCHDOG_PATH = CONFIG_PATH.parent.parent / "logs" / "run-history" / "secrets_watchdog.jsonl"


def audit() -> None:
    """Record secret rotation status."""

    config = load_extension_config()
    settings = config.get("secrets_watchdog")
    if not settings.get("enabled", False):
        return

    results: List[Dict[str, Any]] = []
    for item in settings.get("secrets", []):
        env_name = item.get("env")
        present = bool(env_name and os.getenv(env_name))
        results.append(
            {
                "secret": env_name,
                "present": present,
                "rotation_days": item.get("rotation_days"),
            }
        )

    dump_jsonl(
        WATCHDOG_PATH,
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results": results,
        },
    )


def cli() -> None:
    audit()

