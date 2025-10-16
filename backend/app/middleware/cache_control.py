"""
Cache-Control Middleware

Adds intelligent cache headers to API responses to support SWR (stale-while-revalidate) caching.

Phase 2: Performance Optimization
"""

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Add Cache-Control headers to API responses based on endpoint patterns

    Strategy:
    - Positions/Orders: max-age=5s, stale-while-revalidate=10s (frequent updates)
    - Market Data: max-age=10s, stale-while-revalidate=60s (medium frequency)
    - News: max-age=300s, stale-while-revalidate=600s (infrequent updates)
    - Static Data: max-age=3600s (1 hour, rarely changes)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Process request
        response = await call_next(request)

        # Only add cache headers to GET requests with 200 OK responses
        if request.method != "GET" or response.status_code != 200:
            return response

        path = request.url.path

        # High-frequency data (positions, account, orders)
        if any(endpoint in path for endpoint in ["/positions", "/account", "/orders/history"]):
            response.headers["Cache-Control"] = "public, max-age=5, stale-while-revalidate=10"

        # Medium-frequency data (market quotes, indices)
        elif any(endpoint in path for endpoint in ["/quotes", "/market/indices", "/analytics"]):
            response.headers["Cache-Control"] = "public, max-age=10, stale-while-revalidate=60"

        # Low-frequency data (news, company data)
        elif any(endpoint in path for endpoint in ["/news", "/company"]):
            response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=600"

        # Static data (strategies, preferences, templates)
        elif any(endpoint in path for endpoint in ["/strategies/templates", "/users/preferences"]):
            response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=7200"

        # Default: moderate caching
        else:
            response.headers["Cache-Control"] = "public, max-age=30, stale-while-revalidate=60"

        # Add ETag support for conditional requests
        response.headers["Vary"] = "Authorization"

        return response
