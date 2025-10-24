"""
Trade Signal Generator
Combines technical indicators with sentiment analysis to generate trade signals
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import pandas as pd
from pydantic import BaseModel

from .feature_engineering import FeatureEngineer
from .sentiment_analyzer import SentimentAnalyzer, SentimentScore

logger = logging.getLogger(__name__)


class SignalType(str, Enum):
    """Trade signal types"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class SignalStrength(str, Enum):
    """Signal strength levels"""

    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"


class TradeSignal(BaseModel):
    """Generated trade signal"""

    symbol: str
    signal: SignalType
    strength: SignalStrength
    confidence: float  # 0.0 to 1.0
    price: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    reasoning: str
    technical_score: float  # -1.0 to 1.0
    sentiment_score: float  # -1.0 to 1.0
    combined_score: float  # -1.0 to 1.0
    timestamp: datetime
    indicators: Dict[str, float]  # Key technical indicators


class SignalGenerator:
    """Generates trade signals using ML and sentiment analysis"""

    def __init__(
        self,
        sentiment_weight: float = 0.3,
        technical_weight: float = 0.7,
    ):
        """
        Initialize signal generator

        Args:
            sentiment_weight: Weight for sentiment score (0-1)
            technical_weight: Weight for technical score (0-1)
        """
        self.sentiment_analyzer = SentimentAnalyzer()
        self.feature_engineer = FeatureEngineer()
        self.sentiment_weight = sentiment_weight
        self.technical_weight = technical_weight

    async def generate_signal(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        news_articles: Optional[List[Dict]] = None,
    ) -> TradeSignal:
        """
        Generate a trade signal for a symbol

        Args:
            symbol: Stock/asset symbol
            price_data: Historical price DataFrame (OHLCV)
            news_articles: Optional news articles for sentiment

        Returns:
            TradeSignal with recommendation
        """
        try:
            # 1. Calculate technical indicators
            technical_score, indicators = self._calculate_technical_score(price_data)

            # 2. Get sentiment score
            sentiment_score = 0.0
            sentiment_reasoning = "No sentiment data available"

            if news_articles:
                sentiment_result = await self.sentiment_analyzer.analyze_news_batch(
                    symbol, news_articles
                )
                sentiment_score = sentiment_result.score
                sentiment_reasoning = sentiment_result.reasoning

            # 3. Combine scores
            combined_score = (
                technical_score * self.technical_weight + sentiment_score * self.sentiment_weight
            )

            # 4. Generate signal
            signal, strength, confidence = self._determine_signal(
                combined_score, technical_score, sentiment_score
            )

            # 5. Calculate targets
            current_price = float(price_data["close"].iloc[-1])
            target_price, stop_loss = self._calculate_targets(
                current_price, signal, strength, indicators
            )

            # 6. Generate reasoning
            reasoning = self._generate_reasoning(
                signal,
                technical_score,
                sentiment_score,
                indicators,
                sentiment_reasoning,
            )

            return TradeSignal(
                symbol=symbol,
                signal=signal,
                strength=strength,
                confidence=confidence,
                price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                reasoning=reasoning,
                technical_score=technical_score,
                sentiment_score=sentiment_score,
                combined_score=combined_score,
                timestamp=datetime.utcnow(),
                indicators=indicators,
            )

        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            # Return HOLD signal on error
            return self._create_hold_signal(symbol, str(e))

    def _calculate_technical_score(self, df: pd.DataFrame) -> tuple[float, Dict[str, float]]:
        """
        Calculate technical analysis score

        Returns:
            (score, indicators_dict)
        """
        # Calculate indicators
        df_with_indicators = self.feature_engineer.add_technical_indicators(df)

        # Extract latest values
        latest = df_with_indicators.iloc[-1]

        indicators = {
            "rsi": float(latest.get("rsi_14", 50)),
            "macd": float(latest.get("macd", 0)),
            "macd_signal": float(latest.get("macd_signal", 0)),
            "bb_position": float(latest.get("bb_position", 0)),  # Position within Bollinger Bands
            "sma_20": float(latest.get("sma_20", latest["close"])),
            "sma_50": float(latest.get("sma_50", latest["close"])),
            "volume_ratio": float(latest.get("volume_ratio", 1)),  # Current vs average volume
        }

        # Calculate composite technical score
        score = 0.0
        weight_sum = 0.0

        # RSI (30 = oversold/bullish, 70 = overbought/bearish)
        if indicators["rsi"] < 30:
            score += 0.8 * 0.25  # Bullish
            weight_sum += 0.25
        elif indicators["rsi"] > 70:
            score -= 0.8 * 0.25  # Bearish
            weight_sum += 0.25
        else:
            # Neutral zone
            rsi_normalized = (indicators["rsi"] - 50) / 20  # -1 to 1
            score += rsi_normalized * 0.25
            weight_sum += 0.25

        # MACD (above signal = bullish, below = bearish)
        macd_diff = indicators["macd"] - indicators["macd_signal"]
        macd_score = max(-1, min(1, macd_diff * 10))  # Normalize
        score += macd_score * 0.3
        weight_sum += 0.3

        # Bollinger Bands position (0 = lower band, 1 = upper band)
        bb_score = (indicators["bb_position"] - 0.5) * 2  # Convert to -1 to 1
        score += bb_score * 0.2
        weight_sum += 0.2

        # Moving Average Crossover
        price = float(latest["close"])
        if price > indicators["sma_20"] > indicators["sma_50"]:
            score += 0.5 * 0.15  # Bullish
            weight_sum += 0.15
        elif price < indicators["sma_20"] < indicators["sma_50"]:
            score -= 0.5 * 0.15  # Bearish
            weight_sum += 0.15
        else:
            weight_sum += 0.15

        # Volume confirmation
        if indicators["volume_ratio"] > 1.5:
            score *= 1.1  # Amplify signal with high volume
        elif indicators["volume_ratio"] < 0.5:
            score *= 0.9  # Reduce signal with low volume

        # Normalize score
        if weight_sum > 0:
            score = score / weight_sum

        # Clamp to [-1, 1]
        score = max(-1.0, min(1.0, score))

        return score, indicators

    def _determine_signal(
        self, combined_score: float, technical_score: float, sentiment_score: float
    ) -> tuple[SignalType, SignalStrength, float]:
        """
        Determine signal type, strength, and confidence

        Returns:
            (signal, strength, confidence)
        """
        # Determine signal type
        if combined_score > 0.3:
            signal = SignalType.BUY
        elif combined_score < -0.3:
            signal = SignalType.SELL
        else:
            signal = SignalType.HOLD

        # Determine strength
        abs_score = abs(combined_score)
        if abs_score > 0.7:
            strength = SignalStrength.STRONG
        elif abs_score > 0.4:
            strength = SignalStrength.MODERATE
        else:
            strength = SignalStrength.WEAK

        # Calculate confidence (agreement between technical and sentiment)
        agreement = 1 - abs(technical_score - sentiment_score) / 2
        confidence = (abs_score + agreement) / 2
        confidence = max(0.0, min(1.0, confidence))

        return signal, strength, confidence

    def _calculate_targets(
        self,
        current_price: float,
        signal: SignalType,
        strength: SignalStrength,
        indicators: Dict[str, float],
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Calculate target price and stop loss

        Returns:
            (target_price, stop_loss)
        """
        if signal == SignalType.HOLD:
            return None, None

        # Base risk/reward on signal strength
        if strength == SignalStrength.STRONG:
            target_pct = 0.05  # 5% target
            stop_pct = 0.02  # 2% stop loss
        elif strength == SignalStrength.MODERATE:
            target_pct = 0.03  # 3% target
            stop_pct = 0.015  # 1.5% stop loss
        else:  # WEAK
            target_pct = 0.02  # 2% target
            stop_pct = 0.01  # 1% stop loss

        if signal == SignalType.BUY:
            target_price = current_price * (1 + target_pct)
            stop_loss = current_price * (1 - stop_pct)
        else:  # SELL
            target_price = current_price * (1 - target_pct)
            stop_loss = current_price * (1 + stop_pct)

        return round(target_price, 2), round(stop_loss, 2)

    def _generate_reasoning(
        self,
        signal: SignalType,
        technical_score: float,
        sentiment_score: float,
        indicators: Dict[str, float],
        sentiment_reasoning: str,
    ) -> str:
        """Generate human-readable reasoning for the signal"""
        parts = []

        # Overall signal
        parts.append(
            f"{signal.value} signal with technical score {technical_score:.2f} and sentiment score {sentiment_score:.2f}."
        )

        # Technical analysis
        tech_parts = []
        if indicators["rsi"] < 30:
            tech_parts.append("RSI oversold")
        elif indicators["rsi"] > 70:
            tech_parts.append("RSI overbought")

        macd_diff = indicators["macd"] - indicators["macd_signal"]
        if macd_diff > 0:
            tech_parts.append("MACD bullish crossover")
        elif macd_diff < 0:
            tech_parts.append("MACD bearish crossover")

        if tech_parts:
            parts.append(f"Technical: {', '.join(tech_parts)}.")

        # Sentiment
        parts.append(f"Sentiment: {sentiment_reasoning}")

        return " ".join(parts)

    def _create_hold_signal(self, symbol: str, error: str) -> TradeSignal:
        """Create a HOLD signal (fallback)"""
        return TradeSignal(
            symbol=symbol,
            signal=SignalType.HOLD,
            strength=SignalStrength.WEAK,
            confidence=0.0,
            price=0.0,
            target_price=None,
            stop_loss=None,
            reasoning=f"Unable to generate signal: {error}",
            technical_score=0.0,
            sentiment_score=0.0,
            combined_score=0.0,
            timestamp=datetime.utcnow(),
            indicators={},
        )


# Global instance
_signal_generator: Optional[SignalGenerator] = None


def get_signal_generator() -> SignalGenerator:
    """Get or create signal generator instance"""
    global _signal_generator
    if _signal_generator is None:
        _signal_generator = SignalGenerator()
    return _signal_generator
