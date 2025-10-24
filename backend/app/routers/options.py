"""
Options Trading Router

Provides endpoints for options chain data, Greeks calculation, and multi-leg options strategies.
Integrates with Tradier API for real-time options data with Greeks.

Phase 1 Implementation:
- Options chain fetching with Greeks (Tradier API)
- Real-time market data
- Multi-leg order support
"""

from datetime import datetime
from typing import Any, List, Optional
import requests
import asyncio
import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..core.config import settings
from ..core.auth import require_bearer
from ..services.options_greeks import calculate_option_greeks
from ..services.tradier_client import get_tradier_client

router = APIRouter(prefix="/options", tags=["options"])
logger = logging.getLogger(__name__)

# 5-minute cache for options chain data
# maxsize=100 allows caching up to 100 different symbol+expiration combinations
CACHE_TTL_SECONDS = 300
options_cache: dict[str, tuple[float, dict[str, Any]]] = {}


# ============================================================================
# TRADIER CLIENT HELPER
# ============================================================================

def _get_tradier_client():
    """Get Tradier client instance"""
    return get_tradier_client()


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> Optional[int]:
    try:
        if value is None or value == "":
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _normalize_expirations(data: dict) -> List[str]:
    expirations = data.get("expirations", {}).get("date", [])
    if isinstance(expirations, list):
        return [str(exp) for exp in expirations]
    if expirations:
        return [str(expirations)]
    return []


def _extract_underlying_price(chain_data: dict, quote: Optional[dict]) -> Optional[float]:
    candidates = [
        chain_data.get("underlying_price"),
        chain_data.get("underlying", {}).get("last"),
        chain_data.get("underlying", {}).get("close"),
        (quote or {}).get("last"),
        (quote or {}).get("close"),
    ]
    for candidate in candidates:
        value = _safe_float(candidate)
        if value is not None:
            return value
    return None


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
    bid: Optional[float] = Field(None, description="Current bid price")
    ask: Optional[float] = Field(None, description="Current ask price")
    last_price: Optional[float] = Field(None, description="Last traded price")
    volume: Optional[int] = Field(None, description="Trading volume")
    open_interest: Optional[int] = Field(None, description="Open interest")

    # Greeks (populated by greeks service)
    delta: Optional[float] = Field(None, description="Delta (sensitivity to price)")
    gamma: Optional[float] = Field(None, description="Gamma (rate of delta change)")
    theta: Optional[float] = Field(None, description="Theta (time decay)")
    vega: Optional[float] = Field(None, description="Vega (sensitivity to volatility)")
    rho: Optional[float] = Field(None, description="Rho (sensitivity to interest rates)")

    # Implied volatility
    implied_volatility: Optional[float] = Field(None, description="Implied volatility")


class OptionsChainResponse(BaseModel):
    """Options chain for a symbol and expiration"""

    symbol: str
    expiration_date: str
    underlying_price: Optional[float] = None
    calls: List[OptionContract] = Field(default_factory=list)
    puts: List[OptionContract] = Field(default_factory=list)
    strikes: List[float] = Field(default_factory=list, description="Sorted list of strikes")
    total_contracts: int = 0


class ExpirationDate(BaseModel):
    """Available expiration date"""

    date: str
    days_to_expiry: int


# ============================================================================
# ENDPOINTS
# ============================================================================


async def _build_options_chain_response(symbol: str, expiration: Optional[str]) -> OptionsChainResponse:
    normalized_symbol = symbol.upper()
    client = _get_tradier_client()

    try:
        expiry = expiration
        if not expiry:
            exp_data = await asyncio.to_thread(client.get_option_expirations, normalized_symbol)
            expirations = _normalize_expirations(exp_data)
            if not expirations:
                raise HTTPException(status_code=404, detail=f"No expiration dates found for {normalized_symbol}")
            expiry = expirations[0]

        cache_key = f"options_{normalized_symbol}_{expiry}"
        cached_entry = options_cache.get(cache_key)
        now = time.time()
        if cached_entry:
            cached_timestamp, cached_payload = cached_entry
            if now - cached_timestamp < CACHE_TTL_SECONDS:
                logger.info("[Options] Cache hit for %s", cache_key)
                return OptionsChainResponse.model_validate(cached_payload)
            options_cache.pop(cache_key, None)

        logger.info("[Options] Cache miss for %s - fetching from Tradier", cache_key)
        quote_task = asyncio.to_thread(client.get_quote, normalized_symbol)
        chain_task = asyncio.to_thread(client.get_option_chains, normalized_symbol, expiry)
        quote_data, chain_data = await asyncio.gather(quote_task, chain_task)

        if not chain_data:
            raise HTTPException(status_code=502, detail="Empty response from Tradier API")

        options_section = chain_data.get("options", {})
        if not options_section and "option" in chain_data:
            options_section = chain_data

        option_list = options_section.get("option", [])
        if isinstance(option_list, dict):
            option_list = [option_list]

        calls: List[OptionContract] = []
        puts: List[OptionContract] = []

        for raw_contract in option_list:
            strike = _safe_float(raw_contract.get("strike"))
            if strike is None:
                continue

            greeks = raw_contract.get("greeks", {})
            option_type = (raw_contract.get("option_type") or "").lower()

            contract = OptionContract(
                symbol=raw_contract.get("symbol", ""),
                underlying_symbol=normalized_symbol,
                option_type=option_type or "call",
                strike_price=strike,
                expiration_date=raw_contract.get("expiration_date", expiry),
                bid=_safe_float(raw_contract.get("bid")),
                ask=_safe_float(raw_contract.get("ask")),
                last_price=_safe_float(raw_contract.get("last")),
                volume=_safe_int(raw_contract.get("volume")),
                open_interest=_safe_int(raw_contract.get("open_interest")),
                delta=_safe_float(greeks.get("delta")),
                gamma=_safe_float(greeks.get("gamma")),
                theta=_safe_float(greeks.get("theta")),
                vega=_safe_float(greeks.get("vega")),
                rho=_safe_float(greeks.get("rho")),
                implied_volatility=_safe_float(greeks.get("mid_iv")),
            )

            if option_type == "put":
                puts.append(contract)
            else:
                calls.append(contract)

        calls.sort(key=lambda contract: contract.strike_price)
        puts.sort(key=lambda contract: contract.strike_price)
        strikes = sorted({contract.strike_price for contract in (*calls, *puts)})

        underlying_price = _extract_underlying_price(chain_data, quote_data)

        response = OptionsChainResponse(
            symbol=normalized_symbol,
            expiration_date=expiry,
            underlying_price=underlying_price,
            calls=calls,
            puts=puts,
            strikes=strikes,
            total_contracts=len(calls) + len(puts),
        )

        options_cache[cache_key] = (time.time(), response.model_dump())
        return response

    except HTTPException:
        raise
    except requests.exceptions.HTTPError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Tradier API error: {exc.response.text}",
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to build options chain for %s (%s)", symbol, expiration)
        raise HTTPException(status_code=500, detail=f"Error fetching options chain: {exc}") from exc


@router.get(
    "/chain/{symbol}",
    response_model=OptionsChainResponse,
    dependencies=[Depends(require_bearer)],
)
@router.get(
    "/chains/{symbol}",
    response_model=OptionsChainResponse,
    dependencies=[Depends(require_bearer)],
)
async def get_options_chain(
    symbol: str,
    expiration: Optional[str] = Query(
        None, description="Expiration date (YYYY-MM-DD). If omitted, uses the nearest expiration."
    ),
):
    return await _build_options_chain_response(symbol, expiration)


@router.get(
    "/chain",
    response_model=OptionsChainResponse,
    dependencies=[Depends(require_bearer)],
)
async def get_options_chain_by_query(
    symbol: str = Query(..., description="Underlying symbol (e.g., SPY)"),
    expiration: Optional[str] = Query(
        None, description="Expiration date (YYYY-MM-DD). If omitted, uses the nearest expiration."
    ),
):
    return await _build_options_chain_response(symbol, expiration)


@router.get("/expirations/{symbol}", response_model=List[ExpirationDate])
async def get_expiration_dates(symbol: str, authorization: str = Depends(require_bearer)):
    """
    Get available expiration dates for a symbol

    Returns list of available option expiration dates with days until expiry.
    Uses Tradier API for real-time expiration data.
    """
    try:
        client = _get_tradier_client()
        exp_data = await asyncio.to_thread(client.get_option_expirations, symbol.upper())

        expiration_list = _normalize_expirations(exp_data)
        if not expiration_list:
            return []

        today = datetime.utcnow().date()
        response: List[ExpirationDate] = []

        for exp_date_str in expiration_list:
            try:
                exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
            except ValueError:
                logger.warning("[Options] Skipping invalid expiration date: %s", exp_date_str)
                continue

            days_to_expiry = max((exp_date - today).days, 0)
            response.append(ExpirationDate(date=exp_date_str, days_to_expiry=days_to_expiry))

        return response

    except requests.exceptions.HTTPError as e:
        logger.error(f"Tradier HTTP error: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Tradier API error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error fetching expirations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching expirations: {str(e)}"
        )


@router.get("/greeks", dependencies=[Depends(require_bearer)])
async def calculate_greeks(
    symbol: str = Query(..., description="Underlying symbol (e.g., SPY)"),
    strike: float = Query(..., description="Strike price"),
    expiration: str = Query(..., description="Expiration date (YYYY-MM-DD)"),
    option_type: str = Query(..., description="call or put"),
):
    """Calculate Greeks and theoretical pricing for a specific option contract."""

    normalized_type = option_type.lower()
    if normalized_type not in {"call", "put"}:
        raise HTTPException(status_code=400, detail="option_type must be 'call' or 'put'")

    chain = await _build_options_chain_response(symbol, expiration)
    target_contracts = chain.calls if normalized_type == "call" else chain.puts
    strike_value = float(strike)

    contract = next(
        (c for c in target_contracts if abs(c.strike_price - strike_value) < 1e-6),
        None,
    )

    if contract is None:
        raise HTTPException(status_code=404, detail="Option contract not found in current chain")

    underlying_price = chain.underlying_price
    if underlying_price is None:
        client = _get_tradier_client()
        quote = await asyncio.to_thread(client.get_quote, symbol.upper())
        underlying_price = _safe_float(quote.get("last")) or _safe_float(quote.get("close"))
        if underlying_price is None:
            raise HTTPException(status_code=502, detail="Unable to determine underlying price")

    try:
        expiry_date = datetime.strptime(expiration, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid expiration format") from exc

    implied_vol = contract.implied_volatility or 0.25
    greeks = calculate_option_greeks(
        spot_price=underlying_price,
        strike_price=strike_value,
        expiry_date=expiry_date,
        volatility=implied_vol,
        option_type=normalized_type,
    )

    market_price = contract.last_price
    if market_price is None and contract.bid is not None and contract.ask is not None:
        market_price = round((contract.bid + contract.ask) / 2, 2)

    response = {
        "symbol": contract.symbol or symbol.upper(),
        "strike": strike_value,
        "expiry": expiration,
        "option_type": normalized_type,
        "delta": greeks.delta,
        "gamma": greeks.gamma,
        "theta": greeks.theta,
        "vega": greeks.vega,
        "rho": greeks.rho,
        "theoretical_price": greeks.theoretical_price,
        "intrinsic_value": greeks.intrinsic_value,
        "extrinsic_value": greeks.extrinsic_value,
        "probability_itm": greeks.probability_itm,
        "market_price": market_price,
        "implied_volatility": implied_vol,
        "volume": contract.volume,
        "open_interest": contract.open_interest,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "tradier",
    }

    return response


@router.get("/contract/{option_symbol}", response_model=OptionContract, dependencies=[Depends(require_bearer)])
async def get_option_contract(option_symbol: str):
    """
    Get details for a specific option contract

    Returns contract details including current pricing and Greeks.

    **TODO:** Implement Alpaca API integration
    """
    # TODO: Fetch single contract from Alpaca
    # TODO: Calculate Greeks

    raise HTTPException(status_code=501, detail="Contract details endpoint not yet implemented - Phase 1 scaffold")


# ============================================================================
# HELPER FUNCTIONS (to be implemented)
# ============================================================================


async def fetch_options_chain_from_alpaca(symbol: str, expiration: Optional[str] = None) -> dict:
    """
    Fetch options chain from Alpaca API

    **TODO:** Implement Alpaca options API call
    """
    pass


async def calculate_greeks_for_contracts(contracts: List[dict], underlying_price: float) -> List[OptionContract]:
    """
    Calculate Greeks for option contracts

    **TODO:** Integrate with greeks.py service
    """
    pass
