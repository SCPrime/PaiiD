"""Lightweight cachetools fallback used in tests."""

from __future__ import annotations

import time
from typing import Any, Callable, Hashable


class TTLCache(dict):
    def __init__(self, maxsize: int = 128, ttl: float = 600.0):
        super().__init__()
        self.maxsize = maxsize
        self.ttl = ttl
        self._expires: dict[Hashable, float] = {}

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self._purge()
        if len(self) >= self.maxsize:
            oldest_key = next(iter(self), None)
            if oldest_key is not None:
                super().__delitem__(oldest_key)
                self._expires.pop(oldest_key, None)
        self._expires[key] = time.time() + self.ttl
        super().__setitem__(key, value)

    def __getitem__(self, key: Hashable) -> Any:
        self._purge()
        expires_at = self._expires.get(key)
        if expires_at is None or expires_at < time.time():
            self._expires.pop(key, None)
            raise KeyError(key)
        return super().__getitem__(key)

    def __contains__(self, key: object) -> bool:  # type: ignore[override]
        if not super().__contains__(key):
            return False
        expires_at = self._expires.get(key)
        if expires_at is None or expires_at < time.time():
            self._expires.pop(key, None)
            super().pop(key, None)
            return False
        return True

    def get(self, key: Hashable, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def _purge(self) -> None:
        now = time.time()
        expired = [key for key, expiry in self._expires.items() if expiry < now]
        for key in expired:
            self._expires.pop(key, None)
            super().pop(key, None)


def cached(cache: TTLCache) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        store = cache

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(sorted(kwargs.items())))
            if key in store:
                try:
                    return store[key]
                except KeyError:
                    pass
            result = func(*args, **kwargs)
            store[key] = result
            return result

        return wrapper

    return decorator

__all__ = ["TTLCache", "cached"]
