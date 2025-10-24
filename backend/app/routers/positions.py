"""
Position Management API
"""

from fastapi import APIRouter, Depends

from app.core.jwt import get_current_user
from app.services.position_tracker import (
    PortfolioGreeks,
    Position,
    PositionTrackerService,
)


router = APIRouter(prefix="/api/positions", tags=["positions"])


@router.get("", response_model=list[Position], dependencies=[Depends(get_current_user)])
async def get_positions():
    """Get all open positions with real-time P&L and Greeks"""
    service = PositionTrackerService()
    return await service.get_open_positions()


@router.get(
    "/greeks", response_model=PortfolioGreeks, dependencies=[Depends(get_current_user)]
)
async def get_portfolio_greeks():
    """Get aggregate portfolio Greeks"""
    service = PositionTrackerService()
    return await service.get_portfolio_greeks()


@router.post("/{position_id}/close", dependencies=[Depends(get_current_user)])
async def close_position(position_id: str, limit_price: float | None = None):
    """Close an open position"""
    service = PositionTrackerService()
    return await service.close_position(position_id, limit_price)
