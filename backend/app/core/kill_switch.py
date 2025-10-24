"""In-memory kill-switch state tracking utilities."""

from __future__ import annotations

from datetime import datetime
from threading import RLock
from typing import Any, Dict, Optional


_lock = RLock()
_status: Dict[str, Any] = {
    "trading_halted": False,
    "updated_at": None,
    "updated_by": None,
    "reason": None,
}


def set_kill(
    state: bool,
    *,
    actor: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Update the kill-switch state.

    Args:
        state: Desired trading halt state.
        actor: Optional metadata about the actor performing the change.
        reason: Optional human-readable reason for the change.

    Returns:
        Copy of the updated kill-switch status for convenience.
    """

    with _lock:
        _status["trading_halted"] = bool(state)
        _status["updated_at"] = datetime.utcnow()
        _status["updated_by"] = actor.copy() if actor else None
        _status["reason"] = reason
        return get_status()


def is_killed() -> bool:
    with _lock:
        return bool(_status["trading_halted"])


def get_status() -> Dict[str, Any]:
    """Return a snapshot of the current kill-switch status."""

    with _lock:
        status = dict(_status)
        if status["updated_by"] is not None:
            status["updated_by"] = dict(status["updated_by"])
        return status
