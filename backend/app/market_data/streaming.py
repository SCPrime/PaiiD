"""High level Tradier streaming client built on top of the service layer."""

from __future__ import annotations

import asyncio
import inspect
import logging
from datetime import datetime
from typing import Awaitable, Callable

from app.services.tradier_stream import TradierStreamService, get_tradier_stream

from .persistence import IntradayBarRepository
from .subscriptions import SubscriptionManager

logger = logging.getLogger(__name__)


EventListener = Callable[[dict], Awaitable[None] | None]


class TradierStreamingClient:
    """Coordinates streaming subscriptions, listeners, and persistence."""

    def __init__(
        self,
        *,
        stream_service: TradierStreamService | None = None,
        repository: IntradayBarRepository | None = None,
    ) -> None:
        self._service = stream_service or get_tradier_stream()
        self._repository = repository or IntradayBarRepository()
        self._listeners: list[EventListener] = []
        self._listener_registered = False
        self._listener_lock = asyncio.Lock()
        self.subscription_manager = SubscriptionManager(
            subscribe_callback=self._service.subscribe_quotes,
            unsubscribe_callback=self._service.unsubscribe_quotes,
        )

    async def ensure_listener_registered(self) -> None:
        """Attach the persistence listener to the service once."""

        if self._listener_registered:
            return

        async with self._listener_lock:
            if self._listener_registered:
                return

            self._service.register_listener(self._dispatch_event)
            self._listener_registered = True
            logger.debug("Market data listener registered with streaming service")

    async def start(self) -> None:
        """Ensure the underlying service is running."""

        await self.ensure_listener_registered()
        if not self._service.is_running():
            await self._service.start()

    async def stop(self) -> None:
        """Stop the underlying streaming service."""

        await self._service.stop()

    async def reconnect(self) -> None:
        """Force a reconnect by restarting the service."""

        await self._service.stop()
        await self._service.start()

    async def subscribe(self, symbols: list[str], consumer_id: str) -> None:
        """Subscribe a consumer to one or more symbols."""

        await self.ensure_listener_registered()
        await self.subscription_manager.add_symbols(symbols, consumer_id)

    async def unsubscribe(self, symbols: list[str], consumer_id: str) -> None:
        """Remove a consumer subscription."""

        await self.subscription_manager.remove_symbols(symbols, consumer_id)

    async def remove_consumer(self, consumer_id: str) -> None:
        """Remove all subscriptions for a consumer."""

        await self.subscription_manager.remove_consumer(consumer_id)

    def add_listener(self, listener: EventListener) -> None:
        """Register an additional consumer listener for market data events."""

        self._listeners.append(listener)

    async def get_intraday_bars(self, symbol: str, *, limit: int = 100) -> list[dict]:
        """Return persisted intraday bars."""

        bars = self._repository.get_intraday_bars(symbol, limit=limit)
        return [
            {
                "symbol": bar.symbol,
                "interval": bar.interval,
                "timestamp": bar.timestamp.isoformat(),
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            for bar in bars
        ]

    async def _dispatch_event(self, payload: dict) -> None:
        """Persist incoming events and fan them out to listeners."""

        try:
            await self._persist_event(payload)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to persist streaming payload: %s", exc)

        for listener in list(self._listeners):
            try:
                result = listener(payload)
                if inspect.isawaitable(result):
                    await result
            except Exception:  # pragma: no cover - listener isolation
                logger.exception("Market data listener raised an exception")

    async def _persist_event(self, payload: dict) -> None:
        """Persist trade and summary messages into the repository."""

        message_type = payload.get("type")
        symbol = payload.get("symbol")
        if not symbol:
            return

        timestamp_str = payload.get("timestamp")
        timestamp = (
            datetime.fromisoformat(timestamp_str)
            if isinstance(timestamp_str, str)
            else datetime.utcnow()
        )

        if message_type == "trade":
            price = payload.get("price")
            size = payload.get("size")
            self._repository.record_trade(
                symbol=symbol.upper(),
                price=float(price) if price is not None else None,
                size=float(size) if size is not None else None,
                timestamp=timestamp,
            )
        elif message_type == "summary":
            self._repository.apply_summary(
                symbol=symbol.upper(),
                interval="session",
                timestamp=timestamp,
                open_=self._safe_float(payload.get("open")),
                high=self._safe_float(payload.get("high")),
                low=self._safe_float(payload.get("low")),
                close=self._safe_float(payload.get("close")),
                volume=self._safe_float(payload.get("volume")),
            )

    @staticmethod
    def _safe_float(value: object) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None


_tradier_streaming_client: TradierStreamingClient | None = None


def get_tradier_streaming_client() -> TradierStreamingClient:
    """Return the singleton streaming client."""

    global _tradier_streaming_client
    if _tradier_streaming_client is None:
        _tradier_streaming_client = TradierStreamingClient()
    return _tradier_streaming_client
