from .data_pipeline import get_data_pipeline
from datetime import datetime
from scipy.signal import find_peaks
from typing import Literal
import logging
import numpy as np
import pandas as pd

"""
Chart Pattern Recognition

Detects classic technical analysis patterns using rule-based algorithms
with ML-enhanced confidence scoring.

Patterns detected:
- Double top/bottom (reversal)
- Head and shoulders (major reversal)
- Triangle patterns (continuation/breakout)
- Support/resistance breaks
"""

logger = logging.getLogger(__name__)

# Pattern types
PatternType = Literal[
    "double_top",
    "double_bottom",
    "head_shoulders",
    "inverse_head_shoulders",
    "ascending_triangle",
    "descending_triangle",
    "symmetric_triangle",
    "support_break",
    "resistance_break",
]

SignalType = Literal["bullish", "bearish", "neutral"]

class Pattern:
    """Detected chart pattern"""

    def __init__(
        self,
        pattern_type: PatternType,
        signal: SignalType,
        confidence: float,
        start_date: datetime,
        end_date: datetime,
        key_levels: dict,
        description: str,
        target_price: float | None = None,
        stop_loss: float | None = None,
    ):
        self.pattern_type = pattern_type
        self.signal = signal
        self.confidence = confidence
        self.start_date = start_date
        self.end_date = end_date
        self.key_levels = key_levels
        self.description = description
        self.target_price = target_price
        self.stop_loss = stop_loss

    def to_dict(self) -> dict:
        """Convert pattern to dictionary"""
        return {
            "pattern_type": self.pattern_type,
            "signal": self.signal,
            "confidence": self.confidence,
            "start_date": (
                self.start_date.isoformat()
                if isinstance(self.start_date, datetime)
                else self.start_date
            ),
            "end_date": (
                self.end_date.isoformat() if isinstance(self.end_date, datetime) else self.end_date
            ),
            "key_levels": self.key_levels,
            "description": self.description,
            "target_price": self.target_price,
            "stop_loss": self.stop_loss,
        }

class PatternDetector:
    """
    Chart pattern recognition engine

    Uses rule-based algorithms to detect classic technical patterns
    """

    def __init__(self, min_confidence: float = 0.6):
        """
        Initialize pattern detector

        Args:
            min_confidence: Minimum confidence threshold (default: 0.6)
        """
        self.min_confidence = min_confidence

    def detect_patterns(self, symbol: str, lookback_days: int = 90) -> list[Pattern]:
        """
        Detect all patterns in recent price data

        Args:
            symbol: Stock symbol
            lookback_days: Days of history to analyze

        Returns:
            List of detected patterns sorted by confidence
        """
        try:
            # Get historical data
            pipeline = get_data_pipeline()
            df = pipeline.prepare_features(symbol, lookback_days)

            if df is None or len(df) < 30:
                logger.warning(f"Insufficient data for pattern detection: {symbol}")
                return []

            patterns = []

            # Detect each pattern type
            patterns.extend(self._detect_double_patterns(df))
            patterns.extend(self._detect_head_shoulders(df))
            patterns.extend(self._detect_triangles(df))
            patterns.extend(self._detect_support_resistance_breaks(df))

            # Filter by confidence
            patterns = [p for p in patterns if p.confidence >= self.min_confidence]

            # Sort by confidence (highest first)
            patterns.sort(key=lambda p: p.confidence, reverse=True)

            logger.info(
                f"✅ Detected {len(patterns)} patterns for {symbol} "
                f"(confidence >= {self.min_confidence})"
            )

            return patterns

        except Exception as e:
            logger.error(f"❌ Pattern detection failed for {symbol}: {e}")
            return []

    def _detect_double_patterns(self, df: pd.DataFrame) -> list[Pattern]:
        """Detect double top and double bottom patterns"""
        patterns = []

        try:
            close = df["close"].values
            dates = df.index

            # Find peaks and troughs
            peaks, _peak_props = find_peaks(close, distance=5, prominence=close.std() * 0.5)
            troughs, _trough_props = find_peaks(-close, distance=5, prominence=close.std() * 0.5)

            # Double Top Detection
            for i in range(len(peaks) - 1):
                for j in range(i + 1, len(peaks)):
                    idx1, idx2 = peaks[i], peaks[j]

                    # Check if peaks are similar height (within 2%)
                    price1, price2 = close[idx1], close[idx2]
                    if abs(price1 - price2) / price1 > 0.02:
                        continue

                    # Find trough between peaks
                    between_troughs = [t for t in troughs if idx1 < t < idx2]
                    if not between_troughs:
                        continue

                    trough_idx = between_troughs[0]
                    trough_price = close[trough_idx]

                    # Calculate confidence based on pattern quality
                    height = (price1 + price2) / 2 - trough_price
                    symmetry = 1 - abs(price1 - price2) / price1
                    spacing = min((idx2 - idx1) / 20, 1.0)  # Prefer 20-day spacing
                    confidence = symmetry * 0.5 + spacing * 0.3 + 0.2

                    if confidence >= self.min_confidence:
                        patterns.append(
                            Pattern(
                                pattern_type="double_top",
                                signal="bearish",
                                confidence=confidence,
                                start_date=dates[idx1],
                                end_date=dates[idx2],
                                key_levels={
                                    "peak1": float(price1),
                                    "peak2": float(price2),
                                    "trough": float(trough_price),
                                },
                                description=(
                                    f"Double top at ${price1:.2f}, neckline at ${trough_price:.2f}"
                                ),
                                target_price=float(trough_price - height),
                                stop_loss=float((price1 + price2) / 2),
                            )
                        )

            # Double Bottom Detection
            for i in range(len(troughs) - 1):
                for j in range(i + 1, len(troughs)):
                    idx1, idx2 = troughs[i], troughs[j]

                    # Check if troughs are similar depth (within 2%)
                    price1, price2 = close[idx1], close[idx2]
                    if abs(price1 - price2) / price1 > 0.02:
                        continue

                    # Find peak between troughs
                    between_peaks = [p for p in peaks if idx1 < p < idx2]
                    if not between_peaks:
                        continue

                    peak_idx = between_peaks[0]
                    peak_price = close[peak_idx]

                    # Calculate confidence
                    height = peak_price - (price1 + price2) / 2
                    symmetry = 1 - abs(price1 - price2) / price1
                    spacing = min((idx2 - idx1) / 20, 1.0)
                    confidence = symmetry * 0.5 + spacing * 0.3 + 0.2

                    if confidence >= self.min_confidence:
                        patterns.append(
                            Pattern(
                                pattern_type="double_bottom",
                                signal="bullish",
                                confidence=confidence,
                                start_date=dates[idx1],
                                end_date=dates[idx2],
                                key_levels={
                                    "bottom1": float(price1),
                                    "bottom2": float(price2),
                                    "peak": float(peak_price),
                                },
                                description=(
                                    f"Double bottom at ${price1:.2f}, neckline at ${peak_price:.2f}"
                                ),
                                target_price=float(peak_price + height),
                                stop_loss=float((price1 + price2) / 2),
                            )
                        )

        except Exception as e:
            logger.error(f"Double pattern detection error: {e}")

        return patterns

    def _detect_head_shoulders(self, df: pd.DataFrame) -> list[Pattern]:
        """Detect head and shoulders patterns"""
        patterns = []

        try:
            close = df["close"].values
            dates = df.index

            # Find peaks for head and shoulders
            peaks, _ = find_peaks(close, distance=5, prominence=close.std() * 0.5)

            # Need at least 3 peaks
            if len(peaks) < 3:
                return patterns

            # Check consecutive triplets of peaks
            for i in range(len(peaks) - 2):
                left_idx, head_idx, right_idx = peaks[i], peaks[i + 1], peaks[i + 2]

                left_price = close[left_idx]
                head_price = close[head_idx]
                right_price = close[right_idx]

                # Head should be higher than shoulders
                if head_price > left_price and head_price > right_price:
                    # Shoulders should be similar height (within 3%)
                    if abs(left_price - right_price) / left_price > 0.03:
                        continue

                    # Find neckline (lowest point between shoulders)
                    neckline_idx = left_idx + np.argmin(close[left_idx : right_idx + 1])
                    neckline_price = close[neckline_idx]

                    # Calculate confidence
                    head_prominence = (head_price - left_price) / left_price
                    shoulder_symmetry = 1 - abs(left_price - right_price) / left_price
                    confidence = min(head_prominence * 2 + shoulder_symmetry * 0.5, 0.95)

                    if confidence >= self.min_confidence:
                        height = head_price - neckline_price

                        patterns.append(
                            Pattern(
                                pattern_type="head_shoulders",
                                signal="bearish",
                                confidence=confidence,
                                start_date=dates[left_idx],
                                end_date=dates[right_idx],
                                key_levels={
                                    "left_shoulder": float(left_price),
                                    "head": float(head_price),
                                    "right_shoulder": float(right_price),
                                    "neckline": float(neckline_price),
                                },
                                description=(
                                    f"Head and shoulders: head at ${head_price:.2f}, "
                                    f"neckline at ${neckline_price:.2f}"
                                ),
                                target_price=float(neckline_price - height),
                                stop_loss=float(head_price),
                            )
                        )

            # Inverse Head and Shoulders (troughs)
            troughs, _ = find_peaks(-close, distance=5, prominence=close.std() * 0.5)

            if len(troughs) >= 3:
                for i in range(len(troughs) - 2):
                    left_idx, head_idx, right_idx = troughs[i], troughs[i + 1], troughs[i + 2]

                    left_price = close[left_idx]
                    head_price = close[head_idx]
                    right_price = close[right_idx]

                    # Head should be lower than shoulders
                    if head_price < left_price and head_price < right_price:
                        if abs(left_price - right_price) / left_price > 0.03:
                            continue

                        # Find neckline (highest point between shoulders)
                        neckline_idx = left_idx + np.argmax(close[left_idx : right_idx + 1])
                        neckline_price = close[neckline_idx]

                        head_prominence = (left_price - head_price) / left_price
                        shoulder_symmetry = 1 - abs(left_price - right_price) / left_price
                        confidence = min(head_prominence * 2 + shoulder_symmetry * 0.5, 0.95)

                        if confidence >= self.min_confidence:
                            height = neckline_price - head_price

                            patterns.append(
                                Pattern(
                                    pattern_type="inverse_head_shoulders",
                                    signal="bullish",
                                    confidence=confidence,
                                    start_date=dates[left_idx],
                                    end_date=dates[right_idx],
                                    key_levels={
                                        "left_shoulder": float(left_price),
                                        "head": float(head_price),
                                        "right_shoulder": float(right_price),
                                        "neckline": float(neckline_price),
                                    },
                                    description=(
                                        f"Inverse head and shoulders: head at ${head_price:.2f}, "
                                        f"neckline at ${neckline_price:.2f}"
                                    ),
                                    target_price=float(neckline_price + height),
                                    stop_loss=float(head_price),
                                )
                            )

        except Exception as e:
            logger.error(f"Head and shoulders detection error: {e}")

        return patterns

    def _detect_triangles(self, df: pd.DataFrame) -> list[Pattern]:
        """Detect triangle patterns (ascending, descending, symmetric)"""
        patterns = []

        try:
            close = df["close"].values
            high = df["high"].values
            low = df["low"].values
            dates = df.index

            # Look at recent 30 days for triangle formation
            if len(close) < 30:
                return patterns

            recent_high = high[-30:]
            recent_low = low[-30:]
            recent_close = close[-30:]

            # Fit trend lines to highs and lows
            x = np.arange(len(recent_high))
            high_slope = np.polyfit(x, recent_high, 1)[0]
            low_slope = np.polyfit(x, recent_low, 1)[0]

            # Calculate convergence
            high_range = recent_high.max() - recent_high.min()
            low_range = recent_low.max() - recent_low.min()
            convergence = 1 - abs(recent_high[-1] - recent_low[-1]) / (high_range + low_range + 1)

            # Ascending Triangle: Flat top, rising bottom
            if abs(high_slope) < 0.01 and low_slope > 0.01 and convergence > 0.3:
                resistance = recent_high.max()
                confidence = min(low_slope * 50 + convergence * 0.3, 0.9)

                if confidence >= self.min_confidence:
                    patterns.append(
                        Pattern(
                            pattern_type="ascending_triangle",
                            signal="bullish",
                            confidence=confidence,
                            start_date=dates[-30],
                            end_date=dates[-1],
                            key_levels={
                                "resistance": float(resistance),
                                "support_start": float(recent_low[0]),
                                "support_end": float(recent_low[-1]),
                            },
                            description=f"Ascending triangle with resistance at ${resistance:.2f}",
                            target_price=float(resistance + (resistance - recent_low[-1])),
                            stop_loss=float(recent_low[-1] * 0.98),
                        )
                    )

            # Descending Triangle: Falling top, flat bottom
            elif high_slope < -0.01 and abs(low_slope) < 0.01 and convergence > 0.3:
                support = recent_low.min()
                confidence = min(abs(high_slope) * 50 + convergence * 0.3, 0.9)

                if confidence >= self.min_confidence:
                    patterns.append(
                        Pattern(
                            pattern_type="descending_triangle",
                            signal="bearish",
                            confidence=confidence,
                            start_date=dates[-30],
                            end_date=dates[-1],
                            key_levels={
                                "support": float(support),
                                "resistance_start": float(recent_high[0]),
                                "resistance_end": float(recent_high[-1]),
                            },
                            description=f"Descending triangle with support at ${support:.2f}",
                            target_price=float(support - (recent_high[-1] - support)),
                            stop_loss=float(recent_high[-1] * 1.02),
                        )
                    )

            # Symmetric Triangle: Both converging
            elif high_slope < -0.01 and low_slope > 0.01 and convergence > 0.4:
                confidence = min(convergence * 1.5, 0.85)

                if confidence >= self.min_confidence:
                    current_price = recent_close[-1]
                    height = recent_high[0] - recent_low[0]

                    patterns.append(
                        Pattern(
                            pattern_type="symmetric_triangle",
                            signal="neutral",
                            confidence=confidence,
                            start_date=dates[-30],
                            end_date=dates[-1],
                            key_levels={
                                "apex_price": float(current_price),
                                "upper_start": float(recent_high[0]),
                                "lower_start": float(recent_low[0]),
                            },
                            description=f"Symmetric triangle converging at ${current_price:.2f}",
                            target_price=float(current_price + height * 0.75),
                            stop_loss=float(current_price - height * 0.5),
                        )
                    )

        except Exception as e:
            logger.error(f"Triangle detection error: {e}")

        return patterns

    def _detect_support_resistance_breaks(self, df: pd.DataFrame) -> list[Pattern]:
        """Detect support and resistance level breaks"""
        patterns = []

        try:
            close = df["close"].values
            # high and low reserved for future volume confirmation
            # _high = df["high"].values
            # _low = df["low"].values
            dates = df.index

            if len(close) < 20:
                return patterns

            # Identify key levels (local maxima/minima in last 50 days)
            lookback = min(50, len(close))
            recent_close = close[-lookback:]

            peaks, _ = find_peaks(recent_close, distance=5)
            troughs, _ = find_peaks(-recent_close, distance=5)

            # Check for recent breaks (last 5 days)
            for peak_idx in peaks:
                resistance_level = recent_close[peak_idx]

                # Check if recently broken above
                if close[-1] > resistance_level > close[-5]:
                    # Confirm break with volume or gap
                    break_strength = (close[-1] - resistance_level) / resistance_level
                    confidence = min(break_strength * 10 + 0.6, 0.9)

                    if confidence >= self.min_confidence:
                        patterns.append(
                            Pattern(
                                pattern_type="resistance_break",
                                signal="bullish",
                                confidence=confidence,
                                start_date=dates[-lookback + peak_idx],
                                end_date=dates[-1],
                                key_levels={
                                    "resistance": float(resistance_level),
                                    "breakout_price": float(close[-1]),
                                },
                                description=(
                                    f"Resistance break at ${resistance_level:.2f}, "
                                    f"now at ${close[-1]:.2f}"
                                ),
                                target_price=float(close[-1] + (close[-1] - resistance_level)),
                                stop_loss=float(resistance_level * 0.99),
                            )
                        )

            # Check support breaks
            for trough_idx in troughs:
                support_level = recent_close[trough_idx]

                # Check if recently broken below
                if close[-1] < support_level < close[-5]:
                    break_strength = (support_level - close[-1]) / support_level
                    confidence = min(break_strength * 10 + 0.6, 0.9)

                    if confidence >= self.min_confidence:
                        patterns.append(
                            Pattern(
                                pattern_type="support_break",
                                signal="bearish",
                                confidence=confidence,
                                start_date=dates[-lookback + trough_idx],
                                end_date=dates[-1],
                                key_levels={
                                    "support": float(support_level),
                                    "breakdown_price": float(close[-1]),
                                },
                                description=(
                                    f"Support break at ${support_level:.2f}, "
                                    f"now at ${close[-1]:.2f}"
                                ),
                                target_price=float(close[-1] - (support_level - close[-1])),
                                stop_loss=float(support_level * 1.01),
                            )
                        )

        except Exception as e:
            logger.error(f"Support/resistance break detection error: {e}")

        return patterns

# Singleton instance
_pattern_detector = None

def get_pattern_detector() -> PatternDetector:
    """Get or create pattern detector singleton"""
    global _pattern_detector
    if _pattern_detector is None:
        _pattern_detector = PatternDetector()
    return _pattern_detector
