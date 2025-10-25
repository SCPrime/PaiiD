from .data_pipeline import get_data_pipeline
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Literal
import joblib
import logging
import numpy as np
import pandas as pd

"""
Market Regime Detection

Uses unsupervised learning (K-Means clustering) to identify different
market states: trending bullish, trending bearish, ranging, high volatility.

This enables the strategy selector to recommend different strategies
based on the current market regime.
"""




logger = logging.getLogger(__name__)

# Market regime types
MarketRegime = Literal["trending_bullish", "trending_bearish", "ranging", "high_volatility"]

class MarketRegimeDetector:
    """
    Detects market regimes using K-Means clustering on market features
    """

    def __init__(self, n_clusters: int = 4):
        """
        Initialize market regime detector

        Args:
            n_clusters: Number of clusters (default: 4 regimes)
        """
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
        self.scaler = StandardScaler()
        self.regime_labels = {}  # Maps cluster ID to regime name
        self.is_fitted = False

    def extract_regime_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features specifically for regime detection

        Args:
            df: DataFrame with OHLC data and technical indicators

        Returns:
            DataFrame with regime features
        """
        try:
            close = df["close"]
            high = df["high"]
            low = df["low"]
            volume = df["volume"]

            regime_features = pd.DataFrame(index=df.index)

            # 1. Trend Strength (ADX if available, else calculate simple trend)
            if "adx" in df.columns:
                regime_features["trend_strength"] = df["adx"]
            else:
                # Simple trend: 20-day slope
                regime_features["trend_strength"] = close.rolling(window=20).apply(
                    lambda x: np.polyfit(range(len(x)), x, 1)[0]
                )

            # 2. Trend Direction (positive/negative)
            regime_features["trend_direction"] = (close - close.shift(20)) / close.shift(20)

            # 3. Volatility (20-day standard deviation)
            regime_features["volatility"] = close.pct_change().rolling(window=20).std()

            # 4. Volume Trend (relative to average)
            regime_features["volume_trend"] = volume / volume.rolling(window=20).mean()

            # 5. Price Range (high-low relative to close)
            regime_features["price_range"] = (high - low) / close

            # 6. RSI (if available, else calculate)
            if "rsi" in df.columns:
                regime_features["rsi"] = df["rsi"]
            else:
                # Simple RSI calculation
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                regime_features["rsi"] = 100 - (100 / (1 + rs))

            # 7. MACD Signal (if available)
            if "macd_diff" in df.columns:
                regime_features["macd_signal"] = df["macd_diff"]
            else:
                # Simple MACD: 12-26 EMA difference
                ema12 = close.ewm(span=12).mean()
                ema26 = close.ewm(span=26).mean()
                regime_features["macd_signal"] = ema12 - ema26

            # Drop NaN rows
            regime_features = regime_features.dropna()

            return regime_features

        except Exception as e:
            logger.error(f"Feature extraction for regime detection failed: {e}")
            return pd.DataFrame()

    def train(self, symbol: str = "SPY", lookback_days: int = 730) -> bool:
        """
        Train the regime detector on historical data

        Args:
            symbol: Symbol to use for training (default: SPY)
            lookback_days: Days of history (default: 2 years)

        Returns:
            True if training successful, False otherwise
        """
        try:
            logger.info(f"Training market regime detector on {symbol}...")

            # Get historical data
            pipeline = get_data_pipeline()
            features_df = pipeline.prepare_features(symbol, lookback_days)

            if features_df is None or features_df.empty:
                logger.error(f"No data available for training: {symbol}")
                return False

            # Extract regime features
            regime_features = self.extract_regime_features(features_df)

            if regime_features.empty:
                logger.error("Regime feature extraction returned empty")
                return False

            logger.info(
                f"Extracted {len(regime_features)} samples with "
                f"{len(regime_features.columns)} features"
            )

            # Normalize features
            # ruff: noqa: N806  # X_scaled follows ML convention
            X_scaled = self.scaler.fit_transform(regime_features)

            # Fit K-Means
            self.kmeans.fit(X_scaled)

            # Label clusters based on characteristics
            self.regime_labels = self._label_clusters(regime_features, self.kmeans.labels_)

            self.is_fitted = True

            logger.info(f"✅ Market regime detector trained successfully:\n   {self.regime_labels}")

            return True

        except Exception as e:
            logger.error(f"❌ Market regime training failed: {e}")
            return False

    def _label_clusters(
        self, features: pd.DataFrame, labels: np.ndarray
    ) -> dict[int, MarketRegime]:
        """
        Assign human-readable labels to clusters based on their characteristics

        Args:
            features: Feature DataFrame
            labels: Cluster labels from K-Means

        Returns:
            Dictionary mapping cluster ID to regime name
        """
        cluster_profiles = {}

        # Calculate mean features for each cluster
        for cluster_id in range(self.n_clusters):
            mask = labels == cluster_id
            cluster_data = features[mask]

            avg_trend_direction = cluster_data["trend_direction"].mean()
            avg_trend_strength = cluster_data["trend_strength"].mean()
            avg_volatility = cluster_data["volatility"].mean()
            avg_rsi = cluster_data["rsi"].mean()

            cluster_profiles[cluster_id] = {
                "trend_direction": avg_trend_direction,
                "trend_strength": avg_trend_strength,
                "volatility": avg_volatility,
                "rsi": avg_rsi,
            }

        # Assign labels based on cluster characteristics
        regime_map = {}

        # Find high volatility cluster (highest avg volatility)
        volatility_scores = {cid: prof["volatility"] for cid, prof in cluster_profiles.items()}
        high_vol_cluster = max(volatility_scores, key=volatility_scores.get)
        regime_map[high_vol_cluster] = "high_volatility"

        # Find trending bullish (positive trend direction + high trend strength)
        remaining_clusters = [cid for cid in cluster_profiles.keys() if cid != high_vol_cluster]

        trend_bullish_scores = {
            cid: cluster_profiles[cid]["trend_direction"] + cluster_profiles[cid]["trend_strength"]
            for cid in remaining_clusters
        }
        bullish_cluster = max(trend_bullish_scores, key=trend_bullish_scores.get)
        regime_map[bullish_cluster] = "trending_bullish"

        # Find trending bearish (negative trend direction + high trend strength)
        remaining_clusters = [cid for cid in remaining_clusters if cid != bullish_cluster]

        trend_bearish_scores = {
            cid: -cluster_profiles[cid]["trend_direction"] + cluster_profiles[cid]["trend_strength"]
            for cid in remaining_clusters
        }
        bearish_cluster = max(trend_bearish_scores, key=trend_bearish_scores.get)
        regime_map[bearish_cluster] = "trending_bearish"

        # Remaining cluster is ranging
        ranging_cluster = next(cid for cid in range(self.n_clusters) if cid not in regime_map)
        regime_map[ranging_cluster] = "ranging"

        return regime_map

    def predict(self, symbol: str, lookback_days: int = 90) -> dict[str, str | float | dict]:
        """
        Predict current market regime for a symbol

        Args:
            symbol: Stock symbol
            lookback_days: Days of recent history to analyze (default: 90)

        Returns:
            Dictionary with regime prediction and confidence
        """
        try:
            if not self.is_fitted:
                logger.warning("Model not trained yet, training on SPY first...")
                self.train()

            # Get recent data
            pipeline = get_data_pipeline()
            features_df = pipeline.prepare_features(symbol, lookback_days)

            if features_df is None or features_df.empty:
                return {
                    "regime": "unknown",
                    "confidence": 0.0,
                    "error": "No data available",
                }

            # Extract regime features
            regime_features = self.extract_regime_features(features_df)

            if regime_features.empty:
                return {
                    "regime": "unknown",
                    "confidence": 0.0,
                    "error": "Feature extraction failed",
                }

            # Get latest features
            latest_features = regime_features.iloc[-1:].values

            # Normalize
            latest_scaled = self.scaler.transform(latest_features)

            # Predict cluster
            cluster_id = self.kmeans.predict(latest_scaled)[0]

            # Get regime name
            regime = self.regime_labels.get(cluster_id, "unknown")

            # Calculate confidence (inverse distance to cluster center)
            distances = self.kmeans.transform(latest_scaled)[0]
            min_distance = distances[cluster_id]
            max_distance = distances.max()

            # Confidence: closer to center = higher confidence
            confidence = 1.0 - (min_distance / (max_distance + 1e-10))

            # Get feature summary
            feature_summary = {
                "trend_direction": float(regime_features["trend_direction"].iloc[-1]),
                "trend_strength": float(regime_features["trend_strength"].iloc[-1]),
                "volatility": float(regime_features["volatility"].iloc[-1]),
                "rsi": float(regime_features["rsi"].iloc[-1]),
                "volume_trend": float(regime_features["volume_trend"].iloc[-1]),
            }

            logger.info(f"✅ Market regime for {symbol}: {regime} (confidence: {confidence:.2f})")

            return {
                "regime": regime,
                "confidence": float(confidence),
                "features": feature_summary,
                "cluster_id": int(cluster_id),
            }

        except Exception as e:
            logger.error(f"❌ Market regime prediction failed for {symbol}: {e}")
            return {
                "regime": "unknown",
                "confidence": 0.0,
                "error": str(e),
            }

    def get_recommended_strategies(self, regime: str) -> list[str]:
        """
        Get recommended strategy types for a given market regime

        Args:
            regime: Market regime name

        Returns:
            List of recommended strategy IDs
        """
        recommendations = {
            "trending_bullish": [
                "trend-following-ma-crossover",
                "momentum-breakout",
            ],
            "trending_bearish": [
                "mean-reversion-bb-rsi",
                "volatility-breakout",  # For shorting opportunities
            ],
            "ranging": [
                "mean-reversion-bb-rsi",
                "support-resistance-bounce",
            ],
            "high_volatility": [
                "volatility-breakout",
                "options-straddle",  # If options available
            ],
        }

        return recommendations.get(regime, [])

    def save_model(self, filepath: str) -> bool:
        """
        Save trained model to disk

        Args:
            filepath: Path to save model (e.g., "models/regime_detector.pkl")

        Returns:
            True if successful, False otherwise
        """
        try:
            model_data = {
                "kmeans": self.kmeans,
                "scaler": self.scaler,
                "regime_labels": self.regime_labels,
                "n_clusters": self.n_clusters,
                "is_fitted": self.is_fitted,
            }

            joblib.dump(model_data, filepath)
            logger.info(f"✅ Model saved to {filepath}")
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
            True if successful, False otherwise
        """
        try:
            model_data = joblib.load(filepath)

            self.kmeans = model_data["kmeans"]
            self.scaler = model_data["scaler"]
            self.regime_labels = model_data["regime_labels"]
            self.n_clusters = model_data["n_clusters"]
            self.is_fitted = model_data["is_fitted"]

            logger.info(f"✅ Model loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"❌ Model load failed: {e}")
            return False

# Singleton instance
_regime_detector = None

def get_regime_detector() -> MarketRegimeDetector:
    """Get or create market regime detector singleton"""
    global _regime_detector
    if _regime_detector is None:
        _regime_detector = MarketRegimeDetector()
    return _regime_detector
