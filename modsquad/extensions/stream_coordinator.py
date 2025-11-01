"""Stream coordinator for parallel MOD SQUAD execution."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH

LOCK_FILE = CONFIG_PATH.parent.parent / "logs" / "file-locks.json"
COORDINATION_LOG = CONFIG_PATH.parent.parent / "logs" / "run-history" / "stream_coordinator.jsonl"


def acquire_lock(agent: str, file_path: str) -> bool:
    """Request file lock for an agent."""
    locks = _load_locks()
    
    if file_path in locks and locks[file_path]["agent"] != agent:
        return False
    
    locks[file_path] = {
        "agent": agent,
        "acquired_at": datetime.utcnow().isoformat() + "Z",
    }
    _save_locks(locks)
    _log_event("acquire", agent, file_path, success=True)
    return True


def release_lock(agent: str, file_path: str) -> None:
    """Release file lock held by an agent."""
    locks = _load_locks()
    
    if file_path in locks and locks[file_path]["agent"] == agent:
        del locks[file_path]
        _save_locks(locks)
        _log_event("release", agent, file_path, success=True)


def check_conflicts() -> list[dict[str, Any]]:
    """Check for potential file conflicts across active branches."""
    # Placeholder: In full implementation, would run git diff across branches
    return []


def _load_locks() -> dict[str, Any]:
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOCK_FILE.exists():
        return {}
    return json.loads(LOCK_FILE.read_text(encoding="utf-8"))


def _save_locks(locks: dict[str, Any]) -> None:
    LOCK_FILE.write_text(json.dumps(locks, indent=2), encoding="utf-8")


def _log_event(action: str, agent: str, file_path: str, success: bool) -> None:
    COORDINATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "agent": agent,
        "file_path": file_path,
        "success": success,
    }
    with COORDINATION_LOG.open("a", encoding="utf-8") as handle:
        json.dump(entry, handle)
        handle.write("\n")


__all__ = ["acquire_lock", "check_conflicts", "release_lock"]

