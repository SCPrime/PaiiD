"""Maintenance notifier extension for MOD SQUAD."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

LOG_PATH = CONFIG_PATH.parent.parent / "logs" / "run-history" / "maintenance_notifier.jsonl"


def build_payload(window: str, status: str, details: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "window": window,
        "status": status,
        "details": details,
    }


def run(window: str, status: str, details: Dict[str, Any] | None = None) -> None:
    """Entry point triggered after maintenance batches."""

    config = load_extension_config()
    settings = config.get("maintenance_notifier")
    if not settings.get("enabled", False):
        return

    payload = build_payload(window, status, details or {})
    dump_jsonl(LOG_PATH, payload)

    webhook_env = settings.get("webhook_env", "")
    if webhook_env and webhook_env not in os.environ:
        dump_jsonl(LOG_PATH, {"warning": f"Webhook env '{webhook_env}' not set"})


def cli(window: str, status: str, details_path: str | None = None) -> None:
    """CLI helper for scheduled jobs."""

    details: Dict[str, Any] = {}
    if details_path:
        path = Path(details_path)
        if path.exists():
            details = {"source": str(path)}
    run(window, status, details)

