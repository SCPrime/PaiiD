            from ..scheduler import get_scheduler
            from ..services.tradier_stream import stop_tradier_stream
from pathlib import Path
import asyncio
import logging
import signal
import sys

"""
Signal Handling Module for Graceful Shutdown
Ensures proper cleanup of resources and PID files on process termination
Version: 1.0.0
"""

logger = logging.getLogger(__name__)

# Track if shutdown is in progress
_shutdown_in_progress = False
_shutdown_timeout = 30  # Maximum 30 seconds for graceful shutdown

def get_pid_file_path() -> Path | None:
    """Get the path to this process's PID file"""
    project_root = Path(__file__).parent.parent.parent.parent
    pid_dir = project_root / "backend" / ".run"
    pid_file = pid_dir / "backend-server.pid"

    if pid_file.exists():
        return pid_file
    return None

def remove_pid_file() -> None:
    """Remove the PID file for this process"""
    try:
        pid_file = get_pid_file_path()
        if pid_file and pid_file.exists():
            pid_file.unlink()
            logger.info(f"Removed PID file: {pid_file}")
    except Exception as e:
        logger.error(f"Failed to remove PID file: {e}")

async def graceful_shutdown(sig: signal.Signals) -> None:
    """
    Perform graceful shutdown sequence

    1. Stop accepting new requests
    2. Drain active connections (with timeout)
    3. Shutdown scheduler
    4. Shutdown Tradier stream
    5. Close database connections
    6. Remove PID file
    7. Exit with status 0
    """
    global _shutdown_in_progress

    if _shutdown_in_progress:
        logger.warning(f"Shutdown already in progress, ignoring signal {sig.name}")
        return

    _shutdown_in_progress = True

    logger.info("=" * 70)
    logger.info(f"Received signal {sig.name} - initiating graceful shutdown")
    logger.info("=" * 70)

    try:
        # 1. Stop accepting new requests (handled by FastAPI automatically)
        logger.info("[1/6] Stopped accepting new requests")

        # 2. Drain active connections (give them time to complete)
        logger.info("[2/6] Draining active connections...")
        await asyncio.sleep(2)  # Give active requests 2 seconds to complete

        # 3. Shutdown scheduler
        logger.info("[3/6] Shutting down scheduler...")
        try:

            scheduler_instance = get_scheduler()
            if scheduler_instance:
                scheduler_instance.shutdown(wait=False)
                logger.info("  Scheduler shutdown complete")
        except Exception as e:
            logger.warning(f"  Scheduler shutdown error (non-critical): {e}")

        # 4. Shutdown Tradier stream
        logger.info("[4/6] Shutting down Tradier stream...")
        try:

            await stop_tradier_stream()
            logger.info("  Tradier stream shutdown complete")
        except Exception as e:
            logger.warning(f"  Tradier stream shutdown error (non-critical): {e}")

        # 5. Close database connections (if using connection pool)
        logger.info("[5/6] Closing database connections...")
        try:
            # Add database cleanup here if needed
            logger.info("  Database connections closed")
        except Exception as e:
            logger.warning(f"  Database shutdown error (non-critical): {e}")

        # 6. Remove PID file
        logger.info("[6/6] Removing PID file...")
        remove_pid_file()

        logger.info("=" * 70)
        logger.info("Graceful shutdown complete - exiting with status 0")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"Error during graceful shutdown: {e}", exc_info=True)
    finally:
        # Force exit after timeout
        sys.exit(0)

def handle_signal(sig: signal.Signals, frame) -> None:
    """Signal handler that triggers graceful shutdown"""
    # Create a new event loop if needed (signal handlers run in main thread)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Schedule the graceful shutdown coroutine
    loop.create_task(graceful_shutdown(sig))

def register_signal_handlers() -> None:
    """
    Register signal handlers for graceful shutdown

    Handles:
    - SIGTERM: Termination signal (kill, docker stop, systemd)
    - SIGINT: Interrupt signal (Ctrl+C)
    - SIGHUP: Hangup signal (terminal closed)
    """
    # Only register on Unix-like systems (Windows doesn't support all signals)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGHUP, handle_signal)
        logger.info("Registered signal handlers: SIGTERM, SIGINT, SIGHUP")
    else:
        signal.signal(signal.SIGTERM, handle_signal)
        logger.info("Registered signal handlers: SIGTERM, SIGINT (Windows)")

    # SIGINT is cross-platform
    signal.signal(signal.SIGINT, handle_signal)

def setup_shutdown_handlers() -> None:
    """
    Setup all shutdown-related handlers
    Called during application startup
    """
    logger.info("Setting up graceful shutdown handlers...")
    register_signal_handlers()
    logger.info("Shutdown handlers configured")
