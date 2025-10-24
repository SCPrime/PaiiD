from app.core import store


def reset_store_state():
    store._redis = None
    if hasattr(store.idem_check_and_store, "_mem"):
        store.idem_check_and_store._mem.clear()  # type: ignore[attr-defined]


def test_idem_check_and_store_memory(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    reset_store_state()
    monkeypatch.setattr(store.time, "time", lambda: 1000.0)

    assert store.idem_check_and_store("order-1", ttl_sec=10) is True
    assert store.idem_check_and_store("order-1", ttl_sec=10) is False

    # Advance time beyond TTL to ensure entry expires
    monkeypatch.setattr(store.time, "time", lambda: 1012.0)
    assert store.idem_check_and_store("order-1", ttl_sec=10) is True


def test_idem_check_and_store_with_fake_redis(fake_redis):
    reset_store_state()
    assert store.idem_check_and_store("order-redis", ttl_sec=30) is True
    assert store.idem_check_and_store("order-redis", ttl_sec=30) is False
    assert fake_redis.ttl("idemp:order-redis") > 0

    # Removing the key should allow it to be reprocessed
    fake_redis.delete("idemp:order-redis")
    assert store.idem_check_and_store("order-redis", ttl_sec=30) is True

