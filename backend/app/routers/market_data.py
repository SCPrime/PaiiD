        from ..services.fixture_loader import get_fixture_loader
        from ..services.fixture_loader import get_fixture_loader
    from ..core.config import settings
    from ..core.config import settings
from ..services.cache import CacheService, get_cache
from ..services.tradier_client import get_tradier_client
from app.core.jwt import get_current_user
from app.models.database import User
from datetime import UTC, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
import logging

"""
Market data endpoints using Tradier API

🚨 TRADIER INTEGRATION ACTIVE 🚨
This module uses Tradier API for ALL market data.
Alpaca is ONLY used for paper trading execution (see orders.py).
"""





logger = logging.getLogger(__name__)

# Runtime notice (kept minimal)
logger.info("market_data router loaded (Tradier integration)")

router = APIRouter()

@router.get("/market/quote/{symbol}")
async def get_quote(
    symbol: str,
    current_user: User = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
):
    """Get real-time quote for a symbol using Tradier (cached for 15s)

    Supports fixture mode for deterministic testing when USE_TEST_FIXTURES=true.
    """
    # Check if we should use test fixtures

    if settings.USE_TEST_FIXTURES:
        logger.info("Using test fixtures for quote data")

        fixture_loader = get_fixture_loader()
        quotes_data = fixture_loader.load_market_quotes([symbol])

        if not quotes_data or symbol.upper() not in quotes_data:
            raise HTTPException(
                status_code=404, detail=f"No fixture data available for symbol {symbol}"
            )

        quote = quotes_data[symbol.upper()]

        result = {
            "symbol": symbol.upper(),
            "bid": float(quote.get("bid", 0)),
            "ask": float(quote.get("ask", 0)),
            "last": float(quote.get("last", 0)),
            "volume": int(quote.get("volume", 0)),
            "timestamp": quote.get("timestamp", datetime.now(UTC).isoformat()),
            "test_fixture": True,  # Mark as fixture data
        }

        return result

    # Check cache first
    cache_key = f"quote:{symbol.upper()}"
    cached_quote = cache.get(cache_key)
    if cached_quote:
        logger.info(f"✅ Cache HIT for quote {symbol}")
        return cached_quote

    try:
        client = get_tradier_client()
        quotes_data = client.get_quotes([symbol])

        if not quotes_data or symbol.upper() not in quotes_data:
            raise HTTPException(status_code=404, detail=f"No quote found for {symbol}")

        quote = quotes_data[symbol.upper()]

        result = {
            "symbol": symbol.upper(),
            "bid": float(quote.get("bid", 0)),
            "ask": float(quote.get("ask", 0)),
            "last": float(quote.get("last", 0)),
            "volume": int(quote.get("volume", 0)),
            "timestamp": quote.get("trade_date", datetime.now().isoformat()),
        }

        # Cache for 15 seconds
        cache.set(cache_key, result, ttl=15)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Tradier quote request failed for {symbol}: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quote: {e!s}")

@router.get("/market/quotes")
async def get_quotes(symbols: str, current_user: User = Depends(get_current_user)):
    """Get quotes for multiple symbols (comma-separated) using Tradier

    Supports fixture mode for deterministic testing when USE_TEST_FIXTURES=true.
    """
    # Check if we should use test fixtures

    if settings.USE_TEST_FIXTURES:
        logger.info("Using test fixtures for quotes data")

        fixture_loader = get_fixture_loader()
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        quotes_data = fixture_loader.load_market_quotes(symbol_list)

        result = {}
        for symbol in symbol_list:
            if symbol in quotes_data:
                q = quotes_data[symbol]
                result[symbol] = {
                    "bid": float(q.get("bid", 0)),
                    "ask": float(q.get("ask", 0)),
                    "last": float(q.get("last", 0)),
                    "timestamp": q.get("timestamp", datetime.now(UTC).isoformat()),
                    "test_fixture": True,  # Mark as fixture data
                }

        logger.info(f"✅ Retrieved {len(result)} fixture quotes")
        return result

    try:
        client = get_tradier_client()
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        quotes_data = client.get_quotes(symbol_list)

        result = {}
        for symbol in symbol_list:
            if symbol in quotes_data:
                q = quotes_data[symbol]
                result[symbol] = {
                    "bid": float(q.get("bid", 0)),
                    "ask": float(q.get("ask", 0)),
                    "last": float(q.get("last", 0)),
                    "timestamp": q.get("trade_date", datetime.now(UTC).isoformat()),
                }

        logger.info(f"✅ Retrieved {len(result)} quotes from Tradier")
        return result
    except Exception as e:
        logger.error(f"❌ Tradier quotes request failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quotes: {e!s}")

@router.get("/market/bars/{symbol}")
async def get_bars(
    symbol: str,
    timeframe: str = "daily",
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    """Get historical price bars using Tradier"""
    try:
        client = get_tradier_client()

        # Map timeframe to Tradier intervals
        interval_map = {
            "1Min": "1min",
            "5Min": "5min",
            "15Min": "15min",
            "1Hour": "1hour",
            "1Day": "daily",
            "daily": "daily",
            "weekly": "weekly",
            "monthly": "monthly",
        }

        interval = interval_map.get(timeframe, "daily")

        # Calculate date range based on limit
        end_date = datetime.now(UTC)
        if interval in ["1min", "5min", "15min"]:
            start_date = end_date - timedelta(
                days=min(limit // 78, 30)
            )  # Market hours limit
        elif interval == "1hour":
            start_date = end_date - timedelta(days=min(limit // 6, 90))
        else:  # daily, weekly, monthly
            start_date = end_date - timedelta(days=limit * 2)  # Approximate

        bars_data = client.get_historical_quotes(
            symbol=symbol,
            interval=interval,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

        result = []
        for bar in bars_data[:limit]:
            result.append(
                {
                    "timestamp": bar.get("date", bar.get("time", "")),
                    "open": float(bar.get("open", 0)),
                    "high": float(bar.get("high", 0)),
                    "low": float(bar.get("low", 0)),
                    "close": float(bar.get("close", 0)),
                    "volume": int(bar.get("volume", 0)),
                }
            )

        logger.info(f"✅ Retrieved {len(result)} bars for {symbol} from Tradier")
        return {"symbol": symbol.upper(), "bars": result}
    except Exception as e:
        logger.error(f"❌ Tradier bars request failed for {symbol}: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch bars: {e!s}")

@router.get("/market/scanner/under4")
async def scan_under_4(current_user: User = Depends(get_current_user)):
    """Scan for stocks under $4 with volume using Tradier"""
    try:
        # Pre-defined list of liquid stocks that trade near/under $4
        candidates = [
            "SOFI",
            "PLUG",
            "RIOT",
            "NIO",
            "F",
            "VALE",
            "BTG",
            "GOLD",
            "SIRI",
            "TLRY",
            "SNAP",
            "BBD",
        ]

        client = get_tradier_client()
        quotes_data = client.get_quotes(candidates)

        results = []
        for symbol in candidates:
            if symbol in quotes_data:
                q = quotes_data[symbol]
                ask_price = float(q.get("ask", 0))
                last_price = float(q.get("last", 0))
                price = last_price if last_price > 0 else ask_price

                if 0.50 < price < 4.00:  # Filter under $4, above $0.50
                    results.append(
                        {
                            "symbol": symbol,
                            "price": price,
                            "bid": float(q.get("bid", 0)),
                            "ask": ask_price,
                            "volume": int(q.get("volume", 0)),
                            "timestamp": q.get(
                                "trade_date", datetime.now(UTC).isoformat()
                            ),
                        }
                    )

        # Sort by price ascending
        results.sort(key=lambda x: x["price"])

        logger.info(f"✅ Scanner found {len(results)} stocks under $4 from Tradier")
        return {"candidates": results, "count": len(results)}
    except Exception as e:
        logger.error(f"❌ Tradier scanner request failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to scan stocks: {e!s}")
