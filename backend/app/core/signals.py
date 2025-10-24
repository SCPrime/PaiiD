"""Graceful shutdown signal registration for the FastAPI application."""

from __future__ import annotations

import logging
import signal
from types import FrameType
from typing import Callable, Iterable, Optional

_logger = logging.getLogger(__name__)


def _create_handler(signame: str) -> Callable[[int, Optional[FrameType]], None]:
    def _handler(signum: int, frame: Optional[FrameType]) -> None:
        _logger.info("Received %s (%s). Initiating graceful shutdown.", signame, signum)

    return _handler


def _iter_supported_signals(names: Iterable[str]) -> Iterable[tuple[str, int]]:
    for name in names:
        if hasattr(signal, name):
            yield name, getattr(signal, name)


def setup_shutdown_handlers() -> None:
    """Register POSIX signal handlers in a cross-platform safe way."""

    registered = []
    for signame, signum in _iter_supported_signals(["SIGTERM", "SIGINT"]):
        try:
            signal.signal(signum, _create_handler(signame))
            registered.append(signame)
        except (OSError, RuntimeError, ValueError) as exc:
            _logger.debug("Skipping signal %s: %s", signame, exc)

    if registered:
        _logger.info("Registered shutdown handlers for: %s", ", ".join(registered))
    else:
        _logger.info("No OS signals were registered for graceful shutdown.")


__all__ = ["setup_shutdown_handlers"]
