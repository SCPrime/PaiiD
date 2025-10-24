"""
Redis Client for ML Prediction Caching
High-performance caching layer for expensive ML operations
"""

import json
import logging
from typing import Any

from redis import asyncio as aioredis


logger = logging.getLogger(__name__)

# Global Redis client
_redis_client = None


class RedisCache:
    """Async Redis cache for ML predictions"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client = None
        self._connected = False

    async def connect(self):
        """Connect to Redis"""
        if self.client is None:
            try:
                self.client = await aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                )
                # Test connection
                await self.client.ping()
                self._connected = True
                logger.info(f"✅ Redis connected: {self.redis_url}")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}. Running without cache.")
                self._connected = False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            self._connected = False
            logger.info("Redis disconnected")

    async def get(self, key: str) -> str | None:
        """Get value from cache"""
        if not self._connected:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.warning(f"Redis GET failed: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int = 300):
        """Set value in cache with TTL (seconds)"""
        if not self._connected:
            return False
        try:
            await self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.warning(f"Redis SET failed: {e}")
            return False

    async def setex(self, key: str, ttl: int, value: str):
        """Set value with expiration (alias for compatibility)"""
        return await self.set(key, value, ttl)

    async def delete(self, key: str):
        """Delete key from cache"""
        if not self._connected:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE failed: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._connected:
            return False
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.warning(f"Redis EXISTS failed: {e}")
            return False

    async def keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern"""
        if not self._connected:
            return []
        try:
            return await self.client.keys(pattern)
        except Exception as e:
            logger.warning(f"Redis KEYS failed: {e}")
            return []

    async def flushdb(self):
        """Clear all keys (USE WITH CAUTION)"""
        if not self._connected:
            return False
        try:
            await self.client.flushdb()
            logger.info("Redis database flushed")
            return True
        except Exception as e:
            logger.error(f"Redis FLUSHDB failed: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._connected


class MLPredictionCache:
    """High-level cache for ML predictions"""

    def __init__(self, redis: RedisCache):
        self.redis = redis

    async def cache_prediction(
        self,
        model_id: str,
        input_hash: str,
        prediction: Any,
        ttl: int = 300,
    ):
        """
        Cache an ML prediction

        Args:
            model_id: Model identifier (e.g., "regime_detector")
            input_hash: Hash of input parameters
            prediction: Prediction result (will be JSON serialized)
            ttl: Time to live in seconds (default 5 minutes)
        """
        key = f"ml:prediction:{model_id}:{input_hash}"
        value = json.dumps(prediction, default=str)
        await self.redis.set(key, value, ttl)

    async def get_cached_prediction(
        self,
        model_id: str,
        input_hash: str,
    ) -> Any | None:
        """
        Get cached prediction

        Args:
            model_id: Model identifier
            input_hash: Hash of input parameters

        Returns:
            Cached prediction or None if not found
        """
        key = f"ml:prediction:{model_id}:{input_hash}"
        cached = await self.redis.get(key)
        if cached:
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                logger.warning(f"Failed to decode cached prediction: {key}")
                return None
        return None

    async def invalidate_model_cache(self, model_id: str):
        """Invalidate all cached predictions for a model"""
        pattern = f"ml:prediction:{model_id}:*"
        keys = await self.redis.keys(pattern)
        for key in keys:
            await self.redis.delete(key)
        logger.info(f"Invalidated {len(keys)} cached predictions for {model_id}")


# Global instances
_redis_cache = None
_ml_prediction_cache = None


async def get_redis() -> RedisCache:
    """Get or create Redis cache instance"""
    global _redis_cache
    if _redis_cache is None:
        # Try to get Redis URL from environment
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        _redis_cache = RedisCache(redis_url)
        await _redis_cache.connect()
    return _redis_cache


async def get_ml_cache() -> MLPredictionCache:
    """Get or create ML prediction cache"""
    global _ml_prediction_cache
    if _ml_prediction_cache is None:
        redis = await get_redis()
        _ml_prediction_cache = MLPredictionCache(redis)
    return _ml_prediction_cache


def generate_input_hash(**kwargs) -> str:
    """Generate hash from input parameters"""
    import hashlib
    # Sort kwargs for consistent hashing
    sorted_items = sorted(kwargs.items())
    input_str = json.dumps(sorted_items, sort_keys=True)
    return hashlib.md5(input_str.encode()).hexdigest()
