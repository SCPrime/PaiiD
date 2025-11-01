"""
Circuit breaker pattern for MOD SQUAD extensions.
Prevents cascading failures and enforces <0.5% risk per extension.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict

from .utils import CONFIG_PATH, dump_jsonl

CIRCUIT_BREAKER_LOG = CONFIG_PATH.parent.parent / "logs" / "circuit_breaker.jsonl"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Too many failures, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker for extension functions.

    Tracks failures and opens circuit after threshold reached.
    Prevents cascading failures across MOD SQUAD extensions.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        timeout: int = 300,  # 5 minutes
        half_open_attempts: int = 1,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds before attempting recovery
            half_open_attempts: Test attempts in half-open state
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_attempts = half_open_attempts

        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute function through circuit breaker.

        Returns:
            Dict with status and result or error
        """
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self._log_state_change("HALF_OPEN", func.__name__)
            else:
                return {
                    "status": "circuit_open",
                    "message": f"Circuit breaker OPEN for {func.__name__}",
                    "retry_after": self._get_retry_after(),
                }

        # Try to execute function
        try:
            result = func(*args, **kwargs)

            # Success - reset failure count if circuit was half-open
            if self.state == CircuitState.HALF_OPEN:
                self._reset()
                self._log_state_change("CLOSED", func.__name__)

            return {
                "status": "success",
                "result": result,
                "circuit_state": self.state.value,
            }

        except Exception as e:
            self._record_failure(func.__name__)

            return {
                "status": "failed",
                "error": str(e),
                "circuit_state": self.state.value,
                "failure_count": self.failure_count,
            }

    def _record_failure(self, func_name: str):
        """Record a failure and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self._log_state_change("OPEN", func_name)

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.timeout

    def _reset(self):
        """Reset circuit breaker to closed state."""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def _get_retry_after(self) -> int:
        """Get seconds until circuit can be retried."""
        if self.last_failure_time is None:
            return 0

        elapsed = time.time() - self.last_failure_time
        return max(0, int(self.timeout - elapsed))

    def _log_state_change(self, new_state: str, func_name: str):
        """Log circuit state changes."""
        dump_jsonl(
            CIRCUIT_BREAKER_LOG,
            {
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "function": func_name,
                "state": new_state,
                "failure_count": self.failure_count,
            }
        )


def circuit_breaker(
    failure_threshold: int = 3,
    timeout: int = 300,
):
    """
    Decorator to apply circuit breaker to extension run() functions.

    Usage:
        @circuit_breaker(failure_threshold=3, timeout=300)
        def run():
            # extension logic
    """
    breaker = CircuitBreaker(failure_threshold=failure_threshold, timeout=timeout)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper

    return decorator


__all__ = ["CircuitBreaker", "CircuitState", "circuit_breaker"]
