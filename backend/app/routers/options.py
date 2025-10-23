"""
Options trading endpoints - Greeks calculation and analysis

Uses Tradier API for options chain data and Black-Scholes-Merton model
for Greeks calculation (Delta, Gamma, Theta, Vega, Rho).
"""

from datetime import datetime
from typing import Literal

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..core.auth import require_bearer
from ..core.config import settings
from ..services.cache import CacheService, get_cache
from ..services.options_greeks import calculate_option_greeks


router = APIRouter(tags=["options"])


class GreeksResponse(BaseModel):
    """Options Greeks calculation response"""

    symbol: str
    strike: float
    expiry: str
    option_type: Literal["call", "put"]

    # Greeks
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float

    # Pricing
    theoretical_price: float
    intrinsic_value: float
    extrinsic_value: float
    probability_itm: float

    # Market data (if available)
    market_price: float | None = None
    implied_volatility: float | None = None
    volume: int | None = None
    open_interest: int | None = None

    timestamp: str
    source: str


class OptionsChainResponse(BaseModel):
    """Options chain data for a specific expiration"""

    symbol: str
    expiration: str
    strikes: list[float]
    options: list[dict]  # Full option contracts with bid/ask/volume/greeks


@router.get("/options/chain", dependencies=[Depends(require_bearer)])
async def get_options_chain(
    symbol: str = Query(..., description="Stock symbol (e.g., SPY)"),
    expiration: str = Query(
        None,
        description="Specific expiration date (YYYY-MM-DD). If not provided, returns all available expirations.",
    ),
    cache: CacheService = Depends(get_cache),
) -> OptionsChainResponse | dict:
    """
    Fetch options chain from Tradier API

    Returns available strikes, bid/ask prices, volume, and Greeks for options contracts.

    Example:
        GET /api/options/chain?symbol=SPY&expiration=2025-12-19

    Returns:
        - List of strikes
        - Full option contracts with market data
        - Greeks if available from Tradier
    """
    cache_key = f"options:chain:{symbol}:{expiration or 'all'}"
    cached = cache.get(cache_key)
    if cached:
        print(f"[Options Chain] ✅ Cache HIT for {symbol} (exp: {expiration or 'all'})")
        return cached

    try:
        # Step 1: If no expiration provided, fetch available expirations
        if not expiration:
            expirations_resp = requests.get(
                f"{settings.TRADIER_API_BASE_URL}/markets/options/expirations",
                headers={
                    "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
                    "Accept": "application/json",
                },
                params={"symbol": symbol, "includeAllRoots": "false"},
                timeout=5,
            )

            if expirations_resp.status_code == 200:
                exp_data = expirations_resp.json()
                expirations = exp_data.get("expirations", {}).get("date", [])

                result = {
                    "symbol": symbol.upper(),
                    "expirations": expirations,
                }

                cache.set(cache_key, result, ttl=300)  # Cache for 5 min
                print(f"[Options Chain] ✅ Fetched {len(expirations)} expirations for {symbol}")
                return result
            else:
                raise HTTPException(
                    status_code=expirations_resp.status_code,
                    detail=f"Failed to fetch expirations: {expirations_resp.text}",
                )

        # Step 2: Fetch options chain for specific expiration
        options_resp = requests.get(
            f"{settings.TRADIER_API_BASE_URL}/markets/options/chains",
            headers={
                "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
                "Accept": "application/json",
            },
            params={"symbol": symbol, "expiration": expiration, "greeks": "true"},
            timeout=10,
        )

        if options_resp.status_code != 200:
            raise HTTPException(
                status_code=options_resp.status_code,
                detail=f"Failed to fetch options chain: {options_resp.text}",
            )

        options_data = options_resp.json()
        options_list = options_data.get("options", {}).get("option", [])
        if isinstance(options_list, dict):
            options_list = [options_list]

        # Extract unique strikes
        strikes = sorted(set(float(opt.get("strike", 0)) for opt in options_list))

        # Build response
        result = {
            "symbol": symbol.upper(),
            "expiration": expiration,
            "strikes": strikes,
            "options": options_list,
        }

        cache.set(cache_key, result, ttl=60)  # Cache for 1 min
        print(
            f"[Options Chain] ✅ Fetched {len(options_list)} contracts ({len(strikes)} strikes) for {symbol} (exp: {expiration})"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Options Chain] ❌ Error fetching chain: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch options chain: {e!s}")


@router.get("/options/greeks", dependencies=[Depends(require_bearer)])
async def get_option_greeks(
    symbol: str = Query(..., description="Stock symbol (e.g., SPY)"),
    strike: float = Query(..., description="Strike price (e.g., 450.00)"),
    expiry: str = Query(..., description="Expiration date (YYYY-MM-DD format)"),
    option_type: Literal["call", "put"] = Query(..., description="Option type: call or put"),
    cache: CacheService = Depends(get_cache),
) -> GreeksResponse:
    """
    Calculate options Greeks using Black-Scholes-Merton model

    Fetches current stock price and implied volatility from Tradier,
    then calculates Delta, Gamma, Theta, Vega, and Rho.

    Example:
        GET /api/options/greeks?symbol=SPY&strike=450&expiry=2025-12-19&option_type=call

    Returns:
        - All 5 Greeks (Delta, Gamma, Theta, Vega, Rho)
        - Theoretical price and intrinsic/extrinsic values
        - Probability of finishing in-the-money
        - Market price and implied volatility (if available)
    """
    # Validate expiry format
    try:
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid expiry format. Use YYYY-MM-DD (e.g., 2025-12-19)"
        )

    # Check if expiry is in the past
    if expiry_date < datetime.now():
        raise HTTPException(status_code=400, detail="Expiry date cannot be in the past")

    # Check cache first (60s TTL for options data)
    cache_key = f"options:greeks:{symbol}:{strike}:{expiry}:{option_type}"
    cached = cache.get(cache_key)
    if cached:
        print(f"[Options Greeks] ✅ Cache HIT for {symbol} {strike} {option_type}")
        return GreeksResponse(**{**cached, "cached": True})

    try:
        # Step 1: Get current stock price from Tradier
        spot_price = None
        try:
            quote_resp = requests.get(
                f"{settings.TRADIER_API_BASE_URL}/markets/quotes",
                headers={
                    "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate",
                },
                params={"symbols": symbol, "greeks": "false"},
                timeout=5,
            )

            if quote_resp.status_code == 200:
                quote_data = quote_resp.json()
                quotes = quote_data.get("quotes", {}).get("quote", [])
                if isinstance(quotes, dict):
                    quotes = [quotes]

                for quote in quotes:
                    if quote.get("symbol") == symbol:
                        spot_price = float(quote.get("last", 0))
                        break

            if not spot_price or spot_price == 0:
                raise ValueError(f"Unable to fetch current price for {symbol}")

            print(f"[Options Greeks] ✅ Fetched spot price for {symbol}: ${spot_price:.2f}")

        except Exception as e:
            raise HTTPException(
                status_code=503, detail=f"Unable to fetch current stock price: {e!s}"
            )

        # Step 2: Get options chain data from Tradier (for implied volatility and market price)
        market_price = None
        implied_volatility = None
        volume = None
        open_interest = None

        try:
            options_resp = requests.get(
                f"{settings.TRADIER_API_BASE_URL}/markets/options/chains",
                headers={
                    "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate",
                },
                params={"symbol": symbol, "expiration": expiry, "greeks": "true"},
                timeout=10,
            )

            if options_resp.status_code == 200:
                options_data = options_resp.json()
                options_list = options_data.get("options", {}).get("option", [])
                if isinstance(options_list, dict):
                    options_list = [options_list]

                # Find matching option contract
                for option in options_list:
                    if (
                        abs(float(option.get("strike", 0)) - strike) < 0.01
                        and option.get("option_type", "").lower() == option_type
                    ):
                        market_price = float(option.get("last", 0)) or float(option.get("bid", 0))
                        implied_volatility = float(option.get("greeks", {}).get("mid_iv", 0))
                        volume = int(option.get("volume", 0))
                        open_interest = int(option.get("open_interest", 0))
                        break

                print(
                    f"[Options Greeks] ✅ Found market data - IV: {implied_volatility:.2%}, Price: ${market_price:.2f}"
                    if implied_volatility
                    else "[Options Greeks] ⚠️ No exact match found in options chain, using estimated IV"
                )

        except Exception as e:
            print(f"[Options Greeks] ⚠️ Could not fetch options chain: {e}")
            # Continue without market data - we'll use estimated IV

        # Step 3: Estimate implied volatility if not available from Tradier
        if not implied_volatility or implied_volatility == 0:
            # Use historical volatility estimate (conservative 30% default for equity options)
            # TODO: Enhance this by fetching historical volatility from Tradier historical API
            implied_volatility = 0.30
            print("[Options Greeks] ℹ️ Using default IV estimate: 30%")

        # Step 4: Calculate Greeks using Black-Scholes-Merton
        greeks = calculate_option_greeks(
            spot_price=spot_price,
            strike_price=strike,
            expiry_date=expiry_date,
            volatility=implied_volatility,
            option_type=option_type,
            dividend_yield=0.0,  # TODO: Fetch dividend yield for dividend-paying stocks
        )

        # Build response
        response_data = {
            "symbol": symbol.upper(),
            "strike": strike,
            "expiry": expiry,
            "option_type": option_type,
            "delta": round(greeks.delta, 4),
            "gamma": round(greeks.gamma, 4),
            "theta": round(greeks.theta, 4),
            "vega": round(greeks.vega, 4),
            "rho": round(greeks.rho, 4),
            "theoretical_price": round(greeks.theoretical_price, 2),
            "intrinsic_value": round(greeks.intrinsic_value, 2),
            "extrinsic_value": round(greeks.extrinsic_value, 2),
            "probability_itm": round(greeks.probability_itm, 4),
            "market_price": round(market_price, 2) if market_price else None,
            "implied_volatility": round(implied_volatility, 4) if implied_volatility else None,
            "volume": volume,
            "open_interest": open_interest,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "black_scholes",
        }

        # Cache for 60 seconds
        cache.set(cache_key, response_data, ttl=60)

        print(
            f"[Options Greeks] ✅ Calculated Greeks for {symbol} ${strike} {option_type} (exp: {expiry})"
        )
        print(
            f"[Options Greeks]    Delta: {greeks.delta:.4f}, Theta: {greeks.theta:.4f}, Vega: {greeks.vega:.4f}"
        )

        return GreeksResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Options Greeks] ❌ Calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Greeks calculation failed: {e!s}")
