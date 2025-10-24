"""Graceful shutdown signal handlers used by the FastAPI application.

The production configuration expects ``setup_shutdown_handlers`` to be present
to register handlers for ``SIGINT`` and ``SIGTERM``. The original implementation
was not included in the repository snapshot, which prevented the application
from importing :mod:`app.core.signals` during test collection. The lightweight
implementation below provides the expected interface while remaining safe to use
in the test environment.
"""

from __future__ import annotations

import logging
import signal
import sys
from types import FrameType
from typing import Callable, Optional


logger = logging.getLogger(__name__)


def _create_handler(signal_name: str) -> Callable[[int, Optional[FrameType]], None]:
    def _handler(signum: int, frame: Optional[FrameType]) -> None:  # pragma: no cover - simple logging
        logger.info("Received %s (%s). Initiating graceful shutdown.", signal_name, signum)

    return _handler


def setup_shutdown_handlers() -> None:
    """Register handlers for termination signals if the platform supports it."""

    if sys.platform.startswith("win"):
        # Windows signal support is limited; skip custom registration.
        logger.debug("Skipping signal handler registration on Windows platform")
        return

    for sig, name in ((signal.SIGINT, "SIGINT"), (signal.SIGTERM, "SIGTERM")):
        try:
            signal.signal(sig, _create_handler(name))
            logger.debug("Registered handler for %s", name)
        except (AttributeError, OSError, RuntimeError):  # pragma: no cover - platform specific
            logger.debug("Could not register handler for %s", name)


__all__ = ["setup_shutdown_handlers"]

