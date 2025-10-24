"""
Position Management API
"""

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, require_current_user
from app.services.position_tracker import (
    PortfolioGreeks,
    Position,
    PositionTrackerService,
)


router = APIRouter(
    prefix="/api/positions",
    tags=["positions"],
    dependencies=[Depends(require_current_user)],
)


@router.get("", response_model=list[Position])
async def get_positions(_current_user: CurrentUser):
    """Get all open positions with real-time P&L and Greeks"""
    service = PositionTrackerService()
    return await service.get_open_positions()


@router.get("/greeks", response_model=PortfolioGreeks)
async def get_portfolio_greeks(_current_user: CurrentUser):
    """Get aggregate portfolio Greeks"""
    service = PositionTrackerService()
    return await service.get_portfolio_greeks()


@router.post("/{position_id}/close")
async def close_position(
    position_id: str,
    _current_user: CurrentUser,
    limit_price: float | None = None,
):
    """Close an open position"""
    service = PositionTrackerService()
    return await service.close_position(position_id, limit_price)
