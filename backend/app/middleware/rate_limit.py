"""
Rate Limiting Middleware

Protects API from abuse and DoS attacks using SlowAPI.

Phase 3: Bulletproof Reliability
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from typing import Callable
import os

# Check if running in test mode
TESTING = os.getenv("TESTING", "false").lower() == "true"

# Initialize rate limiter with IP-based keying
# In test mode, use extremely high limits to effectively disable rate limiting
if TESTING:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["100000/minute"],  # Effectively unlimited in tests
        storage_uri="memory://",
        strategy="fixed-window",
        headers_enabled=False,  # Disable headers in test mode
        enabled=False  # Disable rate limiting entirely in tests
    )
else:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"],  # Global default: 100 requests per minute per IP
        storage_uri="memory://",  # Use in-memory storage (can upgrade to Redis for production)
        strategy="fixed-window",  # Fixed window strategy
        headers_enabled=True,  # Enable rate limit headers (X-RateLimit-*)
    )

# Custom rate limit exceeded handler
async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded responses.

    Returns:
        429 Too Many Requests with Retry-After header
    """
    from fastapi.responses import JSONResponse

    # Extract retry-after from exception
    retry_after = exc.detail.split("Retry after ")[1] if "Retry after" in exc.detail else "60 seconds"

    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Please try again later.",
            "retry_after": retry_after,
            "limit": str(exc.detail)
        },
        headers={
            "Retry-After": "60",  # Tell client to wait 60 seconds
            "X-RateLimit-Limit": str(limiter.limit),
            "X-RateLimit-Remaining": "0",
        }
    )


# Decorators for different endpoint types

def rate_limit_standard(func):
    """Standard rate limit: 60 req/min"""
    return limiter.limit("60/minute")(func)


def rate_limit_strict(func):
    """Strict rate limit for expensive operations: 10 req/min"""
    return limiter.limit("10/minute")(func)


def rate_limit_relaxed(func):
    """Relaxed rate limit for read-heavy operations: 100 req/min"""
    return limiter.limit("100/minute")(func)


def rate_limit_very_strict(func):
    """Very strict for auth/sensitive endpoints: 5 req/min"""
    return limiter.limit("5/minute")(func)


# Export limiter and handlers
__all__ = [
    'limiter',
    'custom_rate_limit_exceeded_handler',
    'rate_limit_standard',
    'rate_limit_strict',
    'rate_limit_relaxed',
    'rate_limit_very_strict'
]
