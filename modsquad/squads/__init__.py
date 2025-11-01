"""
MOD SQUAD Elite Specialty Squads
Permanent deployment configuration for all environments
"""

from . import alpha, bravo, charlie, delta, echo, foxtrot, sun_tzu, armani

# Auto-activate ALPHA SQUAD on import (always-on services)
alpha.activate()


def status_all():
    """Get status of all squads."""
    return {
        "alpha": alpha.status(),
        "bravo": bravo.status(),
        "charlie": charlie.status(),
        "delta": delta.status(),
        "echo": echo.status(),
        "foxtrot": foxtrot.status(),
        "sun_tzu": sun_tzu.status(),
        "armani": armani.status(),
    }


def deploy_all(skip_slow=False):
    """Deploy all squads in optimal order."""
    return foxtrot.orchestrate_all(skip_slow=skip_slow)


__all__ = [
    "alpha",
    "bravo",
    "charlie",
    "delta",
    "echo",
    "foxtrot",
    "sun_tzu",
    "armani",
    "status_all",
    "deploy_all",
]
