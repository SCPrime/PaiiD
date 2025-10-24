"""Lightweight in-project replacement for :mod:`cachetools` TTLCache.

The production environment installs ``cachetools`` but the execution
sandbox used for automated tests does not allow fetching new packages.
The order options router only needs a minimal TTL-based mapping, so this
module implements the subset of behaviour that the application relies on
without introducing an external dependency.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Iterable, Iterator, MutableMapping, Tuple, TypeVar


_K = TypeVar("_K")
_V = TypeVar("_V")


class TTLCache(MutableMapping[_K, _V]):
    """A minimal TTL-based cache with an LRU eviction strategy.

    The implementation purposefully keeps the surface area small and only
    provides the functionality required by the application code:

    * key membership checks (``key in cache``)
    * item access/assignment via ``cache[key]``
    * ``get`` and ``clear`` helpers

    Expired entries are discarded lazily when the cache is accessed. When
    the cache exceeds ``maxsize`` the least-recently-used entry is evicted.
    """

    def __init__(self, maxsize: int = 128, ttl: float = 600.0) -> None:
        self.maxsize = maxsize
        self.ttl = ttl
        self._store: "OrderedDict[_K, Tuple[_V, float]]" = OrderedDict()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _now(self) -> float:
        return time.monotonic()

    def _expire(self) -> None:
        """Remove any entries whose TTL has elapsed."""
        now = self._now()
        expired: Iterable[_K] = [key for key, (_, deadline) in self._store.items() if deadline <= now]
        for key in expired:
            self._store.pop(key, None)

    def _evict_if_needed(self) -> None:
        while len(self._store) > self.maxsize:
            self._store.popitem(last=False)

    # ------------------------------------------------------------------
    # MutableMapping interface
    # ------------------------------------------------------------------
    def __getitem__(self, key: _K) -> _V:
        self._expire()
        value, deadline = self._store[key]
        if deadline <= self._now():
            # Entry expired since the last purge; behave like a missing key.
            self._store.pop(key, None)
            raise KeyError(key)
        # Maintain LRU order.
        self._store.move_to_end(key)
        return value

    def __setitem__(self, key: _K, value: _V) -> None:
        self._expire()
        self._store[key] = (value, self._now() + self.ttl)
        self._store.move_to_end(key)
        self._evict_if_needed()

    def __delitem__(self, key: _K) -> None:
        self._store.pop(key)

    def __iter__(self) -> Iterator[_K]:
        self._expire()
        return iter(self._store.keys())

    def __len__(self) -> int:
        self._expire()
        return len(self._store)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def __contains__(self, key: object) -> bool:  # type: ignore[override]
        self._expire()
        if key in self._store:
            _, deadline = self._store[key]  # type: ignore[index]
            if deadline > self._now():
                return True
            self._store.pop(key, None)
        return False

    def get(self, key: _K, default: _V | None = None) -> _V | None:
        try:
            return self[key]
        except KeyError:
            return default

    def clear(self) -> None:
        self._store.clear()


__all__ = ["TTLCache"]
