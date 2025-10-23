"""
Redis Configuration - Graceful Degradation
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis not installed - caching disabled")
    REDIS_AVAILABLE = False
    redis = None

class CacheService:
    def __init__(self, url: Optional[str] = None):
        if not REDIS_AVAILABLE or not url:
            self.client = None
            logger.info("Cache disabled (no Redis)")
        else:
            try:
                self.client = redis.from_url(url)
                self.client.ping()
            except Exception as e:
                logger.warning(f"Redis unavailable: {e}")
                self.client = None
