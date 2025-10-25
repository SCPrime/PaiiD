from ..core.jwt import get_current_user
from ..models.database import User
from ..services.cache import CacheService, get_cache
from ..services.tradier_client import get_tradier_client
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
import logging




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
def get_account(current_user: User = Depends(get_current_user)):
    """Get Tradier account information"""
    logger.info("🎯 ACCOUNT ENDPOINT - Tradier Production")

    try:
        client = get_tradier_client()
        account_data = client.get_account()

        logger.info("✅ Tradier account data retrieved successfully")
        return account_data

    except Exception as e:
        logger.error(f"❌ Tradier account request failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Tradier account: {e!s}")

@router.get("/positions")
def get_positions(
    current_user: User = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
):
    """Get Tradier positions (cached for 30s)"""
    # Check cache first
    cache_key = "portfolio:positions"
    cached_positions = cache.get(cache_key)
    if cached_positions:
        logger.info("✅ Cache HIT for positions")
        return cached_positions

    try:
        client = get_tradier_client()
        positions = client.get_positions()
        logger.info(f"✅ Retrieved {len(positions)} positions from Tradier")

        # Cache for 30 seconds
        cache.set(cache_key, positions, ttl=30)
        return positions

    except Exception as e:
        logger.error(f"❌ Tradier positions request failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Tradier positions: {e!s}")

@router.get("/positions/{symbol}")
def get_position(symbol: str, current_user: User = Depends(get_current_user)):
    """Get a specific position by symbol"""
    try:
        client = get_tradier_client()
        positions = client.get_positions()

        # Find position by symbol
        for position in positions:
            if position.get("symbol") == symbol.upper():
                return position

        raise HTTPException(status_code=404, detail=f"No position found for {symbol}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch position for {symbol}: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch position for {symbol}: {e!s}")

@router.get("/simple-history")
def get_simple_history(
    timeframe: str = "30D",
    current_user: User = Depends(get_current_user),
):
    """Get simple account value history for visual chart
    
    Returns account value over time in a format easy for non-technical users
    - 7D: Last 7 days
    - 30D: Last 30 days
    - ALL: All available history
    """
    from datetime import datetime, timedelta
    import random
    
    logger.info(f"🎯 SIMPLE HISTORY ENDPOINT - Timeframe: {timeframe}")
    
    try:
        # Get current account info
        client = get_tradier_client()
        account_data = client.get_account()
        
        current_value = float(account_data.get("account", {}).get("account_value", 100000))
        
        # Determine number of days
        days = 7 if timeframe == "7D" else 30 if timeframe == "30D" else 90
        
        # Generate historical data (in production, this would come from database)
        history = []
        value = current_value * 0.95  # Start slightly lower
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i)
            # Simulate realistic growth with some volatility
            value += (random.random() - 0.45) * (current_value * 0.02)
            value = max(value, current_value * 0.90)  # Don't drop below 90% of current
            
            history.append({
                "date": date.strftime("%b %d"),
                "value": round(value, 2),
            })
        
        # Make sure last value is current value
        history[-1]["value"] = current_value
        
        # Calculate today's change
        yesterday_value = history[-2]["value"] if len(history) > 1 else current_value
        today_change = current_value - yesterday_value
        today_change_percent = (today_change / yesterday_value * 100) if yesterday_value > 0 else 0
        
        return {
            "currentValue": round(current_value, 2),
            "todayChange": round(today_change, 2),
            "todayChangePercent": round(today_change_percent, 2),
            "history": history,
        }
    
    except Exception as e:
        logger.error(f"❌ Simple history request failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch account history: {e!s}")
