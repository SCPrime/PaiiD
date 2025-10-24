"""Service layer for recommendation history operations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session

from .models import RecommendationHistory, RecommendationTag
from .schemas import (
    RecommendationCreate,
    RecommendationFilterParams,
    RecommendationListResponse,
    RecommendationListSummary,
    RecommendationRead,
    RecommendationRiskLevel,
    RecommendationSortKey,
    SortDirection,
)


def _apply_filters(
    query,
    filters: RecommendationFilterParams,
) -> Iterable[RecommendationHistory]:
    """Apply SQLAlchemy filters based on the provided filter params."""

    if filters.symbol:
        query = query.filter(RecommendationHistory.symbol == filters.symbol.upper())

    if filters.actions:
        query = query.filter(
            RecommendationHistory.recommendation_type.in_(
                action.value for action in filters.actions
            )
        )

    if filters.statuses:
        query = query.filter(RecommendationHistory.status.in_(filters.statuses))

    if filters.risk_levels:
        query = query.filter(
            RecommendationHistory.risk_level.in_(level.value for level in filters.risk_levels)
        )

    if filters.min_confidence is not None:
        query = query.filter(RecommendationHistory.confidence_score >= filters.min_confidence)
    if filters.max_confidence is not None:
        query = query.filter(RecommendationHistory.confidence_score <= filters.max_confidence)

    if filters.min_risk_score is not None:
        query = query.filter(RecommendationHistory.risk_score >= filters.min_risk_score)
    if filters.max_risk_score is not None:
        query = query.filter(RecommendationHistory.risk_score <= filters.max_risk_score)

    if filters.min_volatility is not None:
        query = query.filter(RecommendationHistory.volatility_score >= filters.min_volatility)
    if filters.max_volatility is not None:
        query = query.filter(RecommendationHistory.volatility_score <= filters.max_volatility)

    if filters.volatility_labels:
        query = query.filter(RecommendationHistory.volatility_label.in_(filters.volatility_labels))

    if filters.min_momentum is not None:
        query = query.filter(RecommendationHistory.momentum_score >= filters.min_momentum)
    if filters.max_momentum is not None:
        query = query.filter(RecommendationHistory.momentum_score <= filters.max_momentum)

    if filters.momentum_trends:
        query = query.filter(RecommendationHistory.momentum_trend.in_(filters.momentum_trends))

    if filters.time_horizons:
        query = query.filter(RecommendationHistory.time_horizon.in_(filters.time_horizons))

    if filters.search:
        like_term = f"%{filters.search.lower()}%"
        query = query.filter(
            func.lower(RecommendationHistory.symbol).like(like_term)
            | func.lower(RecommendationHistory.reasoning).like(like_term)
            | func.lower(RecommendationHistory.market_context).like(like_term)
        )

    return query


_SORT_COLUMN_MAP = {
    RecommendationSortKey.CREATED_AT: RecommendationHistory.created_at,
    RecommendationSortKey.CONFIDENCE: RecommendationHistory.confidence_score,
    RecommendationSortKey.RISK: RecommendationHistory.risk_score,
    RecommendationSortKey.VOLATILITY: RecommendationHistory.volatility_score,
    RecommendationSortKey.MOMENTUM: RecommendationHistory.momentum_score,
}


def _apply_sorting(query, sort_key: RecommendationSortKey, direction: SortDirection):
    column = _SORT_COLUMN_MAP.get(sort_key, RecommendationHistory.created_at)
    order_fn = desc if direction == SortDirection.DESC else asc
    return query.order_by(order_fn(column), desc(RecommendationHistory.id))


def create_recommendation(
    db: Session, data: RecommendationCreate, user_id: int
) -> RecommendationHistory:
    """Persist a recommendation record and attached tags."""

    recommendation = RecommendationHistory(
        user_id=user_id,
        symbol=data.symbol.upper(),
        recommendation_type=data.recommendation_type.value,
        confidence_score=data.confidence_score,
        analysis_data=data.analysis_data,
        risk_level=data.risk_level.value,
        risk_score=data.risk_score,
        volatility_score=data.volatility_score,
        volatility_label=data.volatility_label,
        momentum_score=data.momentum_score,
        momentum_trend=data.momentum_trend,
        time_horizon=data.time_horizon,
        suggested_entry_price=data.suggested_entry_price,
        suggested_stop_loss=data.suggested_stop_loss,
        suggested_take_profit=data.suggested_take_profit,
        suggested_position_size=data.suggested_position_size,
        reasoning=data.reasoning,
        market_context=data.market_context,
        status=data.status,
        expires_at=data.expires_at,
    )

    recommendation.tags = [RecommendationTag(tag=tag.strip()) for tag in data.tags if tag.strip()]

    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation


def list_recommendations(
    db: Session,
    filters: RecommendationFilterParams,
    sort_key: RecommendationSortKey,
    direction: SortDirection,
    limit: int,
    offset: int,
) -> RecommendationListResponse:
    """Return filtered and sorted recommendations with summary metadata."""

    query = db.query(RecommendationHistory)
    query = _apply_filters(query, filters)

    total = query.count()

    query = _apply_sorting(query, sort_key, direction)
    items = query.offset(offset).limit(limit).all()

    recommendations = [
        RecommendationRead.model_validate(item, from_attributes=True) for item in items
    ]

    risk_breakdown = Counter(
        (
            rec.risk_level.value
            if isinstance(rec.risk_level, RecommendationRiskLevel)
            else rec.risk_level
        )
        for rec in recommendations
    )
    high_confidence = sum(1 for rec in recommendations if rec.confidence_score >= 80)

    summary = RecommendationListSummary(
        total=total,
        high_confidence=high_confidence,
        risk_breakdown=dict(risk_breakdown),
    )

    return RecommendationListResponse(items=recommendations, total=total, summary=summary)


__all__ = [
    "create_recommendation",
    "list_recommendations",
]
