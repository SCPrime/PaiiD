from app.core.jwt import get_current_user
from app.models.database import User
from app.services.cache import CacheService, get_cache
from app.services.tradier_stream import get_tradier_stream
from collections.abc import AsyncGenerator
from fastapi import APIRouter, Depends, Query
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
import logging
import time

"""
Server-Sent Events (SSE) Streaming Endpoints

This module provides Server-Sent Events for real-time data streaming.

ARCHITECTURE:
- Tradier API: ALL market data (quotes, streaming, analysis)
- Alpaca API: ONLY paper trade execution (orders, positions, account)

Phase 2.A - Real-Time Data Implementation (Tradier WebSocket streaming)
Phase 5.C - Heartbeat mechanism for connection monitoring
"""

logger = logging.getLogger(__name__)

router = APIRouter(tags=["streaming"])

# Configuration
HEARTBEAT_INTERVAL = 15  # Send heartbeat every 15 seconds
DATA_CHECK_INTERVAL = 1  # Check for new data every 1 second

@router.get("/stream/prices")
async def stream_prices(
    symbols: str = Query(..., description="Comma-separated list of symbols (e.g., AAPL,MSFT,TSLA)"),
    current_user: User = Depends(get_current_user),
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
                    logger.debug("💓 Heartbeat sent (prices stream)")

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
async def stream_positions(
    current_user: User = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
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
                        yield {
                            "event": "position_update",
                            "data": json.dumps(positions_data),
                        }
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
                    logger.debug("💓 Heartbeat sent (positions stream)")

                # Wait 2 seconds before checking again
                await asyncio.sleep(2)

        except asyncio.CancelledError:
            logger.info("📡 Client disconnected from position stream")
            raise
        except Exception as e:
            logger.error(f"❌ Error in position stream: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(position_generator())

@router.get("/stream/market-indices")
async def stream_market_indices(
    current_user: User = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
):
    """
    Stream real-time market indices (Dow Jones, NASDAQ) via Server-Sent Events

    This endpoint:
    1. Reads $DJI and COMP:GIDS from Redis cache (updated by Tradier WebSocket)
    2. Sends formatted data every 1s when prices change
    3. Optimized for RadialMenu center circle display

    Response Format (SSE):
        event: indices_update
        data: {
            "dow": {"last": 42500.00, "change": 125.50, "changePercent": 0.30},
            "nasdaq": {"last": 18350.00, "change": 98.75, "changePercent": 0.54}
        }

    Usage:
        const eventSource = new EventSource('/api/proxy/stream/market-indices');
        eventSource.addEventListener('indices_update', (e) => {
            const { dow, nasdaq } = JSON.parse(e.data);
            updateRadialMenu(dow, nasdaq);
        });
    """
    logger.info("📡 Client subscribed to market indices stream")

    async def indices_generator() -> AsyncGenerator:
        """
        Generate market indices updates from Redis cache with periodic heartbeats.

        Sends:
        - indices_update: When index prices change (every 1s)
        - heartbeat: Every 15s to keep connection alive
        """
        last_indices_hash = None
        last_heartbeat_time = time.time()

        try:
            while True:
                current_time = time.time()
                indices = {}

                # Read $DJI from cache
                dji_trade = cache.get("price:$DJI")
                dji_quote = cache.get("quote:$DJI")

                if dji_trade:
                    indices["dow"] = {
                        "last": round(dji_trade.get("price", 0), 2),
                        "timestamp": dji_trade.get("timestamp"),
                    }
                elif dji_quote:
                    indices["dow"] = {
                        "last": round(dji_quote.get("mid", 0), 2),
                        "timestamp": dji_quote.get("timestamp"),
                    }

                # Read COMP:GIDS from cache
                comp_trade = cache.get("price:COMP:GIDS")
                comp_quote = cache.get("quote:COMP:GIDS")

                if comp_trade:
                    indices["nasdaq"] = {
                        "last": round(comp_trade.get("price", 0), 2),
                        "timestamp": comp_trade.get("timestamp"),
                    }
                elif comp_quote:
                    indices["nasdaq"] = {
                        "last": round(comp_quote.get("mid", 0), 2),
                        "timestamp": comp_quote.get("timestamp"),
                    }

                # Add change percentage if available from summary data
                for symbol, key in [("$DJI", "dow"), ("COMP:GIDS", "nasdaq")]:
                    summary = cache.get(f"summary:{symbol}")
                    if summary and key in indices:
                        # Convert open_price to float (Tradier sends strings)
                        try:
                            open_price = float(summary.get("open", 0))
                            current_price = float(indices[key]["last"])
                            if open_price > 0:
                                change = current_price - open_price
                                change_percent = (change / open_price) * 100
                                indices[key]["change"] = round(change, 2)
                                indices[key]["changePercent"] = round(change_percent, 2)
                        except (ValueError, TypeError) as e:
                            logger.debug(f"⚠️ Could not calculate change for {key}: {e}")

                # Send update if data changed
                if indices:
                    current_hash = hash(json.dumps(indices, sort_keys=True))
                    if current_hash != last_indices_hash:
                        yield {"event": "indices_update", "data": json.dumps(indices)}
                        last_indices_hash = current_hash
                        logger.debug(
                            f"📊 Sent indices update: DOW={indices.get('dow', {}).get('last')}, NASDAQ={indices.get('nasdaq', {}).get('last')}"
                        )

                # Send periodic heartbeat
                if current_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps(
                            {
                                "timestamp": current_time,
                                "stream_type": "market_indices",
                            }
                        ),
                    }
                    last_heartbeat_time = current_time
                    logger.debug("💓 Heartbeat sent (indices stream)")

                # Wait before next check
                await asyncio.sleep(DATA_CHECK_INTERVAL)

        except asyncio.CancelledError:
            logger.info("📡 Client disconnected from indices stream")
            raise
        except Exception as e:
            logger.error(f"❌ Error in indices stream: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(indices_generator())

@router.get("/stream/status")
async def stream_status(current_user: User = Depends(get_current_user)):
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
