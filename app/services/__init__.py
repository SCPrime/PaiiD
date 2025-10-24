"""Compatibility wrapper exposing ``backend.app.services`` under ``app.services``."""

from __future__ import annotations

from pathlib import Path

from .. import _ensure_path  # type: ignore[attr-defined]

_backend_services = Path(__file__).resolve().parents[2] / "backend" / "app" / "services"
_ensure_path(__path__, _backend_services)

from backend.app.services import *  # noqa: F401,F403
