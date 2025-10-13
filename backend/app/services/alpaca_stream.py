"""
Alpaca WebSocket Streaming Service

Provides real-time market data streaming from Alpaca using WebSockets.
Caches latest prices in Redis for SSE endpoints to consume.

Phase 2.A - Real-Time Data Implementation
"""

import asyncio
import logging
from typing import Set, Optional, Callable
from alpaca.data.live import StockDataStream
from alpaca.data.models import Trade, Quote
from app.core.config import settings
from app.services.cache import get_cache

logger = logging.getLogger(__name__)


class AlpacaStreamService:
    """
    Manages real-time streaming of market data from Alpaca

    Features:
    - WebSocket connection to Alpaca's streaming API
    - Auto-reconnection with exponential backoff
    - Subscribe/unsubscribe to symbols dynamically
    - Cache prices in Redis (5s TTL)
    - Graceful shutdown
    """

    def __init__(self):
        """Initialize the streaming service"""
        self.stream: Optional[StockDataStream] = None
        self.active_symbols: Set[str] = set()
        self.cache = get_cache()
        self.running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

        # Callbacks for external listeners
        self.price_callbacks: list[Callable] = []

        logger.info("AlpacaStreamService initialized")

    async def start(self):
        """Start the WebSocket connection"""
        if not settings.ALPACA_PAPER_API_KEY or not settings.ALPACA_PAPER_SECRET_KEY:
            logger.error("Alpaca API credentials not configured")
            return

        try:
            # Initialize Alpaca data stream
            self.stream = StockDataStream(
                api_key=settings.ALPACA_PAPER_API_KEY,
                secret_key=settings.ALPACA_PAPER_SECRET_KEY,
                feed='iex'  # IEX feed for paper trading
            )

            # Register handlers
            self.stream._trade_handler = self._handle_trade
            self.stream._quote_handler = self._handle_quote

            self.running = True
            logger.info("✅ Alpaca WebSocket stream started")

            # Run the stream (this blocks until stopped)
            await self.stream._run_forever()

        except Exception as e:
            logger.error(f"❌ Failed to start Alpaca stream: {e}")
            await self._handle_reconnect()

    async def stop(self):
        """Stop the WebSocket connection gracefully"""
        self.running = False
        if self.stream:
            try:
                await self.stream.stop_ws()
                logger.info("✅ Alpaca WebSocket stream stopped")
            except Exception as e:
                logger.error(f"Error stopping stream: {e}")

    async def subscribe_trades(self, symbols: list[str]):
        """
        Subscribe to real-time trades for given symbols

        Args:
            symbols: List of stock symbols (e.g., ["AAPL", "MSFT"])
        """
        if not self.stream:
            logger.warning("Stream not initialized, cannot subscribe")
            return

        try:
            # Add to active symbols set
            new_symbols = set(symbols) - self.active_symbols
            if new_symbols:
                self.stream.subscribe_trades(self._handle_trade, *list(new_symbols))
                self.active_symbols.update(new_symbols)
                logger.info(f"✅ Subscribed to trades: {list(new_symbols)}")
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to trades: {e}")

    async def subscribe_quotes(self, symbols: list[str]):
        """
        Subscribe to real-time quotes for given symbols

        Args:
            symbols: List of stock symbols (e.g., ["AAPL", "MSFT"])
        """
        if not self.stream:
            logger.warning("Stream not initialized, cannot subscribe")
            return

        try:
            # Add to active symbols set
            new_symbols = set(symbols) - self.active_symbols
            if new_symbols:
                self.stream.subscribe_quotes(self._handle_quote, *list(new_symbols))
                self.active_symbols.update(new_symbols)
                logger.info(f"✅ Subscribed to quotes: {list(new_symbols)}")
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to quotes: {e}")

    async def unsubscribe_trades(self, symbols: list[str]):
        """Unsubscribe from trade updates"""
        if not self.stream:
            return

        try:
            self.stream.unsubscribe_trades(*symbols)
            self.active_symbols -= set(symbols)
            logger.info(f"✅ Unsubscribed from trades: {symbols}")
        except Exception as e:
            logger.error(f"❌ Failed to unsubscribe from trades: {e}")

    async def unsubscribe_quotes(self, symbols: list[str]):
        """Unsubscribe from quote updates"""
        if not self.stream:
            return

        try:
            self.stream.unsubscribe_quotes(*symbols)
            self.active_symbols -= set(symbols)
            logger.info(f"✅ Unsubscribe from quotes: {symbols}")
        except Exception as e:
            logger.error(f"❌ Failed to unsubscribe from quotes: {e}")

    async def _handle_trade(self, trade: Trade):
        """
        Handle incoming trade data

        Caches latest price in Redis for SSE consumption
        """
        try:
            symbol = trade.symbol
            price = float(trade.price)
            timestamp = trade.timestamp.isoformat()

            # Cache in Redis with 5s TTL
            cache_data = {
                "symbol": symbol,
                "price": price,
                "timestamp": timestamp,
                "type": "trade",
                "size": int(trade.size)
            }

            self.cache.set(f"price:{symbol}", cache_data, ttl=5)

            # Notify any registered callbacks
            for callback in self.price_callbacks:
                try:
                    await callback(symbol, price, cache_data)
                except Exception as e:
                    logger.error(f"Error in price callback: {e}")

            logger.debug(f"📈 Trade: {symbol} @ ${price:.2f}")

        except Exception as e:
            logger.error(f"Error handling trade: {e}")

    async def _handle_quote(self, quote: Quote):
        """
        Handle incoming quote data (bid/ask)

        Caches latest quote in Redis for SSE consumption
        """
        try:
            symbol = quote.symbol
            bid_price = float(quote.bid_price) if quote.bid_price else 0
            ask_price = float(quote.ask_price) if quote.ask_price else 0
            mid_price = (bid_price + ask_price) / 2 if bid_price and ask_price else 0
            timestamp = quote.timestamp.isoformat()

            # Cache in Redis with 5s TTL
            cache_data = {
                "symbol": symbol,
                "bid": bid_price,
                "ask": ask_price,
                "mid": mid_price,
                "timestamp": timestamp,
                "type": "quote",
                "bid_size": int(quote.bid_size) if quote.bid_size else 0,
                "ask_size": int(quote.ask_size) if quote.ask_size else 0
            }

            self.cache.set(f"quote:{symbol}", cache_data, ttl=5)

            # Notify callbacks with mid price
            for callback in self.price_callbacks:
                try:
                    await callback(symbol, mid_price, cache_data)
                except Exception as e:
                    logger.error(f"Error in price callback: {e}")

            logger.debug(f"📊 Quote: {symbol} bid=${bid_price:.2f} ask=${ask_price:.2f}")

        except Exception as e:
            logger.error(f"Error handling quote: {e}")

    async def _handle_reconnect(self):
        """Handle reconnection with exponential backoff"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"❌ Max reconnect attempts ({self.max_reconnect_attempts}) reached")
            return

        self.reconnect_attempts += 1
        wait_time = min(2 ** self.reconnect_attempts, 60)  # Max 60s backoff

        logger.warning(f"⚠️ Reconnecting in {wait_time}s (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        await asyncio.sleep(wait_time)

        await self.start()

    def register_price_callback(self, callback: Callable):
        """
        Register a callback to be notified of price updates

        Callback signature: async def callback(symbol: str, price: float, data: dict)
        """
        self.price_callbacks.append(callback)

    def get_active_symbols(self) -> Set[str]:
        """Get currently subscribed symbols"""
        return self.active_symbols.copy()

    def is_running(self) -> bool:
        """Check if stream is actively running"""
        return self.running


# Singleton instance
_alpaca_stream_service: Optional[AlpacaStreamService] = None


def get_alpaca_stream() -> AlpacaStreamService:
    """Get singleton Alpaca stream service"""
    global _alpaca_stream_service
    if _alpaca_stream_service is None:
        _alpaca_stream_service = AlpacaStreamService()
    return _alpaca_stream_service


async def start_alpaca_stream():
    """Helper to start the stream (call from main.py startup)"""
    service = get_alpaca_stream()
    # Run in background task
    asyncio.create_task(service.start())
    logger.info("🚀 Alpaca streaming service started in background")


async def stop_alpaca_stream():
    """Helper to stop the stream (call from main.py shutdown)"""
    service = get_alpaca_stream()
    await service.stop()
    logger.info("🛑 Alpaca streaming service stopped")
