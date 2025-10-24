from __future__ import annotations

import time
from collections import OrderedDict
from typing import Iterator, MutableMapping, TypeVar

KT = TypeVar("KT")
VT = TypeVar("VT")


class TTLCache(OrderedDict, MutableMapping[KT, VT]):
    """Minimal TTL cache implementation for environments without cachetools."""

    def __init__(self, maxsize: int, ttl: float):
        super().__init__()
        self.maxsize = maxsize
        self.ttl = ttl

    def __getitem__(self, key: KT) -> VT:
        value, expires_at = super().__getitem__(key)
        if expires_at < time.time():
            super().__delitem__(key)
            raise KeyError(key)
        return value

    def __setitem__(self, key: KT, value: VT) -> None:
        super().__setitem__(key, (value, time.time() + self.ttl))
        self._evict()

    def __delitem__(self, key: KT) -> None:
        super().__delitem__(key)

    def __iter__(self) -> Iterator[KT]:
        return super().__iter__()

    def __len__(self) -> int:
        self._purge_expired()
        return super().__len__()

    def get(self, key: KT, default: VT | None = None) -> VT | None:
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: KT, default: VT | None = None) -> VT | None:
        if key in self:
            value, _ = super().pop(key)
            return value
        return default

    def clear(self) -> None:  # type: ignore[override]
        super().clear()

    def _evict(self) -> None:
        self._purge_expired()
        while len(super()) > self.maxsize:
            super().popitem(last=False)

    def _purge_expired(self) -> None:
        now = time.time()
        expired_keys = [key for key, (_, expiry) in super().items() if expiry < now]
        for key in expired_keys:
            super().__delitem__(key)


__all__ = ["TTLCache"]
