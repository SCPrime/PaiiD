"""FastAPI router exposing recommendation history endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..core.auth import require_bearer
from ..db.session import get_db
from .schemas import (
    RecommendationCreate,
    RecommendationFilterParams,
    RecommendationListResponse,
    RecommendationRead,
    RecommendationSortKey,
    SortDirection,
)
from .service import create_recommendation, list_recommendations


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post(
    "/history",
    response_model=RecommendationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_bearer)],
)
def create_history_entry(
    payload: RecommendationCreate,
    db: Session = Depends(get_db),
) -> RecommendationRead:
    """Persist a recommendation to the history table."""

    try:
        entry = create_recommendation(db, payload, user_id=1)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return RecommendationRead.model_validate(entry, from_attributes=True)


@router.get(
    "/history",
    response_model=RecommendationListResponse,
    dependencies=[Depends(require_bearer)],
)
def get_history(
    symbol: str | None = Query(None, description="Filter by symbol"),
    actions: list[str] | None = Query(
        None, description="Filter by recommendation type (buy, sell, hold)"
    ),
    statuses: list[str] | None = Query(None, description="Filter by status"),
    risk_levels: list[str] | None = Query(None, description="Filter by risk bucket"),
    min_confidence: float | None = Query(None, ge=0, le=100),
    max_confidence: float | None = Query(None, ge=0, le=100),
    min_risk_score: float | None = Query(None, ge=0, le=100),
    max_risk_score: float | None = Query(None, ge=0, le=100),
    min_volatility: float | None = Query(None, ge=0),
    max_volatility: float | None = Query(None, ge=0),
    volatility_labels: list[str] | None = Query(None, description="Volatility classes"),
    min_momentum: float | None = Query(None),
    max_momentum: float | None = Query(None),
    momentum_trends: list[str] | None = Query(None, description="Momentum trend labels"),
    time_horizons: list[str] | None = Query(None, description="Time horizon labels"),
    search: str | None = Query(None, description="Free-text search"),
    sort_by: RecommendationSortKey = Query(
        RecommendationSortKey.CREATED_AT, description="Sort column"
    ),
    sort_direction: SortDirection = Query(SortDirection.DESC, description="Sort direction"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> RecommendationListResponse:
    """Return filtered recommendation history entries."""

    filters = RecommendationFilterParams(
        symbol=symbol,
        actions=actions,
        statuses=statuses,
        risk_levels=risk_levels,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        min_risk_score=min_risk_score,
        max_risk_score=max_risk_score,
        min_volatility=min_volatility,
        max_volatility=max_volatility,
        volatility_labels=volatility_labels,
        min_momentum=min_momentum,
        max_momentum=max_momentum,
        momentum_trends=momentum_trends,
        time_horizons=time_horizons,
        search=search,
    )

    return list_recommendations(
        db,
        filters=filters,
        sort_key=sort_by,
        direction=sort_direction,
        limit=limit,
        offset=offset,
    )


__all__ = ["router"]
