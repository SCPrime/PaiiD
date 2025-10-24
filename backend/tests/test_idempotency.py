from app.core import idempotency


def reset_idempotency_state():
    idempotency._redis = None
    idempotency._seen.clear()


def test_check_and_store_memory(monkeypatch):
    reset_idempotency_state()
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setattr(idempotency.settings, "IDMP_TTL_SECONDS", 2, raising=False)
    monkeypatch.setattr(idempotency.time, "time", lambda: 1000.0)

    assert idempotency.check_and_store("req-1") is True
    assert idempotency.check_and_store("req-1") is False

    # Simulate TTL expiry
    monkeypatch.setattr(idempotency.time, "time", lambda: 1003.0)
    assert idempotency.check_and_store("req-1") is True


def test_check_and_store_with_fake_redis(fake_redis, monkeypatch):
    reset_idempotency_state()
    monkeypatch.setattr(idempotency.settings, "IDMP_TTL_SECONDS", 5, raising=False)

    assert idempotency.check_and_store("req-redis") is True
    assert idempotency.check_and_store("req-redis") is False
    assert fake_redis.ttl("idemp:req-redis") > 0

    fake_redis.delete("idemp:req-redis")
    assert idempotency.check_and_store("req-redis") is True
