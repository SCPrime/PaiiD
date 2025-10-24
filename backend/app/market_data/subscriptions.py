"""Subscription tracking for streaming consumers."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Awaitable, Callable

Symbol = str
ConsumerId = str

SubscribeCallback = Callable[[list[Symbol]], Awaitable[None]]
UnsubscribeCallback = Callable[[list[Symbol]], Awaitable[None]]


class SubscriptionManager:
    """Track consumer subscriptions and manage stream-level subscriptions."""

    def __init__(
        self,
        *,
        subscribe_callback: SubscribeCallback,
        unsubscribe_callback: UnsubscribeCallback,
    ) -> None:
        self._subscribe_callback = subscribe_callback
        self._unsubscribe_callback = unsubscribe_callback
        self._symbol_consumers: dict[Symbol, set[ConsumerId]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def add_symbols(self, symbols: list[Symbol], consumer_id: ConsumerId) -> None:
        """Register interest from a consumer and subscribe if necessary."""

        async with self._lock:
            new_symbols: list[Symbol] = []
            for symbol in symbols:
                normalized = symbol.upper()
                consumers = self._symbol_consumers[normalized]
                if not consumers:
                    new_symbols.append(normalized)
                consumers.add(consumer_id)

        if new_symbols:
            await self._subscribe_callback(new_symbols)

    async def remove_symbols(self, symbols: list[Symbol], consumer_id: ConsumerId) -> None:
        """Remove interest for a subset of symbols."""

        async with self._lock:
            to_unsubscribe: list[Symbol] = []
            for symbol in symbols:
                normalized = symbol.upper()
                consumers = self._symbol_consumers.get(normalized)
                if not consumers:
                    continue
                consumers.discard(consumer_id)
                if not consumers:
                    to_unsubscribe.append(normalized)
                    del self._symbol_consumers[normalized]

        if to_unsubscribe:
            await self._unsubscribe_callback(to_unsubscribe)

    async def remove_consumer(self, consumer_id: ConsumerId) -> None:
        """Remove a consumer from all tracked subscriptions."""

        async with self._lock:
            to_unsubscribe: list[Symbol] = []
            for symbol, consumers in list(self._symbol_consumers.items()):
                if consumer_id in consumers:
                    consumers.remove(consumer_id)
                    if not consumers:
                        to_unsubscribe.append(symbol)
                        del self._symbol_consumers[symbol]

        if to_unsubscribe:
            await self._unsubscribe_callback(to_unsubscribe)

    def active_symbols(self) -> set[Symbol]:
        """Return the set of symbols that currently have consumers."""

        return set(self._symbol_consumers.keys())

    def consumers_for(self, symbol: Symbol) -> set[ConsumerId]:
        """Return consumers subscribed to a symbol."""

        return set(self._symbol_consumers.get(symbol.upper(), set()))
