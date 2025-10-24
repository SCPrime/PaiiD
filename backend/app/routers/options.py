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
from typing import List, Optional, Literal
import time
import requests
import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, PositiveInt, confloat

from ..core.config import settings
from ..core.auth import require_bearer
from ..services.tradier_client import get_tradier_client

router = APIRouter(prefix="/options", tags=["options"])
logger = logging.getLogger(__name__)


class _TTLCache:
    """Lightweight TTL cache replacement to avoid external dependency."""

    def __init__(self, maxsize: int, ttl: int):
        self.maxsize = maxsize
        self.ttl = ttl
        self._store: dict[str, tuple[float, dict]] = {}

    def _evict_expired(self):
        now = time.time()
        keys_to_delete = [key for key, (created_at, _) in self._store.items() if now - created_at > self.ttl]
        for key in keys_to_delete:
            del self._store[key]

    def __contains__(self, key: str) -> bool:
        self._evict_expired()
        return key in self._store

    def __getitem__(self, key: str):
        self._evict_expired()
        value = self._store[key][1]
        return value

    def __setitem__(self, key: str, value: dict):
        self._evict_expired()
        if key not in self._store and len(self._store) >= self.maxsize:
            oldest_key = min(self._store.items(), key=lambda item: item[1][0])[0]
            del self._store[oldest_key]
        self._store[key] = (time.time(), value)


# 5-minute cache for options chain data
options_cache = _TTLCache(maxsize=100, ttl=300)


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


class GreeksExposure(BaseModel):
    """Aggregated Greeks exposure values."""

    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    rho: float = 0.0


class ChainGreeksExposure(BaseModel):
    """Call, put, and net exposure snapshot."""

    calls: GreeksExposure
    puts: GreeksExposure
    net: GreeksExposure


class OptionsChainResponse(BaseModel):
    """Options chain for a symbol and expiration"""

    symbol: str
    expiration_date: str
    underlying_price: Optional[float] = None
    calls: List[OptionContract] = []
    puts: List[OptionContract] = []
    total_contracts: int = 0
    greeks_exposure: ChainGreeksExposure
    as_of: Optional[str] = None


class OptionOrderLeg(BaseModel):
    """Single option leg definition."""

    option_symbol: str = Field(..., description="Full OCC option symbol")
    side: str = Field(..., description="buy_to_open, sell_to_close, etc.")
    quantity: PositiveInt = Field(..., description="Number of contracts")


class OptionOrderRequest(BaseModel):
    """Payload for placing an options order."""

    symbol: str = Field(..., description="Underlying symbol")
    option_symbol: Optional[str] = Field(None, description="Single-leg OCC option symbol")
    side: Optional[str] = Field(
        None,
        description="Order side when using single leg",
        pattern=r"^(buy|sell|buy_to_open|buy_to_close|sell_to_open|sell_to_close)$",
    )
    quantity: Optional[PositiveInt] = Field(None, description="Contracts for single-leg order")
    order_type: Literal["market", "limit", "stop", "stop_limit"] = "market"
    duration: Literal["day", "gtc", "pre", "post", "gtc_pre", "gtc_post"] = "day"
    price: Optional[confloat(gt=0)] = Field(None, description="Limit price if applicable")
    stop: Optional[confloat(gt=0)] = Field(None, description="Stop price if applicable")
    preview: bool = Field(False, description="If true, preview without execution")
    legs: Optional[List[OptionOrderLeg]] = Field(
        None,
        description="Multi-leg definition (currently limited to 1 leg execution)",
    )


class OptionOrderResponse(BaseModel):
    """Response payload for option order submission."""

    status: str
    order_id: Optional[str] = None
    message: Optional[str] = None
    raw_response: dict


class ExpirationDate(BaseModel):
    """Available expiration date"""

    date: str
    days_to_expiry: int


# ============================================================================
# ENDPOINTS
# ============================================================================



@router.get("/chains/{symbol}", response_model=OptionsChainResponse, dependencies=[Depends(require_bearer)])
async def get_options_chain(
    symbol: str,
    expiration: Optional[str] = Query(
        None,
        description="Expiration date (YYYY-MM-DD). If not provided, uses nearest expiration.",
    ),
    option_type: Literal["all", "call", "put"] = Query(
        "all",
        description="Filter results to calls, puts, or all",
    ),
    min_volume: Optional[int] = Query(
        None,
        ge=0,
        description="Filter out contracts below this daily volume",
    ),
    min_open_interest: Optional[int] = Query(
        None,
        ge=0,
        description="Filter out contracts below this open interest",
    ),
):
    """Return normalized options chain data enriched with Greeks exposure."""

    logger.info(
        "[Options] Chain request",
        extra={
            "symbol": symbol,
            "expiration": expiration,
            "option_type": option_type,
            "min_volume": min_volume,
            "min_open_interest": min_open_interest,
        },
    )

    try:
        client = _get_tradier_client()

        if not expiration:
            exp_data = await asyncio.to_thread(client.get_option_expirations, symbol)
            expirations = exp_data.get("expirations", {}).get("date", [])
            if not expirations:
                raise HTTPException(
                    status_code=404,
                    detail=f"No expiration dates found for {symbol}",
                )
            expiration = expirations[0] if isinstance(expirations, list) else expirations

        cache_key = f"options_{symbol}_{expiration}_{option_type}_{min_volume}_{min_open_interest}"

        if cache_key in options_cache:
            logger.info(f"✅ CACHE HIT: {cache_key}")
            chain_data = options_cache[cache_key]
        else:
            logger.info(f"❌ CACHE MISS: {cache_key} - Fetching from Tradier API")
            chain_data = await asyncio.to_thread(
                client.get_normalized_option_chain,
                symbol,
                expiration,
                option_type,
                None,
                min_volume,
                min_open_interest,
            )
            options_cache[cache_key] = chain_data
            logger.info(f"💾 CACHED: {cache_key} (TTL: 5 minutes)")

        if not chain_data:
            raise HTTPException(status_code=500, detail="Empty response from Tradier API")

        normalized_expiration = chain_data.get("expiration_date") or expiration or ""

        calls = [OptionContract(**contract) for contract in chain_data.get("calls", [])]
        puts = [OptionContract(**contract) for contract in chain_data.get("puts", [])]

        exposure_payload = chain_data.get("greeks_exposure", {})
        exposure = ChainGreeksExposure(
            calls=GreeksExposure(**(exposure_payload.get("calls") or {})),
            puts=GreeksExposure(**(exposure_payload.get("puts") or {})),
            net=GreeksExposure(**(exposure_payload.get("net") or {})),
        )

        return OptionsChainResponse(
            symbol=symbol,
            expiration_date=normalized_expiration,
            underlying_price=chain_data.get("underlying_price"),
            calls=calls,
            puts=puts,
            total_contracts=len(calls) + len(puts),
            greeks_exposure=exposure,
            as_of=chain_data.get("as_of"),
        )

    except requests.exceptions.HTTPError as e:
        logger.error("Tradier HTTP error while fetching chain", exc_info=True)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Tradier API error: {str(e)}",
        )
    except Exception as e:
        logger.exception("Unexpected error fetching options chain")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching options chain: {str(e)}",
        )
@router.get("/expirations/{symbol}", response_model=List[ExpirationDate])
def get_expiration_dates(symbol: str, authorization: str = Depends(require_bearer)):
    """
    Get available expiration dates for a symbol

    Returns list of available option expiration dates with days until expiry.
    Uses Tradier API for real-time expiration data.
    """
    try:
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

            result.append(ExpirationDate(
                date=exp_date_str,
                days_to_expiry=days_to_expiry
            ))

        return result

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


@router.post("/orders", response_model=OptionOrderResponse, dependencies=[Depends(require_bearer)])
async def place_option_order(request: OptionOrderRequest):
    """Place a validated option order via Tradier."""

    logger.info(
        "[Options] Order request",
        extra={
            "symbol": request.symbol,
            "option_symbol": request.option_symbol,
            "side": request.side,
            "quantity": request.quantity,
            "order_type": request.order_type,
            "duration": request.duration,
            "preview": request.preview,
            "legs": len(request.legs or []),
        },
    )

    if request.legs and len(request.legs) > 1:
        raise HTTPException(
            status_code=422,
            detail="Multi-leg option orders are not supported yet. Submit one leg at a time.",
        )

    if not request.option_symbol and not request.legs:
        raise HTTPException(
            status_code=422,
            detail="Provide option_symbol for single-leg orders or supply legs[] for custom payloads.",
        )

    if request.option_symbol and not all([request.side, request.quantity]):
        raise HTTPException(
            status_code=422,
            detail="side and quantity are required for single-leg orders.",
        )

    if request.order_type in {"limit", "stop_limit"} and request.price is None:
        raise HTTPException(status_code=422, detail="price is required for limit orders")

    if request.order_type in {"stop", "stop_limit"} and request.stop is None:
        raise HTTPException(status_code=422, detail="stop is required for stop orders")

    client = _get_tradier_client()

    try:
        if request.option_symbol:
            response = await asyncio.to_thread(
                client.place_option_order,
                request.symbol,
                request.option_symbol,
                request.side,  # type: ignore[arg-type]
                request.quantity,  # type: ignore[arg-type]
                request.order_type,
                request.duration,
                request.price,
                request.stop,
                request.preview,
            )
        else:
            # Currently unsupported multi-leg path
            leg = request.legs[0]
            response = await asyncio.to_thread(
                client.place_option_order,
                request.symbol,
                leg.option_symbol,
                leg.side,
                leg.quantity,
                request.order_type,
                request.duration,
                request.price,
                request.stop,
                request.preview,
            )

        order_id = response.get("order", {}).get("id") or response.get("id")
        status = response.get("order", {}).get("status") or response.get("status") or "submitted"

        return OptionOrderResponse(
            status=status,
            order_id=order_id,
            message="Preview order generated" if request.preview else "Order submitted",
            raw_response=response,
        )
    except ValueError as e:
        logger.warning("Validation error placing option order", exc_info=True)
        raise HTTPException(status_code=422, detail=str(e))
    except requests.exceptions.HTTPError as e:
        logger.error("Tradier HTTP error while placing order", exc_info=True)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Tradier API error: {str(e)}",
        )
    except Exception as e:
        logger.exception("Unexpected error placing option order")
        raise HTTPException(status_code=500, detail=f"Error placing option order: {str(e)}")


@router.post("/greeks", dependencies=[Depends(require_bearer)])
async def calculate_greeks(
    symbol: str = Query(..., description="Option symbol"),
    underlying_price: float = Query(..., description="Current price of underlying asset"),
    strike: float = Query(..., description="Strike price"),
    expiration: str = Query(..., description="Expiration date (YYYY-MM-DD)"),
    option_type: str = Query(..., description="call or put"),
):
    """
    Calculate Greeks for a specific option contract

    Returns delta, gamma, theta, vega, and rho for the given option parameters.
    Uses Black-Scholes model for calculation.

    **TODO:** Implement full Greeks calculation engine
    """
    # Placeholder implementation
    raise HTTPException(status_code=501, detail="Greeks calculation endpoint not yet implemented - Phase 1 scaffold")


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
