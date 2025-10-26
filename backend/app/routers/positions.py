"""
Position Management API
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from ..core.unified_auth import get_current_user_unified
from ..models.database import User
from ..services.position_tracker import (
    PortfolioGreeks,
    Position,
    PositionTrackerService,
)


router = APIRouter(prefix="/api/positions", tags=["positions"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[Position])
async def get_positions(current_user: User = Depends(get_current_user_unified)):
    """Get all open positions with real-time P&L and Greeks

    Supports fixture mode for deterministic testing when USE_TEST_FIXTURES=true.
    """
    # Check if we should use test fixtures
    from ..core.config import settings

    if settings.USE_TEST_FIXTURES:
        from ..services.fixture_loader import get_fixture_loader

        fixture_loader = get_fixture_loader()
        positions_data = fixture_loader.load_positions()

        # Convert fixture data to Position objects
        positions = []
        for pos_data in positions_data:
            position = Position(
                id=pos_data.get("id", ""),
                symbol=pos_data.get("symbol", ""),
                quantity=pos_data.get("quantity", 0),
                entry_price=pos_data.get("entry_price", 0.0),
                current_price=pos_data.get("current_price", 0.0),
                unrealized_pnl=pos_data.get("unrealized_pnl", 0.0),
                delta=pos_data.get("delta", 0.0),
                gamma=pos_data.get("gamma", 0.0),
                theta=pos_data.get("theta", 0.0),
                vega=pos_data.get("vega", 0.0),
                rho=pos_data.get("rho", 0.0),
                test_fixture=True,  # Mark as fixture data
            )
            positions.append(position)

        return {
            "data": [p.model_dump() for p in positions],
            "count": len(positions),
            "timestamp": datetime.now().isoformat(),
        }

    try:
        service = PositionTrackerService()
        positions = await service.get_open_positions()
        return {
            "data": [p.model_dump() if hasattr(p, "model_dump") else p for p in positions],
            "count": len(positions),
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get positions: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch positions") from e


@router.get("/greeks", response_model=PortfolioGreeks)
async def get_portfolio_greeks(current_user: User = Depends(get_current_user_unified)):
    """Get aggregate portfolio Greeks"""
    try:
        service = PositionTrackerService()
        greeks = await service.get_portfolio_greeks()
        return {
            "data": greeks.model_dump() if hasattr(greeks, "model_dump") else greeks,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get portfolio greeks: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio greeks") from e


@router.post("/{position_id}/close")
async def close_position(
    position_id: str,
    limit_price: float | None = None,
    current_user: User = Depends(get_current_user_unified),
):
    """Close an open position"""
    try:
        service = PositionTrackerService()
        result = await service.close_position(position_id, limit_price)
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to close position {position_id}: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to close position") from e
