from app.services import cache


def reset_cache_singleton():
    cache._cache_service = None


def test_cache_service_disabled(monkeypatch):
    reset_cache_singleton()
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setattr(cache.settings, "REDIS_URL", None, raising=False)

    service = cache.CacheService()
    assert service.available is False
    assert service.get("missing") is None
    assert service.set("missing", {"value": 1}) is False
    assert service.delete("missing") is False
    assert service.ttl("missing") is None
    assert service.clear_pattern("prefix:*") == 0


def test_cache_service_round_trip(fake_redis):
    reset_cache_singleton()

    service = cache.CacheService()
    assert service.available is True

    payload = {"price": 101.25}
    assert service.set("market:spy", payload, ttl=5) is True
    assert service.get("market:spy") == payload
    assert isinstance(service.ttl("market:spy"), int)
    assert service.delete("market:spy") is True
    assert service.get("market:spy") is None

    # Pattern clearing uses redis.delete with splat expansion
    service.set("market:spy", payload, ttl=5)
    service.set("market:qqq", payload, ttl=5)
    assert service.clear_pattern("market:*") == 2


def test_get_cache_returns_singleton(fake_redis):
    reset_cache_singleton()
    instance_one = cache.get_cache()
    instance_two = cache.get_cache()

    assert instance_one is instance_two
    assert instance_one.available is True
