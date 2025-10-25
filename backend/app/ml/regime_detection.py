"""
Advanced Market Regime Detection Module
ML-powered market regime classification for PaiiD
"""

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
import talib
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler


logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regime classifications"""

    TRENDING_BULL = "trending_bull"
    TRENDING_BEAR = "trending_bear"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"


@dataclass
class RegimeAnalysis:
    """Market regime analysis result"""

    current_regime: MarketRegime
    confidence: float
    regime_strength: str  # "weak", "moderate", "strong", "very_strong"
    trend_direction: str  # "bullish", "bearish", "neutral"
    volatility_level: str  # "low", "medium", "high", "extreme"
    momentum_score: float  # -1.0 to 1.0
    regime_duration: int  # days in current regime
    regime_probability: dict[MarketRegime, float]  # probability for each regime
    key_indicators: dict[str, float]
    trading_implications: list[str]
    risk_level: str  # "low", "medium", "high", "extreme"
    recommended_strategies: list[str]


class AdvancedRegimeDetector:
    """Advanced market regime detection using ML"""

    def __init__(self):
        self.lookback_period = 252  # 1 year of trading days
        self.min_regime_duration = 5  # minimum days for regime
        self.volatility_threshold = 0.02  # 2% daily volatility threshold
        self.trend_threshold = 0.1  # 10% trend threshold

        # Initialize ML models
        self.regime_classifier = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42
        )
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()

        # Training data storage
        self.training_data = None
        self.is_trained = False

    def detect_regime(
        self,
        ohlcv_data: pd.DataFrame,
        volume_data: pd.Series = None,
        market_data: pd.DataFrame = None,
    ) -> RegimeAnalysis:
        """
        Detect current market regime using advanced ML techniques

        Args:
            ohlcv_data: OHLCV price data
            volume_data: Volume data (optional)
            market_data: Additional market data (VIX, sector data, etc.)

        Returns:
            Comprehensive regime analysis
        """
        try:
            # Calculate features
            features = self._calculate_features(ohlcv_data, volume_data, market_data)

            # Detect regime using multiple methods
            regime_ml = self._detect_regime_ml(features)
            regime_technical = self._detect_regime_technical(ohlcv_data, features)
            regime_volatility = self._detect_regime_volatility(ohlcv_data, features)

            # Combine results
            final_regime = self._combine_regime_results(
                regime_ml, regime_technical, regime_volatility
            )

            # Calculate regime probabilities
            regime_probs = self._calculate_regime_probabilities(features)

            # Generate analysis
            analysis = self._generate_regime_analysis(
                final_regime, features, regime_probs, ohlcv_data
            )

            logger.info(
                f"Detected regime: {analysis.current_regime.value} "
                f"(confidence: {analysis.confidence:.2f})"
            )

            return analysis

        except Exception as e:
            logger.error(f"Error in regime detection: {e}")
            return self._get_default_regime_analysis()

    def _calculate_features(
        self,
        ohlcv_data: pd.DataFrame,
        volume_data: pd.Series = None,
        market_data: pd.DataFrame = None,
    ) -> dict[str, float]:
        """Calculate comprehensive feature set for regime detection"""
        features = {}

        try:
            # Price-based features
            close = ohlcv_data["close"].values
            high = ohlcv_data["high"].values
            low = ohlcv_data["low"].values
            open_price = ohlcv_data["open"].values

            # Returns
            returns = np.diff(close) / close[:-1]
            features["mean_return"] = np.mean(returns)
            features["std_return"] = np.std(returns)
            features["skewness"] = self._calculate_skewness(returns)
            features["kurtosis"] = self._calculate_kurtosis(returns)

            # Trend features
            features["trend_strength"] = self._calculate_trend_strength(close)
            features["trend_direction"] = self._calculate_trend_direction(close)
            features["momentum"] = self._calculate_momentum(close)

            # Volatility features
            features["volatility"] = self._calculate_volatility(close)
            features["volatility_ratio"] = self._calculate_volatility_ratio(close)
            features["atr_ratio"] = self._calculate_atr_ratio(high, low, close)

            # Technical indicators
            features["rsi"] = self._calculate_rsi(close)
            features["macd_signal"] = self._calculate_macd_signal(close)
            features["bollinger_position"] = self._calculate_bollinger_position(close)
            features["adx"] = self._calculate_adx(high, low, close)

            # Volume features
            if volume_data is not None:
                features["volume_trend"] = self._calculate_volume_trend(volume_data)
                features["volume_volatility"] = self._calculate_volume_volatility(
                    volume_data
                )
                features["price_volume_correlation"] = (
                    self._calculate_price_volume_correlation(close, volume_data)
                )

            # Market regime features
            features["regime_persistence"] = self._calculate_regime_persistence(close)
            features["breakout_potential"] = self._calculate_breakout_potential(
                close, high, low
            )
            features["reversal_potential"] = self._calculate_reversal_potential(close)

            # Market structure features
            features["support_resistance_strength"] = self._calculate_sr_strength(
                high, low
            )
            features["consolidation_ratio"] = self._calculate_consolidation_ratio(close)

            # Additional market data features
            if market_data is not None:
                features.update(self._calculate_market_features(market_data))

            # Ensure all features are finite
            for key, value in features.items():
                if not np.isfinite(value):
                    features[key] = 0.0

        except Exception as e:
            logger.error(f"Error calculating features: {e}")
            # Return default features
            features = self._get_default_features()

        return features

    def _detect_regime_ml(
        self, features: dict[str, float]
    ) -> tuple[MarketRegime, float]:
        """Detect regime using trained ML model"""
        if not self.is_trained:
            return MarketRegime.RANGING, 0.5

        try:
            # Prepare features for prediction
            feature_vector = np.array([list(features.values())]).reshape(1, -1)
            feature_vector = self.scaler.transform(feature_vector)

            # Predict regime
            regime_probs = self.regime_classifier.predict_proba(feature_vector)[0]
            regime_idx = np.argmax(regime_probs)
            confidence = regime_probs[regime_idx]

            # Map to regime
            regime_mapping = {
                0: MarketRegime.TRENDING_BULL,
                1: MarketRegime.TRENDING_BEAR,
                2: MarketRegime.RANGING,
                3: MarketRegime.HIGH_VOLATILITY,
                4: MarketRegime.LOW_VOLATILITY,
                5: MarketRegime.BREAKOUT,
                6: MarketRegime.REVERSAL,
                7: MarketRegime.ACCUMULATION,
                8: MarketRegime.DISTRIBUTION,
            }

            regime = regime_mapping.get(regime_idx, MarketRegime.RANGING)
            return regime, confidence

        except Exception as e:
            logger.error(f"Error in ML regime detection: {e}")
            return MarketRegime.RANGING, 0.5

    def _detect_regime_technical(
        self, ohlcv_data: pd.DataFrame, features: dict[str, float]
    ) -> tuple[MarketRegime, float]:
        """Detect regime using technical analysis"""
        try:
            close = ohlcv_data["close"].values

            # Trend analysis
            trend_strength = features["trend_strength"]
            trend_direction = features["trend_direction"]

            # Volatility analysis
            volatility = features["volatility"]

            # Momentum analysis
            momentum = features["momentum"]

            # Determine regime based on technical indicators
            if trend_strength > 0.6:
                if trend_direction > 0:
                    return MarketRegime.TRENDING_BULL, min(trend_strength, 0.9)
                else:
                    return MarketRegime.TRENDING_BEAR, min(trend_strength, 0.9)
            elif volatility > self.volatility_threshold * 2:
                return MarketRegime.HIGH_VOLATILITY, min(volatility * 10, 0.9)
            elif volatility < self.volatility_threshold * 0.5:
                return MarketRegime.LOW_VOLATILITY, min(0.9, 1.0 - volatility * 20)
            elif abs(momentum) > 0.1:
                return MarketRegime.BREAKOUT, min(abs(momentum) * 2, 0.8)
            else:
                return MarketRegime.RANGING, 0.6

        except Exception as e:
            logger.error(f"Error in technical regime detection: {e}")
            return MarketRegime.RANGING, 0.5

    def _detect_regime_volatility(
        self, ohlcv_data: pd.DataFrame, features: dict[str, float]
    ) -> tuple[MarketRegime, float]:
        """Detect regime based on volatility patterns"""
        try:
            volatility = features["volatility"]
            volatility_ratio = features["volatility_ratio"]

            # High volatility regime
            if volatility > self.volatility_threshold * 1.5:
                return MarketRegime.HIGH_VOLATILITY, min(volatility * 15, 0.9)

            # Low volatility regime
            elif volatility < self.volatility_threshold * 0.5:
                return MarketRegime.LOW_VOLATILITY, min(0.9, 1.0 - volatility * 20)

            # Normal volatility - check for other patterns
            elif volatility_ratio > 1.5:
                return MarketRegime.BREAKOUT, min(volatility_ratio * 0.3, 0.8)
            else:
                return MarketRegime.RANGING, 0.6

        except Exception as e:
            logger.error(f"Error in volatility regime detection: {e}")
            return MarketRegime.RANGING, 0.5

    def _combine_regime_results(
        self,
        regime_ml: tuple[MarketRegime, float],
        regime_technical: tuple[MarketRegime, float],
        regime_volatility: tuple[MarketRegime, float],
    ) -> MarketRegime:
        """Combine multiple regime detection results"""
        # Weighted voting system
        regimes = [regime_ml[0], regime_technical[0], regime_volatility[0]]
        confidences = [regime_ml[1], regime_technical[1], regime_volatility[1]]

        # Count votes with confidence weighting
        regime_scores = {}
        for regime, confidence in zip(regimes, confidences, strict=False):
            if regime not in regime_scores:
                regime_scores[regime] = 0
            regime_scores[regime] += confidence

        # Return regime with highest score
        return max(regime_scores.items(), key=lambda x: x[1])[0]

    def _calculate_regime_probabilities(
        self, features: dict[str, float]
    ) -> dict[MarketRegime, float]:
        """Calculate probabilities for each regime"""
        probabilities = {}

        try:
            if self.is_trained:
                # Use ML model probabilities
                feature_vector = np.array([list(features.values())]).reshape(1, -1)
                feature_vector = self.scaler.transform(feature_vector)
                regime_probs = self.regime_classifier.predict_proba(feature_vector)[0]

                regime_mapping = {
                    0: MarketRegime.TRENDING_BULL,
                    1: MarketRegime.TRENDING_BEAR,
                    2: MarketRegime.RANGING,
                    3: MarketRegime.HIGH_VOLATILITY,
                    4: MarketRegime.LOW_VOLATILITY,
                    5: MarketRegime.BREAKOUT,
                    6: MarketRegime.REVERSAL,
                    7: MarketRegime.ACCUMULATION,
                    8: MarketRegime.DISTRIBUTION,
                }

                for i, prob in enumerate(regime_probs):
                    regime = regime_mapping.get(i, MarketRegime.RANGING)
                    probabilities[regime] = float(prob)
            else:
                # Use heuristic probabilities
                probabilities = self._calculate_heuristic_probabilities(features)

        except Exception as e:
            logger.error(f"Error calculating regime probabilities: {e}")
            probabilities = dict.fromkeys(MarketRegime, 0.1)
            probabilities[MarketRegime.RANGING] = 0.4

        return probabilities

    def _generate_regime_analysis(
        self,
        regime: MarketRegime,
        features: dict[str, float],
        regime_probs: dict[MarketRegime, float],
        ohlcv_data: pd.DataFrame,
    ) -> RegimeAnalysis:
        """Generate comprehensive regime analysis"""

        # Calculate derived metrics
        confidence = regime_probs.get(regime, 0.5)
        regime_strength = self._get_regime_strength(confidence)
        trend_direction = self._get_trend_direction(regime, features)
        volatility_level = self._get_volatility_level(features["volatility"])
        momentum_score = features.get("momentum", 0.0)

        # Calculate regime duration (simplified)
        regime_duration = self._estimate_regime_duration(ohlcv_data)

        # Generate trading implications
        trading_implications = self._get_trading_implications(regime, features)

        # Calculate risk level
        risk_level = self._calculate_risk_level(regime, features)

        # Get recommended strategies
        recommended_strategies = self._get_recommended_strategies(regime, features)

        return RegimeAnalysis(
            current_regime=regime,
            confidence=confidence,
            regime_strength=regime_strength,
            trend_direction=trend_direction,
            volatility_level=volatility_level,
            momentum_score=momentum_score,
            regime_duration=regime_duration,
            regime_probability=regime_probs,
            key_indicators=features,
            trading_implications=trading_implications,
            risk_level=risk_level,
            recommended_strategies=recommended_strategies,
        )

    # Helper methods for feature calculation
    def _calculate_skewness(self, returns: np.ndarray) -> float:
        """Calculate skewness of returns"""
        from scipy.stats import skew

        return float(skew(returns))

    def _calculate_kurtosis(self, returns: np.ndarray) -> float:
        """Calculate kurtosis of returns"""
        from scipy.stats import kurtosis

        return float(kurtosis(returns))

    def _calculate_trend_strength(self, close: np.ndarray) -> float:
        """Calculate trend strength using ADX"""
        if len(close) < 14:
            return 0.0
        high = np.roll(close, 1)  # Simplified high
        low = np.roll(close, -1)  # Simplified low
        adx = talib.ADX(high, low, close, timeperiod=14)
        return float(adx[-1]) / 100.0 if not np.isnan(adx[-1]) else 0.0

    def _calculate_trend_direction(self, close: np.ndarray) -> float:
        """Calculate trend direction (-1 to 1)"""
        if len(close) < 20:
            return 0.0
        sma_short = talib.SMA(close, timeperiod=10)
        sma_long = talib.SMA(close, timeperiod=20)
        if (
            len(sma_short) > 0
            and len(sma_long) > 0
            and not np.isnan(sma_short[-1])
            and not np.isnan(sma_long[-1])
        ):
            return (sma_short[-1] - sma_long[-1]) / sma_long[-1]
        return 0.0

    def _calculate_momentum(self, close: np.ndarray) -> float:
        """Calculate momentum"""
        if len(close) < 10:
            return 0.0
        return (close[-1] - close[-10]) / close[-10]

    def _calculate_volatility(self, close: np.ndarray) -> float:
        """Calculate volatility"""
        if len(close) < 20:
            return 0.0
        returns = np.diff(close) / close[:-1]
        return float(np.std(returns))

    def _calculate_volatility_ratio(self, close: np.ndarray) -> float:
        """Calculate volatility ratio (recent vs historical)"""
        if len(close) < 40:
            return 1.0
        recent_vol = self._calculate_volatility(close[-20:])
        historical_vol = self._calculate_volatility(close[:-20])
        return recent_vol / historical_vol if historical_vol > 0 else 1.0

    def _calculate_atr_ratio(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> float:
        """Calculate ATR ratio"""
        if len(close) < 14:
            return 0.0
        atr = talib.ATR(high, low, close, timeperiod=14)
        return float(atr[-1] / close[-1]) if not np.isnan(atr[-1]) else 0.0

    def _calculate_rsi(self, close: np.ndarray) -> float:
        """Calculate RSI"""
        if len(close) < 14:
            return 50.0
        rsi = talib.RSI(close, timeperiod=14)
        return float(rsi[-1]) / 100.0 if not np.isnan(rsi[-1]) else 0.5

    def _calculate_macd_signal(self, close: np.ndarray) -> float:
        """Calculate MACD signal"""
        if len(close) < 26:
            return 0.0
        macd, signal, _ = talib.MACD(close)
        if (
            len(macd) > 0
            and len(signal) > 0
            and not np.isnan(macd[-1])
            and not np.isnan(signal[-1])
        ):
            return float(macd[-1] - signal[-1])
        return 0.0

    def _calculate_bollinger_position(self, close: np.ndarray) -> float:
        """Calculate Bollinger Bands position"""
        if len(close) < 20:
            return 0.5
        upper, middle, lower = talib.BBANDS(close, timeperiod=20)
        if not np.isnan(upper[-1]) and not np.isnan(lower[-1]):
            return float((close[-1] - lower[-1]) / (upper[-1] - lower[-1]))
        return 0.5

    def _calculate_adx(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> float:
        """Calculate ADX"""
        if len(close) < 14:
            return 0.0
        adx = talib.ADX(high, low, close, timeperiod=14)
        return float(adx[-1]) / 100.0 if not np.isnan(adx[-1]) else 0.0

    def _calculate_volume_trend(self, volume: pd.Series) -> float:
        """Calculate volume trend"""
        if len(volume) < 10:
            return 0.0
        return float(volume.tail(5).mean() / volume.head(5).mean() - 1.0)

    def _calculate_volume_volatility(self, volume: pd.Series) -> float:
        """Calculate volume volatility"""
        if len(volume) < 10:
            return 0.0
        return float(volume.std() / volume.mean())

    def _calculate_price_volume_correlation(
        self, close: np.ndarray, volume: pd.Series
    ) -> float:
        """Calculate price-volume correlation"""
        if len(close) != len(volume):
            return 0.0
        return float(np.corrcoef(close, volume)[0, 1])

    def _calculate_regime_persistence(self, close: np.ndarray) -> float:
        """Calculate regime persistence"""
        if len(close) < 20:
            return 0.0
        # Simplified persistence calculation
        returns = np.diff(close) / close[:-1]
        return float(np.mean(np.abs(returns)))

    def _calculate_breakout_potential(
        self, close: np.ndarray, high: np.ndarray, low: np.ndarray
    ) -> float:
        """Calculate breakout potential"""
        if len(close) < 20:
            return 0.0
        recent_high = np.max(high[-10:])
        recent_low = np.min(low[-10:])
        current_price = close[-1]
        return float((current_price - recent_low) / (recent_high - recent_low))

    def _calculate_reversal_potential(self, close: np.ndarray) -> float:
        """Calculate reversal potential"""
        if len(close) < 20:
            return 0.0
        # Simplified reversal potential
        returns = np.diff(close) / close[:-1]
        return float(np.std(returns))

    def _calculate_sr_strength(self, high: np.ndarray, low: np.ndarray) -> float:
        """Calculate support/resistance strength"""
        if len(high) < 20:
            return 0.0
        # Simplified SR strength
        return float(np.std(high) / np.mean(high))

    def _calculate_consolidation_ratio(self, close: np.ndarray) -> float:
        """Calculate consolidation ratio"""
        if len(close) < 20:
            return 0.0
        recent_range = np.max(close[-10:]) - np.min(close[-10:])
        historical_range = np.max(close) - np.min(close)
        return float(recent_range / historical_range)

    def _calculate_market_features(self, market_data: pd.DataFrame) -> dict[str, float]:
        """Calculate additional market features"""
        features = {}

        # VIX features
        if "vix" in market_data.columns:
            vix = market_data["vix"].values
            features["vix_level"] = float(vix[-1]) if len(vix) > 0 else 20.0
            features["vix_trend"] = (
                float(np.mean(np.diff(vix[-5:]))) if len(vix) > 5 else 0.0
            )

        # Sector features
        if "sector_performance" in market_data.columns:
            sector_perf = market_data["sector_performance"].values
            features["sector_dispersion"] = (
                float(np.std(sector_perf)) if len(sector_perf) > 0 else 0.0
            )

        return features

    def _get_default_features(self) -> dict[str, float]:
        """Get default feature values"""
        return {
            "mean_return": 0.0,
            "std_return": 0.02,
            "skewness": 0.0,
            "kurtosis": 3.0,
            "trend_strength": 0.0,
            "trend_direction": 0.0,
            "momentum": 0.0,
            "volatility": 0.02,
            "volatility_ratio": 1.0,
            "atr_ratio": 0.02,
            "rsi": 0.5,
            "macd_signal": 0.0,
            "bollinger_position": 0.5,
            "adx": 0.0,
            "volume_trend": 0.0,
            "volume_volatility": 0.0,
            "price_volume_correlation": 0.0,
            "regime_persistence": 0.0,
            "breakout_potential": 0.5,
            "reversal_potential": 0.0,
            "support_resistance_strength": 0.0,
            "consolidation_ratio": 0.5,
        }

    def _get_regime_strength(self, confidence: float) -> str:
        """Get regime strength based on confidence"""
        if confidence >= 0.8:
            return "very_strong"
        elif confidence >= 0.7:
            return "strong"
        elif confidence >= 0.6:
            return "moderate"
        else:
            return "weak"

    def _get_trend_direction(
        self, regime: MarketRegime, features: dict[str, float]
    ) -> str:
        """Get trend direction based on regime and features"""
        if regime == MarketRegime.TRENDING_BULL:
            return "bullish"
        elif regime == MarketRegime.TRENDING_BEAR:
            return "bearish"
        elif features.get("trend_direction", 0) > 0.05:
            return "bullish"
        elif features.get("trend_direction", 0) < -0.05:
            return "bearish"
        else:
            return "neutral"

    def _get_volatility_level(self, volatility: float) -> str:
        """Get volatility level"""
        if volatility > 0.05:
            return "extreme"
        elif volatility > 0.03:
            return "high"
        elif volatility > 0.015:
            return "medium"
        else:
            return "low"

    def _estimate_regime_duration(self, ohlcv_data: pd.DataFrame) -> int:
        """Estimate regime duration (simplified)"""
        # This would require historical regime tracking
        return 10  # Placeholder

    def _get_trading_implications(
        self, regime: MarketRegime, features: dict[str, float]
    ) -> list[str]:
        """Get trading implications for regime"""
        implications = []

        if regime == MarketRegime.TRENDING_BULL:
            implications.extend(
                [
                    "Favor long positions and momentum strategies",
                    "Use pullbacks as buying opportunities",
                    "Consider trend-following indicators",
                ]
            )
        elif regime == MarketRegime.TRENDING_BEAR:
            implications.extend(
                [
                    "Favor short positions and defensive strategies",
                    "Use rallies as selling opportunities",
                    "Consider contrarian indicators",
                ]
            )
        elif regime == MarketRegime.HIGH_VOLATILITY:
            implications.extend(
                [
                    "Increase position sizing carefully",
                    "Use wider stop losses",
                    "Consider volatility-based strategies",
                ]
            )
        elif regime == MarketRegime.RANGING:
            implications.extend(
                [
                    "Use range-bound strategies",
                    "Buy support, sell resistance",
                    "Consider mean reversion strategies",
                ]
            )

        return implications

    def _calculate_risk_level(
        self, regime: MarketRegime, features: dict[str, float]
    ) -> str:
        """Calculate risk level based on regime and features"""
        volatility = features.get("volatility", 0.02)

        if regime == MarketRegime.HIGH_VOLATILITY or volatility > 0.05:
            return "extreme"
        elif (
            regime in [MarketRegime.TRENDING_BEAR, MarketRegime.REVERSAL]
            or volatility > 0.03
        ):
            return "high"
        elif (
            regime in [MarketRegime.TRENDING_BULL, MarketRegime.BREAKOUT]
            or volatility > 0.02
        ):
            return "medium"
        else:
            return "low"

    def _get_recommended_strategies(
        self, regime: MarketRegime, features: dict[str, float]
    ) -> list[str]:
        """Get recommended strategies for regime"""
        strategies = []

        if regime == MarketRegime.TRENDING_BULL:
            strategies.extend(
                ["Momentum trading", "Trend following", "Breakout strategies"]
            )
        elif regime == MarketRegime.TRENDING_BEAR:
            strategies.extend(
                ["Short selling", "Contrarian strategies", "Defensive positioning"]
            )
        elif regime == MarketRegime.RANGING:
            strategies.extend(["Mean reversion", "Range trading", "Options strategies"])
        elif regime == MarketRegime.HIGH_VOLATILITY:
            strategies.extend(
                ["Volatility trading", "Options strategies", "Risk management"]
            )
        elif regime == MarketRegime.BREAKOUT:
            strategies.extend(
                ["Breakout trading", "Momentum strategies", "Volume analysis"]
            )

        return strategies

    def _calculate_heuristic_probabilities(
        self, features: dict[str, float]
    ) -> dict[MarketRegime, float]:
        """Calculate heuristic regime probabilities"""
        probs = dict.fromkeys(MarketRegime, 0.1)

        # Adjust based on features
        trend_strength = features.get("trend_strength", 0)
        trend_direction = features.get("trend_direction", 0)
        volatility = features.get("volatility", 0.02)

        if trend_strength > 0.6:
            if trend_direction > 0:
                probs[MarketRegime.TRENDING_BULL] = 0.4
            else:
                probs[MarketRegime.TRENDING_BEAR] = 0.4
        elif volatility > 0.03:
            probs[MarketRegime.HIGH_VOLATILITY] = 0.4
        elif volatility < 0.01:
            probs[MarketRegime.LOW_VOLATILITY] = 0.4
        else:
            probs[MarketRegime.RANGING] = 0.4

        return probs

    def _get_default_regime_analysis(self) -> RegimeAnalysis:
        """Get default regime analysis when detection fails"""
        return RegimeAnalysis(
            current_regime=MarketRegime.RANGING,
            confidence=0.5,
            regime_strength="moderate",
            trend_direction="neutral",
            volatility_level="medium",
            momentum_score=0.0,
            regime_duration=10,
            regime_probability=dict.fromkeys(MarketRegime, 0.1),
            key_indicators={},
            trading_implications=["Monitor market conditions", "Use risk management"],
            risk_level="medium",
            recommended_strategies=["Conservative strategies", "Risk management"],
        )
