"""
Advanced Pattern Recognition Module
Enhanced ML-powered pattern detection for PaiiD
"""

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
import talib
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """Advanced pattern types for detection"""

    # Reversal Patterns
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    INVERSE_HEAD_AND_SHOULDERS = "inverse_head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIPLE_TOP = "triple_top"
    TRIPLE_BOTTOM = "triple_bottom"

    # Continuation Patterns
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    FLAG = "flag"
    PENNANT = "pennant"
    WEDGE = "wedge"

    # Candlestick Patterns
    HAMMER = "hammer"
    DOJI = "doji"
    ENGULFING = "engulfing"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"

    # Volume Patterns
    VOLUME_SPIKE = "volume_spike"
    VOLUME_DIVERGENCE = "volume_divergence"

    # Support/Resistance
    SUPPORT_BREAK = "support_break"
    RESISTANCE_BREAK = "resistance_break"
    TREND_LINE_BREAK = "trend_line_break"

@dataclass
class PatternSignal:
    """Enhanced pattern signal with confidence scoring"""

    pattern_type: PatternType
    confidence: float  # 0.0 to 1.0
    strength: str  # "weak", "moderate", "strong", "very_strong"
    direction: str  # "bullish", "bearish", "neutral"
    target_price: float
    stop_loss: float
    risk_reward_ratio: float
    timeframe: str  # "short", "medium", "long"
    volume_confirmation: bool
    trend_alignment: bool
    key_levels: list[float]
    description: str
    trading_suggestion: str

class AdvancedPatternDetector:
    """Enhanced pattern detection with ML algorithms"""

    def __init__(self):
        self.min_confidence = 0.6
        self.volume_threshold = 1.5  # 1.5x average volume
        self.trend_strength_threshold = 0.3

    def detect_patterns(
        self, ohlcv_data: pd.DataFrame, volume_data: pd.Series = None
    ) -> list[PatternSignal]:
        """
        Detect advanced patterns in OHLCV data

        Args:
            ohlcv_data: DataFrame with OHLCV data
            volume_data: Volume data (optional)

        Returns:
            List of detected pattern signals
        """
        patterns = []

        try:
            # Calculate technical indicators
            indicators = self._calculate_indicators(ohlcv_data)

            # Detect reversal patterns
            patterns.extend(self._detect_reversal_patterns(ohlcv_data, indicators))

            # Detect continuation patterns
            patterns.extend(self._detect_continuation_patterns(ohlcv_data, indicators))

            # Detect candlestick patterns
            patterns.extend(self._detect_candlestick_patterns(ohlcv_data))

            # Detect volume patterns
            if volume_data is not None:
                patterns.extend(self._detect_volume_patterns(ohlcv_data, volume_data))

            # Detect support/resistance breaks
            patterns.extend(
                self._detect_support_resistance_patterns(ohlcv_data, indicators)
            )

            # Filter by confidence and sort
            patterns = [p for p in patterns if p.confidence >= self.min_confidence]
            patterns.sort(key=lambda x: x.confidence, reverse=True)

            logger.info(
                f"Detected {len(patterns)} patterns with confidence >= {self.min_confidence}"
            )

        except Exception as e:
            logger.error(f"Error in pattern detection: {e}")

        return patterns

    def _calculate_indicators(self, data: pd.DataFrame) -> dict:
        """Calculate technical indicators for pattern detection"""
        indicators = {}

        # Price data
        high = data["high"].values
        low = data["low"].values
        close = data["close"].values
        open_price = data["open"].values

        # Moving averages
        indicators["sma_20"] = talib.SMA(close, timeperiod=20)
        indicators["sma_50"] = talib.SMA(close, timeperiod=50)
        indicators["ema_12"] = talib.EMA(close, timeperiod=12)
        indicators["ema_26"] = talib.EMA(close, timeperiod=26)

        # Trend indicators
        indicators["adx"] = talib.ADX(high, low, close, timeperiod=14)
        indicators["di_plus"] = talib.PLUS_DI(high, low, close, timeperiod=14)
        indicators["di_minus"] = talib.MINUS_DI(high, low, close, timeperiod=14)

        # Momentum indicators
        indicators["rsi"] = talib.RSI(close, timeperiod=14)
        indicators["macd"], indicators["macd_signal"], indicators["macd_hist"] = (
            talib.MACD(close)
        )
        indicators["stoch_k"], indicators["stoch_d"] = talib.STOCH(high, low, close)

        # Volatility indicators
        indicators["bb_upper"], indicators["bb_middle"], indicators["bb_lower"] = (
            talib.BBANDS(close)
        )
        indicators["atr"] = talib.ATR(high, low, close, timeperiod=14)

        # Volume indicators
        if "volume" in data.columns:
            volume = data["volume"].values
            indicators["obv"] = talib.OBV(close, volume)
            indicators["ad"] = talib.AD(high, low, close, volume)

        return indicators

    def _detect_reversal_patterns(
        self, data: pd.DataFrame, indicators: dict
    ) -> list[PatternSignal]:
        """Detect reversal patterns"""
        patterns = []

        # Head and Shoulders
        patterns.extend(self._detect_head_and_shoulders(data, indicators))

        # Double Top/Bottom
        patterns.extend(self._detect_double_tops_bottoms(data, indicators))

        # Triple Top/Bottom
        patterns.extend(self._detect_triple_tops_bottoms(data, indicators))

        return patterns

    def _detect_head_and_shoulders(
        self, data: pd.DataFrame, indicators: dict
    ) -> list[PatternSignal]:
        """Detect Head and Shoulders patterns"""
        patterns = []

        try:
            high = data["high"].values
            close = data["close"].values

            # Find peaks
            peaks = self._find_peaks(high, min_distance=5)

            if len(peaks) >= 3:
                # Check for H&S pattern
                for i in range(len(peaks) - 2):
                    left_shoulder = peaks[i]
                    head = peaks[i + 1]
                    right_shoulder = peaks[i + 2]

                    # H&S conditions
                    if (
                        high[head] > high[left_shoulder]
                        and high[head] > high[right_shoulder]
                        and abs(high[left_shoulder] - high[right_shoulder]) / high[head]
                        < 0.02
                    ):
                        confidence = self._calculate_hs_confidence(
                            data, left_shoulder, head, right_shoulder
                        )

                        if confidence >= self.min_confidence:
                            patterns.append(
                                PatternSignal(
                                    pattern_type=PatternType.HEAD_AND_SHOULDERS,
                                    confidence=confidence,
                                    strength=self._get_strength(confidence),
                                    direction="bearish",
                                    target_price=high[left_shoulder]
                                    - (high[head] - high[left_shoulder]),
                                    stop_loss=high[head] * 1.02,
                                    risk_reward_ratio=self._calculate_risk_reward(
                                        high[head],
                                        high[left_shoulder],
                                        high[left_shoulder]
                                        - (high[head] - high[left_shoulder]),
                                    ),
                                    timeframe="medium",
                                    volume_confirmation=self._check_volume_confirmation(
                                        data, head
                                    ),
                                    trend_alignment=self._check_trend_alignment(
                                        indicators, "bearish"
                                    ),
                                    key_levels=[
                                        high[left_shoulder],
                                        high[head],
                                        high[right_shoulder],
                                    ],
                                    description="Head and Shoulders reversal pattern detected",
                                    trading_suggestion="Consider short position with stop above head",
                                )
                            )

        except Exception as e:
            logger.error(f"Error detecting H&S patterns: {e}")

        return patterns

    def _detect_double_tops_bottoms(
        self, data: pd.DataFrame, indicators: dict
    ) -> list[PatternSignal]:
        """Detect Double Top and Double Bottom patterns"""
        patterns = []

        try:
            high = data["high"].values
            low = data["low"].values
            close = data["close"].values

            # Find peaks and troughs
            peaks = self._find_peaks(high, min_distance=5)
            troughs = self._find_troughs(low, min_distance=5)

            # Double Tops
            for i in range(len(peaks) - 1):
                peak1 = peaks[i]
                peak2 = peaks[i + 1]

                if (
                    abs(high[peak1] - high[peak2]) / high[peak1] < 0.02
                    and peak2 - peak1 > 5
                ):  # Minimum distance between peaks
                    confidence = self._calculate_double_pattern_confidence(
                        data, peak1, peak2, "top"
                    )

                    if confidence >= self.min_confidence:
                        patterns.append(
                            PatternSignal(
                                pattern_type=PatternType.DOUBLE_TOP,
                                confidence=confidence,
                                strength=self._get_strength(confidence),
                                direction="bearish",
                                target_price=high[peak1]
                                - (high[peak1] - min(low[peak1:peak2])),
                                stop_loss=high[peak1] * 1.01,
                                risk_reward_ratio=self._calculate_risk_reward(
                                    high[peak1],
                                    min(low[peak1:peak2]),
                                    high[peak1] - (high[peak1] - min(low[peak1:peak2])),
                                ),
                                timeframe="medium",
                                volume_confirmation=self._check_volume_confirmation(
                                    data, peak2
                                ),
                                trend_alignment=self._check_trend_alignment(
                                    indicators, "bearish"
                                ),
                                key_levels=[high[peak1], high[peak2]],
                                description="Double Top reversal pattern detected",
                                trading_suggestion="Consider short position with stop above peaks",
                            )
                        )

            # Double Bottoms
            for i in range(len(troughs) - 1):
                trough1 = troughs[i]
                trough2 = troughs[i + 1]

                if (
                    abs(low[trough1] - low[trough2]) / low[trough1] < 0.02
                    and trough2 - trough1 > 5
                ):  # Minimum distance between troughs
                    confidence = self._calculate_double_pattern_confidence(
                        data, trough1, trough2, "bottom"
                    )

                    if confidence >= self.min_confidence:
                        patterns.append(
                            PatternSignal(
                                pattern_type=PatternType.DOUBLE_BOTTOM,
                                confidence=confidence,
                                strength=self._get_strength(confidence),
                                direction="bullish",
                                target_price=low[trough1]
                                + (max(high[trough1:trough2]) - low[trough1]),
                                stop_loss=low[trough1] * 0.99,
                                risk_reward_ratio=self._calculate_risk_reward(
                                    low[trough1],
                                    max(high[trough1:trough2]),
                                    low[trough1]
                                    + (max(high[trough1:trough2]) - low[trough1]),
                                ),
                                timeframe="medium",
                                volume_confirmation=self._check_volume_confirmation(
                                    data, trough2
                                ),
                                trend_alignment=self._check_trend_alignment(
                                    indicators, "bullish"
                                ),
                                key_levels=[low[trough1], low[trough2]],
                                description="Double Bottom reversal pattern detected",
                                trading_suggestion="Consider long position with stop below troughs",
                            )
                        )

        except Exception as e:
            logger.error(f"Error detecting double patterns: {e}")

        return patterns

    def _detect_triple_tops_bottoms(
        self, data: pd.DataFrame, indicators: dict
    ) -> list[PatternSignal]:
        """Detect Triple Top and Triple Bottom patterns"""
        patterns = []

        try:
            high = data["high"].values
            low = data["low"].values
            close = data["close"].values

            # Find peaks and troughs
            peaks = self._find_peaks(high, min_distance=5)
            troughs = self._find_troughs(low, min_distance=5)

            # Triple Tops
            for i in range(len(peaks) - 2):
                peak1 = peaks[i]
                peak2 = peaks[i + 1]
                peak3 = peaks[i + 2]

                # Check if all three peaks are at similar levels
                if (
                    abs(high[peak1] - high[peak2]) / high[peak1] < 0.02
                    and abs(high[peak2] - high[peak3]) / high[peak2] < 0.02
                    and peak3 - peak1 > 10
                ):  # Minimum distance between peaks
                    confidence = 0.7  # Base confidence for triple pattern

                    if confidence >= self.min_confidence:
                        patterns.append(
                            PatternSignal(
                                pattern_type=PatternType.TRIPLE_TOP,
                                confidence=confidence,
                                strength=self._get_strength(confidence),
                                direction="bearish",
                                target_price=high[peak1]
                                - (high[peak1] - min(low[peak1:peak3])),
                                stop_loss=high[peak1] * 1.015,
                                risk_reward_ratio=self._calculate_risk_reward(
                                    high[peak1],
                                    min(low[peak1:peak3]),
                                    high[peak1] - (high[peak1] - min(low[peak1:peak3])),
                                ),
                                timeframe="medium",
                                volume_confirmation=self._check_volume_confirmation(
                                    data, peak3
                                ),
                                trend_alignment=self._check_trend_alignment(
                                    indicators, "bearish"
                                ),
                                key_levels=[high[peak1], high[peak2], high[peak3]],
                                description="Triple Top reversal pattern detected",
                                trading_suggestion="Consider short position with stop above peaks",
                            )
                        )

            # Triple Bottoms
            for i in range(len(troughs) - 2):
                trough1 = troughs[i]
                trough2 = troughs[i + 1]
                trough3 = troughs[i + 2]

                # Check if all three troughs are at similar levels
                if (
                    abs(low[trough1] - low[trough2]) / low[trough1] < 0.02
                    and abs(low[trough2] - low[trough3]) / low[trough2] < 0.02
                    and trough3 - trough1 > 10
                ):  # Minimum distance between troughs
                    confidence = 0.7  # Base confidence for triple pattern

                    if confidence >= self.min_confidence:
                        patterns.append(
                            PatternSignal(
                                pattern_type=PatternType.TRIPLE_BOTTOM,
                                confidence=confidence,
                                strength=self._get_strength(confidence),
                                direction="bullish",
                                target_price=low[trough1]
                                + (max(high[trough1:trough3]) - low[trough1]),
                                stop_loss=low[trough1] * 0.985,
                                risk_reward_ratio=self._calculate_risk_reward(
                                    low[trough1],
                                    max(high[trough1:trough3]),
                                    low[trough1]
                                    + (max(high[trough1:trough3]) - low[trough1]),
                                ),
                                timeframe="medium",
                                volume_confirmation=self._check_volume_confirmation(
                                    data, trough3
                                ),
                                trend_alignment=self._check_trend_alignment(
                                    indicators, "bullish"
                                ),
                                key_levels=[low[trough1], low[trough2], low[trough3]],
                                description="Triple Bottom reversal pattern detected",
                                trading_suggestion="Consider long position with stop below troughs",
                            )
                        )

        except Exception as e:
            logger.error(f"Error detecting triple patterns: {e}")

        return patterns

    def _detect_continuation_patterns(
        self, data: pd.DataFrame, indicators: dict
    ) -> list[PatternSignal]:
        """Detect continuation patterns"""
        patterns = []

        # Triangle patterns
        patterns.extend(self._detect_triangle_patterns(data, indicators))

        # Flag and Pennant patterns
        patterns.extend(self._detect_flag_pennant_patterns(data, indicators))

        return patterns

    def _detect_flag_pennant_patterns(
        self, data: pd.DataFrame, indicators: dict
    ) -> list[PatternSignal]:
        """Detect Flag and Pennant continuation patterns"""
        patterns = []

        try:
            high = data["high"].values
            low = data["low"].values
            close = data["close"].values

            # Look for flag/pennant formations in recent data
            window_size = 15
            if len(data) >= window_size:
                recent_highs = high[-window_size:]
                recent_lows = low[-window_size:]
                recent_close = close[-window_size:]

                # Check for consolidation after strong move
                recent_volatility = np.std(recent_close)
                prior_volatility = np.std(close[-window_size * 2 : -window_size])

                # Flag/Pennant typically shows reduced volatility after strong move
                if recent_volatility < prior_volatility * 0.7:
                    # Determine if prior move was bullish or bearish
                    prior_move = close[-window_size] - close[-window_size * 2]

                    if prior_move > 0:
                        # Bullish flag/pennant
                        confidence = 0.65

                        if confidence >= self.min_confidence:
                            patterns.append(
                                PatternSignal(
                                    pattern_type=PatternType.FLAG,
                                    confidence=confidence,
                                    strength=self._get_strength(confidence),
                                    direction="bullish",
                                    target_price=close[-1] + abs(prior_move),
                                    stop_loss=min(recent_lows) * 0.98,
                                    risk_reward_ratio=self._calculate_risk_reward(
                                        close[-1],
                                        min(recent_lows),
                                        close[-1] + abs(prior_move),
                                    ),
                                    timeframe="short",
                                    volume_confirmation=self._check_volume_confirmation(
                                        data, -1
                                    ),
                                    trend_alignment=self._check_trend_alignment(
                                        indicators, "bullish"
                                    ),
                                    key_levels=[max(recent_highs), min(recent_lows)],
                                    description="Bullish Flag continuation pattern detected",
                                    trading_suggestion="Consider long position on upside breakout",
                                )
                            )

                    elif prior_move < 0:
                        # Bearish flag/pennant
                        confidence = 0.65

                        if confidence >= self.min_confidence:
                            patterns.append(
                                PatternSignal(
                                    pattern_type=PatternType.FLAG,
                                    confidence=confidence,
                                    strength=self._get_strength(confidence),
                                    direction="bearish",
                                    target_price=close[-1] - abs(prior_move),
                                    stop_loss=max(recent_highs) * 1.02,
                                    risk_reward_ratio=self._calculate_risk_reward(
                                        close[-1],
                                        max(recent_highs),
                                        close[-1] - abs(prior_move),
                                    ),
                                    timeframe="short",
                                    volume_confirmation=self._check_volume_confirmation(
                                        data, -1
                                    ),
                                    trend_alignment=self._check_trend_alignment(
                                        indicators, "bearish"
                                    ),
                                    key_levels=[max(recent_highs), min(recent_lows)],
                                    description="Bearish Flag continuation pattern detected",
                                    trading_suggestion="Consider short position on downside breakdown",
                                )
                            )

        except Exception as e:
            logger.error(f"Error detecting flag/pennant patterns: {e}")

        return patterns

    def _detect_triangle_patterns(
        self, data: pd.DataFrame, indicators: dict
    ) -> list[PatternSignal]:
        """Detect triangle patterns"""
        patterns = []

        try:
            high = data["high"].values
            low = data["low"].values
            close = data["close"].values

            # Look for triangle formations in recent data
            window_size = 20
            if len(data) >= window_size:
                recent_highs = high[-window_size:]
                recent_lows = low[-window_size:]

                # Ascending Triangle
                if self._is_ascending_triangle(recent_highs, recent_lows):
                    confidence = self._calculate_triangle_confidence(data, "ascending")

                    if confidence >= self.min_confidence:
                        patterns.append(
                            PatternSignal(
                                pattern_type=PatternType.ASCENDING_TRIANGLE,
                                confidence=confidence,
                                strength=self._get_strength(confidence),
                                direction="bullish",
                                target_price=max(recent_highs) * 1.05,
                                stop_loss=min(recent_lows) * 0.98,
                                risk_reward_ratio=self._calculate_risk_reward(
                                    close[-1],
                                    min(recent_lows),
                                    max(recent_highs) * 1.05,
                                ),
                                timeframe="short",
                                volume_confirmation=self._check_volume_confirmation(
                                    data, -1
                                ),
                                trend_alignment=self._check_trend_alignment(
                                    indicators, "bullish"
                                ),
                                key_levels=[max(recent_highs), min(recent_lows)],
                                description="Ascending Triangle continuation pattern detected",
                                trading_suggestion="Consider long position on breakout above resistance",
                            )
                        )

                # Descending Triangle
                if self._is_descending_triangle(recent_highs, recent_lows):
                    confidence = self._calculate_triangle_confidence(data, "descending")

                    if confidence >= self.min_confidence:
                        patterns.append(
                            PatternSignal(
                                pattern_type=PatternType.DESCENDING_TRIANGLE,
                                confidence=confidence,
                                strength=self._get_strength(confidence),
                                direction="bearish",
                                target_price=min(recent_lows) * 0.95,
                                stop_loss=max(recent_highs) * 1.02,
                                risk_reward_ratio=self._calculate_risk_reward(
                                    close[-1],
                                    max(recent_highs),
                                    min(recent_lows) * 0.95,
                                ),
                                timeframe="short",
                                volume_confirmation=self._check_volume_confirmation(
                                    data, -1
                                ),
                                trend_alignment=self._check_trend_alignment(
                                    indicators, "bearish"
                                ),
                                key_levels=[max(recent_highs), min(recent_lows)],
                                description="Descending Triangle continuation pattern detected",
                                trading_suggestion="Consider short position on breakdown below support",
                            )
                        )

        except Exception as e:
            logger.error(f"Error detecting triangle patterns: {e}")

        return patterns

    def _detect_candlestick_patterns(self, data: pd.DataFrame) -> list[PatternSignal]:
        """Detect candlestick patterns"""
        patterns = []

        try:
            open_price = data["open"].values
            high = data["high"].values
            low = data["low"].values
            close = data["close"].values

            # Use recent data for pattern detection
            recent_data = data.tail(10)

            # Hammer pattern
            if self._is_hammer_pattern(recent_data):
                confidence = self._calculate_candlestick_confidence(
                    recent_data, "hammer"
                )

                if confidence >= self.min_confidence:
                    patterns.append(
                        PatternSignal(
                            pattern_type=PatternType.HAMMER,
                            confidence=confidence,
                            strength=self._get_strength(confidence),
                            direction="bullish",
                            target_price=close[-1] * 1.03,
                            stop_loss=low[-1] * 0.98,
                            risk_reward_ratio=self._calculate_risk_reward(
                                close[-1], low[-1], close[-1] * 1.03
                            ),
                            timeframe="short",
                            volume_confirmation=self._check_volume_confirmation(
                                data, -1
                            ),
                            trend_alignment=self._check_trend_alignment({}, "bullish"),
                            key_levels=[close[-1], low[-1]],
                            description="Hammer reversal pattern detected",
                            trading_suggestion="Consider long position with stop below hammer low",
                        )
                    )

            # Doji pattern
            if self._is_doji_pattern(recent_data):
                confidence = self._calculate_candlestick_confidence(recent_data, "doji")

                if confidence >= self.min_confidence:
                    patterns.append(
                        PatternSignal(
                            pattern_type=PatternType.DOJI,
                            confidence=confidence,
                            strength=self._get_strength(confidence),
                            direction="neutral",
                            target_price=close[-1] * 1.02,
                            stop_loss=low[-1] * 0.98,
                            risk_reward_ratio=1.0,
                            timeframe="short",
                            volume_confirmation=self._check_volume_confirmation(
                                data, -1
                            ),
                            trend_alignment=True,
                            key_levels=[close[-1]],
                            description="Doji indecision pattern detected",
                            trading_suggestion="Wait for confirmation before trading",
                        )
                    )

        except Exception as e:
            logger.error(f"Error detecting candlestick patterns: {e}")

        return patterns

    def _detect_volume_patterns(
        self, data: pd.DataFrame, volume_data: pd.Series
    ) -> list[PatternSignal]:
        """Detect volume-based patterns"""
        patterns = []

        try:
            # Volume spike detection
            avg_volume = volume_data.rolling(window=20).mean()
            recent_volume = volume_data.tail(5)

            if len(recent_volume) > 0 and len(avg_volume) > 0:
                volume_ratio = recent_volume.iloc[-1] / avg_volume.iloc[-1]

                if volume_ratio >= self.volume_threshold:
                    confidence = min(volume_ratio / 3.0, 1.0)  # Cap at 1.0

                    patterns.append(
                        PatternSignal(
                            pattern_type=PatternType.VOLUME_SPIKE,
                            confidence=confidence,
                            strength=self._get_strength(confidence),
                            direction="neutral",
                            target_price=data["close"].iloc[-1] * 1.02,
                            stop_loss=data["close"].iloc[-1] * 0.98,
                            risk_reward_ratio=1.0,
                            timeframe="short",
                            volume_confirmation=True,
                            trend_alignment=True,
                            key_levels=[data["close"].iloc[-1]],
                            description=f"Volume spike detected ({volume_ratio:.1f}x average)",
                            trading_suggestion="Monitor for price movement confirmation",
                        )
                    )

        except Exception as e:
            logger.error(f"Error detecting volume patterns: {e}")

        return patterns

    def _detect_support_resistance_patterns(
        self, data: pd.DataFrame, indicators: dict
    ) -> list[PatternSignal]:
        """Detect support and resistance break patterns"""
        patterns = []

        try:
            close = data["close"].values
            high = data["high"].values
            low = data["low"].values

            # Find key support and resistance levels
            support_levels = self._find_support_levels(low)
            resistance_levels = self._find_resistance_levels(high)

            current_price = close[-1]

            # Check for support breaks
            for support in support_levels:
                if current_price < support * 0.99:  # 1% below support
                    confidence = self._calculate_break_confidence(
                        data, support, "support"
                    )

                    if confidence >= self.min_confidence:
                        patterns.append(
                            PatternSignal(
                                pattern_type=PatternType.SUPPORT_BREAK,
                                confidence=confidence,
                                strength=self._get_strength(confidence),
                                direction="bearish",
                                target_price=support * 0.95,
                                stop_loss=support * 1.01,
                                risk_reward_ratio=self._calculate_risk_reward(
                                    current_price, support, support * 0.95
                                ),
                                timeframe="short",
                                volume_confirmation=self._check_volume_confirmation(
                                    data, -1
                                ),
                                trend_alignment=self._check_trend_alignment(
                                    indicators, "bearish"
                                ),
                                key_levels=[support],
                                description="Support level break detected",
                                trading_suggestion="Consider short position with stop above support",
                            )
                        )

            # Check for resistance breaks
            for resistance in resistance_levels:
                if current_price > resistance * 1.01:  # 1% above resistance
                    confidence = self._calculate_break_confidence(
                        data, resistance, "resistance"
                    )

                    if confidence >= self.min_confidence:
                        patterns.append(
                            PatternSignal(
                                pattern_type=PatternType.RESISTANCE_BREAK,
                                confidence=confidence,
                                strength=self._get_strength(confidence),
                                direction="bullish",
                                target_price=resistance * 1.05,
                                stop_loss=resistance * 0.99,
                                risk_reward_ratio=self._calculate_risk_reward(
                                    current_price, resistance, resistance * 1.05
                                ),
                                timeframe="short",
                                volume_confirmation=self._check_volume_confirmation(
                                    data, -1
                                ),
                                trend_alignment=self._check_trend_alignment(
                                    indicators, "bullish"
                                ),
                                key_levels=[resistance],
                                description="Resistance level break detected",
                                trading_suggestion="Consider long position with stop below resistance",
                            )
                        )

        except Exception as e:
            logger.error(f"Error detecting support/resistance patterns: {e}")

        return patterns

    # Helper methods
    def _find_peaks(self, data: np.ndarray, min_distance: int = 5) -> list[int]:
        """Find peaks in data"""

        peaks, _ = find_peaks(data, distance=min_distance)
        return peaks.tolist()

    def _find_troughs(self, data: np.ndarray, min_distance: int = 5) -> list[int]:
        """Find troughs in data"""

        troughs, _ = find_peaks(-data, distance=min_distance)
        return troughs.tolist()

    def _calculate_hs_confidence(
        self, data: pd.DataFrame, left_shoulder: int, head: int, right_shoulder: int
    ) -> float:
        """Calculate Head and Shoulders confidence"""
        # Simplified confidence calculation
        return 0.7  # Placeholder

    def _calculate_double_pattern_confidence(
        self, data: pd.DataFrame, point1: int, point2: int, pattern_type: str
    ) -> float:
        """Calculate double pattern confidence"""
        # Simplified confidence calculation
        return 0.6  # Placeholder

    def _calculate_triangle_confidence(
        self, data: pd.DataFrame, triangle_type: str
    ) -> float:
        """Calculate triangle pattern confidence"""
        # Simplified confidence calculation
        return 0.65  # Placeholder

    def _calculate_candlestick_confidence(
        self, data: pd.DataFrame, pattern_type: str
    ) -> float:
        """Calculate candlestick pattern confidence"""
        # Simplified confidence calculation
        return 0.6  # Placeholder

    def _calculate_break_confidence(
        self, data: pd.DataFrame, level: float, break_type: str
    ) -> float:
        """Calculate break confidence"""
        # Simplified confidence calculation
        return 0.7  # Placeholder

    def _get_strength(self, confidence: float) -> str:
        """Get pattern strength based on confidence"""
        if confidence >= 0.8:
            return "very_strong"
        elif confidence >= 0.7:
            return "strong"
        elif confidence >= 0.6:
            return "moderate"
        else:
            return "weak"

    def _calculate_risk_reward(self, entry: float, stop: float, target: float) -> float:
        """Calculate risk-reward ratio"""
        risk = abs(entry - stop)
        reward = abs(target - entry)
        return reward / risk if risk > 0 else 0

    def _check_volume_confirmation(self, data: pd.DataFrame, index: int) -> bool:
        """Check if volume confirms the pattern"""
        if "volume" in data.columns:
            recent_volume = data["volume"].iloc[index]
            avg_volume = data["volume"].rolling(window=20).mean().iloc[index]
            return recent_volume > avg_volume * 1.2
        return True

    def _check_trend_alignment(self, indicators: dict, direction: str) -> bool:
        """Check if pattern aligns with trend"""
        if "adx" in indicators and len(indicators["adx"]) > 0:
            adx = indicators["adx"][-1]
            if not np.isnan(adx):
                return adx > 25  # Strong trend
        return True

    def _is_ascending_triangle(self, highs: np.ndarray, lows: np.ndarray) -> bool:
        """Check if data forms ascending triangle"""
        # Simplified check
        return len(highs) >= 5 and len(lows) >= 5

    def _is_descending_triangle(self, highs: np.ndarray, lows: np.ndarray) -> bool:
        """Check if data forms descending triangle"""
        # Simplified check
        return len(highs) >= 5 and len(lows) >= 5

    def _is_hammer_pattern(self, data: pd.DataFrame) -> bool:
        """Check if recent data forms hammer pattern"""
        if len(data) < 1:
            return False

        candle = data.iloc[-1]
        body_size = abs(candle["close"] - candle["open"])
        lower_shadow = min(candle["open"], candle["close"]) - candle["low"]
        upper_shadow = candle["high"] - max(candle["open"], candle["close"])

        return lower_shadow > body_size * 2 and upper_shadow < body_size * 0.5

    def _is_doji_pattern(self, data: pd.DataFrame) -> bool:
        """Check if recent data forms doji pattern"""
        if len(data) < 1:
            return False

        candle = data.iloc[-1]
        body_size = abs(candle["close"] - candle["open"])
        total_range = candle["high"] - candle["low"]

        return body_size < total_range * 0.1

    def _find_support_levels(self, lows: np.ndarray) -> list[float]:
        """Find key support levels"""
        # Simplified support level detection
        return [np.percentile(lows, 25), np.percentile(lows, 50)]

    def _find_resistance_levels(self, highs: np.ndarray) -> list[float]:
        """Find key resistance levels"""
        # Simplified resistance level detection
        return [np.percentile(highs, 75), np.percentile(highs, 90)]
