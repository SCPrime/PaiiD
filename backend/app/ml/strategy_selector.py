"""
Strategy Recommendation Engine

Uses supervised learning (Random Forest) to recommend optimal trading strategies
based on current market conditions and historical performance data.

The model learns from backtesting results: which strategies performed best
in which market regimes and feature combinations.
"""

import logging
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from ..services.backtesting_engine import BacktestingEngine
from ..services.strategy_templates import get_all_strategy_templates
from .data_pipeline import get_data_pipeline
from .market_regime import get_regime_detector


logger = logging.getLogger(__name__)


class StrategySelector:
    """
    ML-powered strategy recommendation system

    Learns from historical backtest results to predict which strategy
    will perform best in current market conditions.
    """

    def __init__(self, n_estimators: int = 100):
        """
        Initialize strategy selector

        Args:
            n_estimators: Number of trees in Random Forest (default: 100)
        """
        self.n_estimators = n_estimators
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,  # Use all CPU cores
        )
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.is_fitted = False

    def create_training_dataset(
        self,
        symbols: list[str],
        lookback_days: int = 365,
        min_samples_per_strategy: int = 10,
    ) -> tuple[pd.DataFrame, pd.Series] | None:
        """
        Create training dataset by running backtests on historical data

        Args:
            symbols: List of symbols to backtest
            lookback_days: Days of history per symbol
            min_samples_per_strategy: Minimum samples needed per strategy

        Returns:
            Tuple of (features DataFrame, target Series) or None if failed
        """
        try:
            logger.info(
                f"Creating training dataset from {len(symbols)} symbols, "
                f"{lookback_days} days lookback..."
            )

            pipeline = get_data_pipeline()
            regime_detector = get_regime_detector()
            backtest_engine = BacktestingEngine()

            # Get all available strategies
            strategies = get_all_strategy_templates()
            if not strategies:
                logger.error("No strategy templates available")
                return None

            strategy_ids = list(strategies.keys())
            logger.info(f"Training with {len(strategy_ids)} strategies: {strategy_ids}")

            all_samples = []

            # For each symbol, create multiple time windows and backtest
            for symbol in symbols:
                logger.info(f"Processing {symbol}...")

                # Fetch historical data
                features_df = pipeline.prepare_features(symbol, lookback_days=lookback_days)

                if features_df is None or len(features_df) < 100:
                    logger.warning(f"Insufficient data for {symbol}, skipping")
                    continue

                # Create sliding windows (e.g., 60-day windows with 20-day stride)
                window_size = 60
                stride = 20

                for start_idx in range(0, len(features_df) - window_size, stride):
                    end_idx = start_idx + window_size
                    window_data = features_df.iloc[start_idx:end_idx]

                    # Extract market features for this window
                    window_features = self._extract_window_features(window_data)

                    # Detect market regime for this window
                    regime_result = regime_detector.predict(symbol, lookback_days=window_size)
                    window_features["regime"] = regime_result.get("regime", "unknown")

                    # Backtest each strategy on this window
                    strategy_results = {}

                    for strategy_id, _strategy_template in strategies.items():
                        try:
                            # Run backtest
                            result = backtest_engine.run_backtest(
                                symbol=symbol,
                                strategy_id=strategy_id,
                                start_date=window_data.index[0],
                                end_date=window_data.index[-1],
                            )

                            if result and result.total_return is not None:
                                # Calculate strategy score (Sharpe ratio weighted by win rate)
                                sharpe = result.sharpe_ratio or 0.0
                                win_rate = result.win_rate or 0.0
                                score = sharpe * (1 + win_rate)

                                strategy_results[strategy_id] = {
                                    "score": score,
                                    "return": result.total_return,
                                    "sharpe": sharpe,
                                    "win_rate": win_rate,
                                }
                        except Exception as e:
                            logger.debug(f"Backtest failed for {strategy_id} on {symbol}: {e}")
                            continue

                    # Find best performing strategy for this window
                    if strategy_results:
                        best_strategy = max(strategy_results.items(), key=lambda x: x[1]["score"])[
                            0
                        ]

                        # Create training sample
                        sample = {
                            **window_features,
                            "best_strategy": best_strategy,
                            "symbol": symbol,
                        }
                        all_samples.append(sample)

            if not all_samples:
                logger.error("No training samples created")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(all_samples)

            # Check if we have enough samples per strategy
            strategy_counts = df["best_strategy"].value_counts()
            logger.info(f"Strategy distribution:\n{strategy_counts}")

            # Filter out strategies with too few samples
            valid_strategies = strategy_counts[strategy_counts >= min_samples_per_strategy].index
            df = df[df["best_strategy"].isin(valid_strategies)]

            if len(df) == 0:
                logger.error("No samples remaining after filtering")
                return None

            # Separate features and target
            feature_cols = [
                col for col in df.columns if col not in ["best_strategy", "symbol", "regime"]
            ]

            # Add regime as categorical feature
            regime_dummies = pd.get_dummies(df["regime"], prefix="regime")
            feature_cols.extend(regime_dummies.columns)

            # ruff: noqa: N806  # X and y follow ML convention
            X = pd.concat([df[feature_cols], regime_dummies], axis=1)
            y = df["best_strategy"]

            self.feature_names = X.columns.tolist()

            logger.info(
                f"✅ Training dataset created: {len(X)} samples, "
                f"{len(X.columns)} features, {len(y.unique())} strategies"
            )

            return X, y

        except Exception as e:
            logger.error(f"❌ Training dataset creation failed: {e}")
            return None

    def _extract_window_features(self, window_data: pd.DataFrame) -> dict[str, float]:
        """
        Extract summary features from a time window

        Args:
            window_data: DataFrame with technical indicators

        Returns:
            Dictionary of aggregated features
        """
        features = {}

        # Trend features (mean of last 20 days)
        if "sma_20" in window_data.columns:
            features["avg_sma_20"] = window_data["sma_20"].tail(20).mean()
        if "adx" in window_data.columns:
            features["avg_adx"] = window_data["adx"].tail(20).mean()

        # Momentum features
        if "rsi" in window_data.columns:
            features["avg_rsi"] = window_data["rsi"].tail(20).mean()
            features["rsi_trend"] = (
                window_data["rsi"].tail(20).mean() - window_data["rsi"].head(20).mean()
            )

        # Volatility features
        if "volatility_20" in window_data.columns:
            features["avg_volatility"] = window_data["volatility_20"].tail(20).mean()
        if "atr" in window_data.columns:
            features["avg_atr"] = window_data["atr"].tail(20).mean()

        # Volume features
        if "volume_ratio" in window_data.columns:
            features["avg_volume_ratio"] = window_data["volume_ratio"].tail(20).mean()

        # Price action
        if "close" in window_data.columns:
            close = window_data["close"]
            features["price_trend"] = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]
            features["price_volatility"] = close.pct_change().std()

        return features

    def train(
        self,
        symbols: list[str] | None = None,
        lookback_days: int = 365,
        test_size: float = 0.2,
    ) -> dict[str, Any]:
        """
        Train the strategy selector model

        Args:
            symbols: List of symbols to train on (default: SPY, QQQ, IWM, DIA)
            lookback_days: Days of history per symbol
            test_size: Fraction for testing (default: 0.2)

        Returns:
            Training results with accuracy metrics
        """
        try:
            if symbols is None:
                symbols = ["SPY", "QQQ", "IWM", "DIA"]  # Major indices

            logger.info(f"Training strategy selector on {symbols}...")

            # Create training dataset
            result = self.create_training_dataset(symbols, lookback_days)

            if result is None:
                return {
                    "success": False,
                    "error": "Training dataset creation failed",
                }

            # ruff: noqa: N806  # X and y follow ML convention
            X, y = result

            # Encode strategy labels
            y_encoded = self.label_encoder.fit_transform(y)

            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
            )

            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Train Random Forest
            logger.info(f"Training Random Forest with {self.n_estimators} trees...")
            self.model.fit(X_train_scaled, y_train)

            # Evaluate
            train_accuracy = self.model.score(X_train_scaled, y_train)
            test_accuracy = self.model.score(X_test_scaled, y_test)

            # Get feature importances
            feature_importance = dict(
                sorted(
                    zip(self.feature_names, self.model.feature_importances_, strict=True),
                    key=lambda x: x[1],
                    reverse=True,
                )
            )

            self.is_fitted = True

            logger.info(
                f"✅ Strategy selector trained successfully:\n"
                f"   Train accuracy: {train_accuracy:.2%}\n"
                f"   Test accuracy: {test_accuracy:.2%}"
            )

            return {
                "success": True,
                "train_accuracy": train_accuracy,
                "test_accuracy": test_accuracy,
                "n_samples": len(X),
                "n_features": len(self.feature_names),
                "strategies": self.label_encoder.classes_.tolist(),
                "top_features": dict(list(feature_importance.items())[:10]),
            }

        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def recommend(
        self, symbol: str, lookback_days: int = 90, top_n: int = 3
    ) -> list[dict[str, Any]]:
        """
        Recommend best strategies for current market conditions

        Args:
            symbol: Stock symbol
            lookback_days: Days of recent history to analyze
            top_n: Number of top recommendations to return

        Returns:
            List of strategy recommendations with probabilities
        """
        try:
            if not self.is_fitted:
                logger.warning("Model not trained yet, training on default symbols...")
                self.train()

            # Get current market features
            pipeline = get_data_pipeline()
            features_df = pipeline.prepare_features(symbol, lookback_days)

            if features_df is None or features_df.empty:
                return []

            # Extract window features
            window_features = self._extract_window_features(features_df)

            # Get current regime
            regime_detector = get_regime_detector()
            regime_result = regime_detector.predict(symbol, lookback_days)
            current_regime = regime_result.get("regime", "unknown")

            # Create regime dummies
            regime_features = {}
            for regime in [
                "trending_bullish",
                "trending_bearish",
                "ranging",
                "high_volatility",
            ]:
                regime_features[f"regime_{regime}"] = 1 if regime == current_regime else 0

            # Combine features
            all_features = {**window_features, **regime_features}

            # Create feature vector matching training format
            feature_vector = pd.DataFrame([all_features])[self.feature_names]

            # Scale features
            feature_scaled = self.scaler.transform(feature_vector)

            # Get predictions
            probabilities = self.model.predict_proba(feature_scaled)[0]
            strategies = self.label_encoder.classes_

            # Create recommendations
            recommendations = []
            for strategy, prob in zip(strategies, probabilities, strict=True):
                recommendations.append(
                    {
                        "strategy_id": strategy,
                        "probability": float(prob),
                        "confidence": float(prob),  # Alias for compatibility
                    }
                )

            # Sort by probability and get top N
            recommendations.sort(key=lambda x: x["probability"], reverse=True)
            top_recommendations = recommendations[:top_n]

            logger.info(
                f"✅ Recommended strategies for {symbol}: "
                f"{[r['strategy_id'] for r in top_recommendations]}"
            )

            return top_recommendations

        except Exception as e:
            logger.error(f"❌ Strategy recommendation failed for {symbol}: {e}")
            return []

    def save_model(self, filepath: str) -> bool:
        """
        Save trained model to disk

        Args:
            filepath: Path to save model

        Returns:
            True if successful
        """
        try:
            model_data = {
                "model": self.model,
                "scaler": self.scaler,
                "label_encoder": self.label_encoder,
                "feature_names": self.feature_names,
                "is_fitted": self.is_fitted,
            }

            joblib.dump(model_data, filepath)
            logger.info(f"✅ Strategy selector saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"❌ Model save failed: {e}")
            return False

    def load_model(self, filepath: str) -> bool:
        """
        Load trained model from disk

        Args:
            filepath: Path to model file

        Returns:
            True if successful
        """
        try:
            model_data = joblib.load(filepath)

            self.model = model_data["model"]
            self.scaler = model_data["scaler"]
            self.label_encoder = model_data["label_encoder"]
            self.feature_names = model_data["feature_names"]
            self.is_fitted = model_data["is_fitted"]

            logger.info(f"✅ Strategy selector loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"❌ Model load failed: {e}")
            return False


# Singleton instance
_strategy_selector = None


def get_strategy_selector() -> StrategySelector:
    """Get or create strategy selector singleton"""
    global _strategy_selector
    if _strategy_selector is None:
        _strategy_selector = StrategySelector()
    return _strategy_selector
