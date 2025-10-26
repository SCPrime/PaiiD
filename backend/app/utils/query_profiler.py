"""
Query Profiling Utilities

Provides decorators and utilities for profiling database queries
and API endpoint performance.
"""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any


logger = logging.getLogger(__name__)


def profile_query(threshold_ms: float = 100.0):
    """
    Decorator to profile and log slow queries

    Args:
        threshold_ms: Log warning if query takes longer than this (default: 100ms)

    Usage:
        @profile_query(threshold_ms=100)
        async def get_trades(db: Session):
            # Your query logic
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start) * 1000

                if duration_ms > threshold_ms:
                    logger.warning(
                        f"⚠️ Slow query detected in {func.__name__}: "
                        f"{duration_ms:.2f}ms (threshold: {threshold_ms}ms)",
                        extra={
                            "function": func.__name__,
                            "duration_ms": round(duration_ms, 2),
                            "threshold_ms": threshold_ms,
                            "is_slow": True
                        }
                    )
                else:
                    logger.debug(
                        f"✅ Query completed: {func.__name__} - {duration_ms:.2f}ms",
                        extra={
                            "function": func.__name__,
                            "duration_ms": round(duration_ms, 2),
                            "is_slow": False
                        }
                    )

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start) * 1000

                if duration_ms > threshold_ms:
                    logger.warning(
                        f"⚠️ Slow query detected in {func.__name__}: "
                        f"{duration_ms:.2f}ms (threshold: {threshold_ms}ms)",
                        extra={
                            "function": func.__name__,
                            "duration_ms": round(duration_ms, 2),
                            "threshold_ms": threshold_ms,
                            "is_slow": True
                        }
                    )
                else:
                    logger.debug(
                        f"✅ Query completed: {func.__name__} - {duration_ms:.2f}ms",
                        extra={
                            "function": func.__name__,
                            "duration_ms": round(duration_ms, 2),
                            "is_slow": False
                        }
                    )

        # Return appropriate wrapper based on whether function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def profile_endpoint(threshold_ms: float = 500.0):
    """
    Decorator to profile API endpoint performance

    Args:
        threshold_ms: Log warning if endpoint takes longer than this (default: 500ms)

    Usage:
        @router.get("/analytics/portfolio")
        @profile_endpoint(threshold_ms=500)
        async def get_portfolio_analytics():
            # Your endpoint logic
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            endpoint_name = func.__name__

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start) * 1000

                if duration_ms > threshold_ms:
                    logger.warning(
                        f"⚠️ Slow endpoint: {endpoint_name} - {duration_ms:.2f}ms",
                        extra={
                            "endpoint": endpoint_name,
                            "duration_ms": round(duration_ms, 2),
                            "threshold_ms": threshold_ms,
                            "is_slow": True
                        }
                    )
                else:
                    logger.info(
                        f"✅ Endpoint completed: {endpoint_name} - {duration_ms:.2f}ms",
                        extra={
                            "endpoint": endpoint_name,
                            "duration_ms": round(duration_ms, 2),
                            "is_slow": False
                        }
                    )

        return wrapper

    return decorator


class QueryProfiler:
    """
    Context manager for profiling database operations

    Usage:
        with QueryProfiler("fetch_user_trades") as profiler:
            trades = db.query(Trade).filter(...).all()

        # Automatically logs if slow
    """

    def __init__(self, operation_name: str, threshold_ms: float = 100.0):
        self.operation_name = operation_name
        self.threshold_ms = threshold_ms
        self.start_time = 0.0
        self.duration_ms = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000

        if self.duration_ms > self.threshold_ms:
            logger.warning(
                f"⚠️ Slow operation: {self.operation_name} - {self.duration_ms:.2f}ms",
                extra={
                    "operation": self.operation_name,
                    "duration_ms": round(self.duration_ms, 2),
                    "threshold_ms": self.threshold_ms,
                    "is_slow": True
                }
            )
        else:
            logger.debug(
                f"✅ Operation completed: {self.operation_name} - {self.duration_ms:.2f}ms",
                extra={
                    "operation": self.operation_name,
                    "duration_ms": round(self.duration_ms, 2),
                    "is_slow": False
                }
            )
