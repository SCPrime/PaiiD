"""
Market data endpoints using Tradier API

🚨 TRADIER INTEGRATION ACTIVE 🚨
This module uses Tradier API for ALL market data.
Alpaca is ONLY used for paper trading execution (see orders.py).
"""

import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from ..core.config import get_settings
from ..core.unified_auth import get_current_user_unified
from ..models.database import User
from ..services.cache import CacheService, get_cache
from ..services.tradier_client import get_tradier_client


logger = logging.getLogger(__name__)

# Runtime notice (kept minimal)
logger.info("market_data router loaded (Tradier integration)")

router = APIRouter()


@router.get("/market/quote/{symbol}")
async def get_quote(
    symbol: str = Path(..., min_length=1, max_length=10, description="Stock symbol"),
    current_user: User = Depends(get_current_user_unified),
    cache: CacheService = Depends(get_cache),
):
    """Get real-time quote for a symbol using Tradier (cached with configurable TTL)

    Supports fixture mode for deterministic testing when USE_TEST_FIXTURES=true.
    """
    # Get settings for cache TTL
    settings = get_settings()

    # Check if we should use test fixtures
    if settings.USE_TEST_FIXTURES:
        logger.info("Using test fixtures for quote data")
        from ..services.fixture_loader import get_fixture_loader

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

    # Check cache first (using configurable TTL)
    cache_key = f"quote:{symbol.upper()}"
    cached_quote = cache.get(cache_key)
    if cached_quote:
        logger.info(f"✅ Cache HIT for quote {symbol} (TTL: {settings.CACHE_TTL_QUOTE}s)")
        cached_quote["cached"] = True
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
            "cached": False,
        }

        # Cache with configurable TTL from settings
        cache.set(cache_key, result, ttl=settings.CACHE_TTL_QUOTE)
        logger.info(f"💾 Cached quote {symbol} (TTL: {settings.CACHE_TTL_QUOTE}s)")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Tradier quote request failed for {symbol}: {e!s}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch quote: {e!s}"
        ) from e


@router.get("/market/quotes")
async def get_quotes(
    symbols: str = Query(..., min_length=1, max_length=200, description="Comma-separated symbols"),
    current_user: User = Depends(get_current_user_unified),
    cache: CacheService = Depends(get_cache),
):
    """Get quotes for multiple symbols (comma-separated) using Tradier with intelligent caching

    Supports fixture mode for deterministic testing when USE_TEST_FIXTURES=true.
    """
    # Get settings for cache TTL
    settings = get_settings()

    # Check if we should use test fixtures
    if settings.USE_TEST_FIXTURES:
        logger.info("Using test fixtures for quotes data")
        from ..services.fixture_loader import get_fixture_loader

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
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        result = {}
        cache_misses = []
        cache_hits = 0

        # Check cache for each symbol individually
        for symbol in symbol_list:
            cache_key = f"quote:{symbol}"
            cached = cache.get(cache_key)
            if cached:
                # Extract the quote data (removing meta fields like 'cached')
                result[symbol] = {
                    "bid": cached.get("bid"),
                    "ask": cached.get("ask"),
                    "last": cached.get("last"),
                    "timestamp": cached.get("timestamp"),
                }
                cache_hits += 1
            else:
                cache_misses.append(symbol)

        # Fetch cache misses from API in batch
        if cache_misses:
            client = get_tradier_client()
            quotes_data = client.get_quotes(cache_misses)

            for symbol in cache_misses:
                if symbol in quotes_data:
                    q = quotes_data[symbol]
                    quote = {
                        "bid": float(q.get("bid", 0)),
                        "ask": float(q.get("ask", 0)),
                        "last": float(q.get("last", 0)),
                        "timestamp": q.get("trade_date", datetime.now(UTC).isoformat()),
                    }
                    result[symbol] = quote

                    # Cache individual quote with metadata
                    cache_entry = {**quote, "symbol": symbol, "cached": False}
                    cache.set(f"quote:{symbol}", cache_entry, ttl=settings.CACHE_TTL_QUOTE)

        logger.info(
            f"✅ Retrieved {len(result)} quotes "
            f"(Cache: {cache_hits} hits, {len(cache_misses)} misses)"
        )
        return result
    except Exception as e:
        logger.error(f"❌ Tradier quotes request failed: {e!s}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch quotes: {e!s}"
        ) from e


@router.get("/market/bars/{symbol}")
async def get_bars(
    symbol: str = Path(..., min_length=1, max_length=10, description="Stock symbol"),
    timeframe: str = Query("daily", pattern="^(1Min|5Min|15Min|1Hour|1Day|daily|weekly|monthly)$"),
    limit: int = Query(100, ge=1, le=1000, description="Number of bars to return"),
    current_user: User = Depends(get_current_user_unified),
    cache: CacheService = Depends(get_cache),
):
    """Get historical price bars using Tradier with intelligent caching

    Historical data is cached for 1 hour (configurable) since past bars don't change.
    """
    # Get settings for cache TTL
    settings = get_settings()

    # Create cache key based on symbol, timeframe, and limit
    cache_key = f"bars:{symbol.upper()}:{timeframe}:{limit}"

    # Check cache first
    cached_bars = cache.get(cache_key)
    if cached_bars:
        logger.info(
            f"✅ Cache HIT for bars {symbol} {timeframe} "
            f"(TTL: {settings.CACHE_TTL_HISTORICAL_BARS}s)"
        )
        return {**cached_bars, "cached": True}

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

        response = {"symbol": symbol.upper(), "bars": result, "cached": False}

        # Cache with long TTL since historical data doesn't change
        cache.set(cache_key, response, ttl=settings.CACHE_TTL_HISTORICAL_BARS)
        logger.info(
            f"✅ Retrieved {len(result)} bars for {symbol} from Tradier "
            f"(cached for {settings.CACHE_TTL_HISTORICAL_BARS}s)"
        )
        return response
    except Exception as e:
        logger.error(f"❌ Tradier bars request failed for {symbol}: {e!s}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch bars: {e!s}"
        ) from e


@router.get("/market/scanner/under4")
async def scan_under_4(
    current_user: User = Depends(get_current_user_unified),
    cache: CacheService = Depends(get_cache),
):
    """Scan for stocks under $4 with volume using Tradier with caching

    Scanner results are cached for 3 minutes (configurable) to reduce API load
    while still providing reasonably fresh results.
    """
    # Get settings for cache TTL
    settings = get_settings()

    # Check cache first
    cache_key = "scanner:under4"
    cached_results = cache.get(cache_key)
    if cached_results:
        logger.info(f"✅ Cache HIT for scanner under $4 (TTL: {settings.CACHE_TTL_SCANNER}s)")
        return {**cached_results, "cached": True}

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

        response = {"candidates": results, "count": len(results), "cached": False}

        # Cache scanner results
        cache.set(cache_key, response, ttl=settings.CACHE_TTL_SCANNER)
        logger.info(
            f"✅ Scanner found {len(results)} stocks under $4 from Tradier "
            f"(cached for {settings.CACHE_TTL_SCANNER}s)"
        )
        return response
    except Exception as e:
        logger.error(f"❌ Tradier scanner request failed: {e!s}")
        raise HTTPException(
            status_code=500, detail=f"Failed to scan stocks: {e!s}"
        ) from e


@router.get("/market/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user_unified),
):
    """
    Get cache performance statistics

    Returns cache hit/miss rates and performance metrics from the health monitor.
    Useful for monitoring cache effectiveness and tuning TTL values.
    """
    from ..services.health_monitor import health_monitor

    total_cache_ops = health_monitor.cache_hits + health_monitor.cache_misses
    hit_rate = (
        (health_monitor.cache_hits / total_cache_ops * 100)
        if total_cache_ops > 0
        else 0.0
    )

    stats = {
        "cache_hits": health_monitor.cache_hits,
        "cache_misses": health_monitor.cache_misses,
        "total_requests": total_cache_ops,
        "hit_rate_percent": hit_rate,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    logger.info(
        f"📊 Cache Stats: {stats['cache_hits']} hits, {stats['cache_misses']} misses "
        f"({stats['hit_rate_percent']:.1f}% hit rate)"
    )

    return stats


@router.post("/market/cache/clear")
async def clear_market_cache(
    current_user: User = Depends(get_current_user_unified),
    cache: CacheService = Depends(get_cache),
):
    """
    Clear all market data caches

    Invalidates all cached quotes, bars, scanner results, etc.
    Use this to force fresh data from Tradier API.
    """
    # Clear all market-related cache patterns
    patterns_cleared = 0

    patterns = [
        "quote:*",
        "bars:*",
        "scanner:*",
    ]

    for pattern in patterns:
        count = cache.clear_pattern(pattern)
        patterns_cleared += count

    logger.info(f"🧹 Cleared {patterns_cleared} market cache entries")

    return {
        "success": True,
        "entries_cleared": patterns_cleared,
        "timestamp": datetime.now(UTC).isoformat(),
    }
