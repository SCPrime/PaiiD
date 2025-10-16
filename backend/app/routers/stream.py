"""
Server-Sent Events (SSE) Streaming Endpoints

This module provides Server-Sent Events for real-time data streaming.

ARCHITECTURE:
- Tradier API: ALL market data (quotes, streaming, analysis)
- Alpaca API: ONLY paper trade execution (orders, positions, account)

Phase 2.A - Real-Time Data Implementation (Tradier WebSocket streaming)
Phase 5.C - Heartbeat mechanism for connection monitoring
"""

import asyncio
import json
import logging
import time
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Query
from sse_starlette.sse import EventSourceResponse

from app.core.auth import require_bearer
from app.services.cache import CacheService, get_cache
from app.services.tradier_stream import get_tradier_stream

logger = logging.getLogger(__name__)

router = APIRouter(tags=["streaming"])

# Configuration
HEARTBEAT_INTERVAL = 15  # Send heartbeat every 15 seconds
DATA_CHECK_INTERVAL = 1  # Check for new data every 1 second


@router.get("/stream/prices")
async def stream_prices(
    symbols: str = Query(..., description="Comma-separated list of symbols (e.g., AAPL,MSFT,TSLA)"),
    _=Depends(require_bearer),
    cache: CacheService = Depends(get_cache),
):
    """
    Stream real-time price updates for specified symbols via Server-Sent Events

    Uses Tradier WebSocket for live market data streaming.

    Query Parameters:
        symbols: Comma-separated stock symbols (e.g., "AAPL,MSFT,TSLA")

    Response Format (SSE):
        event: price_update
        data: {"AAPL": {"price": 175.43, "timestamp": "2024-10-13T..."}, ...}

    Usage:
        const eventSource = new EventSource('/api/stream/prices?symbols=AAPL,MSFT');
        eventSource.addEventListener('price_update', (e) => {
            const prices = JSON.parse(e.data);
            console.log(prices);
        });
    """
    # Parse symbols
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]

    if not symbol_list:
        logger.warning("No symbols provided for streaming")
        return {"error": "No symbols specified"}

    logger.info(f"📡 Client subscribed to price stream for: {symbol_list}")

    # Subscribe to Tradier streaming
    tradier_stream = get_tradier_stream()
    await tradier_stream.subscribe_quotes(symbol_list)

    async def price_generator() -> AsyncGenerator:
        """
        Generate price updates from Redis cache with periodic heartbeats.

        Sends:
        - price_update: When price data changes (every 1s)
        - heartbeat: Every 15s to keep connection alive and detect timeouts
        """
        last_heartbeat_time = time.time()

        try:
            while True:
                current_time = time.time()
                prices = {}

                # Read latest prices from Redis cache
                for symbol in symbol_list:
                    # Try trade price first (more accurate)
                    trade_data = cache.get(f"price:{symbol}")
                    if trade_data:
                        prices[symbol] = {
                            "price": trade_data.get("price", 0),
                            "timestamp": trade_data.get("timestamp"),
                            "type": "trade",
                            "size": trade_data.get("size", 0),
                        }
                    else:
                        # Fall back to quote data (bid/ask)
                        quote_data = cache.get(f"quote:{symbol}")
                        if quote_data:
                            prices[symbol] = {
                                "price": quote_data.get("mid", 0),  # Use mid price
                                "bid": quote_data.get("bid", 0),
                                "ask": quote_data.get("ask", 0),
                                "timestamp": quote_data.get("timestamp"),
                                "type": "quote",
                            }

                # Send price update if we have data
                if prices:
                    yield {"event": "price_update", "data": json.dumps(prices)}

                # Send periodic heartbeat (every HEARTBEAT_INTERVAL seconds)
                if current_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps(
                            {
                                "timestamp": current_time,
                                "symbols": symbol_list,
                                "stream_type": "prices",
                            }
                        ),
                    }
                    last_heartbeat_time = current_time
                    logger.debug(f"💓 Heartbeat sent (prices stream)")

                # Wait before next data check
                await asyncio.sleep(DATA_CHECK_INTERVAL)

        except asyncio.CancelledError:
            logger.info(f"📡 Client disconnected from price stream: {symbol_list}")
            # Cleanup not needed - Tradier stream continues for other clients
            raise
        except Exception as e:
            logger.error(f"❌ Error in price stream: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(price_generator())


@router.get("/stream/positions")
async def stream_positions(_=Depends(require_bearer), cache: CacheService = Depends(get_cache)):
    """
    Stream position updates via Server-Sent Events

    This endpoint:
    1. Monitors position changes from cache
    2. Sends position updates when detected
    3. Useful for instant P&L updates across multiple clients

    Response Format (SSE):
        event: position_update
        data: [{"symbol": "AAPL", "qty": 10, "pnl": 150.00, ...}, ...]
    """
    logger.info("📡 Client subscribed to position stream")

    async def position_generator() -> AsyncGenerator:
        """
        Generate position updates from Redis cache with periodic heartbeats.

        Sends:
        - position_update: When positions change (checked every 2s)
        - heartbeat: Every 15s to keep connection alive and detect timeouts
        """
        last_positions_hash = None
        last_heartbeat_time = time.time()

        try:
            while True:
                current_time = time.time()

                # Read positions from cache
                positions_data = cache.get("portfolio:positions")

                if positions_data:
                    # Calculate hash to detect changes
                    current_hash = hash(json.dumps(positions_data, sort_keys=True))

                    # Only send update if positions changed
                    if current_hash != last_positions_hash:
                        yield {"event": "position_update", "data": json.dumps(positions_data)}
                        last_positions_hash = current_hash

                # Send periodic heartbeat (every HEARTBEAT_INTERVAL seconds)
                if current_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps(
                            {
                                "timestamp": current_time,
                                "stream_type": "positions",
                                "position_count": len(positions_data) if positions_data else 0,
                            }
                        ),
                    }
                    last_heartbeat_time = current_time
                    logger.debug(f"💓 Heartbeat sent (positions stream)")

                # Wait 2 seconds before checking again
                await asyncio.sleep(2)

        except asyncio.CancelledError:
            logger.info("📡 Client disconnected from position stream")
            raise
        except Exception as e:
            logger.error(f"❌ Error in position stream: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(position_generator())


@router.get("/stream/status")
async def stream_status(_=Depends(require_bearer)):
    """
    Get streaming service status

    Returns:
        {
            "streaming_available": bool,
            "provider": str,
            "active_symbols": ["AAPL", "MSFT", ...],
            "stream_count": int
        }
    """
    tradier_stream = get_tradier_stream()
    active_symbols = list(tradier_stream.get_active_symbols())

    return {
        "streaming_available": tradier_stream.is_running(),
        "provider": "Tradier WebSocket",
        "active_symbols": active_symbols,
        "stream_count": len(active_symbols),
    }
