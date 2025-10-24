"""Minimal TTL cache implementation used for testing environments.

This lightweight fallback provides the subset of cachetools.TTLCache
behaviour that the application relies on without pulling in the external
package. Keys expire after the configured TTL and the cache evicts the
oldest entry when the maximum size is exceeded.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Generic, Iterator, MutableMapping, Tuple, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class TTLCache(Generic[K, V], MutableMapping[K, V]):
    def __init__(self, maxsize: int, ttl: int) -> None:
        self.maxsize = maxsize
        self.ttl = ttl
        self._store: "OrderedDict[K, Tuple[V, float]]" = OrderedDict()

    def __getitem__(self, key: K) -> V:
        self._purge_expired()
        value, expires_at = self._store[key]
        if expires_at < time.time():
            del self._store[key]
            raise KeyError(key)
        return value

    def __setitem__(self, key: K, value: V) -> None:
        self._purge_expired()
        if key in self._store:
            del self._store[key]
        elif len(self._store) >= self.maxsize:
            self._store.popitem(last=False)
        self._store[key] = (value, time.time() + self.ttl)

    def __delitem__(self, key: K) -> None:
        del self._store[key]

    def __iter__(self) -> Iterator[K]:
        self._purge_expired()
        return iter(self._store.keys())

    def __len__(self) -> int:
        self._purge_expired()
        return len(self._store)

    def __contains__(self, key: object) -> bool:  # type: ignore[override]
        try:
            self.__getitem__(key)  # type: ignore[arg-type]
            return True
        except KeyError:
            return False

    def get(self, key: K, default: V | None = None) -> V | None:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def _purge_expired(self) -> None:
        now = time.time()
        expired_keys = [k for k, (_, expires_at) in self._store.items() if expires_at < now]
        for key in expired_keys:
            del self._store[key]
