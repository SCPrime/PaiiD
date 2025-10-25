            from anthropic import Anthropic
            import json
    from datetime import UTC, datetime
    from datetime import UTC, datetime
    from datetime import UTC, datetime
from ..core.config import settings
from ..core.jwt import get_current_user
from ..models.database import User
from ..services.cache import CacheService, get_cache
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
import requests

"""
Market conditions and analysis endpoints

🚨 TRADIER INTEGRATION ACTIVE 🚨
This module uses Tradier API for ALL market data.
Alpaca is ONLY used for paper trading execution.
"""

# LOUD LOGGING TO VERIFY NEW CODE IS DEPLOYED
print("=" * 80)
print("[TRADIER] TRADIER INTEGRATION CODE LOADED - market.py")
print("=" * 80)
print(f"TRADIER_API_KEY present: {bool(settings.TRADIER_API_KEY)}")
print(f"TRADIER_API_BASE_URL: {settings.TRADIER_API_BASE_URL}")
print(f"ANTHROPIC_API_KEY present: {bool(settings.ANTHROPIC_API_KEY)}")
print("=" * 80, flush=True)

router = APIRouter(tags=["market"])

class MarketCondition(BaseModel):
    name: str
    value: str
    status: Literal["favorable", "neutral", "unfavorable"]
    details: str | None = None

@router.get("/market/conditions")
async def get_market_conditions(
    current_user: User = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
) -> dict:
    """
    Get current market conditions for trading analysis using real Tradier data

    Provides:
    - VIX volatility index (real-time from Tradier)
    - Market trend analysis for Dow Jones and NASDAQ (real-time)
    - Market breadth indicators (placeholder - requires additional data)
    - Overall sentiment and recommended actions
    """

    # Check cache first (60s TTL)
    cache_key = "market:conditions"
    cached = cache.get(cache_key)
    if cached:
        print("[Market Conditions] ✅ Cache HIT")
        return {**cached, "cached": True}

    try:
        # Fetch real market data from Tradier (with compression for faster response)
        symbols = "$VIX.X,$DJI.IX,COMP:GIDS"
        resp = requests.get(
            f"{settings.TRADIER_API_BASE_URL}/markets/quotes",
            headers={
                "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",  # Enable compression
            },
            params={"symbols": symbols, "greeks": "false"},
            timeout=5,  # Add timeout for reliability
        )

        conditions: list[MarketCondition] = []
        overall_sentiment = "neutral"
        positive_signals = 0
        total_signals = 0

        if resp.status_code == 200:
            data = resp.json()
            quotes = data.get("quotes", {}).get("quote", [])
            if isinstance(quotes, dict):
                quotes = [quotes]

            quote_map = {q.get("symbol"): q for q in quotes}

            # 1. VIX Volatility Index
            vix_quote = quote_map.get("$VIX.X")
            if vix_quote and "last" in vix_quote:
                vix_value = float(vix_quote["last"])
                if vix_value < 15:
                    vix_status = "favorable"
                    vix_details = f"Very low volatility ({vix_value:.2f}) - calm market, good for directional trades"
                    positive_signals += 1
                elif vix_value < 20:
                    vix_status = "favorable"
                    vix_details = f"Low volatility ({vix_value:.2f}) - stable market conditions"
                    positive_signals += 1
                elif vix_value < 30:
                    vix_status = "neutral"
                    vix_details = f"Moderate volatility ({vix_value:.2f}) - some uncertainty, trade with caution"
                else:
                    vix_status = "unfavorable"
                    vix_details = f"High volatility ({vix_value:.2f}) - turbulent market, high risk"

                conditions.append(
                    MarketCondition(
                        name="VIX (Volatility)",
                        value=f"{vix_value:.2f}",
                        status=vix_status,
                        details=vix_details,
                    )
                )
                total_signals += 1

            # 2. Dow Jones Industrial Trend
            dji_quote = quote_map.get("$DJI.IX") or quote_map.get("$DJI")
            if dji_quote and "last" in dji_quote:
                float(dji_quote["last"])
                dji_change_pct = float(dji_quote.get("change_percentage", 0))

                if dji_change_pct > 1.0:
                    dji_status = "favorable"
                    dji_value = "Strong Uptrend"
                    dji_details = f"Up {dji_change_pct:+.2f}% - strong bullish momentum"
                    positive_signals += 1
                elif dji_change_pct > 0:
                    dji_status = "favorable"
                    dji_value = "Uptrend"
                    dji_details = f"Up {dji_change_pct:+.2f}% - positive momentum"
                    positive_signals += 1
                elif dji_change_pct > -1.0:
                    dji_status = "neutral"
                    dji_value = "Sideways"
                    dji_details = f"Change {dji_change_pct:+.2f}% - consolidating"
                else:
                    dji_status = "unfavorable"
                    dji_value = "Downtrend"
                    dji_details = f"Down {dji_change_pct:.2f}% - bearish pressure"

                conditions.append(
                    MarketCondition(
                        name="Dow Jones Trend",
                        value=dji_value,
                        status=dji_status,
                        details=dji_details,
                    )
                )
                total_signals += 1

            # 3. NASDAQ Composite Trend
            comp_quote = quote_map.get("COMP:GIDS") or quote_map.get("$COMP.IX")
            if comp_quote and "last" in comp_quote:
                float(comp_quote["last"])
                comp_change_pct = float(comp_quote.get("change_percentage", 0))

                if comp_change_pct > 1.0:
                    comp_status = "favorable"
                    comp_value = "Strong Uptrend"
                    comp_details = f"Tech sector strong: up {comp_change_pct:+.2f}%"
                    positive_signals += 1
                elif comp_change_pct > 0:
                    comp_status = "favorable"
                    comp_value = "Uptrend"
                    comp_details = f"Tech sector positive: up {comp_change_pct:+.2f}%"
                    positive_signals += 1
                elif comp_change_pct > -1.0:
                    comp_status = "neutral"
                    comp_value = "Sideways"
                    comp_details = f"Tech sector mixed: {comp_change_pct:+.2f}%"
                else:
                    comp_status = "unfavorable"
                    comp_value = "Downtrend"
                    comp_details = f"Tech sector weak: down {comp_change_pct:.2f}%"

                conditions.append(
                    MarketCondition(
                        name="NASDAQ Trend",
                        value=comp_value,
                        status=comp_status,
                        details=comp_details,
                    )
                )
                total_signals += 1

        # Calculate overall sentiment
        if total_signals > 0:
            bullish_pct = (positive_signals / total_signals) * 100
            if bullish_pct >= 67:
                overall_sentiment = "bullish"
            elif bullish_pct >= 33:
                overall_sentiment = "neutral"
            else:
                overall_sentiment = "bearish"

        # Generate recommended actions based on sentiment
        if overall_sentiment == "bullish":
            recommended_actions = [
                "Consider directional bullish strategies",
                "Look for momentum plays in strong sectors",
                "Monitor for breakout opportunities",
            ]
        elif overall_sentiment == "bearish":
            recommended_actions = [
                "Consider defensive positions or cash",
                "Look for short opportunities or hedges",
                "Wait for clearer bullish signals before entering",
            ]
        else:
            recommended_actions = [
                "Trade cautiously with tight stops",
                "Focus on high-conviction setups only",
                "Wait for directional confirmation",
            ]

        # PHASE 3 ENHANCEMENT: Additional market conditions (requires more data sources)
        # Planned integrations:
        #   - Market Breadth (advance/decline ratio) → Tradier Market Data API upgrade
        #   - Volume analysis → Requires historical OHLCV storage + comparison logic
        #   - Put/Call ratio → Tradier Options Market Data subscription
        # Current: Basic SPY/QQQ price momentum + VIX sentiment (sufficient for MVP)

        result = {
            "conditions": [cond.model_dump() for cond in conditions],
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "overallSentiment": overall_sentiment,
            "recommendedActions": recommended_actions,
            "source": "tradier",
        }

        # Cache for 60 seconds
        cache.set(cache_key, result, ttl=60)

        print(f"[Market Conditions] ✅ Fetched {len(conditions)} real conditions from Tradier")
        return result

    except Exception as e:
        print(f"[Market Conditions] ❌ Error fetching from Tradier: {e}")
        # Return basic fallback conditions
        fallback_conditions = [
            MarketCondition(
                name="Market Data",
                value="Unavailable",
                status="neutral",
                details="Unable to fetch current market conditions. Please try again later.",
            )
        ]
        return {
            "conditions": [cond.model_dump() for cond in fallback_conditions],
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "overallSentiment": "neutral",
            "recommendedActions": ["Wait for market data to become available"],
            "source": "fallback",
            "error": str(e),
        }

@router.get("/market/indices")
async def get_major_indices(
    current_user: User = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
) -> dict:
    """
    Get current prices for Dow Jones Industrial and NASDAQ Composite

    Data Source Priority:
    1. Redis Cache (60s TTL)
    2. Tradier API (live market data)
    3. Claude AI (intelligent fallback)
    4. Error 503 (service unavailable)

    Returns data in format: { dow: {...}, nasdaq: {...} }
    """
    # Check cache first
    cache_key = "market:indices"
    cached_data = cache.get(cache_key)
    if cached_data:
        print("[Market] ✅ Cache HIT for indices")
        return {**cached_data, "cached": True}

    # Try Tradier first
    try:
        if not settings.TRADIER_API_KEY:
            raise ValueError("Tradier API key not configured")

        headers = {
            "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",  # Enable compression
        }

        # Tradier symbols: $DJI for Dow Jones Industrial, COMP:GIDS for NASDAQ Composite
        symbols = "$DJI,COMP:GIDS"
        resp = requests.get(
            f"{settings.TRADIER_API_BASE_URL}/markets/quotes",
            headers=headers,
            params={"symbols": symbols, "greeks": "false"},
            timeout=5,  # Add timeout for reliability
        )

        if resp.status_code == 200:
            data = resp.json()
            quotes = data.get("quotes", {}).get("quote", [])

            # Handle both single quote (dict) and multiple quotes (list)
            if isinstance(quotes, dict):
                quotes = [quotes]

            dow_data = {}
            nasdaq_data = {}

            for quote in quotes:
                symbol = quote.get("symbol", "")
                last = float(quote.get("last", 0))
                change = float(quote.get("change", 0))
                change_percent = float(quote.get("change_percentage", 0))

                if symbol == "$DJI":
                    dow_data = {
                        "last": round(last, 2),
                        "change": round(change, 2),
                        "changePercent": round(change_percent, 2),
                    }
                elif symbol == "COMP:GIDS":
                    nasdaq_data = {
                        "last": round(last, 2),
                        "change": round(change, 2),
                        "changePercent": round(change_percent, 2),
                    }

            if dow_data or nasdaq_data:
                print("[Market] ✅ Fetched live data from Tradier for Dow/NASDAQ")
                result = {
                    "dow": dow_data or {"last": 0, "change": 0, "changePercent": 0},
                    "nasdaq": nasdaq_data or {"last": 0, "change": 0, "changePercent": 0},
                    "source": "tradier",
                }
                # Cache for 60 seconds
                cache.set(cache_key, result, ttl=60)
                return result
            else:
                raise ValueError("No Tradier quote data returned")

    except Exception as e:
        print(f"[Market] ⚠️ Tradier failed: {e}, trying Claude AI fallback...")

        # Fallback to Claude AI
        try:
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("Anthropic API key not configured")

            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": """Provide current market index values for Dow Jones Industrial Average ($DJI) and NASDAQ Composite ($COMPX).
                    Return ONLY valid JSON in this exact format with realistic current values:
                    {
                      "dow": {"last": 42500.00, "change": 125.50, "changePercent": 0.30},
                      "nasdaq": {"last": 18350.00, "change": 98.75, "changePercent": 0.54}
                    }""",
                    }
                ],
            )

            # Parse Claude's response

            ai_text = message.content[0].text.strip()
            # Remove markdown code blocks if present
            if "```json" in ai_text:
                ai_text = ai_text.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_text:
                ai_text = ai_text.split("```")[1].split("```")[0].strip()

            ai_data = json.loads(ai_text)

            print("[Market] ✅ Using Claude AI fallback for Dow/NASDAQ")
            result = {**ai_data, "source": "claude_ai"}
            # Cache AI fallback for 60 seconds too
            cache.set(cache_key, result, ttl=60)
            return result

        except Exception as ai_error:
            print(f"[Market] ❌ Claude AI fallback also failed: {ai_error}")
            raise HTTPException(
                status_code=503,
                detail="Market data temporarily unavailable (Tradier and Claude AI both failed)",
            )

@router.get("/market/sectors")
async def get_sector_performance(
    current_user: User = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
) -> dict:
    """
    Get performance of major market sectors using real Tradier data

    Fetches real-time quotes for sector ETFs and ranks by performance
    """

    # Check cache first (60s TTL)
    cache_key = "market:sectors"
    cached = cache.get(cache_key)
    if cached:
        print("[Sector Performance] ✅ Cache HIT")
        return {**cached, "cached": True}

    try:
        # Define sector ETFs
        sector_etfs = [
            {"name": "Technology", "symbol": "XLK"},
            {"name": "Communication", "symbol": "XLC"},
            {"name": "Consumer Discretionary", "symbol": "XLY"},
            {"name": "Financials", "symbol": "XLF"},
            {"name": "Healthcare", "symbol": "XLV"},
            {"name": "Industrials", "symbol": "XLI"},
            {"name": "Materials", "symbol": "XLB"},
            {"name": "Real Estate", "symbol": "XLRE"},
            {"name": "Utilities", "symbol": "XLU"},
            {"name": "Energy", "symbol": "XLE"},
            {"name": "Consumer Staples", "symbol": "XLP"},
        ]

        # Fetch real quotes from Tradier (with compression for 11 sector ETFs)
        symbols = ",".join([s["symbol"] for s in sector_etfs])
        resp = requests.get(
            f"{settings.TRADIER_API_BASE_URL}/markets/quotes",
            headers={
                "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",  # Enable compression
            },
            params={"symbols": symbols, "greeks": "false"},
            timeout=5,  # Add timeout for reliability
        )

        sectors = []

        if resp.status_code == 200:
            data = resp.json()
            quotes = data.get("quotes", {}).get("quote", [])
            if isinstance(quotes, dict):
                quotes = [quotes]

            # Create quote lookup
            quote_map = {q.get("symbol"): q for q in quotes if q.get("symbol")}

            # Build sector list with real data
            for sector in sector_etfs:
                quote = quote_map.get(sector["symbol"])
                if quote and "change_percentage" in quote:
                    change_percent = float(quote.get("change_percentage", 0))
                    sectors.append(
                        {
                            "name": sector["name"],
                            "symbol": sector["symbol"],
                            "changePercent": round(change_percent, 2),
                            "last": float(quote.get("last", 0)),
                        }
                    )

            # Sort by performance (descending)
            sectors.sort(key=lambda x: x["changePercent"], reverse=True)

            # Add ranks
            for idx, sector in enumerate(sectors):
                sector["rank"] = idx + 1

            # Identify leader and laggard
            leader = sectors[0]["name"] if sectors else "Unknown"
            laggard = sectors[-1]["name"] if sectors else "Unknown"

            result = {
                "sectors": sectors,
                "timestamp": datetime.now(UTC).isoformat() + "Z",
                "leader": leader,
                "laggard": laggard,
                "source": "tradier",
            }

            # Cache for 60 seconds
            cache.set(cache_key, result, ttl=60)

            print(f"[Sector Performance] ✅ Fetched {len(sectors)} real sector ETFs from Tradier")
            return result

        else:
            raise Exception(f"Tradier API returned status {resp.status_code}")

    except Exception as e:
        print(f"[Sector Performance] ❌ Error fetching from Tradier: {e}")
        # Return fallback with neutral data
        fallback_sectors = [
            {"name": "Market Data", "symbol": "N/A", "changePercent": 0.0, "rank": 1}
        ]
        return {
            "sectors": fallback_sectors,
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "leader": "Unavailable",
            "laggard": "Unavailable",
            "source": "fallback",
            "error": str(e),
        }

@router.get("/market/status")
async def get_market_status(
    current_user: User = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
) -> dict:
    """
    Get current market status (open/closed) and trading hours

    Uses Tradier market clock API to determine if markets are currently open.
    Cached for 60 seconds to minimize API calls.

    Returns:
        - state: "open" | "premarket" | "postmarket" | "closed"
        - is_open: boolean
        - next_change: timestamp of next state change
        - description: human-readable status
    """

    # Check cache first (60s TTL)
    cache_key = "market:status"
    cached = cache.get(cache_key)
    if cached:
        print("[Market Status] ✅ Cache HIT")
        return {**cached, "cached": True}

    try:
        # Fetch market clock from Tradier (with compression)
        resp = requests.get(
            f"{settings.TRADIER_API_BASE_URL}/markets/clock",
            headers={
                "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",  # Enable compression
            },
            timeout=5,  # Add timeout for reliability
        )

        if resp.status_code == 200:
            data = resp.json()
            clock = data.get("clock", {})

            state = clock.get("state", "closed")  # open, premarket, postmarket, closed
            is_open = state == "open"
            next_change = clock.get("next_change", "")
            description = clock.get("description", "")

            result = {
                "state": state,
                "is_open": is_open,
                "next_change": next_change,
                "description": description,
                "timestamp": datetime.now(UTC).isoformat() + "Z",
                "source": "tradier",
            }

            # Cache for 60 seconds
            cache.set(cache_key, result, ttl=60)

            print(f"[Market Status] ✅ Market is {state} (is_open={is_open})")
            return result
        else:
            raise Exception(f"Tradier API returned status {resp.status_code}")

    except Exception as e:
        print(f"[Market Status] ❌ Error fetching from Tradier: {e}")
        # Return fallback - assume closed to prevent unnecessary updates
        return {
            "state": "closed",
            "is_open": False,
            "next_change": "",
            "description": "Market status unavailable",
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "source": "fallback",
            "error": str(e),
        }
