from typing import Any
import logging

"""
Technical Indicators Service

Calculates common technical indicators for trading signals:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (SMA, EMA)
- Volume indicators
"""

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Calculate technical indicators from price data"""

    @staticmethod
    def calculate_rsi(prices: list[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index

        Args:
            prices: List of closing prices (most recent last)
            period: RSI period (default 14)

        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 50.0  # Neutral default

        # Calculate price changes
        changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]

        # Separate gains and losses
        gains = [max(change, 0) for change in changes]
        losses = [abs(min(change, 0)) for change in changes]

        # Calculate average gain and loss
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    @staticmethod
    def calculate_macd(
        prices: list[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9
    ) -> dict[str, float]:
        """
        Calculate MACD (Moving Average Convergence Divergence)

        Returns:
            dict with macd, signal, histogram values
        """
        if len(prices) < slow_period + signal_period:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}

        # Calculate MACD line for each bar (need historical values for signal line EMA)
        macd_values = []
        for i in range(slow_period, len(prices)):
            fast_ema = TechnicalIndicators._calculate_ema(prices[: i + 1], fast_period)
            slow_ema = TechnicalIndicators._calculate_ema(prices[: i + 1], slow_period)
            macd_values.append(fast_ema - slow_ema)

        # Calculate signal line as EMA of MACD line
        if len(macd_values) >= signal_period:
            signal_line = TechnicalIndicators._calculate_ema(macd_values, signal_period)
        else:
            # Fallback if insufficient data
            signal_line = sum(macd_values) / len(macd_values) if macd_values else 0.0

        macd_line = macd_values[-1] if macd_values else 0.0
        histogram = macd_line - signal_line

        return {
            "macd": round(macd_line, 4),
            "signal": round(signal_line, 4),
            "histogram": round(histogram, 4),
        }

    @staticmethod
    def calculate_bollinger_bands(
        prices: list[float], period: int = 20, std_dev: float = 2.0
    ) -> dict[str, float]:
        """
        Calculate Bollinger Bands

        Returns:
            dict with upper, middle, lower bands
        """
        if len(prices) < period:
            current = prices[-1] if prices else 100.0
            return {"upper": current * 1.02, "middle": current, "lower": current * 0.98}

        recent_prices = prices[-period:]

        # Calculate SMA (middle band)
        sma = sum(recent_prices) / period

        # Calculate standard deviation
        variance = sum((p - sma) ** 2 for p in recent_prices) / period
        std = variance**0.5

        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)

        return {"upper": round(upper, 2), "middle": round(sma, 2), "lower": round(lower, 2)}

    @staticmethod
    def calculate_bb_width(prices: list[float], period: int = 20, std_dev: float = 2.0) -> float:
        """
        Calculate Bollinger Band Width as percentage of price

        Measures volatility - wider bands = higher volatility

        Returns:
            Band width as percentage (e.g., 4.5 = 4.5% width)
        """
        bb = TechnicalIndicators.calculate_bollinger_bands(prices, period, std_dev)

        if bb["middle"] == 0:
            return 0.0

        # Width = (upper - lower) / middle * 100
        width_pct = ((bb["upper"] - bb["lower"]) / bb["middle"]) * 100

        return round(width_pct, 2)

    @staticmethod
    def calculate_atr(
        highs: list[float], lows: list[float], closes: list[float], period: int = 14
    ) -> float:
        """
        Calculate Average True Range (ATR) - volatility indicator

        ATR measures market volatility by decomposing the entire range of an asset

        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            period: ATR period (default 14)

        Returns:
            ATR value (absolute price movement)
        """
        if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
            # Not enough data - return simple range
            if highs and lows:
                return round(highs[-1] - lows[-1], 2)
            return 0.0

        # Calculate True Range for each bar
        true_ranges = []
        for i in range(1, len(closes)):
            high = highs[i]
            low = lows[i]
            prev_close = closes[i - 1]

            # True Range = max(high-low, abs(high-prev_close), abs(low-prev_close))
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            true_ranges.append(tr)

        # ATR is simple moving average of True Range
        if len(true_ranges) >= period:
            atr = sum(true_ranges[-period:]) / period
        else:
            atr = sum(true_ranges) / len(true_ranges) if true_ranges else 0.0

        return round(atr, 2)

    @staticmethod
    def calculate_moving_averages(prices: list[float]) -> dict[str, float]:
        """
        Calculate key moving averages

        Returns:
            dict with SMA20, SMA50, SMA200, EMA12
        """
        result = {}

        if len(prices) >= 20:
            result["sma_20"] = round(sum(prices[-20:]) / 20, 2)

        if len(prices) >= 50:
            result["sma_50"] = round(sum(prices[-50:]) / 50, 2)

        if len(prices) >= 200:
            result["sma_200"] = round(sum(prices[-200:]) / 200, 2)

        if len(prices) >= 12:
            result["ema_12"] = round(TechnicalIndicators._calculate_ema(prices, 12), 2)

        return result

    @staticmethod
    def _calculate_ema(prices: list[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0.0

        # Use SMA as initial EMA
        sma = sum(prices[:period]) / period
        multiplier = 2 / (period + 1)

        ema = sma
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    @staticmethod
    def analyze_trend(prices: list[float]) -> dict[str, Any]:
        """
        Analyze price trend

        Returns:
            dict with trend direction, strength, support/resistance
        """
        if len(prices) < 20:
            return {
                "direction": "neutral",
                "strength": 0.5,
                "support": prices[-1] * 0.95 if prices else 0,
                "resistance": prices[-1] * 1.05 if prices else 0,
            }

        recent = prices[-20:]
        current_price = prices[-1]

        # Calculate trend slope
        x_values = list(range(len(recent)))
        n = len(recent)

        # Simple linear regression
        sum_x = sum(x_values)
        sum_y = sum(recent)
        sum_xy = sum(x * y for x, y in zip(x_values, recent, strict=False))
        sum_x2 = sum(x**2 for x in x_values)

        # Guard against division by zero (shouldn't happen with sequential x_values, but defensive)
        denominator = n * sum_x2 - sum_x**2
        if denominator == 0:
            # All x values identical - return neutral trend
            return {
                "direction": "neutral",
                "strength": 0.5,
                "support": min(recent[-10:]),
                "resistance": max(recent[-10:]),
            }

        slope = (n * sum_xy - sum_x * sum_y) / denominator

        # Determine trend direction and strength
        if slope > 0.1:
            direction = "bullish"
            strength = min(abs(slope) / current_price * 1000, 1.0)
        elif slope < -0.1:
            direction = "bearish"
            strength = min(abs(slope) / current_price * 1000, 1.0)
        else:
            direction = "neutral"
            strength = 0.5

        # Calculate support and resistance (simplified)
        support = min(recent[-10:])
        resistance = max(recent[-10:])

        return {
            "direction": direction,
            "strength": round(strength, 2),
            "support": round(support, 2),
            "resistance": round(resistance, 2),
        }

    @staticmethod
    def generate_signal(
        symbol: str, prices: list[float], volumes: list[float] | None = None
    ) -> dict[str, Any]:
        """
        Generate trading signal based on multiple indicators

        Returns:
            Comprehensive signal with action, confidence, reasons
        """
        if len(prices) < 20:
            return {
                "action": "HOLD",
                "confidence": 50.0,
                "reasons": ["Insufficient data for analysis"],
                "indicators": {},
            }

        current_price = prices[-1]

        # Calculate all indicators
        rsi = TechnicalIndicators.calculate_rsi(prices)
        macd = TechnicalIndicators.calculate_macd(prices)
        bb = TechnicalIndicators.calculate_bollinger_bands(prices)
        ma = TechnicalIndicators.calculate_moving_averages(prices)
        trend = TechnicalIndicators.analyze_trend(prices)

        # Scoring system
        bullish_score = 0
        bearish_score = 0
        reasons = []

        # RSI Analysis
        if rsi < 30:
            bullish_score += 2
            reasons.append(f"RSI oversold at {rsi:.1f}")
        elif rsi > 70:
            bearish_score += 2
            reasons.append(f"RSI overbought at {rsi:.1f}")
        elif 40 <= rsi <= 60:
            reasons.append(f"RSI neutral at {rsi:.1f}")

        # MACD Analysis
        if macd["histogram"] > 0:
            bullish_score += 1
            reasons.append("MACD bullish crossover")
        elif macd["histogram"] < 0:
            bearish_score += 1
            reasons.append("MACD bearish crossover")

        # Bollinger Bands Analysis
        if current_price < bb["lower"]:
            bullish_score += 1
            reasons.append("Price below lower Bollinger Band")
        elif current_price > bb["upper"]:
            bearish_score += 1
            reasons.append("Price above upper Bollinger Band")

        # Moving Average Analysis
        if "sma_50" in ma and "sma_200" in ma:
            if ma["sma_50"] > ma["sma_200"]:
                bullish_score += 1
                reasons.append("Golden cross: 50-day above 200-day MA")
            else:
                bearish_score += 1
                reasons.append("Death cross: 50-day below 200-day MA")

        if "sma_20" in ma:
            if current_price > ma["sma_20"]:
                bullish_score += 1
                reasons.append("Price above 20-day MA")
            else:
                bearish_score += 1
                reasons.append("Price below 20-day MA")

        # Trend Analysis
        if trend["direction"] == "bullish":
            bullish_score += trend["strength"] * 2
            reasons.append(f"Bullish trend with strength {trend['strength']:.1f}")
        elif trend["direction"] == "bearish":
            bearish_score += trend["strength"] * 2
            reasons.append(f"Bearish trend with strength {trend['strength']:.1f}")

        # Determine action and confidence
        total_score = bullish_score + bearish_score
        if total_score == 0:
            action = "HOLD"
            confidence = 50.0
        elif bullish_score > bearish_score:
            action = "BUY"
            confidence = min(50 + (bullish_score / total_score * 50), 95)
        else:
            action = "SELL"
            confidence = min(50 + (bearish_score / total_score * 50), 95)

        # Calculate entry/exit prices
        if action == "BUY":
            entry_price = current_price * 0.998  # Slight discount
            stop_loss = max(bb["lower"], trend["support"])
            take_profit = min(bb["upper"], trend["resistance"])
        elif action == "SELL":
            entry_price = current_price * 1.002  # Slight premium
            stop_loss = min(bb["upper"], trend["resistance"])
            take_profit = max(bb["lower"], trend["support"])
        else:  # HOLD
            entry_price = current_price
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.05

        return {
            "symbol": symbol,
            "action": action,
            "confidence": round(confidence, 1),
            "current_price": round(current_price, 2),
            "entry_price": round(entry_price, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "reasons": reasons[:5],  # Top 5 reasons
            "indicators": {
                "rsi": rsi,
                "macd": macd,
                "bollinger_bands": bb,
                "moving_averages": ma,
                "trend": trend,
            },
            # Calculate risk/reward ratio with proper guard
            # Risk = distance from entry to stop, Reward = distance from entry to target
            "risk_reward_ratio": (
                round(abs(take_profit - entry_price) / abs(entry_price - stop_loss), 2)
                if abs(entry_price - stop_loss) > 0.01
                else 0
            ),  # 0 if entry == stop (invalid signal)
            "bullish_score": round(bullish_score, 2),
            "bearish_score": round(bearish_score, 2),
        }
