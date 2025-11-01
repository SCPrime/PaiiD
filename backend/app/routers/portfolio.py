import logging
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core.unified_auth import get_current_user_unified
from ..models.database import User
from ..services.cache import CacheService, get_cache
from ..services.tradier_client import get_tradier_client


logger = logging.getLogger(__name__)

router = APIRouter()


class AlpacaAccount(BaseModel):
    """Alpaca account information"""

    id: str
    account_number: str
    status: Literal["ACTIVE", "INACTIVE"]
    currency: str = "USD"
    buying_power: str
    cash: str
    portfolio_value: str
    equity: str
    last_equity: str
    long_market_value: str
    short_market_value: str
    initial_margin: str
    maintenance_margin: str
    last_maintenance_margin: str
    daytrade_count: int
    daytrading_buying_power: str | None = None
    pattern_day_trader: bool = False
    trading_blocked: bool = False
    transfers_blocked: bool = False
    account_blocked: bool = False
    created_at: str
    trade_suspended_by_user: bool = False
    multiplier: str
    shorting_enabled: bool = True
    long_market_value_change: str | None = None
    short_market_value_change: str | None = None


@router.get("/account")
def get_account(current_user: User = Depends(get_current_user_unified)):
    """Get Tradier account information"""
    try:
        client = get_tradier_client()
        account_data = client.get_account()

        logger.info("Tradier account data retrieved successfully")
        return {
            "data": account_data,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.error("Tradier account request failed", exc_info=e)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch Tradier account: {e!s}"
        ) from e


@router.get("/positions")
def get_positions(
    current_user: User = Depends(get_current_user_unified),
    cache: CacheService = Depends(get_cache),
):
    """Get Tradier positions (cached for 30s)"""
    # Check cache first
    cache_key = "portfolio:positions"
    try:
        cached_positions = cache.get(cache_key)
    except Exception as e:
        logger.warning("Portfolio positions cache read failed", exc_info=e)
        cached_positions = None

    if cached_positions is not None:
        logger.info("Cache hit for positions", extra={"cache_key": cache_key})
        return {
            "data": cached_positions,
            "count": len(cached_positions) if isinstance(cached_positions, list) else 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    try:
        client = get_tradier_client()
        positions = client.get_positions()
        logger.info(
            "Retrieved positions from Tradier",
            extra={"count": len(positions), "cache_key": cache_key},
        )

        # Cache for 30 seconds
        try:
            cache.set(cache_key, positions, ttl=30)
        except Exception as cache_exc:
            logger.warning(
                "Failed to cache positions",
                exc_info=cache_exc,
                extra={"cache_key": cache_key},
            )
        return {
            "data": positions,
            "count": len(positions),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.error("Tradier positions request failed", exc_info=e)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch Tradier positions: {e!s}"
        ) from e


@router.get("/positions/{symbol}")
def get_position(symbol: str, current_user: User = Depends(get_current_user_unified)):
    """Get a specific position by symbol"""
    try:
        client = get_tradier_client()
        positions = client.get_positions()

        # Find position by symbol
        for position in positions:
            if position.get("symbol") == symbol.upper():
                return {
                    "data": position,
                    "timestamp": datetime.now(UTC).isoformat(),
                }

        raise HTTPException(status_code=404, detail=f"No position found for {symbol}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to fetch position",
            exc_info=e,
            extra={"symbol": symbol.upper()},
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch position for {symbol}: {e!s}"
        ) from e
