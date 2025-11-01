"""Metrics streaming extension for MOD SQUAD."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

METRICS_PATH = CONFIG_PATH.parent.parent / "logs" / "run-history" / "metrics.jsonl"


def run(payload: Dict[str, Any]) -> None:
    """Record metrics payload when batches complete."""

    config = load_extension_config()
    settings = config.get("metrics_streamer")
    if not settings.get("enabled", False):
        return

    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **{k: payload.get(k) for k in settings.get("fields", [])},
    }
    dump_jsonl(METRICS_PATH, record)


def cli(metrics_path: str) -> None:
    """CLI helper to stream a metrics file produced by maintenance."""

    path = Path(metrics_path)
    if not path.exists():
        return
    data = {"metrics_source": str(path)}
    run(data)

