"""
Options Trading Router

Provides endpoints for options chain data, Greeks calculation, and multi-leg options strategies.
Integrates with Tradier API for real-time options data with Greeks.

Phase 1 Implementation:
- Options chain fetching with Greeks (Tradier API)
- Real-time market data
- Multi-leg order support
"""

import asyncio
import logging
from datetime import datetime

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..core.auth import require_bearer
from ..services.tradier_client import get_tradier_client
from ..services.cache import get_cache


router = APIRouter(prefix="/options", tags=["options"])
logger = logging.getLogger(__name__)

cache = get_cache()


# ============================================================================
# TRADIER CLIENT HELPER
# ============================================================================


def _get_tradier_client():
    """Get Tradier client instance"""
    return get_tradier_client()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class OptionContract(BaseModel):
    """Single option contract details"""

    symbol: str = Field(..., description="Option symbol (e.g., AAPL250117C00150000)")
    underlying_symbol: str = Field(..., description="Underlying stock symbol")
    option_type: str = Field(..., description="call or put")
    strike_price: float = Field(..., description="Strike price")
    expiration_date: str = Field(..., description="Expiration date (YYYY-MM-DD)")

    # Market data
    bid: float | None = Field(None, description="Current bid price")
    ask: float | None = Field(None, description="Current ask price")
    last_price: float | None = Field(None, description="Last traded price")
    volume: int | None = Field(None, description="Trading volume")
    open_interest: int | None = Field(None, description="Open interest")

    # Greeks (populated by greeks service)
    delta: float | None = Field(None, description="Delta (sensitivity to price)")
    gamma: float | None = Field(None, description="Gamma (rate of delta change)")
    theta: float | None = Field(None, description="Theta (time decay)")
    vega: float | None = Field(None, description="Vega (sensitivity to volatility)")
    rho: float | None = Field(None, description="Rho (sensitivity to interest rates)")

    # Implied volatility
    implied_volatility: float | None = Field(None, description="Implied volatility")


class OptionsChainResponse(BaseModel):
    """Options chain for a symbol and expiration"""

    symbol: str
    expiration_date: str
    underlying_price: float | None = None
    calls: list[OptionContract] = []
    puts: list[OptionContract] = []
    total_contracts: int = 0


class ExpirationDate(BaseModel):
    """Available expiration date"""

    date: str
    days_to_expiry: int


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get(
    "/chain/{symbol}",
    response_model=OptionsChainResponse,
    dependencies=[Depends(require_bearer)],
)
async def get_options_chain(
    symbol: str,
    expiration: str | None = Query(
        None,
        description="Expiration date (YYYY-MM-DD). If not provided, uses nearest expiration.",
    ),
):
    """
    Get options chain for a symbol with Greeks

    Returns calls and puts for the specified expiration date with Greeks calculated.
    Uses Tradier API for real-time options data including delta, gamma, theta, vega.
    Supports fixture mode for deterministic testing when USE_TEST_FIXTURES=true.

    Args:
        symbol: Stock symbol (e.g., SPY, AAPL)
        expiration: Expiration date in YYYY-MM-DD format

    Returns:
        OptionsChainResponse with calls and puts including Greeks
    """
    logger.info(
        f"========== OPTIONS CHAIN ENDPOINT: symbol={symbol}, expiration={expiration} =========="
    )

    try:
        # Check if we should use test fixtures
        from ..core.config import settings

        if settings.USE_TEST_FIXTURES:
            logger.info("Using test fixtures for deterministic testing")
            from ..services.fixture_loader import get_fixture_loader

            fixture_loader = get_fixture_loader()
            chain_data = fixture_loader.load_options_chain(symbol)

            if not chain_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"No fixture data available for symbol {symbol}",
                )

            # Find the requested expiration or use the first one
            expirations = chain_data.get("expiration_dates", [])
            if not expirations:
                raise HTTPException(
                    status_code=404,
                    detail=f"No expiration dates in fixture for {symbol}",
                )

            # Use requested expiration or first available
            target_expiration = expiration or expirations[0]["date"]
            exp_data = next(
                (exp for exp in expirations if exp["date"] == target_expiration),
                expirations[0],
            )

            # Build response from fixture data
            calls = [OptionContract(**call) for call in exp_data.get("calls", [])]
            puts = [OptionContract(**put) for put in exp_data.get("puts", [])]

            return OptionsChainResponse(
                symbol=symbol,
                expiration_date=exp_data["date"],
                underlying_price=chain_data.get("underlying_price"),
                calls=calls,
                puts=puts,
                total_contracts=len(calls) + len(puts),
            )

        # Initialize Tradier client for real API calls
        client = _get_tradier_client()

        # If no expiration provided, get the nearest one
        if not expiration:
            exp_data = await asyncio.to_thread(client.get_option_expirations, symbol)
            expirations = exp_data.get("expirations", {}).get("date", [])
            if not expirations:
                raise HTTPException(
                    status_code=404, detail=f"No expiration dates found for {symbol}"
                )
            expiration = (
                expirations[0] if isinstance(expirations, list) else expirations
            )

    # Check cache first (5-minute TTL)
    cache_key = f"options:{symbol}:{expiration}"
    chain_data = cache.get(cache_key)
    if chain_data:
        logger.info(f"✅ CACHE HIT: {cache_key}")
    else:
        logger.info(f"❌ CACHE MISS: {cache_key} - Fetching from Tradier API")
        chain_data = await asyncio.to_thread(client.get_option_chains, symbol, expiration)
        cache.set(cache_key, chain_data, ttl=300)
        logger.info(f"💾 CACHED: {cache_key} (TTL: 5 minutes)")

        # Parse Tradier response
        # Log response for debugging
        logger.info(
            f"Tradier response keys: {list(chain_data.keys()) if chain_data else 'None'}"
        )

        if not chain_data:
            raise HTTPException(
                status_code=500, detail="Empty response from Tradier API"
            )

        options_data = chain_data.get("options", {})
        if not options_data:
            # Check alternative response structure
            if "option" in chain_data:
                options_data = chain_data

        option_list = options_data.get("option", [])

        if not option_list:
            return OptionsChainResponse(
                symbol=symbol,
                expiration_date=expiration,
                calls=[],
                puts=[],
                total_contracts=0,
            )

        # Separate calls and puts, parse Greeks
        calls = []
        puts = []

        for opt in option_list:
            greeks = opt.get("greeks", {})

            contract = OptionContract(
                symbol=opt.get("symbol", ""),
                underlying_symbol=symbol,
                option_type=opt.get("option_type", ""),
                strike_price=float(opt.get("strike", 0)),
                expiration_date=opt.get("expiration_date", expiration),
                bid=opt.get("bid"),
                ask=opt.get("ask"),
                last_price=opt.get("last"),
                volume=opt.get("volume"),
                open_interest=opt.get("open_interest"),
                delta=greeks.get("delta"),
                gamma=greeks.get("gamma"),
                theta=greeks.get("theta"),
                vega=greeks.get("vega"),
                rho=greeks.get("rho"),
                implied_volatility=greeks.get("mid_iv"),
            )

            if opt.get("option_type") == "call":
                calls.append(contract)
            else:
                puts.append(contract)

        return OptionsChainResponse(
            symbol=symbol,
            expiration_date=expiration,
            underlying_price=None,  # Could fetch from separate quote endpoint
            calls=calls,
            puts=puts,
            total_contracts=len(calls) + len(puts),
        )

    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code, detail=f"Tradier API error: {e!s}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching options chain: {e!s}"
        )


@router.get("/expirations/{symbol}", response_model=list[ExpirationDate])
def get_expiration_dates(symbol: str, authorization: str = Depends(require_bearer)):
    """
    Get available expiration dates for a symbol

    Returns list of available option expiration dates with days until expiry.
    Uses Tradier API for real-time expiration data.
    Supports fixture mode for deterministic testing when USE_TEST_FIXTURES=true.
    """
    try:
        # Check if we should use test fixtures
        from ..core.config import settings

        if settings.USE_TEST_FIXTURES:
            logger.info("Using test fixtures for expiration dates")
            from ..services.fixture_loader import get_fixture_loader

            fixture_loader = get_fixture_loader()
            chain_data = fixture_loader.load_options_chain(symbol)

            if not chain_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"No fixture data available for symbol {symbol}",
                )

            # Return fixture expiration dates
            expirations = chain_data.get("expiration_dates", [])
            if not expirations:
                return []

            expiration_dates = []
            for exp_date in expirations:
                # Calculate days to expiry
                exp_datetime = datetime.strptime(exp_date, "%Y-%m-%d")
                days_to_expiry = (exp_datetime - datetime.now()).days

                expiration_dates.append(
                    ExpirationDate(date=exp_date, days_to_expiry=max(0, days_to_expiry))
                )

            return expiration_dates

        # Get Tradier client instance
        client = _get_tradier_client()

        # Fetch expiration dates from Tradier
        exp_data = client.get_option_expirations(symbol)

        expirations = exp_data.get("expirations", {}).get("date", [])
        if not expirations:
            return []

        # Ensure expirations is a list
        if not isinstance(expirations, list):
            expirations = [expirations]

        # Calculate days to expiry for each
        result = []
        today = datetime.now().date()

        for exp_date_str in expirations:
            exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
            days_to_expiry = (exp_date - today).days

            result.append(
                ExpirationDate(date=exp_date_str, days_to_expiry=days_to_expiry)
            )

        return result

    except requests.exceptions.HTTPError as e:
        logger.error(f"Tradier HTTP error: {e}")
        raise HTTPException(
            status_code=e.response.status_code, detail=f"Tradier API error: {e!s}"
        )
    except Exception as e:
        logger.error(f"Error fetching expirations: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching expirations: {e!s}"
        )


@router.post("/greeks", dependencies=[Depends(require_bearer)])
async def calculate_greeks(
    symbol: str = Query(..., description="Option symbol"),
    underlying_price: float = Query(
        ..., description="Current price of underlying asset"
    ),
    strike: float = Query(..., description="Strike price"),
    expiration: str = Query(..., description="Expiration date (YYYY-MM-DD)"),
    option_type: str = Query(..., description="call or put"),
):
    """
    Calculate Greeks for a specific option contract

    Returns delta, gamma, theta, vega, and rho for the given option parameters.
    Uses Black-Scholes model for calculation.

    **PHASE 1 IMPLEMENTATION:**
    Greeks calculator already implemented in app.services.greeks.GreeksCalculator
    This endpoint will integrate it with options chain data from Alpaca.
    """
    # PHASE 1: Integrate GreeksCalculator with Alpaca options data
    # Implementation plan:
    #   1. Fetch option contract details from Alpaca API
    #   2. Calculate Greeks using existing GreeksCalculator
    #   3. Return combined data (pricing + Greeks)
    raise HTTPException(
        status_code=501,
        detail="Greeks calculation endpoint not yet implemented - Phase 1 scaffold",
    )


@router.get(
    "/contract/{option_symbol}",
    response_model=OptionContract,
    dependencies=[Depends(require_bearer)],
)
async def get_option_contract(option_symbol: str):
    """
    Get details for a specific option contract

    Returns contract details including current pricing and Greeks.

    **PHASE 1 IMPLEMENTATION:** Alpaca Options API integration
    """
    # PHASE 1: Alpaca options contract lookup
    # Implementation plan:
    #   1. Parse option_symbol (e.g., "AAPL250117C00150000")
    #   2. Fetch contract from Alpaca: GET /v2/options/contracts/{option_symbol}
    #   3. Calculate Greeks using GreeksCalculator
    #   4. Return OptionContract model with all data

    raise HTTPException(
        status_code=501,
        detail="Contract details endpoint not yet implemented - Phase 1 scaffold",
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
# Removed stub functions that violated architecture:
# - fetch_options_chain_from_alpaca (use Tradier only)
# - calculate_greeks_for_contracts (already handled by greeks.py service)
