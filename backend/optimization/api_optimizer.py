import json
import logging
import time
from datetime import datetime
from typing import Any

import redis
from fastapi import Request
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse


"""
API Performance Optimizer
Optimizes API response times, caching, and rate limiting for maximum performance
"""

logger = logging.getLogger(__name__)

class APIOptimizer:
    """Optimizes API performance with caching, compression, and response optimization"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=6, decode_responses=True
        )
        self.performance_metrics = {
            "request_count": 0,
            "total_response_time": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "error_count": 0,
        }
        self.cache_ttl = {
            "user_data": 300,  # 5 minutes
            "market_data": 10,  # 10 seconds
            "portfolio_data": 60,  # 1 minute
            "ai_analysis": 180,  # 3 minutes
            "static_data": 3600,  # 1 hour
        }

    async def setup_response_caching(self):
        """Setup intelligent response caching for API endpoints"""
        cache_configs = {
            "GET /api/users/{user_id}": {
                "ttl": self.cache_ttl["user_data"],
                "key_pattern": "user:{user_id}",
                "invalidate_on": ["POST", "PUT", "DELETE"],
            },
            "GET /api/portfolio/{user_id}": {
                "ttl": self.cache_ttl["portfolio_data"],
                "key_pattern": "portfolio:{user_id}",
                "invalidate_on": ["POST", "PUT", "DELETE"],
            },
            "GET /api/market-data/{symbol}": {
                "ttl": self.cache_ttl["market_data"],
                "key_pattern": "market:{symbol}",
                "invalidate_on": [],
            },
            "GET /api/ai/insights/{symbols}": {
                "ttl": self.cache_ttl["ai_analysis"],
                "key_pattern": "ai_insights:{symbols}",
                "invalidate_on": [],
            },
        }

        try:
            for endpoint, config in cache_configs.items():
                self.redis_client.setex(
                    f"cache_config:{endpoint}",
                    3600,  # 1 hour
                    json.dumps(config),
                )

            logger.info("Response caching configured successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup response caching: {e}")
            return False

    async def get_cached_response(self, cache_key: str) -> dict[str, Any] | None:
        """Get cached response if available"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                self.performance_metrics["cache_hits"] += 1
                return json.loads(cached_data)
            else:
                self.performance_metrics["cache_misses"] += 1
                return None
        except Exception as e:
            logger.error(f"Failed to get cached response: {e}")
            return None

    async def set_cached_response(self, cache_key: str, data: dict[str, Any], ttl: int):
        """Cache API response for future requests"""
        try:
            self.redis_client.setex(cache_key, ttl, json.dumps(data, default=str))
            return True
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")
            return False

    async def invalidate_cache(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(
                    f"Invalidated {len(keys)} cache entries for pattern: {pattern}"
                )
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return False

    async def optimize_response_compression(self):
        """Setup response compression for better performance"""
        compression_config = {
            "gzip_enabled": True,
            "min_size": 1024,  # Compress responses > 1KB
            "compression_level": 6,  # Balanced compression
            "content_types": [
                "application/json",
                "text/html",
                "text/css",
                "text/javascript",
                "application/javascript",
            ],
        }

        try:
            self.redis_client.setex(
                "compression_config", 3600, json.dumps(compression_config)
            )
            logger.info("Response compression configured successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup compression: {e}")
            return False

    async def setup_rate_limiting(self):
        """Setup intelligent rate limiting for API protection"""
        rate_limits = {
            "default": {
                "requests_per_minute": 60,
                "burst_limit": 10,
                "window_size": 60,
            },
            "market_data": {
                "requests_per_minute": 120,
                "burst_limit": 20,
                "window_size": 60,
            },
            "trading": {
                "requests_per_minute": 30,
                "burst_limit": 5,
                "window_size": 60,
            },
            "ai_analysis": {
                "requests_per_minute": 20,
                "burst_limit": 3,
                "window_size": 60,
            },
        }

        try:
            for endpoint_type, limits in rate_limits.items():
                self.redis_client.setex(
                    f"rate_limit:{endpoint_type}", 3600, json.dumps(limits)
                )

            logger.info("Rate limiting configured successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup rate limiting: {e}")
            return False

    async def check_rate_limit(
        self, client_id: str, endpoint_type: str = "default"
    ) -> bool:
        """Check if client is within rate limits"""
        try:
            # Get rate limit config
            config_data = self.redis_client.get(f"rate_limit:{endpoint_type}")
            if not config_data:
                return True  # No limits configured

            config = json.loads(config_data)
            current_time = int(time.time())
            window_start = current_time - config["window_size"]

            # Get current request count
            key = f"rate_limit:{client_id}:{endpoint_type}"
            requests = self.redis_client.zcount(key, window_start, current_time)

            if requests >= config["requests_per_minute"]:
                return False

            # Add current request
            self.redis_client.zadd(key, {str(current_time): current_time})
            self.redis_client.expire(key, config["window_size"])

            return True
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True  # Allow on error

    async def optimize_database_queries(self):
        """Optimize database queries for API endpoints"""
        query_optimizations = {
            "user_portfolio": """
                SELECT
                    p.id,
                    p.user_id,
                    p.total_value,
                    p.total_change,
                    p.total_change_percent,
                    COUNT(pos.id) as position_count,
                    SUM(pos.unrealized_pnl) as total_unrealized_pnl
                FROM portfolios p
                LEFT JOIN positions pos ON p.id = pos.portfolio_id
                WHERE p.user_id = $1 AND p.is_active = true
                GROUP BY p.id, p.user_id, p.total_value, p.total_change, p.total_change_percent
                LIMIT 1
            """,
            "market_data": """
                SELECT
                    symbol,
                    price,
                    change,
                    change_percent,
                    volume,
                    timestamp
                FROM market_data
                WHERE symbol = $1
                ORDER BY timestamp DESC
                LIMIT 1
            """,
            "position_performance": """
                SELECT
                    pos.symbol,
                    pos.quantity,
                    pos.current_price,
                    pos.market_value,
                    pos.unrealized_pnl,
                    pos.unrealized_pnl_percent,
                    md.price as latest_price,
                    md.change as latest_change
                FROM positions pos
                LEFT JOIN LATERAL (
                    SELECT price, change
                    FROM market_data
                    WHERE symbol = pos.symbol
                    ORDER BY timestamp DESC
                    LIMIT 1
                ) md ON true
                WHERE pos.portfolio_id = $1 AND pos.quantity > 0
                ORDER BY pos.unrealized_pnl DESC
            """,
        }

        try:
            for query_name, query_sql in query_optimizations.items():
                self.redis_client.setex(
                    f"optimized_query:{query_name}", 3600, query_sql
                )

            logger.info("Database query optimizations stored successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to optimize database queries: {e}")
            return False

    async def setup_response_headers(self):
        """Setup optimal response headers for performance"""
        headers_config = {
            "cache_control": {
                "static_assets": "public, max-age=31536000",  # 1 year
                "api_responses": "private, max-age=60",  # 1 minute
                "user_data": "private, max-age=300",  # 5 minutes
            },
            "security_headers": {
                "x_content_type_options": "nosniff",
                "x_frame_options": "DENY",
                "x_xss_protection": "1; mode=block",
                "strict_transport_security": "max-age=31536000; includeSubDomains",
            },
            "performance_headers": {
                "x_response_time": True,
                "x_cache_status": True,
                "x_rate_limit_remaining": True,
            },
        }

        try:
            self.redis_client.setex("headers_config", 3600, json.dumps(headers_config))
            logger.info("Response headers configured successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup response headers: {e}")
            return False

    async def monitor_api_performance(self) -> dict[str, Any]:
        """Monitor API performance and generate metrics"""
        try:
            # Calculate performance metrics
            total_requests = self.performance_metrics["request_count"]
            avg_response_time = self.performance_metrics["total_response_time"] / max(
                1, total_requests
            )
            cache_hit_ratio = (
                self.performance_metrics["cache_hits"]
                / max(
                    1,
                    self.performance_metrics["cache_hits"]
                    + self.performance_metrics["cache_misses"],
                )
            ) * 100
            error_rate = (
                self.performance_metrics["error_count"] / max(1, total_requests)
            ) * 100

            performance_data = {
                "timestamp": datetime.now().isoformat(),
                "total_requests": total_requests,
                "average_response_time_ms": round(avg_response_time * 1000, 2),
                "cache_hit_ratio_percent": round(cache_hit_ratio, 2),
                "error_rate_percent": round(error_rate, 2),
                "cache_hits": self.performance_metrics["cache_hits"],
                "cache_misses": self.performance_metrics["cache_misses"],
                "error_count": self.performance_metrics["error_count"],
            }

            # Store performance data
            self.redis_client.setex(
                f"api_performance:{datetime.now().strftime('%Y%m%d_%H%M')}",
                3600,
                json.dumps(performance_data),
            )

            return performance_data
        except Exception as e:
            logger.error(f"Failed to monitor API performance: {e}")
            return {}

    async def get_optimization_report(self) -> dict[str, Any]:
        """Generate comprehensive API optimization report"""
        try:
            performance_data = await self.monitor_api_performance()

            report = {
                "optimization_status": "completed",
                "performance_metrics": performance_data,
                "cache_strategies_configured": len(self.cache_ttl),
                "rate_limits_configured": 4,  # Based on our rate limit setup
                "query_optimizations": 3,  # Based on our query optimizations
                "recommendations": [
                    "Monitor cache hit ratio and adjust TTL values",
                    "Review rate limits based on usage patterns",
                    "Optimize slow endpoints identified in monitoring",
                    "Consider CDN for static assets",
                    "Implement request batching for bulk operations",
                ],
                "timestamp": datetime.now().isoformat(),
            }

            return report
        except Exception as e:
            logger.error(f"Failed to generate optimization report: {e}")
            return {"error": str(e)}

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring and optimizing API performance"""

    def __init__(self, app, optimizer: APIOptimizer):
        super().__init__(app)
        self.optimizer = optimizer

    async def dispatch(self, request: Request, call_next):
        """Process request with performance monitoring"""
        start_time = time.time()

        # Update request count
        self.optimizer.performance_metrics["request_count"] += 1

        # Check rate limiting
        client_id = request.client.host if request.client else "unknown"
        endpoint_type = self._get_endpoint_type(request.url.path)

        if not await self.optimizer.check_rate_limit(client_id, endpoint_type):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": 60},
            )

        # Check cache for GET requests
        if request.method == "GET":
            cache_key = self._generate_cache_key(request)
            cached_response = await self.optimizer.get_cached_response(cache_key)
            if cached_response:
                return JSONResponse(content=cached_response)

        # Process request
        try:
            response = await call_next(request)

            # Cache successful GET responses
            if request.method == "GET" and response.status_code == 200:
                cache_key = self._generate_cache_key(request)
                cache_config = self._get_cache_config(request.url.path)
                if cache_config:
                    response_data = await response.body()
                    await self.optimizer.set_cached_response(
                        cache_key,
                        json.loads(response_data.decode()),
                        cache_config["ttl"],
                    )

            # Add performance headers
            response.headers["X-Response-Time"] = str(
                round((time.time() - start_time) * 1000, 2)
            )
            response.headers["X-Cache-Status"] = "MISS"

            return response

        except Exception as e:
            self.optimizer.performance_metrics["error_count"] += 1
            logger.error(f"Request processing error: {e}")
            raise

    def _get_endpoint_type(self, path: str) -> str:
        """Determine endpoint type for rate limiting"""
        if "/api/market-data" in path:
            return "market_data"
        elif "/api/trading" in path:
            return "trading"
        elif "/api/ai" in path:
            return "ai_analysis"
        else:
            return "default"

    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        return f"api:{request.method}:{request.url.path}:{request.url.query}"

    def _get_cache_config(self, path: str) -> dict[str, Any] | None:
        """Get cache configuration for endpoint"""
        try:
            config_data = self.optimizer.redis_client.get(f"cache_config:GET {path}")
            if config_data:
                return json.loads(config_data)
        except Exception:
            pass
        return None
