"""SQLAlchemy models for recommendation history and metadata."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.session import Base


try:  # pragma: no cover - dialect-specific import guard
    from sqlalchemy import JSON
except ImportError:  # pragma: no cover
    JSON = JSONB  # type: ignore


class RecommendationHistory(Base):
    """Persistent record of AI-generated trading recommendations."""

    __tablename__ = "ai_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    recommendation_type: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # buy, sell, hold
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Enhanced risk analytics
    risk_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium", index=True
    )
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Volatility & momentum metadata for filtering
    volatility_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    volatility_label: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    momentum_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    momentum_trend: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    time_horizon: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)

    # Raw indicator data
    analysis_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Execution guidance
    suggested_entry_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    suggested_stop_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    suggested_take_profit: Mapped[float | None] = mapped_column(Float, nullable=True)
    suggested_position_size: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Narrative context
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    market_context: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Lifecycle tracking
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    execution_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_pnl_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    tags: Mapped[list[RecommendationTag]] = relationship(
        "RecommendationTag",
        back_populates="recommendation",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<RecommendationHistory id={self.id} symbol={self.symbol} "
            f"type={self.recommendation_type} confidence={self.confidence_score:.1f}% "
            f"risk={self.risk_level}>"
        )


class RecommendationTag(Base):
    """Tag applied to a recommendation for faceted filtering."""

    __tablename__ = "recommendation_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ai_recommendations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tag: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    recommendation: Mapped[RecommendationHistory] = relationship(
        RecommendationHistory, back_populates="tags"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<RecommendationTag id={self.id} tag='{self.tag}'>"


# Backwards compatibility alias used throughout the codebase
AIRecommendation = RecommendationHistory

__all__ = ["AIRecommendation", "RecommendationHistory", "RecommendationTag"]
