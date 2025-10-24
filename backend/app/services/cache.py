"""Redis cache service and instrumentation helpers."""

import json
import logging
from typing import Any

import redis

from ..core.config import settings


logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service with graceful degradation and instrumentation."""

    def __init__(self):
        self.client: redis.Redis | None = None
        self.available = False
        self._initialize()

    def _initialize(self):
        """Initialize Redis connection and record outcome."""
        if not settings.REDIS_URL:
            logger.info("Redis URL not configured; cache service disabled")
            return

        logger.info("Attempting Redis connection")
        try:
            self.client = redis.from_url(
                str(settings.REDIS_URL),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.client.ping()
            self.available = True
            logger.info("Redis cache connected", extra={"redis_available": True})
        except Exception:  # pragma: no cover - network errors vary
            logger.warning(
                "Redis connection failed; caching disabled",
                extra={"redis_available": False},
                exc_info=True,
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
            logger.debug(
                "Redis unavailable during GET; returning None",
                extra={"redis_key": key, "redis_available": False},
            )
            return None

        try:
            value = self.client.get(key)
            if value:
                try:
                    decoded = json.loads(value)
                except json.JSONDecodeError:
                    logger.warning(
                        "Redis GET decode error; returning None",
                        extra={"redis_key": key},
                        exc_info=True,
                    )
                    return None
                logger.debug(
                    "Redis GET hit", extra={"redis_key": key, "cache_hit": True}
                )
                return decoded
            logger.debug(
                "Redis GET miss", extra={"redis_key": key, "cache_hit": False}
            )
            return None
        except Exception:  # pragma: no cover - redis library exceptions vary
            logger.warning(
                "Redis GET error; returning None",
                extra={"redis_key": key},
                exc_info=True,
            )
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
        if ttl <= 0:
            raise ValueError("TTL must be a positive integer")

        if not self.available or not self.client:
            logger.debug(
                "Redis unavailable during SET; skipping write",
                extra={"redis_key": key, "redis_available": False},
            )
            return False

        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            logger.debug(
                "Redis SET succeeded", extra={"redis_key": key, "redis_ttl": ttl}
            )
            return True
        except (TypeError, ValueError):
            logger.warning(
                "Redis SET serialization error",
                extra={"redis_key": key},
                exc_info=True,
            )
            return False
        except Exception:  # pragma: no cover - redis library exceptions vary
            logger.warning(
                "Redis SET error", extra={"redis_key": key}, exc_info=True
            )
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
            logger.debug(
                "Redis unavailable during DELETE; skipping",
                extra={"redis_key": key, "redis_available": False},
            )
            return False

        try:
            self.client.delete(key)
            logger.debug("Redis DELETE succeeded", extra={"redis_key": key})
            return True
        except Exception:  # pragma: no cover - redis library exceptions vary
            logger.warning(
                "Redis DELETE error", extra={"redis_key": key}, exc_info=True
            )
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
            logger.debug(
                "Redis unavailable during TTL; returning None",
                extra={"redis_key": key, "redis_available": False},
            )
            return None

        try:
            ttl_value = self.client.ttl(key)
            logger.debug(
                "Redis TTL fetched", extra={"redis_key": key, "redis_ttl": ttl_value}
            )
            return ttl_value if ttl_value >= 0 else None
        except Exception:  # pragma: no cover - redis library exceptions vary
            logger.warning(
                "Redis TTL error", extra={"redis_key": key}, exc_info=True
            )
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
            logger.debug(
                "Redis unavailable during CLEAR_PATTERN; skipping",
                extra={"redis_pattern": pattern, "redis_available": False},
            )
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.debug(
                    "Redis CLEAR_PATTERN deleted keys",
                    extra={
                        "redis_pattern": pattern,
                        "redis_deleted_keys": len(keys),
                        "redis_deleted_count": deleted,
                    },
                )
                return deleted
            logger.debug(
                "Redis CLEAR_PATTERN found no keys",
                extra={"redis_pattern": pattern, "redis_deleted_keys": 0},
            )
            return 0
        except Exception:  # pragma: no cover - redis library exceptions vary
            logger.warning(
                "Redis CLEAR_PATTERN error",
                extra={"redis_pattern": pattern},
                exc_info=True,
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
    logger.info("Cache service initialized")
