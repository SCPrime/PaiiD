"""Position Management API"""

import logging

from fastapi import APIRouter, Depends

from app.core.jwt import get_current_user
from app.models.database import User
from app.routers.error_utils import log_and_sanitize_exceptions
from app.services.position_tracker import (
    PortfolioGreeks,
    Position,
    PositionTrackerService,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/positions", tags=["positions"])


@router.get("", response_model=list[Position])
@log_and_sanitize_exceptions(
    logger,
    public_message="Failed to retrieve positions",
    log_message="Unable to load open positions",
)
async def get_positions(_current_user: User = Depends(get_current_user)) -> list[Position]:
    """Get all open positions with real-time P&L and Greeks"""
    service = PositionTrackerService()
    return await service.get_open_positions()


@router.get("/greeks", response_model=PortfolioGreeks)
@log_and_sanitize_exceptions(
    logger,
    public_message="Failed to retrieve portfolio Greeks",
    log_message="Unable to aggregate portfolio Greeks",
)
async def get_portfolio_greeks(
    _current_user: User = Depends(get_current_user),
) -> PortfolioGreeks:
    """Get aggregate portfolio Greeks"""
    service = PositionTrackerService()
    return await service.get_portfolio_greeks()


@router.post("/{position_id}/close")
@log_and_sanitize_exceptions(
    logger,
    public_message="Failed to close position",
    log_message="Unable to close position",
)
async def close_position(
    position_id: str,
    limit_price: float | None = None,
    _current_user: User = Depends(get_current_user),
):
    """Close an open position"""
    service = PositionTrackerService()
    return await service.close_position(position_id, limit_price)
