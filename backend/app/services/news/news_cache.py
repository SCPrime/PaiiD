"""
News Caching Service

Provides caching layer for news articles to reduce API calls
and improve response times. Uses file-based storage with TTL.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ...core.time_utils import ensure_utc, utc_now, utc_now_isoformat

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path("data/news_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Cache TTL (5 minutes for market news, 15 minutes for company news)
MARKET_NEWS_TTL = 300  # 5 minutes
COMPANY_NEWS_TTL = 900  # 15 minutes


class NewsCache:
    """File-based caching for news articles"""

    def __init__(self, max_cache_entries: int = 500, max_cache_size_mb: int = 50):
        """
        Initialize news cache with size limits

        Args:
            max_cache_entries: Maximum number of cache files (default 500)
            max_cache_size_mb: Maximum total cache size in MB (default 50)
        """
        self.cache_dir = CACHE_DIR
        self.max_cache_entries = max_cache_entries
        self.max_cache_size_mb = max_cache_size_mb

    def _enforce_cache_limits(self):
        """
        Enforce cache size limits using LRU eviction

        Evicts oldest cache files if:
        - Total entries exceed max_cache_entries
        - Total size exceeds max_cache_size_mb
        """
        try:
            cache_files = list(self.cache_dir.glob("*.json"))

            if not cache_files:
                return

            # Sort by modification time (oldest first) for LRU eviction
            cache_files.sort(key=lambda f: f.stat().st_mtime)

            # Check entry count limit
            if len(cache_files) > self.max_cache_entries:
                files_to_remove = len(cache_files) - self.max_cache_entries
                for i in range(files_to_remove):
                    cache_files[i].unlink()
                    logger.info(f"🗑️ LRU evicted: {cache_files[i].name} (entry limit)")

                # Update list after removals
                cache_files = cache_files[files_to_remove:]

            # Check total size limit
            total_size_bytes = sum(f.stat().st_size for f in cache_files)
            max_size_bytes = self.max_cache_size_mb * 1024 * 1024

            if total_size_bytes > max_size_bytes:
                # Evict oldest files until under limit
                for cache_file in cache_files:
                    if total_size_bytes <= max_size_bytes:
                        break

                    file_size = cache_file.stat().st_size
                    cache_file.unlink()
                    total_size_bytes -= file_size
                    logger.info(f"🗑️ LRU evicted: {cache_file.name} (size limit)")

        except Exception as e:
            logger.error(f"❌ Cache limit enforcement error: {e!s}")

    def _get_cache_key(self, cache_type: str, **params) -> str:
        """Generate cache key from request parameters"""
        # Sort parameters for consistent keys
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{cache_type}_{param_hash}"

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path to cache file"""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, cache_type: str, **params) -> list[dict[str, Any]] | None:
        """
        Get cached news articles

        Args:
            cache_type: Type of cache ('market' or 'company')
            **params: Request parameters for cache key generation

        Returns:
            Cached articles or None if cache miss/expired
        """
        try:
            cache_key = self._get_cache_key(cache_type, **params)
            cache_path = self._get_cache_path(cache_key)

            if not cache_path.exists():
                logger.debug(f"Cache miss: {cache_key}")
                return None

            # Load cache file
            with open(cache_path) as f:
                cache_data = json.load(f)

            # Check TTL
            cached_at = ensure_utc(
                datetime.fromisoformat(cache_data["cached_at"].replace("Z", "+00:00"))
            )
            ttl = MARKET_NEWS_TTL if cache_type == "market" else COMPANY_NEWS_TTL
            age_seconds = (utc_now() - cached_at).total_seconds()

            if age_seconds > ttl:
                logger.debug(f"Cache expired: {cache_key} (age: {age_seconds:.0f}s, TTL: {ttl}s)")
                # Delete expired cache
                cache_path.unlink()
                return None

            logger.info(f"✅ Cache hit: {cache_key} (age: {age_seconds:.0f}s)")
            return cache_data["articles"]

        except Exception as e:
            logger.error(f"❌ Cache read error: {e!s}")
            return None

    def set(self, cache_type: str, articles: list[dict[str, Any]], **params):
        """
        Store news articles in cache

        Args:
            cache_type: Type of cache ('market' or 'company')
            articles: List of article dictionaries
            **params: Request parameters for cache key generation
        """
        try:
            cache_key = self._get_cache_key(cache_type, **params)
            cache_path = self._get_cache_path(cache_key)

            cache_data = {
                "cached_at": utc_now_isoformat(),
                "params": params,
                "count": len(articles),
                "articles": articles,
            }

            with open(cache_path, "w") as f:
                json.dump(cache_data, f)

            logger.info(f"✅ Cached {len(articles)} articles: {cache_key}")

            # Enforce cache size limits after writing
            self._enforce_cache_limits()

        except Exception as e:
            logger.error(f"❌ Cache write error: {e!s}")

    def invalidate(self, cache_type: str, **params):
        """
        Invalidate specific cache entry

        Args:
            cache_type: Type of cache ('market' or 'company')
            **params: Request parameters for cache key generation
        """
        try:
            cache_key = self._get_cache_key(cache_type, **params)
            cache_path = self._get_cache_path(cache_key)

            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"✅ Invalidated cache: {cache_key}")

        except Exception as e:
            logger.error(f"❌ Cache invalidation error: {e!s}")

    def clear_all(self):
        """Clear all cached news"""
        try:
            count = 0
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1

            logger.info(f"✅ Cleared {count} cache files")

        except Exception as e:
            logger.error(f"❌ Cache clear error: {e!s}")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)

            # Count by type
            market_count = len([f for f in cache_files if f.name.startswith("market_")])
            company_count = len([f for f in cache_files if f.name.startswith("company_")])

            # Check expired
            expired = 0
            for cache_file in cache_files:
                try:
                    with open(cache_file) as f:
                        cache_data = json.load(f)
                    cached_at = ensure_utc(
                        datetime.fromisoformat(cache_data["cached_at"].replace("Z", "+00:00"))
                    )
                    cache_type = "market" if cache_file.name.startswith("market_") else "company"
                    ttl = MARKET_NEWS_TTL if cache_type == "market" else COMPANY_NEWS_TTL
                    age = (utc_now() - cached_at).total_seconds()
                    if age > ttl:
                        expired += 1
                except (OSError, json.JSONDecodeError, KeyError, ValueError) as e:
                    # Corrupted or malformed cache file
                    expired += 1
                    logger.debug(f"Cache stats: corrupted file {cache_file.name}: {e}")

            return {
                "total_entries": len(cache_files),
                "market_cache": market_count,
                "company_cache": company_count,
                "expired_entries": expired,
                "total_size_bytes": total_size,
                "cache_dir": str(self.cache_dir),
            }

        except Exception as e:
            logger.error(f"❌ Stats error: {e!s}")
            return {}


# Singleton instance
_news_cache = None


def get_news_cache() -> NewsCache:
    """Get singleton NewsCache instance"""
    global _news_cache
    if _news_cache is None:
        _news_cache = NewsCache()
    return _news_cache
