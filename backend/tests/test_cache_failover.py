from __future__ import annotations

from pathlib import Path

from app.core import idempotency
from app.services import cache as cache_module
from app.services.news.news_cache import NewsCache


def reset_cache_service(monkeypatch):
    """Helper to reset global cache service between tests."""

    cache_module._cache_service = None  # type: ignore[attr-defined]
    monkeypatch.setattr(cache_module.settings, "REDIS_URL", None)


def test_cache_service_disabled_without_url(monkeypatch):
    reset_cache_service(monkeypatch)

    service = cache_module.get_cache()
    stats = service.get_stats()

    assert stats["status"] == "disabled"
    assert stats["available"] is False
    assert stats["url_configured"] is False


def test_idempotency_fallback_without_redis(monkeypatch):
    reset_cache_service(monkeypatch)

    idempotency._seen.clear()

    assert idempotency.check_and_store("order-123") is True
    assert idempotency.check_and_store("order-123") is False


def test_news_cache_file_fallback(monkeypatch, tmp_path):
    reset_cache_service(monkeypatch)

    news_cache = NewsCache(cache_dir=Path(tmp_path))
    sample_articles = [{"id": 1, "headline": "Redis outage"}]

    news_cache.set("market", sample_articles, category="general", limit=5)
    cached = news_cache.get("market", category="general", limit=5)

    assert cached == sample_articles

    stats = news_cache.get_stats()
    assert stats["redis"]["status"] == "disabled"
    assert stats["fallback_entries"] == 1
