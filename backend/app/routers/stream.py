"""
Server-Sent Events (SSE) Streaming Endpoints

Provides real-time streaming of market data and position updates to frontend clients.

Phase 2.A - Real-Time Data Implementation
"""

import asyncio
import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Query
from sse_starlette.sse import EventSourceResponse
from app.core.auth import require_bearer
from app.services.cache import get_cache, CacheService
from app.services.alpaca_stream import get_alpaca_stream

logger = logging.getLogger(__name__)

router = APIRouter(tags=["streaming"])


@router.get("/stream/prices")
async def stream_prices(
    symbols: str = Query(..., description="Comma-separated list of symbols (e.g., AAPL,MSFT,TSLA)"),
    _=Depends(require_bearer),
    cache: CacheService = Depends(get_cache)
):
    """
    Stream real-time price updates for specified symbols via Server-Sent Events

    This endpoint:
    1. Subscribes to Alpaca WebSocket for the requested symbols
    2. Reads cached prices from Redis (updated by Alpaca stream)
    3. Sends price updates to client every 1 second via SSE
    4. Auto-reconnects on client disconnect

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
    symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]

    if not symbol_list:
        logger.warning("No symbols provided for streaming")
        return {"error": "No symbols specified"}

    logger.info(f"📡 Client subscribed to price stream: {symbol_list}")

    # Ensure Alpaca stream is subscribed to these symbols
    alpaca_stream = get_alpaca_stream()
    await alpaca_stream.subscribe_trades(symbol_list)

    async def price_generator() -> AsyncGenerator:
        """Generate price updates from Redis cache"""
        try:
            while True:
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
                            "size": trade_data.get("size", 0)
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
                                "type": "quote"
                            }

                # Send update if we have any prices
                if prices:
                    yield {
                        "event": "price_update",
                        "data": json.dumps(prices)
                    }
                else:
                    # Send heartbeat to keep connection alive
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps({"timestamp": asyncio.get_event_loop().time()})
                    }

                # Wait 1 second before next update
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info(f"📡 Client disconnected from price stream: {symbol_list}")
            # Cleanup not needed - Alpaca stream continues for other clients
            raise
        except Exception as e:
            logger.error(f"❌ Error in price stream: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(price_generator())


@router.get("/stream/positions")
async def stream_positions(
    _=Depends(require_bearer),
    cache: CacheService = Depends(get_cache)
):
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
        """Generate position updates from Redis cache"""
        last_positions_hash = None

        try:
            while True:
                # Read positions from cache
                positions_data = cache.get("portfolio:positions")

                if positions_data:
                    # Calculate hash to detect changes
                    current_hash = hash(json.dumps(positions_data, sort_keys=True))

                    # Only send update if positions changed
                    if current_hash != last_positions_hash:
                        yield {
                            "event": "position_update",
                            "data": json.dumps(positions_data)
                        }
                        last_positions_hash = current_hash

                # Wait 2 seconds before checking again
                await asyncio.sleep(2)

        except asyncio.CancelledError:
            logger.info("📡 Client disconnected from position stream")
            raise
        except Exception as e:
            logger.error(f"❌ Error in position stream: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(position_generator())


@router.get("/stream/status")
async def stream_status(_=Depends(require_bearer)):
    """
    Get streaming service status

    Returns:
        {
            "alpaca_connected": bool,
            "active_symbols": ["AAPL", "MSFT", ...],
            "stream_count": int
        }
    """
    alpaca_stream = get_alpaca_stream()

    return {
        "alpaca_connected": alpaca_stream.is_running(),
        "active_symbols": list(alpaca_stream.get_active_symbols()),
        "stream_count": len(alpaca_stream.get_active_symbols())
    }
