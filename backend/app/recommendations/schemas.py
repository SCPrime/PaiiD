"""Pydantic schemas and enums for recommendation API."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator


class RecommendationAction(str, Enum):
    """Supported recommendation types."""

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class RecommendationRiskLevel(str, Enum):
    """Risk buckets used by the UI."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecommendationSortKey(str, Enum):
    """Sortable columns for recommendation history."""

    CREATED_AT = "created_at"
    CONFIDENCE = "confidence"
    RISK = "risk"
    VOLATILITY = "volatility"
    MOMENTUM = "momentum"


class SortDirection(str, Enum):
    """Sort direction."""

    ASC = "asc"
    DESC = "desc"


class RecommendationBase(BaseModel):
    """Fields shared between create/read schemas."""

    symbol: str = Field(..., min_length=1, max_length=20)
    recommendation_type: RecommendationAction
    confidence_score: float = Field(..., ge=0, le=100)
    analysis_data: dict = Field(default_factory=dict)
    risk_level: RecommendationRiskLevel = RecommendationRiskLevel.MEDIUM
    risk_score: float | None = Field(default=None, ge=0, le=100)
    volatility_score: float | None = Field(default=None, ge=0)
    volatility_label: str | None = Field(default=None, max_length=20)
    momentum_score: float | None = Field(default=None)
    momentum_trend: str | None = Field(default=None, max_length=20)
    time_horizon: str | None = Field(default=None, max_length=20)
    suggested_entry_price: float | None = Field(default=None, ge=0)
    suggested_stop_loss: float | None = Field(default=None)
    suggested_take_profit: float | None = Field(default=None)
    suggested_position_size: float | None = Field(default=None, ge=0)
    reasoning: str | None = None
    market_context: str | None = None
    tags: list[str] = Field(default_factory=list)
    status: str = Field(default="pending", max_length=20)
    expires_at: datetime | None = None

    class Config:
        populate_by_name = True

    @validator("recommendation_type", pre=True)
    def _normalize_action(cls, value: RecommendationAction | str) -> RecommendationAction:
        if isinstance(value, RecommendationAction):
            return value
        return RecommendationAction(str(value).lower())

    @validator("risk_level", pre=True)
    def _normalize_risk_level(
        cls, value: RecommendationRiskLevel | str | None
    ) -> RecommendationRiskLevel:
        if value is None:
            return RecommendationRiskLevel.MEDIUM
        if isinstance(value, RecommendationRiskLevel):
            return value
        return RecommendationRiskLevel(str(value).lower())

    @validator("tags", pre=True)
    def _extract_tags(cls, value):
        """Support ORM relationship objects as input."""

        if value is None:
            return []
        if isinstance(value, list):
            return [getattr(tag, "tag", tag) for tag in value]
        return value


class RecommendationCreate(RecommendationBase):
    """Payload for creating a recommendation history entry."""

    pass


class RecommendationRead(RecommendationBase):
    """Recommendation entry returned from the API."""

    id: int
    created_at: datetime
    updated_at: datetime
    executed_at: datetime | None = None
    execution_price: float | None = None
    actual_pnl: float | None = None
    actual_pnl_percent: float | None = None

    class Config:
        from_attributes = True


class RecommendationFilterParams(BaseModel):
    """Filtering options accepted by the API."""

    symbol: str | None = None
    actions: Sequence[RecommendationAction] | None = None
    statuses: Sequence[str] | None = None
    risk_levels: Sequence[RecommendationRiskLevel] | None = None
    min_confidence: float | None = Field(default=None, ge=0, le=100)
    max_confidence: float | None = Field(default=None, ge=0, le=100)
    min_risk_score: float | None = Field(default=None, ge=0, le=100)
    max_risk_score: float | None = Field(default=None, ge=0, le=100)
    min_volatility: float | None = Field(default=None, ge=0)
    max_volatility: float | None = Field(default=None, ge=0)
    volatility_labels: Sequence[str] | None = None
    min_momentum: float | None = None
    max_momentum: float | None = None
    momentum_trends: Sequence[str] | None = None
    time_horizons: Sequence[str] | None = None
    search: str | None = None

    @validator("symbol")
    def normalize_symbol(cls, value: str | None) -> str | None:
        """Uppercase symbols for consistent filtering."""

        return value.upper() if value else value

    @validator("actions", pre=True)
    def normalize_actions(
        cls, value: Iterable[str] | None
    ) -> Sequence[RecommendationAction] | None:
        if value is None:
            return None
        return [RecommendationAction(str(item).lower()) for item in value]

    @validator("risk_levels", pre=True)
    def normalize_risk(
        cls, value: Iterable[str] | None
    ) -> Sequence[RecommendationRiskLevel] | None:
        if value is None:
            return None
        return [RecommendationRiskLevel(str(item).lower()) for item in value]

    @validator("volatility_labels", "momentum_trends", "time_horizons", pre=True)
    def normalize_string_lists(cls, value):
        """Normalize string based lists for filtering."""

        if value is None:
            return None
        return [str(item).lower() for item in value if str(item)]


class RecommendationListSummary(BaseModel):
    """Aggregate metrics returned with list endpoints."""

    total: int
    high_confidence: int
    risk_breakdown: dict[str, int]


class RecommendationListResponse(BaseModel):
    """Paginated recommendation list."""

    items: list[RecommendationRead]
    total: int
    summary: RecommendationListSummary


__all__ = [
    "RecommendationAction",
    "RecommendationCreate",
    "RecommendationFilterParams",
    "RecommendationListResponse",
    "RecommendationListSummary",
    "RecommendationRead",
    "RecommendationRiskLevel",
    "RecommendationSortKey",
    "SortDirection",
]
