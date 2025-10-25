from ..db.session import Base
from datetime import datetime
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

"""
ML Analytics Database Models

SQLAlchemy models for ML prediction history, model performance tracking,
and training analytics. Enables long-term ML system monitoring.

Phase 1E: Production Hardening - Database Schema
"""

class MLPredictionHistory(Base):
    """History of ML predictions for accuracy tracking and analysis"""

    __tablename__ = "ml_prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # Model identification
    model_id = Column(String(100), nullable=False, index=True)  # regime_detector, strategy_selector, etc.
    model_version = Column(String(50), nullable=False)  # 1.0.0, 1.1.0, etc.

    # Input parameters (stored as JSON for flexibility)
    # Example: {"symbol": "AAPL", "lookback_days": 90, "features": {...}}
    input_params = Column(JSON, nullable=False)
    input_hash = Column(String(32), nullable=False, index=True)  # MD5 hash for deduplication

    # Prediction output (stored as JSON)
    # Example: {
    #   "regime": "trending_bullish",
    #   "confidence": 0.85,
    #   "cluster_id": 2,
    #   "recommended_strategies": ["momentum_swing", "trend_following"]
    # }
    prediction_output = Column(JSON, nullable=False)

    # Confidence metrics
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    probability_scores = Column(JSON, nullable=True)  # Full probability distribution

    # Ground truth and accuracy (updated after outcome is known)
    actual_outcome = Column(JSON, nullable=True)  # Actual market behavior
    accuracy_score = Column(Float, nullable=True)  # 0.0 to 1.0
    is_correct = Column(Integer, nullable=True)  # 1=correct, 0=incorrect, NULL=pending

    # Performance metrics
    inference_time_ms = Column(Float, nullable=True)  # Model inference latency
    cache_hit = Column(Integer, default=0, nullable=False)  # 1=cached, 0=computed

    # Metadata
    symbol = Column(String(20), nullable=True, index=True)  # For symbol-specific analysis
    market_regime = Column(String(50), nullable=True, index=True)  # Market state at prediction time

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    validated_at = Column(DateTime, nullable=True)  # When accuracy was confirmed

    def __repr__(self):
        return f"<MLPredictionHistory(id={self.id}, model='{self.model_id}', symbol='{self.symbol}', confidence={self.confidence_score:.2f})>"

class MLModelMetrics(Base):
    """ML model performance metrics over time"""

    __tablename__ = "ml_model_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Model identification
    model_id = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False, index=True)

    # Aggregate metrics
    total_predictions = Column(Integer, default=0, nullable=False)
    correct_predictions = Column(Integer, default=0, nullable=False)
    accuracy = Column(Float, nullable=True)  # Overall accuracy (0.0 to 1.0)

    # Confidence calibration
    avg_confidence = Column(Float, nullable=True)
    confidence_accuracy_correlation = Column(Float, nullable=True)  # How well confidence predicts accuracy

    # Performance by regime/category (stored as JSON)
    # Example: {
    #   "trending_bullish": {"accuracy": 0.85, "count": 120},
    #   "trending_bearish": {"accuracy": 0.78, "count": 95},
    #   "ranging": {"accuracy": 0.62, "count": 80}
    # }
    performance_breakdown = Column(JSON, default=dict, nullable=False)

    # Time-based metrics
    last_7_days_accuracy = Column(Float, nullable=True)
    last_30_days_accuracy = Column(Float, nullable=True)
    last_90_days_accuracy = Column(Float, nullable=True)

    # Feature importance (top features from model)
    # Example: [
    #   {"feature": "rsi", "importance": 0.35},
    #   {"feature": "volatility", "importance": 0.28},
    #   ...
    # ]
    feature_importance = Column(JSON, default=list, nullable=False)

    # Training metadata
    training_samples = Column(Integer, nullable=True)
    training_accuracy = Column(Float, nullable=True)
    validation_accuracy = Column(Float, nullable=True)

    # System metrics
    avg_inference_time_ms = Column(Float, nullable=True)
    cache_hit_rate = Column(Float, nullable=True)  # 0.0 to 1.0

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
    last_trained_at = Column(DateTime, nullable=True)
    last_evaluated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<MLModelMetrics(model='{self.model_id}', version='{self.model_version}', accuracy={self.accuracy:.2f}, predictions={self.total_predictions})>"

class MLTrainingJob(Base):
    """Training job history and status tracking"""

    __tablename__ = "ml_training_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # Job identification
    job_id = Column(String(100), unique=True, nullable=False, index=True)  # UUID
    model_id = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)

    # Training parameters (stored as JSON)
    # Example: {"symbol": "SPY", "lookback_days": 730, "n_clusters": 5}
    training_params = Column(JSON, nullable=False)

    # Status tracking
    status = Column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, running, completed, failed
    progress_percent = Column(Float, default=0, nullable=False)  # 0-100

    # Results (populated on completion)
    training_accuracy = Column(Float, nullable=True)
    validation_accuracy = Column(Float, nullable=True)
    test_accuracy = Column(Float, nullable=True)

    # Training metrics (stored as JSON)
    # Example: {
    #   "loss_history": [0.5, 0.3, 0.2, ...],
    #   "validation_loss_history": [0.6, 0.4, 0.25, ...],
    #   "training_time_seconds": 45.2
    # }
    metrics = Column(JSON, default=dict, nullable=False)

    # Error handling
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)

    # Model artifacts
    model_file_path = Column(String(500), nullable=True)  # Path to saved model
    model_size_mb = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<MLTrainingJob(id={self.id}, model='{self.model_id}', status='{self.status}', progress={self.progress_percent:.1f}%)>"

class BacktestResult(Base):
    """Backtest results for strategies and ML models"""

    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    strategy_id = Column(
        Integer, ForeignKey("strategies.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Backtest identification
    backtest_id = Column(String(100), unique=True, nullable=False, index=True)  # UUID
    model_id = Column(String(100), nullable=True, index=True)  # If ML-powered strategy

    # Backtest parameters
    symbol = Column(String(20), nullable=False, index=True)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    initial_capital = Column(Float, default=100000, nullable=False)

    # Strategy configuration (stored as JSON)
    strategy_config = Column(JSON, nullable=False)

    # Performance metrics
    total_return = Column(Float, nullable=True)  # Total % return
    annualized_return = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    max_drawdown_percent = Column(Float, nullable=True)
    calmar_ratio = Column(Float, nullable=True)

    # Trade statistics
    total_trades = Column(Integer, default=0, nullable=False)
    winning_trades = Column(Integer, default=0, nullable=False)
    losing_trades = Column(Integer, default=0, nullable=False)
    win_rate = Column(Float, nullable=True)  # Percentage
    avg_win = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)  # Gross profit / Gross loss

    # Risk metrics
    volatility = Column(Float, nullable=True)  # Annualized volatility
    downside_volatility = Column(Float, nullable=True)
    beta = Column(Float, nullable=True)  # vs SPY
    alpha = Column(Float, nullable=True)  # vs SPY

    # Detailed results (stored as JSON)
    # Example: {
    #   "equity_curve": [{"date": "2024-01-01", "equity": 100000}, ...],
    #   "trades": [{"date": "2024-01-05", "symbol": "AAPL", "side": "buy", ...}, ...],
    #   "monthly_returns": {"2024-01": 0.05, "2024-02": -0.02, ...}
    # }
    detailed_results = Column(JSON, default=dict, nullable=False)

    # Status
    status = Column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    strategy = relationship("Strategy")

    def __repr__(self):
        return f"<BacktestResult(id={self.id}, symbol='{self.symbol}', return={self.total_return:.2f}%, sharpe={self.sharpe_ratio:.2f}, trades={self.total_trades})>"

class FeatureStore(Base):
    """Cached feature engineering results for ML models"""

    __tablename__ = "feature_store"

    id = Column(Integer, primary_key=True, index=True)

    # Data identification
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    timeframe = Column(String(20), nullable=False, index=True)  # 1d, 1h, 5m, etc.

    # Features (stored as JSON for flexibility)
    # Example: {
    #   "rsi": 45.2,
    #   "macd": 1.5,
    #   "sma_20": 175.5,
    #   "volatility": 0.025,
    #   "volume_ratio": 1.2,
    #   ...
    # }
    features = Column(JSON, nullable=False)

    # Feature hash for deduplication
    feature_hash = Column(String(32), nullable=False, index=True)

    # Metadata
    feature_version = Column(String(20), default="1.0", nullable=False)  # Feature engineering version
    computation_time_ms = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)  # TTL for cache invalidation

    def __repr__(self):
        return f"<FeatureStore(symbol='{self.symbol}', date={self.date}, timeframe='{self.timeframe}')>"

# Indexes for performance optimization
# SQLAlchemy automatically creates single-column indexes for columns with index=True
# Add composite indexes for common query patterns

# Example composite indexes (run these via Alembic migration):
# CREATE INDEX idx_ml_pred_model_symbol_date ON ml_prediction_history(model_id, symbol, created_at);
# CREATE INDEX idx_ml_pred_user_model ON ml_prediction_history(user_id, model_id);
# CREATE INDEX idx_backtest_user_symbol ON backtest_results(user_id, symbol, created_at);
# CREATE INDEX idx_feature_store_symbol_date ON feature_store(symbol, date, timeframe);
