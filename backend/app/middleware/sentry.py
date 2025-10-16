"""
Sentry Error Context Middleware

Adds custom context and breadcrumbs to Sentry error reports for better debugging.
"""

import time
from typing import Callable

import sentry_sdk
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SentryContextMiddleware(BaseHTTPMiddleware):
    """
    Adds request context to Sentry error reports
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Add request context to Sentry
        with sentry_sdk.push_scope() as scope:
            # Add request metadata
            scope.set_context(
                "request",
                {
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                    "client_host": request.client.host if request.client else None,
                },
            )

            # Add custom tags for filtering in Sentry
            scope.set_tag("endpoint", request.url.path)
            scope.set_tag("method", request.method)

            # Add breadcrumb for request
            sentry_sdk.add_breadcrumb(
                category="request",
                message=f"{request.method} {request.url.path}",
                level="info",
            )

            # Time the request
            start_time = time.time()

            try:
                response = await call_next(request)

                # Add response status to context
                scope.set_context(
                    "response",
                    {
                        "status_code": response.status_code,
                        "duration_ms": round((time.time() - start_time) * 1000, 2),
                    },
                )

                # Add breadcrumb for response
                sentry_sdk.add_breadcrumb(
                    category="response",
                    message=f"Status {response.status_code}",
                    level="info" if response.status_code < 400 else "warning",
                    data={"duration_ms": round((time.time() - start_time) * 1000, 2)},
                )

                return response

            except Exception as exc:
                # Add error context
                scope.set_context(
                    "error",
                    {
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "duration_ms": round((time.time() - start_time) * 1000, 2),
                    },
                )

                # Add breadcrumb for error
                sentry_sdk.add_breadcrumb(
                    category="error",
                    message=f"Exception: {type(exc).__name__}",
                    level="error",
                    data={"error_message": str(exc)},
                )

                # Capture exception in Sentry
                sentry_sdk.capture_exception(exc)

                # Re-raise to let FastAPI handle it
                raise


def capture_trading_event(event_type: str, symbol: str = None, **kwargs):
    """
    Capture custom trading events in Sentry for analytics

    Args:
        event_type: Type of event (e.g., "order_placed", "position_opened")
        symbol: Stock symbol if applicable
        **kwargs: Additional context data
    """
    sentry_sdk.add_breadcrumb(
        category="trading", message=event_type, level="info", data={"symbol": symbol, **kwargs}
    )


def capture_market_data_fetch(source: str, endpoint: str, success: bool, duration_ms: float = None):
    """
    Capture market data fetch events for monitoring API health

    Args:
        source: Data source (e.g., "tradier", "claude_ai")
        endpoint: API endpoint called
        success: Whether the fetch was successful
        duration_ms: Request duration in milliseconds
    """
    sentry_sdk.add_breadcrumb(
        category="market_data",
        message=f"{source}: {endpoint}",
        level="info" if success else "warning",
        data={
            "source": source,
            "endpoint": endpoint,
            "success": success,
            "duration_ms": duration_ms,
        },
    )


def capture_cache_operation(operation: str, key: str, hit: bool = None):
    """
    Capture cache operations for monitoring cache effectiveness

    Args:
        operation: Cache operation (e.g., "get", "set", "delete")
        key: Cache key
        hit: Whether it was a cache hit (for get operations)
    """
    sentry_sdk.add_breadcrumb(
        category="cache",
        message=f"{operation}: {key}",
        level="debug",
        data={"operation": operation, "key": key, "hit": hit},
    )
