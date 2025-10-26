"""
Strategy-based opportunity screening endpoints
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from ..core.unified_auth import get_current_user_unified
from ..models.database import User
from ..services.screening_service import get_screening_service


router = APIRouter(tags=["screening"])


@router.get("/screening/opportunities")
async def get_opportunities(
    max_price: float | None = None,
    current_user: User = Depends(get_current_user_unified),
) -> dict:
    """
    Get strategy-based trading opportunities

    Args:
        max_price: Optional maximum price to filter opportunities
            (based on available account balance)

    PHASE 2 IMPLEMENTATION: Real-time strategy screening
    Planned features:
    - Integrate user's selected strategies from settings (Phase 1 prerequisite)
    - Calculate technical indicators using TechnicalIndicators service (already exists)
    - Volume analysis with historical comparison (requires OHLCV storage)
    - Options screening with IV rank and Greeks (Phase 1 options integration)
    - Risk-based filtering using user risk_tolerance settings

    Current: Returns curated static examples for UI/UX development and testing
    """
    try:
        screening_service = get_screening_service()
        opportunities = screening_service.get_opportunities(
            max_price=max_price, count_per_type=2
        )

        return {
            "opportunities": [opp.model_dump() for opp in opportunities],
            "timestamp": datetime.now(UTC).isoformat(),
            "strategyCount": len({opp.strategy for opp in opportunities}),
            "filteredByPrice": max_price is not None,
            "maxPrice": max_price,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get opportunities: {e!s}"
        ) from e


@router.get("/screening/strategies")
async def get_available_strategies(
    current_user: User = Depends(get_current_user_unified),
) -> dict:
    """
    Get list of available screening strategies

    Users can enable/disable these in settings
    """
    try:
        screening_service = get_screening_service()
        strategies = screening_service.get_available_strategies()
        return {"strategies": strategies}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get strategies: {e!s}"
        ) from e
