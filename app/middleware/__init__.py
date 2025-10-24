"""Compatibility wrapper exposing ``backend.app.middleware`` under ``app.middleware``."""

from __future__ import annotations

from pathlib import Path

from .. import _ensure_path  # type: ignore[attr-defined]

_backend_middleware = (
    Path(__file__).resolve().parents[2] / "backend" / "app" / "middleware"
)
_ensure_path(__path__, _backend_middleware)

from backend.app.middleware import *  # noqa: F401,F403
