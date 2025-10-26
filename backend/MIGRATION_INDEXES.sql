-- Database Index Migration Script
-- Wave 5 - Database Query Optimization
-- Created: 2025-10-26
--
-- This script creates composite indexes for optimal query performance
-- across all database models. Run this migration AFTER deploying the
-- updated model files.
--
-- IMPORTANT: These indexes are also defined in SQLAlchemy models via
-- __table_args__, so they will be created automatically on new
-- deployments. This script is for existing databases only.

-- ============================================================================
-- USERS TABLE INDEXES
-- ============================================================================

-- Index for role-based queries filtered by active status
CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role, is_active);

-- Index for email lookups filtered by active status
CREATE INDEX IF NOT EXISTS idx_users_email_active ON users(email, is_active);


-- ============================================================================
-- USER_SESSIONS TABLE INDEXES
-- ============================================================================

-- Index for session lookup by user and expiry (for cleanup queries)
CREATE INDEX IF NOT EXISTS idx_sessions_user_expires ON user_sessions(user_id, expires_at);


-- ============================================================================
-- ACTIVITY_LOG TABLE INDEXES
-- ============================================================================

-- Index for user activity timeline queries
CREATE INDEX IF NOT EXISTS idx_activity_user_timestamp ON activity_log(user_id, timestamp);

-- Index for user activity by action type
CREATE INDEX IF NOT EXISTS idx_activity_user_action ON activity_log(user_id, action_type);

-- Index for global action type queries (e.g., admin dashboard)
CREATE INDEX IF NOT EXISTS idx_activity_action_timestamp ON activity_log(action_type, timestamp);


-- ============================================================================
-- STRATEGIES TABLE INDEXES
-- ============================================================================

-- Index for active strategies by user
CREATE INDEX IF NOT EXISTS idx_strategies_user_active ON strategies(user_id, is_active);

-- Index for strategies by user and type
CREATE INDEX IF NOT EXISTS idx_strategies_user_type ON strategies(user_id, strategy_type);

-- Index for active strategies by type (global searches)
CREATE INDEX IF NOT EXISTS idx_strategies_type_active ON strategies(strategy_type, is_active);


-- ============================================================================
-- TRADES TABLE INDEXES
-- ============================================================================

-- Index for trades by user and symbol
CREATE INDEX IF NOT EXISTS idx_trades_user_symbol ON trades(user_id, symbol);

-- Index for user trade history (ordered by time)
CREATE INDEX IF NOT EXISTS idx_trades_user_created ON trades(user_id, created_at);

-- Index for symbol trade history
CREATE INDEX IF NOT EXISTS idx_trades_symbol_created ON trades(symbol, created_at);

-- Index for trade status queries
CREATE INDEX IF NOT EXISTS idx_trades_user_status ON trades(user_id, status);

-- Index for strategy performance tracking
CREATE INDEX IF NOT EXISTS idx_trades_strategy_created ON trades(strategy_id, created_at);


-- ============================================================================
-- PERFORMANCE TABLE INDEXES
-- ============================================================================

-- Index for user performance history
CREATE INDEX IF NOT EXISTS idx_performance_user_date ON performance(user_id, date);


-- ============================================================================
-- EQUITY_SNAPSHOTS TABLE INDEXES
-- ============================================================================

-- Index for equity history queries
CREATE INDEX IF NOT EXISTS idx_equity_user_timestamp ON equity_snapshots(user_id, timestamp);


-- ============================================================================
-- ORDER_TEMPLATES TABLE INDEXES
-- ============================================================================

-- Index for user templates by symbol
CREATE INDEX IF NOT EXISTS idx_templates_user_symbol ON order_templates(user_id, symbol);


-- ============================================================================
-- AI_RECOMMENDATIONS TABLE INDEXES
-- ============================================================================

-- Index for user recommendations by symbol
CREATE INDEX IF NOT EXISTS idx_ai_rec_user_symbol ON ai_recommendations(user_id, symbol);

-- Index for user recommendation history
CREATE INDEX IF NOT EXISTS idx_ai_rec_user_created ON ai_recommendations(user_id, created_at);

-- Index for symbol recommendations by status
CREATE INDEX IF NOT EXISTS idx_ai_rec_symbol_status ON ai_recommendations(symbol, status);

-- Index for user recommendations by status (pending, executed, etc.)
CREATE INDEX IF NOT EXISTS idx_ai_rec_user_status ON ai_recommendations(user_id, status);


-- ============================================================================
-- ML_PREDICTION_HISTORY TABLE INDEXES
-- ============================================================================

-- Index for ML predictions by model, symbol, and date
CREATE INDEX IF NOT EXISTS idx_ml_pred_model_symbol_date
    ON ml_prediction_history(model_id, symbol, created_at);

-- Index for user ML prediction queries
CREATE INDEX IF NOT EXISTS idx_ml_pred_user_model
    ON ml_prediction_history(user_id, model_id);

-- Index for symbol prediction history
CREATE INDEX IF NOT EXISTS idx_ml_pred_symbol_created
    ON ml_prediction_history(symbol, created_at);

-- Index for cache lookups (avoid redundant predictions)
CREATE INDEX IF NOT EXISTS idx_ml_pred_model_hash
    ON ml_prediction_history(model_id, input_hash);


-- ============================================================================
-- ML_MODEL_METRICS TABLE INDEXES
-- ============================================================================

-- Index for model metrics by version
CREATE INDEX IF NOT EXISTS idx_ml_metrics_model_version
    ON ml_model_metrics(model_id, model_version);

-- Index for model performance tracking over time
CREATE INDEX IF NOT EXISTS idx_ml_metrics_model_updated
    ON ml_model_metrics(model_id, updated_at);


-- ============================================================================
-- ML_TRAINING_JOBS TABLE INDEXES
-- ============================================================================

-- Index for user training job history
CREATE INDEX IF NOT EXISTS idx_ml_jobs_user_model
    ON ml_training_jobs(user_id, model_id);

-- Index for model training job status
CREATE INDEX IF NOT EXISTS idx_ml_jobs_model_status
    ON ml_training_jobs(model_id, status);

-- Index for user job history
CREATE INDEX IF NOT EXISTS idx_ml_jobs_user_created
    ON ml_training_jobs(user_id, created_at);


-- ============================================================================
-- BACKTEST_RESULTS TABLE INDEXES
-- ============================================================================

-- Index for user backtest history by symbol
CREATE INDEX IF NOT EXISTS idx_backtest_user_symbol
    ON backtest_results(user_id, symbol, created_at);

-- Index for strategy backtest history
CREATE INDEX IF NOT EXISTS idx_backtest_strategy_created
    ON backtest_results(strategy_id, created_at);

-- Index for backtest queries by date range
CREATE INDEX IF NOT EXISTS idx_backtest_symbol_dates
    ON backtest_results(symbol, start_date, end_date);

-- Index for user backtest status queries
CREATE INDEX IF NOT EXISTS idx_backtest_user_status
    ON backtest_results(user_id, status);


-- ============================================================================
-- FEATURE_STORE TABLE INDEXES
-- ============================================================================

-- Index for feature lookups by symbol, date, and timeframe
CREATE INDEX IF NOT EXISTS idx_feature_store_symbol_date_tf
    ON feature_store(symbol, date, timeframe);

-- Index for feature cache lookups (avoid redundant calculations)
CREATE INDEX IF NOT EXISTS idx_feature_store_symbol_hash
    ON feature_store(symbol, feature_hash);

-- Index for cache cleanup queries (TTL expiration)
CREATE INDEX IF NOT EXISTS idx_feature_store_expires
    ON feature_store(expires_at);


-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify all indexes were created successfully
DO $$
DECLARE
    index_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND indexname LIKE 'idx_%';

    RAISE NOTICE 'Total indexes created: %', index_count;

    IF index_count < 40 THEN
        RAISE WARNING 'Expected at least 40 indexes, found only %', index_count;
    ELSE
        RAISE NOTICE '✅ All indexes created successfully!';
    END IF;
END $$;
