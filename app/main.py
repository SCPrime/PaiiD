"""Compatibility wrapper exposing :mod:`backend.app.main` as :mod:`app.main`."""

from backend.app.main import *  # noqa: F401,F403
from backend.app.main import app  # re-export FastAPI instance explicitly

__all__ = [name for name in globals() if not name.startswith("__")]
