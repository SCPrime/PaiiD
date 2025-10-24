"""Lightweight fallback implementation of the cachetools.TTLCache used in tests."""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any, Iterable


class TTLCache(OrderedDict):
    """Minimal TTL cache compatible with cachetools.TTLCache interface."""

    def __init__(self, maxsize: int = 128, ttl: float | None = 600):
        super().__init__()
        self.maxsize = maxsize
        self.ttl = ttl

    def __getitem__(self, key: Any) -> Any:  # type: ignore[override]
        value, expires_at = super().__getitem__(key)
        if expires_at is not None and expires_at < time.time():
            super().__delitem__(key)
            raise KeyError(key)
        return value

    def __setitem__(self, key: Any, value: Any) -> None:  # type: ignore[override]
        if len(self) >= self.maxsize:
            self._evict_oldest()
        expires_at = time.time() + self.ttl if self.ttl is not None else None
        super().__setitem__(key, (value, expires_at))

    def get(self, key: Any, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: Any, default: Any = None) -> Any:  # type: ignore[override]
        if key in self:
            value = self[key]
            super().__delitem__(key)
            return value
        if default is not None:
            return default
        raise KeyError(key)

    def clear(self) -> None:  # type: ignore[override]
        super().clear()

    def expire(self) -> None:
        """Manually remove expired keys."""
        now = time.time()
        keys_to_remove: Iterable[Any] = [
            key for key, (_, exp) in self.items() if exp is not None and exp < now
        ]
        for key in list(keys_to_remove):
            super().__delitem__(key)

    def _evict_oldest(self) -> None:
        if self:
            oldest_key = next(iter(self))
            super().__delitem__(oldest_key)
