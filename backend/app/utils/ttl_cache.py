"""Lightweight in-project replacement for :mod:`cachetools` TTLCache."""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Generic, Iterator, MutableMapping, Tuple, TypeVar


K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _CacheItem(Generic[V]):
    value: V
    expires_at: float


class TTLCache(MutableMapping[K, V]):
    """A minimal TTL cache implementation.

    This class mirrors the subset of behaviour required by the project without pulling
    in the external ``cachetools`` dependency.  Entries expire after ``ttl`` seconds and
    the cache never grows beyond ``maxsize`` items.  Access updates the eviction order to
    approximate the behaviour of ``cachetools.TTLCache``.
    """

    def __init__(self, maxsize: int, ttl: float):
        if maxsize <= 0:
            raise ValueError("maxsize must be a positive integer")
        if ttl <= 0:
            raise ValueError("ttl must be a positive number of seconds")

        self.maxsize = int(maxsize)
        self.ttl = float(ttl)
        self._store: "OrderedDict[K, _CacheItem[V]]" = OrderedDict()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _current_time(self) -> float:
        return time.monotonic()

    def _purge_expired(self) -> None:
        now = self._current_time()
        expired_keys = [key for key, item in self._store.items() if item.expires_at <= now]
        for key in expired_keys:
            self._store.pop(key, None)

    def _build_item(self, value: V) -> _CacheItem[V]:
        return _CacheItem(value=value, expires_at=self._current_time() + self.ttl)

    # ------------------------------------------------------------------
    # MutableMapping implementation
    # ------------------------------------------------------------------
    def __getitem__(self, key: K) -> V:
        try:
            item = self._store[key]
        except KeyError as exc:
            raise KeyError(key) from exc

        if item.expires_at <= self._current_time():
            # Expired items behave as missing keys.
            self._store.pop(key, None)
            raise KeyError(key)

        # Move key to the end to maintain LRU ordering.
        self._store.move_to_end(key)
        return item.value

    def __setitem__(self, key: K, value: V) -> None:
        self._purge_expired()

        if key in self._store:
            # Remove existing entry to refresh ordering.
            self._store.pop(key)
        elif len(self._store) >= self.maxsize:
            # Evict the least recently used item.
            self._store.popitem(last=False)

        self._store[key] = self._build_item(value)

    def __delitem__(self, key: K) -> None:
        del self._store[key]

    def __iter__(self) -> Iterator[K]:
        self._purge_expired()
        return iter(list(self._store.keys()))

    def __len__(self) -> int:
        self._purge_expired()
        return len(self._store)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def __contains__(self, key: object) -> bool:  # type: ignore[override]
        if key not in self._store:
            return False

        try:
            # ``__getitem__`` handles expiration for us.
            self[key]  # type: ignore[index]
        except KeyError:
            return False
        return True

    def get(self, key: K, default: V | None = None) -> V | None:
        try:
            return self[key]
        except KeyError:
            return default

    def clear(self) -> None:
        self._store.clear()

    def items(self) -> Iterator[Tuple[K, V]]:
        for key in list(self._store.keys()):
            try:
                yield key, self[key]
            except KeyError:
                continue

    def to_dict(self) -> Dict[K, V]:
        return {key: value for key, value in self.items()}


__all__ = ["TTLCache"]
