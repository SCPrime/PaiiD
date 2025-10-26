"""
Enhanced Cache Service

Centralized caching layer with:
- Redis cache operations with automatic fallback
- In-memory cache when Redis unavailable
- Cache invalidation strategies
- TTL management
- Cache warming capabilities
- Cache statistics and monitoring

This is an enhanced version that can coexist with or replace the existing cache.py.
"""

import json
import logging
import time
from collections.abc import Callable
from typing import Any

import redis


logger = logging.getLogger(__name__)


class CacheStats:
    """Cache statistics tracker"""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.errors = 0
        self.start_time = time.time()

    def record_hit(self):
        """Record cache hit"""
        self.hits += 1

    def record_miss(self):
        """Record cache miss"""
        self.misses += 1

    def record_set(self):
        """Record cache set"""
        self.sets += 1

    def record_delete(self):
        """Record cache delete"""
        self.deletes += 1

    def record_error(self):
        """Record cache error"""
        self.errors += 1

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        uptime_seconds = time.time() - self.start_time

        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "errors": self.errors,
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
            "uptime_seconds": round(uptime_seconds, 2),
        }

    def reset(self):
        """Reset statistics"""
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.errors = 0
        self.start_time = time.time()


class CacheService:
    """
    Enhanced cache service with Redis and in-memory fallback.

    Features:
    - Automatic Redis connection with fallback to in-memory cache
    - TTL support for all cache entries
    - Pattern-based invalidation
    - Cache statistics and monitoring
    - Cache warming for frequently accessed data
    """

    def __init__(self, redis_url: str | None = None):
        """
        Initialize cache service.

        Args:
            redis_url: Redis connection URL (e.g., "redis://localhost:6379/0")
                      If None, reads from settings or uses in-memory fallback
        """
        self.redis_client: redis.Redis | None = None
        self.memory_cache: dict[str, tuple[Any, float]] = {}  # (value, expiry_time)
        self.available = False
        self.stats = CacheStats()

        # Initialize Redis connection
        if redis_url:
            self._init_redis(redis_url)
        else:
            # Try to get Redis URL from settings
            try:
                from ..core.config import settings

                if settings.REDIS_URL:
                    self._init_redis(settings.REDIS_URL)
                else:
                    logger.warning("No Redis URL configured, using in-memory cache")
            except Exception as e:
                logger.warning(f"Failed to load settings, using in-memory cache: {e}")

    def _init_redis(self, url: str) -> None:
        """
        Initialize Redis client with fallback.

        Args:
            url: Redis connection URL
        """
        try:
            self.redis_client = redis.from_url(
                url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
                socket_keepalive=True,
            )
            # Test connection
            self.redis_client.ping()
            self.available = True
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory fallback")
            self.redis_client = None
            self.available = False

    async def get(self, key: str) -> Any | None:
        """
        Get value from cache (Redis or memory fallback).

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found

        Example:
            >>> cache = CacheService()
            >>> value = await cache.get("user:123")
        """
        # Try Redis first
        if self.available and self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value is not None:
                    self.stats.record_hit()
                    logger.debug(f"Cache HIT (Redis): {key}")
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis GET error for key '{key}': {e}")
                self.stats.record_error()
                # Fall through to memory cache

        # Try memory cache
        if key in self.memory_cache:
            value, expiry = self.memory_cache[key]
            # Check if expired
            if expiry > time.time():
                self.stats.record_hit()
                logger.debug(f"Cache HIT (Memory): {key}")
                return value
            else:
                # Expired, remove it
                del self.memory_cache[key]

        # Cache miss
        self.stats.record_miss()
        logger.debug(f"Cache MISS: {key}")
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,
    ) -> bool:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 300 = 5 minutes)

        Returns:
            True if successful, False otherwise

        Example:
            >>> cache = CacheService()
            >>> await cache.set("user:123", {"name": "John"}, ttl=600)
        """
        try:
            serialized = json.dumps(value)

            # Try Redis first
            if self.available and self.redis_client:
                try:
                    self.redis_client.setex(key, ttl, serialized)
                    self.stats.record_set()
                    logger.debug(f"Cache SET (Redis): {key} (TTL: {ttl}s)")
                    return True
                except Exception as e:
                    logger.error(f"Redis SET error for key '{key}': {e}")
                    self.stats.record_error()
                    # Fall through to memory cache

            # Use memory cache as fallback
            expiry_time = time.time() + ttl
            self.memory_cache[key] = (value, expiry_time)
            self.stats.record_set()
            logger.debug(f"Cache SET (Memory): {key} (TTL: {ttl}s)")

            # Cleanup expired entries periodically
            self._cleanup_memory_cache()

            return True

        except Exception as e:
            logger.error(f"Cache SET error for key '{key}': {e}")
            self.stats.record_error()
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        success = False

        # Delete from Redis
        if self.available and self.redis_client:
            try:
                self.redis_client.delete(key)
                success = True
                logger.debug(f"Cache DELETE (Redis): {key}")
            except Exception as e:
                logger.error(f"Redis DELETE error for key '{key}': {e}")
                self.stats.record_error()

        # Delete from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
            success = True
            logger.debug(f"Cache DELETE (Memory): {key}")

        if success:
            self.stats.record_delete()

        return success

    async def invalidate(self, pattern: str) -> int:
        """
        Invalidate cache keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "market:*", "user:123:*")

        Returns:
            Number of keys invalidated

        Example:
            >>> cache = CacheService()
            >>> count = await cache.invalidate("market:quotes:*")
            >>> print(f"Invalidated {count} keys")
        """
        count = 0

        # Invalidate in Redis
        if self.available and self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
                    logger.info(f"Invalidated {count} keys matching '{pattern}' in Redis")
            except Exception as e:
                logger.error(f"Redis INVALIDATE error for pattern '{pattern}': {e}")
                self.stats.record_error()

        # Invalidate in memory cache
        # Convert Redis pattern to Python regex (simplified)
        import re

        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        regex = re.compile(regex_pattern)

        memory_keys_to_delete = [
            key for key in self.memory_cache.keys() if regex.match(key)
        ]

        for key in memory_keys_to_delete:
            del self.memory_cache[key]
            count += 1

        if memory_keys_to_delete:
            logger.info(
                f"Invalidated {len(memory_keys_to_delete)} keys "
                f"matching '{pattern}' in memory"
            )

        return count

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: int = 300,
    ) -> Any:
        """
        Get value from cache or set it using factory function.

        This is a common cache pattern that checks cache first,
        and if not found, calls factory function to generate value
        and stores it in cache.

        Args:
            key: Cache key
            factory: Function to call if cache miss
            ttl: Time to live in seconds

        Returns:
            Cached or freshly generated value

        Example:
            >>> cache = CacheService()
            >>> def expensive_calculation():
            ...     return sum(range(1000000))
            >>> result = await cache.get_or_set(
            ...     "calculation:result",
            ...     expensive_calculation,
            ...     ttl=3600
            ... )
        """
        # Try to get from cache
        value = await self.get(key)

        if value is not None:
            return value

        # Cache miss - generate value
        value = factory()

        # Store in cache
        await self.set(key, value, ttl=ttl)

        return value

    async def warm_cache(
        self,
        keys_and_factories: dict[str, tuple[Callable[[], Any], int]],
    ) -> int:
        """
        Warm cache with multiple keys.

        Useful for preloading frequently accessed data.

        Args:
            keys_and_factories: Dictionary mapping cache keys to (factory, ttl) tuples

        Returns:
            Number of keys warmed

        Example:
            >>> cache = CacheService()
            >>> await cache.warm_cache({
            ...     "market:spy": (lambda: get_spy_quote(), 60),
            ...     "market:qqq": (lambda: get_qqq_quote(), 60),
            ... })
        """
        count = 0

        for key, (factory, ttl) in keys_and_factories.items():
            try:
                value = factory() if callable(factory) else factory
                success = await self.set(key, value, ttl=ttl)
                if success:
                    count += 1
            except Exception as e:
                logger.error(f"Failed to warm cache for key '{key}': {e}")

        logger.info(f"Warmed {count}/{len(keys_and_factories)} cache keys")
        return count

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        stats = self.stats.get_stats()
        stats["backend"] = "redis" if self.available else "memory"
        stats["memory_cache_size"] = len(self.memory_cache)

        if self.available and self.redis_client:
            try:
                info = self.redis_client.info("stats")
                stats["redis_total_commands"] = info.get("total_commands_processed", 0)
                stats["redis_keyspace_hits"] = info.get("keyspace_hits", 0)
                stats["redis_keyspace_misses"] = info.get("keyspace_misses", 0)
            except Exception as e:
                logger.error(f"Failed to get Redis stats: {e}")

        return stats

    def reset_stats(self) -> None:
        """Reset cache statistics"""
        self.stats.reset()
        logger.info("Cache statistics reset")

    def _cleanup_memory_cache(self) -> None:
        """
        Cleanup expired entries from memory cache.

        Called periodically to prevent memory leak.
        """
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, expiry) in self.memory_cache.items()
            if expiry <= current_time
        ]

        for key in expired_keys:
            del self.memory_cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired keys from memory cache")

    def clear_all(self) -> bool:
        """
        Clear all cache entries (use with caution).

        Returns:
            True if successful
        """
        try:
            # Clear Redis
            if self.available and self.redis_client:
                self.redis_client.flushdb()
                logger.warning("Cleared all Redis cache entries")

            # Clear memory cache
            self.memory_cache.clear()
            logger.warning("Cleared all memory cache entries")

            return True

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False


# Singleton instance
_cache_service: CacheService | None = None


def get_cache_service(redis_url: str | None = None) -> CacheService:
    """
    Get or create cache service instance.

    Args:
        redis_url: Optional Redis URL

    Returns:
        CacheService instance

    Usage in routers:
        from ..services.cache_service import get_cache_service

        @router.get("/data")
        async def get_data():
            cache = get_cache_service()

            # Get or set pattern
            data = await cache.get_or_set(
                "expensive:data",
                lambda: fetch_expensive_data(),
                ttl=600
            )
            return data
    """
    global _cache_service

    if _cache_service is None:
        _cache_service = CacheService(redis_url=redis_url)

    return _cache_service


def init_cache_service(redis_url: str | None = None) -> None:
    """
    Initialize cache service on application startup.

    Args:
        redis_url: Optional Redis URL
    """
    get_cache_service(redis_url=redis_url)
    logger.info("Cache service initialized")
