"""
News Caching Service

Provides caching layer for news articles to reduce API calls
and improve response times. Uses file-based storage with TTL.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path("data/news_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Cache TTL (5 minutes for market news, 15 minutes for company news)
MARKET_NEWS_TTL = 300  # 5 minutes
COMPANY_NEWS_TTL = 900  # 15 minutes


class NewsCache:
    """File-based caching for news articles"""

    def __init__(self):
        self.cache_dir = CACHE_DIR

    def _get_cache_key(self, cache_type: str, **params) -> str:
        """Generate cache key from request parameters"""
        # Sort parameters for consistent keys
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{cache_type}_{param_hash}"

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path to cache file"""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, cache_type: str, **params) -> Optional[List[Dict[str, Any]]]:
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
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)

            # Check TTL
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            ttl = MARKET_NEWS_TTL if cache_type == 'market' else COMPANY_NEWS_TTL
            age_seconds = (datetime.utcnow() - cached_at).total_seconds()

            if age_seconds > ttl:
                logger.debug(f"Cache expired: {cache_key} (age: {age_seconds:.0f}s, TTL: {ttl}s)")
                # Delete expired cache
                cache_path.unlink()
                return None

            logger.info(f"✅ Cache hit: {cache_key} (age: {age_seconds:.0f}s)")
            return cache_data['articles']

        except Exception as e:
            logger.error(f"❌ Cache read error: {str(e)}")
            return None

    def set(self, cache_type: str, articles: List[Dict[str, Any]], **params):
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
                'cached_at': datetime.utcnow().isoformat(),
                'params': params,
                'count': len(articles),
                'articles': articles
            }

            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)

            logger.info(f"✅ Cached {len(articles)} articles: {cache_key}")

        except Exception as e:
            logger.error(f"❌ Cache write error: {str(e)}")

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
            logger.error(f"❌ Cache invalidation error: {str(e)}")

    def clear_all(self):
        """Clear all cached news"""
        try:
            count = 0
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1

            logger.info(f"✅ Cleared {count} cache files")

        except Exception as e:
            logger.error(f"❌ Cache clear error: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)

            # Count by type
            market_count = len([f for f in cache_files if f.name.startswith('market_')])
            company_count = len([f for f in cache_files if f.name.startswith('company_')])

            # Check expired
            expired = 0
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    cached_at = datetime.fromisoformat(cache_data['cached_at'])
                    cache_type = 'market' if cache_file.name.startswith('market_') else 'company'
                    ttl = MARKET_NEWS_TTL if cache_type == 'market' else COMPANY_NEWS_TTL
                    age = (datetime.utcnow() - cached_at).total_seconds()
                    if age > ttl:
                        expired += 1
                except:
                    expired += 1

            return {
                'total_entries': len(cache_files),
                'market_cache': market_count,
                'company_cache': company_count,
                'expired_entries': expired,
                'total_size_bytes': total_size,
                'cache_dir': str(self.cache_dir)
            }

        except Exception as e:
            logger.error(f"❌ Stats error: {str(e)}")
            return {}


# Singleton instance
_news_cache = None


def get_news_cache() -> NewsCache:
    """Get singleton NewsCache instance"""
    global _news_cache
    if _news_cache is None:
        _news_cache = NewsCache()
    return _news_cache
