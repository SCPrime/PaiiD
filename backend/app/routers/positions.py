"""
Position Management API
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.core.auth import require_bearer
from app.services.position_tracker import (
    PositionTrackerService,
    Position,
    PortfolioGreeks
)

router = APIRouter(prefix="/api/positions", tags=["positions"])


@router.get("", response_model=List[Position], dependencies=[Depends(require_bearer)])
async def get_positions():
    """Get all open positions with real-time P&L and Greeks"""
    service = PositionTrackerService()
    return await service.get_open_positions()


@router.get("/greeks", response_model=PortfolioGreeks, dependencies=[Depends(require_bearer)])
async def get_portfolio_greeks():
    """Get aggregate portfolio Greeks"""
    service = PositionTrackerService()
    return await service.get_portfolio_greeks()


@router.post("/{position_id}/close", dependencies=[Depends(require_bearer)])
async def close_position(position_id: str, limit_price: Optional[float] = None):
    """Close an open position"""
    service = PositionTrackerService()
    return await service.close_position(position_id, limit_price)
