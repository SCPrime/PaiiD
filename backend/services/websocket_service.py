"""
WebSocket Service for Real-Time Market Data Streaming
Handles WebSocket connections, market data broadcasting, and client management
"""

import asyncio
import json
import logging
from datetime import UTC, datetime

import redis
from backend.services.market_data_service import MarketDataService
from fastapi import WebSocket


logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and real-time data broadcasting"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.user_subscriptions: dict[str, set[str]] = {}  # user_id -> set of symbols
        self.symbol_subscribers: dict[str, set[str]] = {}  # symbol -> set of user_ids
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=0, decode_responses=True
        )
        self.market_data_service = MarketDataService()
        self.broadcast_interval = 1.0  # seconds
        self._broadcast_task = None

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection and register user"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_subscriptions[user_id] = set()

        logger.info(f"WebSocket connected for user {user_id}")

        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection",
                "status": "connected",
                "timestamp": datetime.now(UTC).isoformat(),
                "user_id": user_id,
            },
            user_id,
        )

        # Start broadcast task if not already running
        if not self._broadcast_task:
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())

    async def disconnect(self, user_id: str):
        """Remove WebSocket connection and clean up subscriptions"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # Remove user from all symbol subscriptions
        if user_id in self.user_subscriptions:
            for symbol in self.user_subscriptions[user_id]:
                if symbol in self.symbol_subscribers:
                    self.symbol_subscribers[symbol].discard(user_id)
            del self.user_subscriptions[user_id]

        logger.info(f"WebSocket disconnected for user {user_id}")

    async def handle_message(self, user_id: str, message: dict):
        """Handle incoming WebSocket messages"""
        message_type = message.get("type")

        if message_type == "subscribe":
            symbols = message.get("symbols", [])
            await self._subscribe_user_to_symbols(user_id, symbols)

        elif message_type == "unsubscribe":
            symbols = message.get("symbols", [])
            await self._unsubscribe_user_from_symbols(user_id, symbols)

        elif message_type == "ping":
            await self.send_personal_message(
                {"type": "pong", "timestamp": datetime.now(UTC).isoformat()}, user_id
            )

        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def _subscribe_user_to_symbols(self, user_id: str, symbols: list[str]):
        """Subscribe user to real-time updates for specific symbols"""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()

        for symbol in symbols:
            symbol = symbol.upper()
            self.user_subscriptions[user_id].add(symbol)

            if symbol not in self.symbol_subscribers:
                self.symbol_subscribers[symbol] = set()
            self.symbol_subscribers[symbol].add(user_id)

        logger.info(f"User {user_id} subscribed to symbols: {symbols}")

        # Send confirmation
        await self.send_personal_message(
            {
                "type": "subscription_confirmed",
                "symbols": symbols,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            user_id,
        )

    async def _unsubscribe_user_from_symbols(self, user_id: str, symbols: list[str]):
        """Unsubscribe user from specific symbols"""
        if user_id not in self.user_subscriptions:
            return

        for symbol in symbols:
            symbol = symbol.upper()
            self.user_subscriptions[user_id].discard(symbol)

            if symbol in self.symbol_subscribers:
                self.symbol_subscribers[symbol].discard(user_id)

        logger.info(f"User {user_id} unsubscribed from symbols: {symbols}")

    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                await self.disconnect(user_id)

    async def broadcast_to_symbol_subscribers(self, symbol: str, data: dict):
        """Broadcast data to all subscribers of a specific symbol"""
        if symbol in self.symbol_subscribers:
            message = {
                "type": "market_data",
                "symbol": symbol,
                "data": data,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            for user_id in self.symbol_subscribers[symbol].copy():
                await self.send_personal_message(message, user_id)

    async def _broadcast_loop(self):
        """Main broadcast loop for real-time data"""
        while True:
            try:
                await self._update_market_data()
                await asyncio.sleep(self.broadcast_interval)
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _update_market_data(self):
        """Update and broadcast market data for all subscribed symbols"""
        all_subscribed_symbols = set()
        for user_symbols in self.user_subscriptions.values():
            all_subscribed_symbols.update(user_symbols)

        if not all_subscribed_symbols:
            return

        # Get real-time data for all subscribed symbols
        for symbol in all_subscribed_symbols:
            try:
                # Check cache first
                cached_data = self.redis_client.get(f"market_data:{symbol}")
                if cached_data:
                    data = json.loads(cached_data)
                else:
                    # Fetch fresh data
                    data = await self.market_data_service.get_real_time_quote(symbol)
                    if data:
                        # Cache for 30 seconds
                        self.redis_client.setex(
                            f"market_data:{symbol}", 30, json.dumps(data)
                        )

                if data:
                    await self.broadcast_to_symbol_subscribers(symbol, data)

            except Exception as e:
                logger.error(f"Error updating market data for {symbol}: {e}")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


class WebSocketService:
    """Service class for WebSocket operations"""

    @staticmethod
    async def connect_user(websocket: WebSocket, user_id: str):
        """Connect a user to WebSocket service"""
        await websocket_manager.connect(websocket, user_id)

    @staticmethod
    async def disconnect_user(user_id: str):
        """Disconnect a user from WebSocket service"""
        await websocket_manager.disconnect(user_id)

    @staticmethod
    async def handle_user_message(user_id: str, message: dict):
        """Handle message from user"""
        await websocket_manager.handle_message(user_id, message)

    @staticmethod
    async def broadcast_portfolio_update(user_id: str, portfolio_data: dict):
        """Broadcast portfolio update to specific user"""
        message = {
            "type": "portfolio_update",
            "data": portfolio_data,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        await websocket_manager.send_personal_message(message, user_id)

    @staticmethod
    async def broadcast_position_update(user_id: str, position_data: dict):
        """Broadcast position update to specific user"""
        message = {
            "type": "position_update",
            "data": position_data,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        await websocket_manager.send_personal_message(message, user_id)

    @staticmethod
    async def broadcast_trading_alert(user_id: str, alert_data: dict):
        """Broadcast trading alert to specific user"""
        message = {
            "type": "trading_alert",
            "data": alert_data,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        await websocket_manager.send_personal_message(message, user_id)
