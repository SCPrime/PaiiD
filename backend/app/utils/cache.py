"""Lightweight in-memory TTL cache used by the options router.

The production application previously depended on :mod:`cachetools` for the
``TTLCache`` helper. The package is not available in the execution environment
for these tests, so we provide a minimal compatible implementation. Only the
behaviour relied upon by the codebase is reproduced:

* a maximum cache size that evicts the oldest items when exceeded
* automatic removal of expired entries based on the configured TTL
* ``__contains__`` and dictionary-style get/set access

The implementation is intentionally small and dependency free so that it can be
used both in tests and in constrained environments.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Dict, Iterable, MutableMapping, Tuple, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class TTLCache(MutableMapping[K, V]):
    """Simple time-to-live cache with an LRU eviction policy.

    Only the features exercised in the codebase are implemented. The cache keeps
    track of the insertion order so that the least-recently-used entry can be
    dropped when the ``maxsize`` limit is exceeded. Expired entries are cleaned
    up on every read/write operation.
    """

    def __init__(self, maxsize: int, ttl: float) -> None:
        self.maxsize = maxsize
        self.ttl = ttl
        self._store: "OrderedDict[K, Tuple[V, float]]" = OrderedDict()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _now(self) -> float:
        return time.monotonic()

    def _purge_expired(self) -> None:
        current_time = self._now()
        expired_keys = [key for key, (_, expiry) in self._store.items() if expiry <= current_time]
        for key in expired_keys:
            self._store.pop(key, None)

    def _evict_lru(self) -> None:
        while len(self._store) > self.maxsize:
            self._store.popitem(last=False)

    # ------------------------------------------------------------------
    # MutableMapping interface
    # ------------------------------------------------------------------
    def __getitem__(self, key: K) -> V:
        self._purge_expired()
        value, expiry = self._store[key]
        if expiry <= self._now():
            # Entry has expired since the last purge
            self._store.pop(key, None)
            raise KeyError(key)

        # Refresh LRU order
        self._store.move_to_end(key)
        return value

    def __setitem__(self, key: K, value: V) -> None:
        self._purge_expired()
        self._store[key] = (value, self._now() + self.ttl)
        self._store.move_to_end(key)
        self._evict_lru()

    def __delitem__(self, key: K) -> None:
        self._purge_expired()
        del self._store[key]

    def __iter__(self) -> Iterable[K]:  # pragma: no cover - simple delegation
        self._purge_expired()
        return iter(self._store.keys())

    def __len__(self) -> int:
        self._purge_expired()
        return len(self._store)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def __contains__(self, key: object) -> bool:  # type: ignore[override]
        self._purge_expired()
        return key in self._store

    def get(self, key: K, default: V | None = None) -> V | None:  # type: ignore[override]
        try:
            return self[key]
        except KeyError:
            return default

    def items(self) -> Iterable[Tuple[K, V]]:  # pragma: no cover - convenience
        self._purge_expired()
        for key, (value, _) in self._store.items():
            yield key, value


__all__ = ["TTLCache"]

