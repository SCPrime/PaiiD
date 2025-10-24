import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.services.cache import CacheService


class DummyClient:
    def __init__(self):
        self.storage: dict[str, tuple[int, str]] = {}

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.storage[key] = (ttl, value)

    def get(self, key: str) -> str | None:
        stored = self.storage.get(key)
        if not stored:
            return None
        return stored[1]

    def delete(self, key: str) -> None:  # pragma: no cover - not used directly
        self.storage.pop(key, None)

    def ttl(self, key: str) -> int:  # pragma: no cover - not used directly
        stored = self.storage.get(key)
        return stored[0] if stored else -2

    def keys(self, pattern: str) -> list[str]:  # pragma: no cover - not used directly
        return [key for key in self.storage if key.startswith(pattern.rstrip("*"))]


class InvalidJsonClient(DummyClient):
    def get(self, key: str) -> str:
        super().setex(key, 60, "not-json")
        return "not-json"


def test_settings_reject_invalid_redis_url():
    with pytest.raises(ValidationError):
        Settings(REDIS_URL="invalid-url")


def test_settings_empty_redis_url_returns_none():
    settings = Settings(REDIS_URL="")
    assert settings.REDIS_URL is None


def test_cache_service_requires_positive_ttl():
    cache = CacheService()
    cache.available = True
    cache.client = DummyClient()

    with pytest.raises(ValueError):
        cache.set("key", {"value": 1}, ttl=0)


def test_cache_service_serializes_values_and_logs_hits():
    cache = CacheService()
    cache.available = True
    client = DummyClient()
    cache.client = client

    assert cache.set("example", {"value": 1}, ttl=10)
    assert client.storage["example"][0] == 10

    # Successful retrieval returns decoded JSON
    assert cache.get("example") == {"value": 1}


def test_cache_service_handles_invalid_json():
    cache = CacheService()
    cache.available = True
    cache.client = InvalidJsonClient()

    assert cache.get("bad-json") is None
