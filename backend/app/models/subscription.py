        from app.models.subscription import get_monthly_usage
    from ..db.session import SessionLocal
    from ..services.stripe_service import get_stripe_service
    from sqlalchemy import func
from ..db.session import Base
from datetime import UTC, datetime
from sqlalchemy import (
from sqlalchemy.orm import relationship

"""
Subscription Database Models

SQLAlchemy models for subscription management, usage tracking, and payment history.

Phase 2: Monetization Engine
"""


    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)


class Subscription(Base):
    """User subscription and billing information"""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Stripe integration
    stripe_customer_id = Column(String(100), unique=True, nullable=True, index=True)
    stripe_subscription_id = Column(String(100), unique=True, nullable=True, index=True)

    # Subscription details
    tier = Column(
        String(20), default="free", nullable=False, index=True
    )  # free, pro, premium
    status = Column(
        String(20), default="active", nullable=False, index=True
    )  # active, cancelled, past_due, trialing

    # Billing periods
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True, index=True)
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)

    # Cancellation tracking
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)

    # Pricing
    price = Column(Float, default=0, nullable=False)  # Monthly price in USD
    currency = Column(String(3), default="usd", nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    usage_records = relationship(
        "UsageRecord", back_populates="subscription", cascade="all, delete-orphan"
    )
    invoices = relationship(
        "Invoice", back_populates="subscription", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, tier='{self.tier}', status='{self.status}')>"

    @property
    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.status in ["active", "trialing"]

    @property
    def is_trial(self) -> bool:
        """Check if subscription is in trial period"""
        return self.status == "trialing"

    @property
    def days_until_renewal(self) -> int | None:
        """Calculate days until next renewal"""
        if not self.current_period_end:
            return None
        delta = self.current_period_end - datetime.now(UTC)
        return max(0, delta.days)

class UsageRecord(Base):
    """Track usage of subscription features"""

    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Usage tracking
    feature = Column(
        String(50), nullable=False, index=True
    )  # ml_prediction, backtest, strategy_create, etc.
    quantity = Column(Integer, default=1, nullable=False)  # Usually 1 per event

    # Usage metadata (stored as JSON for flexibility)
    # Example: {"model_id": "regime_detector", "symbol": "AAPL", "accuracy": 0.85}
    # Renamed from 'metadata' to avoid conflict with SQLAlchemy's built-in metadata attribute
    usage_metadata = Column(JSON, default=dict, nullable=False)

    # Timestamps
    timestamp = Column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True
    )
    billing_period_start = Column(DateTime, nullable=False, index=True)
    billing_period_end = Column(DateTime, nullable=False)

    # Relationship
    subscription = relationship("Subscription", back_populates="usage_records")

    def __repr__(self):
        return f"<UsageRecord(id={self.id}, subscription_id={self.subscription_id}, feature='{self.feature}', quantity={self.quantity})>"

class Invoice(Base):
    """Payment and invoice history"""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Stripe integration
    stripe_invoice_id = Column(String(100), unique=True, nullable=True, index=True)
    stripe_payment_intent_id = Column(String(100), unique=True, nullable=True)

    # Invoice details
    amount = Column(Float, nullable=False)  # Total amount
    currency = Column(String(3), default="usd", nullable=False)
    status = Column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, paid, failed, refunded

    # Payment details
    paid_at = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)  # card, bank_transfer, etc.

    # Billing period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Line items (stored as JSON)
    # Example: [
    #   {"description": "Pro Plan", "amount": 29.99, "quantity": 1},
    #   {"description": "Additional ML predictions", "amount": 5.00, "quantity": 1}
    # ]
    line_items = Column(JSON, default=list, nullable=False)

    # Invoice URL (from Stripe)
    invoice_url = Column(String(500), nullable=True)
    pdf_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationship
    subscription = relationship("Subscription", back_populates="invoices")

    def __repr__(self):
        return f"<Invoice(id={self.id}, user_id={self.user_id}, amount=${self.amount:.2f}, status='{self.status}')>"

class PaymentMethod(Base):
    """Stored payment methods for users"""

    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Stripe integration
    stripe_payment_method_id = Column(
        String(100), unique=True, nullable=False, index=True
    )

    # Payment method details
    type = Column(String(20), nullable=False)  # card, bank_account, etc.
    brand = Column(String(20), nullable=True)  # visa, mastercard, amex, etc.
    last4 = Column(String(4), nullable=True)  # Last 4 digits
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)

    # Status
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, user_id={self.user_id}, type='{self.type}', last4='{self.last4}')>"

class SubscriptionEvent(Base):
    """Audit log for subscription events (upgrades, downgrades, cancellations)"""

    __tablename__ = "subscription_events"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Event details
    event_type = Column(
        String(50), nullable=False, index=True
    )  # created, upgraded, downgraded, cancelled, reactivated, payment_failed
    from_tier = Column(String(20), nullable=True)  # Previous tier
    to_tier = Column(String(20), nullable=True)  # New tier

    # Event data (stored as JSON)
    # Example: {
    #   "reason": "User upgraded via settings",
    #   "proration_amount": 15.50,
    #   "stripe_event_id": "evt_123"
    # }
    event_data = Column(JSON, default=dict, nullable=False)

    # Timestamps
    timestamp = Column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True
    )

    def __repr__(self):
        return f"<SubscriptionEvent(id={self.id}, subscription_id={self.subscription_id}, event_type='{self.event_type}', timestamp={self.timestamp})>"

# Usage aggregation queries helper functions

def get_monthly_usage(subscription_id: int, feature: str, month_start: datetime) -> int:
    """
    Helper function to calculate monthly usage for a feature

    Usage:
        usage = get_monthly_usage(subscription_id, "ml_prediction", month_start)
    """


    db = SessionLocal()
    try:
        result = (
            db.query(func.sum(UsageRecord.quantity))
            .filter(
                UsageRecord.subscription_id == subscription_id,
                UsageRecord.feature == feature,
                UsageRecord.billing_period_start == month_start,
            )
            .scalar()
        )
        return result or 0
    finally:
        db.close()

def check_feature_limit(
    subscription_id: int,
    feature: str,
    month_start: datetime,
    tier: str,
) -> tuple[bool, int, int]:
    """
    Check if user has exceeded feature limit

    Returns:
        (within_limit, current_usage, limit)

    Usage:
        within_limit, usage, limit = check_feature_limit(sub_id, "ml_prediction", month, "pro")
    """

    stripe_service = get_stripe_service()
    limits = stripe_service.get_tier_limits(tier)

    # Map feature names to limit keys
    feature_limit_map = {
        "ml_prediction": "ml_predictions_per_month",
        "backtest": "backtests_per_month",
        "strategy_create": "strategies",
        "news_fetch": "news_articles_per_day",
    }

    limit_key = feature_limit_map.get(feature)
    if not limit_key:
        return True, 0, -1  # Unknown feature, allow

    limit = limits.get(limit_key, 0)
    if limit == -1:
        return True, 0, -1  # Unlimited

    current_usage = get_monthly_usage(subscription_id, feature, month_start)
    within_limit = current_usage < limit

    return within_limit, current_usage, limit
