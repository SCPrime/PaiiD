"""
Redis Cache Service

Provides Redis caching with graceful fallback when Redis is unavailable.
Implements common cache operations with TTL support and exposes connection
diagnostics for observability.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict

import redis

from ..core.config import settings


class CacheService:
    """Redis cache service with graceful degradation"""

    def __init__(self):
        self.client: redis.Redis | None = None
        self.available = False
        self.latency_ms: float | None = None
        self.last_error: str | None = None
        self.status: str = "disabled"  # disabled|connected|error
        self._initialize()

    def _initialize(self):
        """Initialize Redis connection"""
        self.client = None
        self.available = False
        self.latency_ms = None
        self.last_error = None
        self.status = "disabled"

        if not settings.REDIS_URL:
            print("[WARNING] REDIS_URL not configured - caching disabled", flush=True)
            self.last_error = "REDIS_URL not configured"
            return

        try:
            start = time.perf_counter()
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.client.ping()
            self.available = True
            self.status = "connected"
            self.latency_ms = (time.perf_counter() - start) * 1000
            print("[OK] Redis cache connected", flush=True)
        except Exception as e:
            print(f"[WARNING] Redis connection failed: {e} - caching disabled", flush=True)
            self.client = None
            self.available = False
            self.status = "error"
            self.last_error = str(e)

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
                return json.loads(value)
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

    def set_if_not_exists(self, key: str, value: Any, ttl: int) -> bool:
        """Atomically set a key if it does not already exist."""
        if not self.available or not self.client:
            return False

        try:
            serialized = json.dumps(value)
            # Use native SET with NX flag for atomic behaviour
            result = self.client.set(key, serialized, nx=True, ex=ttl)
            return bool(result)
        except Exception as e:
            print(f"[WARNING] Cache SETNX error for key '{key}': {e}", flush=True)
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
            print(f"[WARNING] Cache CLEAR_PATTERN error for pattern '{pattern}': {e}", flush=True)
            return 0

    def refresh(self):
        """Re-attempt connection using current settings."""
        self._initialize()

    def get_stats(self) -> Dict[str, Any]:
        """Return connection diagnostics for monitoring dashboards."""
        return {
            "status": self.status,
            "available": self.available,
            "latency_ms": self.latency_ms,
            "last_error": self.last_error,
            "url_configured": bool(settings.REDIS_URL),
        }


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
