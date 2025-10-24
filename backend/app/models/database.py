"""
Database Models

SQLAlchemy models for PostgreSQL database.
Defines schema for users, strategies, trades, performance tracking, and equity snapshots.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..db.session import Base


class User(Base):
    """User account and preferences"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # bcrypt hash
    full_name = Column(String(255), nullable=True)

    # Role-based access control
    role = Column(
        String(50), default="personal_only", nullable=False, index=True
    )  # owner, beta_tester, personal_only
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Legacy broker integration
    alpaca_account_id = Column(String(100), unique=True, nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Preferences (stored as JSON for flexibility)
    # Example: {
    #   "risk_tolerance": 50,  # 0-100 (0=ultra-conservative, 100=ultra-aggressive)
    #   "default_position_size": 1000,
    #   "watchlist": ["AAPL", "MSFT"],
    #   "notifications_enabled": true
    # }
    preferences = Column(JSON, default=dict, nullable=False)

    # Relationships
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class UserSession(Base):
    """User session tracking for JWT tokens"""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Token identifiers (JTI - JWT Token ID)
    access_token_jti = Column(String(100), unique=True, nullable=False, index=True)
    refresh_token_jti = Column(String(100), unique=True, nullable=False, index=True)

    # Session metadata
    expires_at = Column(DateTime, nullable=False, index=True)  # Refresh token expiry
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Audit trail
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires={self.expires_at})>"


class ActivityLog(Base):
    """Comprehensive activity log for owner dashboard"""

    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Activity classification
    action_type = Column(
        String(50), nullable=False, index=True
    )  # login, trade_execute, strategy_create, etc.
    resource_type = Column(
        String(50), nullable=True, index=True
    )  # trade, strategy, portfolio, etc.
    resource_id = Column(Integer, nullable=True)  # ID of the affected resource

    # Details (flexible JSON for action-specific data)
    # Example: {"symbol": "AAPL", "quantity": 10, "side": "buy", "price": 175.50}
    details = Column(JSON, default=dict, nullable=False)

    # Audit trail
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User", back_populates="activity_logs")

    def __repr__(self):
        return f"<ActivityLog(id={self.id}, user_id={self.user_id}, action={self.action_type}, timestamp={self.timestamp})>"


class Strategy(Base):
    """Trading strategy configuration"""

    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Strategy metadata
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    strategy_type = Column(
        String(50), nullable=False, index=True
    )  # trend_following, mean_reversion, momentum, custom

    # Strategy configuration (stored as JSON)
    # Example: {"entry_rules": [...], "exit_rules": [...], "rsi_period": 14}
    config = Column(JSON, nullable=False)

    # Status flags
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    is_autopilot = Column(Boolean, default=False, nullable=False)

    # Performance tracking
    total_trades = Column(Integer, default=0, nullable=False)
    win_rate = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_backtest_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")

    def __repr__(self):
        return f"<Strategy(id={self.id}, name='{self.name}', type='{self.strategy_type}')>"


class Trade(Base):
    """Trade execution record"""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="SET NULL"), nullable=True)

    # Trade details
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    order_type = Column(String(20), nullable=False)  # market, limit, stop, stop_limit

    # Limit/stop price (for limit and stop orders)
    limit_price = Column(Float, nullable=True)
    stop_price = Column(Float, nullable=True)

    # Execution details
    broker_order_id = Column(String(100), unique=True, nullable=True, index=True)
    status = Column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, filled, partially_filled, cancelled, failed
    filled_quantity = Column(Float, default=0, nullable=False)
    filled_avg_price = Column(Float, nullable=True)

    # P&L (calculated after close)
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    is_dry_run = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    filled_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="trades")
    strategy = relationship("Strategy")

    def __repr__(self):
        return f"<Trade(id={self.id}, symbol='{self.symbol}', side='{self.side}', qty={self.quantity}, status='{self.status}')>"


class Performance(Base):
    """Daily performance snapshot"""

    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    date = Column(DateTime, nullable=False, index=True)

    # Portfolio metrics
    portfolio_value = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    positions_value = Column(Float, nullable=False)
    num_positions = Column(Integer, default=0, nullable=False)

    # P&L metrics
    total_pnl = Column(Float, default=0, nullable=False)
    total_pnl_percent = Column(Float, default=0, nullable=False)
    day_pnl = Column(Float, default=0, nullable=False)
    day_pnl_percent = Column(Float, default=0, nullable=False)

    # Risk metrics
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    max_drawdown_percent = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)

    # Trade statistics
    total_trades = Column(Integer, default=0, nullable=False)
    winning_trades = Column(Integer, default=0, nullable=False)
    losing_trades = Column(Integer, default=0, nullable=False)
    win_rate = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Performance(id={self.id}, date={self.date}, value=${self.portfolio_value:.2f}, pnl=${self.day_pnl:.2f})>"


class EquitySnapshot(Base):
    """Intraday equity snapshots for charting"""

    __tablename__ = "equity_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Snapshot data
    equity = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    positions_value = Column(Float, nullable=False)
    num_positions = Column(Integer, default=0, nullable=False)

    # Additional context (stored as JSON for flexibility)
    # Example: {"largest_position": "AAPL", "sector_breakdown": {...}}
    extra_data = Column(JSON, default=dict, nullable=False)

    def __repr__(self):
        return (
            f"<EquitySnapshot(id={self.id}, timestamp={self.timestamp}, equity=${self.equity:.2f})>"
        )


class OrderTemplate(Base):
    """Saved order templates for quick execution"""

    __tablename__ = "order_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Template metadata
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Order configuration
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(Float, nullable=False)
    order_type = Column(String(20), nullable=False)  # market, limit
    limit_price = Column(Float, nullable=True)
    asset_class = Column(String(20), nullable=False, default="stock")
    option_type = Column(String(10), nullable=True)
    strike_price = Column(Float, nullable=True)
    expiration_date = Column(String(20), nullable=True)
    order_class = Column(String(20), nullable=False, default="simple")
    take_profit = Column(JSON, nullable=True)
    stop_loss = Column(JSON, nullable=True)
    trail_price = Column(Float, nullable=True)
    trail_percent = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<OrderTemplate(id={self.id}, name='{self.name}', symbol='{self.symbol}', side='{self.side}')>"


class AIRecommendation(Base):
    """AI-generated trading recommendations history"""

    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Recommendation metadata
    symbol = Column(String(20), nullable=False, index=True)
    recommendation_type = Column(String(20), nullable=False, index=True)  # buy, sell, hold
    confidence_score = Column(Float, nullable=False)  # 0-100

    # Market analysis (stored as JSON)
    # Example: {
    #   "technical": {"rsi": 45, "macd": "bullish", "sma_20": 175.5},
    #   "fundamental": {"pe_ratio": 28.5, "market_cap": "2.5T"},
    #   "sentiment": {"score": 0.75, "source": "news"},
    #   "volatility": {"daily": 0.02, "weekly": 0.05}
    # }
    analysis_data = Column(JSON, default=dict, nullable=False)

    # Entry/Exit recommendations
    suggested_entry_price = Column(Float, nullable=True)
    suggested_stop_loss = Column(Float, nullable=True)
    suggested_take_profit = Column(Float, nullable=True)
    suggested_position_size = Column(Float, nullable=True)

    # Reasoning and context
    reasoning = Column(Text, nullable=True)  # AI explanation
    market_context = Column(Text, nullable=True)  # Overall market conditions

    # Status tracking
    status = Column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, executed, ignored, expired
    executed_at = Column(DateTime, nullable=True)
    execution_price = Column(Float, nullable=True)

    # Performance tracking (if recommendation was executed)
    actual_pnl = Column(Float, nullable=True)
    actual_pnl_percent = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)  # 0-100, based on outcome vs prediction

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)  # Recommendation expiry

    def __repr__(self):
        return f"<AIRecommendation(id={self.id}, symbol='{self.symbol}', type='{self.recommendation_type}', confidence={self.confidence_score:.1f}%, status='{self.status}')>"
