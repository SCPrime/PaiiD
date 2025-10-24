"""Signal handling utilities for graceful shutdown."""
from __future__ import annotations

import logging
import signal
from types import FrameType
from typing import Optional


logger = logging.getLogger(__name__)


def _handle_shutdown(signum: int, frame: Optional[FrameType]) -> None:
    """Default signal handler used during shutdown."""
    logger.info("Received shutdown signal %s", signum)


def setup_shutdown_handlers() -> None:
    """Register shutdown handlers for SIGINT and SIGTERM if available."""
    for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
        if sig is not None:
            signal.signal(sig, _handle_shutdown)
