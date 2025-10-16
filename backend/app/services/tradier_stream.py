"""
Tradier Real-Time Streaming Service

Provides real-time market data streaming using Tradier WebSocket API.

ARCHITECTURE:
- Tradier API: ALL market data (quotes, bars, options, analysis, streaming)
- Alpaca API: ONLY paper trade execution (orders, positions, account)

IMPLEMENTATION:
- Creates streaming session via Tradier REST API
- Connects to WebSocket endpoint (wss://ws.tradier.com/v1/markets/events)
- Manages symbol subscriptions dynamically
- Auto-renews session every 4 minutes (expires at 5 minutes)
- Caches latest quotes in Redis (5s TTL) for SSE distribution
- Reconnects automatically on connection loss
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import httpx
import websockets

from app.core.config import settings
from app.services.cache import get_cache

logger = logging.getLogger(__name__)


class TradierStreamService:
    """
    Real-time streaming service for Tradier market data

    Manages WebSocket connection to Tradier for live quotes, trades, and market data.
    Implements auto-reconnection, session renewal, and Redis caching.
    """

    def __init__(self):
        """Initialize the Tradier streaming service"""
        self.active_symbols: Set[str] = set()
        self.running = False
        self.websocket: Optional[Any] = None
        self.session_id: Optional[str] = None
        self.session_created_at: Optional[float] = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.cache = get_cache()

        # WebSocket endpoint
        self.ws_url = "wss://ws.tradier.com/v1/markets/events"

        # Session creation endpoint
        self.session_url = f"{settings.TRADIER_API_BASE_URL}/markets/events/session"

        # Background tasks
        self._connection_task: Optional[asyncio.Task] = None
        self._session_renewal_task: Optional[asyncio.Task] = None

        logger.info("✅ TradierStreamService initialized")

    async def _create_session(self) -> Optional[str]:
        """
        Create a new streaming session via Tradier API

        Returns:
            Session ID string or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.session_url,
                    headers={
                        "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
                        "Accept": "application/json",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    session_id = data.get("stream", {}).get("sessionid")

                    if session_id:
                        self.session_id = session_id
                        self.session_created_at = time.time()
                        logger.info(f"✅ Created Tradier streaming session: {session_id[:8]}...")
                        return session_id
                    else:
                        logger.error(f"❌ No sessionid in response: {data}")
                        return None
                else:
                    logger.error(
                        f"❌ Failed to create session: {response.status_code} - {response.text}"
                    )
                    return None

        except Exception as e:
            logger.error(f"❌ Error creating Tradier session: {e}")
            return None

    async def _renew_session_periodically(self):
        """
        Renew session every 4 minutes (before 5 minute expiration)
        """
        while self.running:
            try:
                # Wait 4 minutes (240 seconds) before renewal
                await asyncio.sleep(240)

                if not self.running:
                    break

                logger.info("🔄 Renewing Tradier streaming session...")
                new_session_id = await self._create_session()

                if new_session_id and self.websocket:
                    # Re-subscribe with new session
                    await self._subscribe_symbols(list(self.active_symbols))
                    logger.info("✅ Session renewed and symbols re-subscribed")
                else:
                    logger.error("❌ Failed to renew session")

            except asyncio.CancelledError:
                logger.info("Session renewal task cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in session renewal: {e}")

    async def _connect_websocket(self):
        """
        Connect to Tradier WebSocket and handle messages
        """
        while self.running:
            try:
                # Create session first
                if not self.session_id:
                    session_id = await self._create_session()
                    if not session_id:
                        logger.error("❌ Failed to create session, retrying in 5s...")
                        await asyncio.sleep(5)
                        continue

                # Connect to WebSocket
                logger.info(f"📡 Connecting to Tradier WebSocket: {self.ws_url}")

                async with websockets.connect(
                    self.ws_url, ping_interval=20, ping_timeout=10
                ) as websocket:
                    self.websocket = websocket
                    self.reconnect_attempts = 0
                    logger.info("✅ WebSocket connected")

                    # Subscribe to active symbols
                    if self.active_symbols:
                        await self._subscribe_symbols(list(self.active_symbols))

                    # Listen for messages
                    async for message in websocket:
                        await self._handle_message(message)

            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"⚠️ WebSocket connection closed: {e}")
                self.websocket = None

                if self.running:
                    # Exponential backoff
                    self.reconnect_attempts += 1
                    wait_time = min(2**self.reconnect_attempts, 60)
                    logger.info(
                        f"🔄 Reconnecting in {wait_time}s (attempt {self.reconnect_attempts})..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    break

            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
                self.websocket = None

                if self.running:
                    await asyncio.sleep(5)
                else:
                    break

    async def _subscribe_symbols(self, symbols: List[str]):
        """
        Subscribe to symbols on WebSocket

        Args:
            symbols: List of stock symbols to subscribe to
        """
        if not self.websocket or not self.session_id:
            logger.warning("⚠️ Cannot subscribe - no active WebSocket or session")
            return

        try:
            subscription_payload = {
                "symbols": symbols,
                "sessionid": self.session_id,
                "linebreak": True,  # Add line breaks to messages
            }

            await self.websocket.send(json.dumps(subscription_payload))
            logger.info(f"📡 Subscribed to symbols: {symbols}")

        except Exception as e:
            logger.error(f"❌ Error subscribing to symbols: {e}")

    async def _handle_message(self, message: str):
        """
        Parse and cache incoming WebSocket messages

        Args:
            message: Raw JSON message from Tradier WebSocket
        """
        try:
            # Parse JSON
            data = json.loads(message)

            # Extract message type and symbol
            msg_type = data.get("type")
            symbol = data.get("symbol")

            if not symbol:
                return

            # Handle different message types
            if msg_type == "quote":
                # Quote update (bid/ask)
                quote_data = {
                    "symbol": symbol,
                    "bid": data.get("bid"),
                    "ask": data.get("ask"),
                    "bidsize": data.get("bidsize"),
                    "asksize": data.get("asksize"),
                    "mid": (
                        (data.get("bid", 0) + data.get("ask", 0)) / 2
                        if data.get("bid") and data.get("ask")
                        else None
                    ),
                    "timestamp": datetime.now().isoformat(),
                    "type": "quote",
                }

                # Cache in Redis (5s TTL)
                self.cache.set(f"quote:{symbol}", quote_data, ttl=5)

            elif msg_type == "trade":
                # Trade update (last price)
                trade_data = {
                    "symbol": symbol,
                    "price": data.get("price"),
                    "size": data.get("size"),
                    "timestamp": datetime.now().isoformat(),
                    "type": "trade",
                }

                # Cache in Redis (5s TTL)
                self.cache.set(f"price:{symbol}", trade_data, ttl=5)

            elif msg_type == "summary":
                # Summary data (open, high, low, close, volume)
                summary_data = {
                    "symbol": symbol,
                    "open": data.get("open"),
                    "high": data.get("high"),
                    "low": data.get("low"),
                    "close": data.get("close"),
                    "volume": data.get("volume"),
                    "timestamp": datetime.now().isoformat(),
                    "type": "summary",
                }

                # Cache in Redis (5s TTL)
                self.cache.set(f"summary:{symbol}", summary_data, ttl=5)

        except json.JSONDecodeError:
            logger.warning(f"⚠️ Invalid JSON message: {message[:100]}")
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")

    async def start(self):
        """Start the streaming service"""
        if self.running:
            logger.warning("⚠️ Streaming service already running")
            return

        logger.info("🚀 Starting Tradier streaming service...")
        self.running = True

        # Start WebSocket connection task
        self._connection_task = asyncio.create_task(self._connect_websocket())

        # Start session renewal task
        self._session_renewal_task = asyncio.create_task(self._renew_session_periodically())

        logger.info("✅ Tradier streaming service started")

    async def stop(self):
        """Stop the streaming service"""
        logger.info("🛑 Stopping Tradier streaming service...")
        self.running = False

        # Cancel background tasks
        if self._connection_task:
            self._connection_task.cancel()
            try:
                await self._connection_task
            except asyncio.CancelledError:
                pass

        if self._session_renewal_task:
            self._session_renewal_task.cancel()
            try:
                await self._session_renewal_task
            except asyncio.CancelledError:
                pass

        # Close WebSocket
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

        logger.info("✅ Tradier streaming service stopped")

    async def subscribe_quotes(self, symbols: List[str]):
        """
        Subscribe to real-time quotes for symbols

        Args:
            symbols: List of stock symbols (e.g., ["AAPL", "MSFT", "TSLA"])
        """
        # Add to active symbols set
        new_symbols = set(s.upper() for s in symbols)
        self.active_symbols.update(new_symbols)

        # Subscribe on WebSocket if connected
        if self.websocket and self.session_id:
            await self._subscribe_symbols(list(self.active_symbols))

        logger.info(f"✅ Subscribed to quotes: {symbols} (total: {len(self.active_symbols)})")

    async def unsubscribe_quotes(self, symbols: List[str]):
        """
        Unsubscribe from quotes

        Args:
            symbols: List of stock symbols to unsubscribe from
        """
        # Remove from active symbols
        symbols_to_remove = set(s.upper() for s in symbols)
        self.active_symbols -= symbols_to_remove

        # Re-subscribe with updated list
        if self.websocket and self.session_id and self.active_symbols:
            await self._subscribe_symbols(list(self.active_symbols))

        logger.info(f"✅ Unsubscribed from: {symbols} (remaining: {len(self.active_symbols)})")

    def is_running(self) -> bool:
        """Check if streaming is active"""
        return self.running

    def get_active_symbols(self) -> Set[str]:
        """Get currently subscribed symbols"""
        return self.active_symbols.copy()


# Singleton instance
_tradier_stream_service: Optional[TradierStreamService] = None


def get_tradier_stream() -> TradierStreamService:
    """Get singleton Tradier stream service"""
    global _tradier_stream_service
    if _tradier_stream_service is None:
        _tradier_stream_service = TradierStreamService()
    return _tradier_stream_service


async def start_tradier_stream():
    """Helper to start the stream (call from main.py startup)"""
    service = get_tradier_stream()
    await service.start()
    logger.info("🚀 Tradier streaming service started in background")


async def stop_tradier_stream():
    """Helper to stop the stream (call from main.py shutdown)"""
    service = get_tradier_stream()
    await service.stop()
    logger.info("🛑 Tradier streaming service stopped")
