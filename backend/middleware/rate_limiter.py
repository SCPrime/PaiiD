import logging

import redis
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import settings


"""
Rate Limiting Middleware
Prevents API throttling and implements rate limiting for market data requests
"""

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter using Redis for distributed rate limiting"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=1,  # Use different DB for rate limiting
            decode_responses=True,
        )

        # Rate limits (requests per minute)
        self.limits = {
            "market_data": 60,  # 60 requests per minute
            "trading": 30,  # 30 requests per minute
            "portfolio": 120,  # 120 requests per minute
            "websocket": 300,  # 300 requests per minute
        }

    async def check_rate_limit(self, request: Request, endpoint_type: str) -> bool:
        """Check if request is within rate limit"""
        try:
            # Get client identifier (IP address or user ID)
            client_id = self._get_client_id(request)

            # Get rate limit for endpoint type
            limit = self.limits.get(endpoint_type, 60)

            # Check current count
            key = f"rate_limit:{endpoint_type}:{client_id}"
            current_count = self.redis_client.get(key)

            if current_count is None:
                # First request, set counter
                self.redis_client.setex(key, 60, 1)  # Expire in 60 seconds
                return True

            current_count = int(current_count)

            if current_count >= limit:
                logger.warning(
                    f"Rate limit exceeded for {client_id} on {endpoint_type}"
                )
                return False

            # Increment counter
            self.redis_client.incr(key)
            return True

        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Allow request on error to avoid blocking legitimate users
            return True

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get user ID from request if available
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    async def get_remaining_requests(self, request: Request, endpoint_type: str) -> int:
        """Get remaining requests for client"""
        try:
            client_id = self._get_client_id(request)
            key = f"rate_limit:{endpoint_type}:{client_id}"

            current_count = self.redis_client.get(key)
            if current_count is None:
                return self.limits.get(endpoint_type, 60)

            limit = self.limits.get(endpoint_type, 60)
            remaining = limit - int(current_count)
            return max(0, remaining)

        except Exception as e:
            logger.error(f"Error getting remaining requests: {e}")
            return 0


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)

            # Determine endpoint type based on path
            endpoint_type = self._get_endpoint_type(request.url.path)

            # Check rate limit
            if not await rate_limiter.check_rate_limit(request, endpoint_type):
                response = JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests for {endpoint_type}",
                        "retry_after": 60,
                    },
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(
                            rate_limiter.limits.get(endpoint_type, 60)
                        ),
                        "X-RateLimit-Remaining": "0",
                    },
                )
                await response(scope, receive, send)
                return

            # Add rate limit headers
            remaining = await rate_limiter.get_remaining_requests(
                request, endpoint_type
            )
            scope["rate_limit_remaining"] = remaining

        await self.app(scope, receive, send)

    def _get_endpoint_type(self, path: str) -> str:
        """Determine endpoint type from path"""
        if "/api/market-data" in path:
            return "market_data"
        elif "/api/trading" in path:
            return "trading"
        elif "/api/portfolio" in path:
            return "portfolio"
        elif "/ws" in path:
            return "websocket"
        else:
            return "general"


class MarketDataRateLimiter:
    """Specialized rate limiter for market data endpoints"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=2,  # Use different DB for market data rate limiting
            decode_responses=True,
        )

        # More granular rate limits for market data
        self.symbol_limits = {
            "quote": 10,  # 10 quotes per minute per symbol
            "historical": 5,  # 5 historical requests per minute
            "search": 20,  # 20 search requests per minute
        }

    async def check_symbol_rate_limit(self, symbol: str, request_type: str) -> bool:
        """Check rate limit for specific symbol and request type"""
        try:
            limit = self.symbol_limits.get(request_type, 10)
            key = f"symbol_rate:{symbol}:{request_type}"

            current_count = self.redis_client.get(key)

            if current_count is None:
                self.redis_client.setex(key, 60, 1)
                return True

            if int(current_count) >= limit:
                return False

            self.redis_client.incr(key)
            return True

        except Exception as e:
            logger.error(f"Symbol rate limiter error: {e}")
            return True

    async def get_symbol_remaining(self, symbol: str, request_type: str) -> int:
        """Get remaining requests for symbol"""
        try:
            limit = self.symbol_limits.get(request_type, 10)
            key = f"symbol_rate:{symbol}:{request_type}"

            current_count = self.redis_client.get(key)
            if current_count is None:
                return limit

            remaining = limit - int(current_count)
            return max(0, remaining)

        except Exception as e:
            logger.error(f"Error getting symbol remaining: {e}")
            return 0


# Global market data rate limiter
market_data_rate_limiter = MarketDataRateLimiter()
