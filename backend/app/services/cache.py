"""
Redis Cache Service

Provides Redis caching with graceful fallback when Redis is unavailable.
Implements common cache operations with TTL support.
"""

import json
from typing import Any

import redis

from ..core.config import settings
from .health_monitor import health_monitor


class CacheService:
    """Redis cache service with graceful degradation"""

    def __init__(self):
        self.client: redis.Redis | None = None
        self.available = False
        self._initialize()

    def _initialize(self):
        """Initialize Redis connection"""
        if not settings.REDIS_URL:
            print("[WARNING] REDIS_URL not configured - caching disabled", flush=True)
            return

        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.client.ping()
            self.available = True
            print("[OK] Redis cache connected", flush=True)
        except Exception as e:
            print(
                f"[WARNING] Redis connection failed: {e} - caching disabled", flush=True
            )
            self.client = None
            self.available = False

    def get(self, key: str) -> Any | None:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/unavailable
        """
        if not self.available or not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                health_monitor.record_cache_hit()
                return json.loads(value)
            health_monitor.record_cache_miss()
            return None
        except Exception as e:
            print(f"[WARNING] Cache GET error for key '{key}': {e}", flush=True)
            return None

    def set(self, key: str, value: Any, ttl: int = 60) -> bool:
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 60)

        Returns:
            True if successful, False otherwise
        """
        if not self.available or not self.client:
            return False

        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"[WARNING] Cache SET error for key '{key}': {e}", flush=True)
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.available or not self.client:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"[WARNING] Cache DELETE error for key '{key}': {e}", flush=True)
            return False

    def ttl(self, key: str) -> int | None:
        """
        Get remaining TTL for key

        Args:
            key: Cache key

        Returns:
            Remaining TTL in seconds, None if key doesn't exist or unavailable
        """
        if not self.available or not self.client:
            return None

        try:
            ttl_value = self.client.ttl(key)
            return ttl_value if ttl_value >= 0 else None
        except Exception as e:
            print(f"[WARNING] Cache TTL error for key '{key}': {e}", flush=True)
            return None

    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern

        Args:
            pattern: Redis key pattern (e.g. "market:*")

        Returns:
            Number of keys deleted
        """
        if not self.available or not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(
                f"[WARNING] Cache CLEAR_PATTERN error for pattern '{pattern}': {e}",
                flush=True,
            )
            return 0


# Global cache instance
_cache_service: CacheService | None = None


def get_cache() -> CacheService:
    """
    Get or create cache service instance

    Usage in FastAPI routes:
        from fastapi import Depends

        @router.get("/endpoint")
        def endpoint(cache: CacheService = Depends(get_cache)):
            value = cache.get("my_key")
            if not value:
                value = expensive_operation()
                cache.set("my_key", value, ttl=60)
            return value
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def init_cache():
    """Initialize cache service on application startup"""
    get_cache()
    print("[OK] Cache service initialized", flush=True)
