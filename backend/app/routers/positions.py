"""Position Management API"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import require_bearer
from app.services.position_tracker import (
    PortfolioGreeks,
    Position,
    PositionTrackerService,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/positions", tags=["positions"])


@router.get("", response_model=list[Position], dependencies=[Depends(require_bearer)])
async def get_positions():
    """Get all open positions with real-time P&L and Greeks"""
    service = PositionTrackerService()
    try:
        positions = await service.get_open_positions()
        logger.info("Retrieved %d open positions", len(positions))
        return positions
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to fetch open positions: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load open positions",
        )


@router.get(
    "/greeks", response_model=PortfolioGreeks, dependencies=[Depends(require_bearer)]
)
async def get_portfolio_greeks():
    """Get aggregate portfolio Greeks"""
    service = PositionTrackerService()
    try:
        portfolio_greeks = await service.get_portfolio_greeks()
        logger.info("Calculated portfolio greeks for %d positions", portfolio_greeks.position_count)
        return portfolio_greeks
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to calculate portfolio greeks: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to calculate portfolio greeks",
        )


@router.post("/{position_id}/close", dependencies=[Depends(require_bearer)])
async def close_position(position_id: str, limit_price: float | None = None):
    """Close an open position"""
    service = PositionTrackerService()
    try:
        result = await service.close_position(position_id, limit_price)
        logger.info("Submitted close order for position %s", position_id)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to close position %s: %s", position_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to close position",
        )
