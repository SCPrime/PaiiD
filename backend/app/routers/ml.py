"""
Machine Learning API Endpoints

Endpoints for ML-powered features:
- Market regime detection
- Strategy recommendations
- Pattern recognition
"""

import logging
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from ..ml import get_regime_detector, get_strategy_selector


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


@router.get("/market-regime")
async def get_market_regime(
    symbol: str = Query("SPY", description="Stock symbol to analyze"),
    lookback_days: int = Query(90, ge=30, le=365, description="Days of history to analyze"),
) -> dict[str, Any]:
    """
    Detect current market regime for a symbol

    Returns:
        - regime: Market state (trending_bullish, trending_bearish, ranging, high_volatility)
        - confidence: Confidence score (0.0 to 1.0)
        - features: Key market features used for classification
        - recommended_strategies: Strategy IDs suitable for this regime

    Example:
        GET /api/ml/market-regime?symbol=AAPL&lookback_days=90
    """
    try:
        logger.info(f"Market regime detection requested for {symbol}")

        detector = get_regime_detector()

        # Predict regime
        result = detector.predict(symbol, lookback_days)

        if result.get("regime") == "unknown":
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Regime detection failed"),
            )

        # Get recommended strategies
        regime = result["regime"]
        recommended_strategies = detector.get_recommended_strategies(regime)

        return {
            "symbol": symbol,
            "regime": regime,
            "confidence": result["confidence"],
            "features": result["features"],
            "cluster_id": result.get("cluster_id"),
            "recommended_strategies": recommended_strategies,
            "lookback_days": lookback_days,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market regime detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Market regime detection failed: {e!s}") from e


@router.post("/train-regime-detector")
async def train_regime_detector(
    symbol: str = Query("SPY", description="Symbol to train on"),
    lookback_days: int = Query(730, ge=365, le=1825, description="Days of training data"),
) -> dict[str, Any]:
    """
    Train or retrain the market regime detector

    This endpoint is typically called:
    - On first use (automatic)
    - Periodically for model updates (e.g., weekly)
    - After significant market changes

    Args:
        symbol: Symbol to use for training (default: SPY)
        lookback_days: Days of historical data (default: 730 = 2 years)

    Returns:
        Training status and regime labels

    Example:
        POST /api/ml/train-regime-detector?symbol=SPY&lookback_days=730
    """
    try:
        logger.info(f"Training regime detector on {symbol} ({lookback_days} days)...")

        detector = get_regime_detector()

        success = detector.train(symbol, lookback_days)

        if not success:
            raise HTTPException(status_code=500, detail="Training failed - check logs for details")

        return {
            "success": True,
            "message": f"Regime detector trained successfully on {symbol}",
            "regime_labels": detector.regime_labels,
            "training_data": {
                "symbol": symbol,
                "lookback_days": lookback_days,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {e!s}") from e


@router.get("/health")
async def ml_health_check() -> dict[str, Any]:
    """
    Check ML module health and readiness

    Returns:
        - regime_detector_ready: Whether detector is trained
        - regime_labels: Cluster labels if trained

    Example:
        GET /api/ml/health
    """
    try:
        detector = get_regime_detector()

        return {
            "status": "healthy",
            "regime_detector_ready": detector.is_fitted,
            "regime_labels": detector.regime_labels if detector.is_fitted else {},
            "n_clusters": detector.n_clusters,
        }

    except Exception as e:
        logger.error(f"ML health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


@router.get("/recommend-strategy")
async def recommend_strategy(
    symbol: str = Query("SPY", description="Stock symbol to analyze"),
    lookback_days: int = Query(90, ge=30, le=365, description="Days of history to analyze"),
    top_n: int = Query(3, ge=1, le=5, description="Number of recommendations"),
) -> dict[str, Any]:
    """
    Recommend optimal trading strategies based on ML predictions

    Uses Random Forest to predict which strategies will perform best
    given current market conditions.

    Returns:
        - symbol: Stock symbol analyzed
        - market_regime: Current market state
        - recommendations: List of strategy recommendations with probabilities
        - timestamp: When analysis was performed

    Example:
        GET /api/ml/recommend-strategy?symbol=AAPL&top_n=3
    """
    try:
        logger.info(f"Strategy recommendation requested for {symbol}")

        selector = get_strategy_selector()

        # Get recommendations
        recommendations = selector.recommend(symbol, lookback_days, top_n)

        if not recommendations:
            # Fallback to regime-based recommendations if ML fails
            logger.warning(f"ML recommendation failed for {symbol}, using regime-based fallback")
            detector = get_regime_detector()
            regime_result = detector.predict(symbol, lookback_days)
            regime = regime_result.get("regime", "unknown")

            fallback_strategies = detector.get_recommended_strategies(regime)
            recommendations = [
                {"strategy_id": s, "probability": 0.5, "confidence": 0.5}
                for s in fallback_strategies[:top_n]
            ]

        # Get current market regime for context
        detector = get_regime_detector()
        regime_result = detector.predict(symbol, lookback_days)

        return {
            "symbol": symbol,
            "market_regime": regime_result.get("regime", "unknown"),
            "regime_confidence": regime_result.get("confidence", 0.0),
            "recommendations": recommendations,
            "lookback_days": lookback_days,
            "timestamp": pd.Timestamp.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Strategy recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Strategy recommendation failed: {e!s}") from e


@router.post("/train-strategy-selector")
async def train_strategy_selector(
    symbols: list[str] = Query(["SPY", "QQQ", "IWM", "DIA"], description="Symbols to train on"),
    lookback_days: int = Query(365, ge=180, le=730, description="Days of training data per symbol"),
) -> dict[str, Any]:
    """
    Train or retrain the strategy selector model

    This is a long-running operation that:
    1. Runs backtests on multiple symbols and time windows
    2. Learns which strategies perform best in which conditions
    3. Trains a Random Forest classifier

    Args:
        symbols: List of symbols to backtest (default: major indices)
        lookback_days: Days of history per symbol

    Returns:
        Training results including accuracy metrics

    Example:
        POST /api/ml/train-strategy-selector?symbols=SPY&symbols=QQQ
    """
    try:
        logger.info(f"Training strategy selector on {symbols} ({lookback_days} days)...")

        selector = get_strategy_selector()

        # Train model
        result = selector.train(symbols, lookback_days)

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Training failed - check logs"),
            )

        return {
            "success": True,
            "message": f"Strategy selector trained on {len(symbols)} symbols",
            **result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {e!s}") from e
