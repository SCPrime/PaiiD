"""Test-friendly signal handlers shim."""

import signal
from typing import Callable


def setup_shutdown_handlers(on_shutdown: Callable | None = None) -> None:
    """Install dummy signal handlers when OS integrations are unavailable."""

    try:
        signals = [signal.SIGTERM, signal.SIGINT]
    except AttributeError:
        signals = []

    for sig in signals:
        signal.signal(sig, lambda *_args: on_shutdown() if on_shutdown else None)
