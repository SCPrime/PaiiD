"""Compatibility wrapper exposing ``backend.app.routers`` under ``app.routers``."""

from __future__ import annotations

from pathlib import Path

from .. import _ensure_path  # type: ignore[attr-defined]

_backend_routers = Path(__file__).resolve().parents[2] / "backend" / "app" / "routers"
_ensure_path(__path__, _backend_routers)

from backend.app.routers import *  # noqa: F401,F403
