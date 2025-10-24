"""
News Caching Service

Provides caching layer for news articles to reduce API calls and improve
response times. Prefers Redis for distributed caching with a file-based
fallback when Redis is unavailable.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from app.services.cache import get_cache


logger = logging.getLogger(__name__)

# Cache directory used for local fallback storage
CACHE_DIR = Path("data/news_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Cache TTL (5 minutes for market news, 15 minutes for company news)
MARKET_NEWS_TTL = 300  # 5 minutes
COMPANY_NEWS_TTL = 900  # 15 minutes


class NewsCache:
    """Distributed news cache with file-system fallback."""

    def __init__(
        self,
        max_cache_entries: int = 500,
        max_cache_size_mb: int = 50,
        cache_dir: Optional[Path] = None,
    ):
        """Initialise news cache with optional overrides for testing."""

        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_cache_entries = max_cache_entries
        self.max_cache_size_mb = max_cache_size_mb
        self.cache_service = get_cache()

    # ------------------------------------------------------------------
    # Redis helpers
    # ------------------------------------------------------------------
    def _redis_key(self, cache_type: str, **params) -> str:
        """Create Redis key namespace for news cache."""

        param_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        return f"news:{cache_type}:{param_hash}"

    # ------------------------------------------------------------------
    # File-system helpers
    # ------------------------------------------------------------------
    def _get_cache_key(self, cache_type: str, **params) -> str:
        """Generate cache key from request parameters."""

        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{cache_type}_{param_hash}"

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path to cache file."""

        return self.cache_dir / f"{cache_key}.json"

    def _enforce_cache_limits(self):
        """Enforce cache size limits using LRU eviction for file fallback."""

        try:
            cache_files = list(self.cache_dir.glob("*.json"))

            if not cache_files:
                return

            cache_files.sort(key=lambda f: f.stat().st_mtime)

            if len(cache_files) > self.max_cache_entries:
                files_to_remove = len(cache_files) - self.max_cache_entries
                for i in range(files_to_remove):
                    cache_files[i].unlink()
                    logger.info(f"🗑️ LRU evicted: {cache_files[i].name} (entry limit)")
                cache_files = cache_files[files_to_remove:]

            total_size_bytes = sum(f.stat().st_size for f in cache_files)
            max_size_bytes = self.max_cache_size_mb * 1024 * 1024

            if total_size_bytes > max_size_bytes:
                for cache_file in cache_files:
                    if total_size_bytes <= max_size_bytes:
                        break
                    file_size = cache_file.stat().st_size
                    cache_file.unlink()
                    total_size_bytes -= file_size
                    logger.info(f"🗑️ LRU evicted: {cache_file.name} (size limit)")

        except Exception as e:
            logger.error(f"❌ Cache limit enforcement error: {e!s}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get(self, cache_type: str, **params) -> list[dict[str, Any]] | None:
        """Get cached news articles using Redis when available."""

        ttl = MARKET_NEWS_TTL if cache_type == "market" else COMPANY_NEWS_TTL

        try:
            redis_key = self._redis_key(cache_type, **params)
            if self.cache_service.available:
                cached = self.cache_service.get(redis_key)
                if cached is not None:
                    logger.info(f"✅ Redis cache hit: {redis_key}")
                    if isinstance(cached, dict) and "articles" in cached:
                        return cached["articles"]
                    return cached

            cache_key = self._get_cache_key(cache_type, **params)
            cache_path = self._get_cache_path(cache_key)

            if not cache_path.exists():
                logger.debug(f"Cache miss: {cache_key}")
                return None

            with open(cache_path) as f:
                cache_data = json.load(f)

            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            age_seconds = (datetime.utcnow() - cached_at).total_seconds()

            if age_seconds > ttl:
                logger.debug(
                    f"Cache expired: {cache_key} (age: {age_seconds:.0f}s, TTL: {ttl}s)"
                )
                cache_path.unlink()
                return None

            logger.info(f"✅ File cache hit: {cache_key} (age: {age_seconds:.0f}s)")
            return cache_data["articles"]

        except Exception as e:
            logger.error(f"❌ Cache read error: {e!s}")
            return None

    def set(self, cache_type: str, articles: list[dict[str, Any]], **params):
        """Store news articles in cache with Redis first, file fallback second."""

        ttl = MARKET_NEWS_TTL if cache_type == "market" else COMPANY_NEWS_TTL
        payload: Dict[str, Any] = {
            "cached_at": datetime.utcnow().isoformat(),
            "params": params,
            "count": len(articles),
            "articles": articles,
        }

        try:
            redis_key = self._redis_key(cache_type, **params)
            if self.cache_service.available:
                stored = self.cache_service.set(redis_key, payload, ttl=ttl)
                if stored:
                    logger.info(f"✅ Cached {len(articles)} articles in Redis: {redis_key}")
                    return
                logger.warning(
                    f"⚠️ Redis cache store failed, falling back to file cache: {redis_key}"
                )

            cache_key = self._get_cache_key(cache_type, **params)
            cache_path = self._get_cache_path(cache_key)

            with open(cache_path, "w") as f:
                json.dump(payload, f)

            logger.info(f"✅ Cached {len(articles)} articles on disk: {cache_key}")
            self._enforce_cache_limits()

        except Exception as e:
            logger.error(f"❌ Cache write error: {e!s}")

    def invalidate(self, cache_type: str, **params):
        """Invalidate specific cache entry across Redis and file cache."""

        try:
            redis_key = self._redis_key(cache_type, **params)
            if self.cache_service.available:
                self.cache_service.delete(redis_key)
                logger.info(f"✅ Invalidated Redis cache: {redis_key}")

            cache_key = self._get_cache_key(cache_type, **params)
            cache_path = self._get_cache_path(cache_key)

            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"✅ Invalidated file cache: {cache_key}")

        except Exception as e:
            logger.error(f"❌ Cache invalidation error: {e!s}")

    def clear_all(self):
        """Clear all cached news entries."""

        try:
            if self.cache_service.available:
                cleared = self.cache_service.clear_pattern("news:*")
                logger.info(f"✅ Cleared {cleared} Redis news cache keys")

            count = 0
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1

            logger.info(f"✅ Cleared {count} cache files")

        except Exception as e:
            logger.error(f"❌ Cache clear error: {e!s}")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics combining Redis status and file fallback metrics."""

        stats: Dict[str, Any] = {
            "redis": get_cache().get_stats(),
            "fallback_entries": 0,
            "fallback_size_bytes": 0,
        }

        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            stats["fallback_entries"] = len(cache_files)
            stats["fallback_size_bytes"] = sum(f.stat().st_size for f in cache_files)
        except Exception as e:
            logger.error(f"❌ Stats error: {e!s}")

        return stats


# Singleton instance used by routers
_news_cache: NewsCache | None = None


def get_news_cache() -> NewsCache:
    """Get singleton NewsCache instance."""

    global _news_cache
    if _news_cache is None:
        _news_cache = NewsCache()
    return _news_cache

