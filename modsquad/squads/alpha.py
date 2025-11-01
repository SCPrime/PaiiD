"""
ALPHA SQUAD - Core Infrastructure & Security
Mission: Foundation services ensuring system integrity and security
Risk Profile: <1% combined | Always Active
"""

import threading

from modsquad.extensions import maintenance_notifier, metrics_streamer, secrets_watchdog

# Squad members
MEMBERS = [
    {"name": "secrets_watchdog", "module": secrets_watchdog, "role": "leader"},
    {"name": "metrics_streamer", "module": metrics_streamer, "role": "telemetry"},
    {"name": "maintenance_notifier", "module": maintenance_notifier, "role": "comms"},
]

_ACTIVE = False

# Pause control for batch execution (prevents interference with always-on tasks)
_alpha_paused = threading.Event()
_alpha_paused.set()  # Initially NOT paused (set = running)


def activate():
    """Activate ALPHA SQUAD (always-on background services)."""
    global _ACTIVE
    if not _ACTIVE:
        # ALPHA SQUAD runs passively - no immediate execution needed
        # Extensions activate on their own run() calls
        _ACTIVE = True
    return {"status": "activated", "squad": "alpha"}


def status():
    """Get ALPHA SQUAD status."""
    return {
        "active": _ACTIVE,
        "members": len(MEMBERS),
        "health": "healthy",
        "risk": "<1%",
    }


def deploy():
    """Deploy ALPHA SQUAD services."""
    results = {}
    for member in MEMBERS:
        try:
            result = member["module"].run()
            results[member["name"]] = {
                "status": "success",
                "result": result,
            }
        except Exception as e:
            results[member["name"]] = {
                "status": "failed",
                "error": str(e),
            }

    return {
        "squad": "alpha",
        "deployed": True,
        "results": results,
    }


def pause_alpha_squad() -> None:
    """Pause ALPHA squad always-on tasks during batch execution."""
    _alpha_paused.clear()
    print("[ALPHA SQUAD] Paused during batch execution")


def resume_alpha_squad() -> None:
    """Resume ALPHA squad always-on tasks after batch execution."""
    _alpha_paused.set()
    print("[ALPHA SQUAD] Resumed")


def is_alpha_paused() -> bool:
    """Check if ALPHA squad is currently paused."""
    return not _alpha_paused.is_set()


def wait_if_paused() -> None:
    """Block until ALPHA squad is resumed (used in always-on tasks)."""
    _alpha_paused.wait()


__all__ = [
    "activate",
    "status",
    "deploy",
    "MEMBERS",
    "pause_alpha_squad",
    "resume_alpha_squad",
    "is_alpha_paused",
    "wait_if_paused",
]
