import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core.auth import CurrentUser, require_current_user
from ..services.cache import CacheService, get_cache
from ..services.tradier_client import get_tradier_client


logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_current_user)])


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
def get_account(current_user: CurrentUser):
    """Get Tradier account information"""
    logger.info("🎯 ACCOUNT ENDPOINT - Tradier Production")

    try:
        client = get_tradier_client()
        account_data = client.get_account()

        logger.info("✅ Tradier account data retrieved successfully")
        return {**account_data, "source": "tradier", "user_id": current_user.id}

    except Exception as e:
        logger.error(f"❌ Tradier account request failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Tradier account: {e!s}")


@router.get("/positions")
def get_positions(
    current_user: CurrentUser, cache: CacheService = Depends(get_cache)
):
    """Get Tradier positions (cached for 30s)"""
    # Check cache first
    cache_key = "portfolio:positions"
    cached_positions = cache.get(cache_key)
    if cached_positions:
        logger.info("✅ Cache HIT for positions")
        if isinstance(cached_positions, dict):
            cached_positions.setdefault("source", "cache")
            cached_positions.setdefault("user_id", current_user.id)
            return cached_positions
        return {"positions": cached_positions, "source": "cache", "user_id": current_user.id}

    try:
        client = get_tradier_client()
        positions = client.get_positions()
        logger.info(f"✅ Retrieved {len(positions)} positions from Tradier")

        # Cache for 30 seconds
        payload = {"positions": positions, "source": "tradier", "user_id": current_user.id}
        cache.set(cache_key, payload, ttl=30)
        return payload

    except Exception as e:
        logger.error(f"❌ Tradier positions request failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Tradier positions: {e!s}")


@router.get("/positions/{symbol}")
def get_position(symbol: str, current_user: CurrentUser):
    """Get a specific position by symbol"""
    try:
        client = get_tradier_client()
        positions = client.get_positions()

        # Find position by symbol
        for position in positions:
            if position.get("symbol") == symbol.upper():
                return {"position": position, "source": "tradier", "user_id": current_user.id}

        raise HTTPException(status_code=404, detail=f"No position found for {symbol}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch position for {symbol}: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch position for {symbol}: {e!s}")
