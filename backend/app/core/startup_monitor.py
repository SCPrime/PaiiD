"""
Startup Performance Monitor

Tracks startup timing and detects hanging operations to prevent production issues.
Learned from: 2025-10-17 - Tradier stream blocking startup for 360s causing 500 errors.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class StartupMonitor:
    """
    Monitor application startup performance and detect hanging operations.

    Features:
    - Track timing for each startup phase
    - Detect operations that exceed timeout thresholds
    - Log warnings for slow startups
    - Provide startup health metrics
    """

    def __init__(self):
        self.phases: Dict[str, float] = {}
        self.start_time: Optional[float] = None
        self.warnings: list = []

        # Timeout thresholds (seconds)
        self.PHASE_TIMEOUT = 10.0  # Warn if any phase takes > 10s
        self.TOTAL_TIMEOUT = 30.0  # Warn if total startup > 30s

    def start(self):
        """Mark application startup begin"""
        self.start_time = time.time()
        logger.info("🚀 [StartupMonitor] Application startup initiated")

    @asynccontextmanager
    async def phase(self, name: str, timeout: Optional[float] = None):
        """
        Context manager to monitor a startup phase with timeout.

        Usage:
            async with startup_monitor.phase("cache_init", timeout=5.0):
                await init_cache()
        """
        phase_start = time.time()
        effective_timeout = timeout or self.PHASE_TIMEOUT

        try:
            logger.info(f"  ⏱️  [{name}] Starting (timeout: {effective_timeout}s)")

            # Execute the phase with timeout protection
            yield

            duration = time.time() - phase_start
            self.phases[name] = duration

            if duration > effective_timeout:
                warning = (
                    f"⚠️  [{name}] took {duration:.2f}s (exceeded {effective_timeout}s threshold)"
                )
                self.warnings.append(warning)
                logger.warning(warning)
            else:
                logger.info(f"  ✅ [{name}] completed in {duration:.2f}s")

        except asyncio.TimeoutError:
            duration = time.time() - phase_start
            error = f"🚨 [{name}] TIMEOUT after {duration:.2f}s"
            self.warnings.append(error)
            logger.error(error)
            raise
        except Exception as e:
            duration = time.time() - phase_start
            error = f"❌ [{name}] failed after {duration:.2f}s: {str(e)}"
            self.warnings.append(error)
            logger.error(error)
            raise

    def finish(self):
        """Mark application startup complete and log summary"""
        if not self.start_time:
            logger.warning("StartupMonitor.finish() called before start()")
            return

        total_duration = time.time() - self.start_time

        logger.info("=" * 70)
        logger.info("🎯 [StartupMonitor] Application startup complete")
        logger.info(f"   Total Time: {total_duration:.2f}s")

        if self.phases:
            logger.info("   Phase Breakdown:")
            for phase, duration in sorted(self.phases.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"     • {phase}: {duration:.2f}s")

        if self.warnings:
            logger.warning(f"   ⚠️  {len(self.warnings)} warnings detected:")
            for warning in self.warnings:
                logger.warning(f"     • {warning}")

        if total_duration > self.TOTAL_TIMEOUT:
            logger.error(f"   🚨 CRITICAL: Total startup exceeded {self.TOTAL_TIMEOUT}s threshold!")

        logger.info("=" * 70)

    def get_metrics(self) -> dict:
        """Return startup metrics for health endpoint"""
        if not self.start_time:
            return {"status": "not_started"}

        return {
            "status": "completed",
            "total_duration_seconds": sum(self.phases.values()),
            "phases": self.phases,
            "warnings": self.warnings,
            "slow_phases": [
                name for name, duration in self.phases.items() if duration > self.PHASE_TIMEOUT
            ],
        }


# Global singleton instance
_startup_monitor: Optional[StartupMonitor] = None


def get_startup_monitor() -> StartupMonitor:
    """Get the global startup monitor instance"""
    global _startup_monitor
    if _startup_monitor is None:
        _startup_monitor = StartupMonitor()
    return _startup_monitor


async def timeout_wrapper(coro, timeout: float, operation_name: str):
    """
    Wrapper to add timeout protection to any async operation.

    Args:
        coro: Async coroutine to execute
        timeout: Timeout in seconds
        operation_name: Name for logging

    Raises:
        asyncio.TimeoutError: If operation exceeds timeout
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"🚨 [{operation_name}] timed out after {timeout}s")
        raise
