"""Compatibility package bridging legacy `app` imports to `backend.app`.

This shim preserves historical import paths used by the test-suite and
third-party integrations after the backend source moved under
``backend/app``. It keeps the filesystem contract (``app/...``) while
re-exporting modules from the new location.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


def _ensure_path(paths: Iterable[str], target: Path) -> None:
    """Insert *target* into ``paths`` if it exists and is missing."""

    if not target.exists():
        return

    target_str = str(target)
    if target_str not in paths:
        # ``__path__`` behaves like a mutable list of filesystem entries.
        paths.insert(0, target_str)


_backend_root = Path(__file__).resolve().parent.parent / "backend" / "app"
_ensure_path(__path__, _backend_root)

__all__ = []
