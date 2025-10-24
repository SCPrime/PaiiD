"""Compatibility wrapper exposing ``backend.app.core`` under ``app.core``."""

from __future__ import annotations

from pathlib import Path

from .. import _ensure_path  # type: ignore[attr-defined]

_backend_core = Path(__file__).resolve().parents[2] / "backend" / "app" / "core"
_ensure_path(__path__, _backend_core)

from backend.app.core import *  # noqa: F401,F403
