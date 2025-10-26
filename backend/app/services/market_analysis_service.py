"""
Market Analysis Service

Centralizes all market data analysis logic including:
- Technical indicator calculations (RSI, MACD, Bollinger Bands)
- Trend analysis and pattern recognition
- Volume analysis and liquidity scoring
- Market regime detection (bull/bear/sideways)

This service extracts cross-cutting business logic from multiple routers
to provide reusable, testable market analysis capabilities.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..services.cache_service import CacheService
from ..services.technical_indicators import TechnicalIndicators
from ..services.tradier_client import TradierClient


logger = logging.getLogger(__name__)


class MarketAnalysisService:
    """
    Market analysis service for technical indicators and market regime detection.

    This service is framework-agnostic and can be used by any router or background task.
    All dependencies are injected for easy mocking in tests.
    """

    def __init__(
        self,
        tradier_client: TradierClient,
        cache_service: CacheService | None = None,
    ):
        """
        Initialize market analysis service.

        Args:
            tradier_client: Tradier API client for market data
            cache_service: Optional cache service for performance optimization
        """
        self.tradier = tradier_client
        self.cache = cache_service
        self.indicators = TechnicalIndicators()

    async def calculate_technical_indicators(
        self,
        symbol: str,
        indicators: list[str],
        lookback_days: int = 90,
    ) -> dict[str, float]:
        """
        Calculate requested technical indicators for a symbol.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            indicators: List of indicator names (e.g., ["rsi", "macd", "bb"])
            lookback_days: Days of historical data to fetch

        Returns:
            Dictionary of indicator values

        Raises:
            ValueError: If symbol is invalid or indicators list is empty
            Exception: If market data fetch fails

        Example:
            >>> service = MarketAnalysisService(tradier, cache)
            >>> indicators = await service.calculate_technical_indicators(
            ...     "AAPL", ["rsi", "macd"], lookback_days=90
            ... )
            >>> print(indicators["rsi"])  # 65.3
        """
        if not symbol or not indicators:
            raise ValueError("Symbol and indicators list are required")

        # Check cache first
        cache_key = f"indicators:{symbol}:{':'.join(sorted(indicators))}:{lookback_days}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache HIT for indicators {symbol}")
                return cached

        # Fetch historical data
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            history = self.tradier.get_historical_quotes(
                symbol=symbol,
                interval="daily",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
            )

            if not history or len(history) < 20:
                raise ValueError(f"Insufficient historical data for {symbol}")

            # Extract price arrays
            prices = [float(bar.get("close", 0)) for bar in history]
            highs = [float(bar.get("high", 0)) for bar in history]
            lows = [float(bar.get("low", 0)) for bar in history]
            volumes = [float(bar.get("volume", 0)) for bar in history]

            # Calculate requested indicators
            result = {}

            for indicator in indicators:
                if indicator.lower() == "rsi":
                    result["rsi"] = self.indicators.calculate_rsi(prices)

                elif indicator.lower() == "macd":
                    macd_data = self.indicators.calculate_macd(prices)
                    result["macd"] = macd_data["macd"]
                    result["macd_signal"] = macd_data["signal"]
                    result["macd_histogram"] = macd_data["histogram"]

                elif indicator.lower() in ["bb", "bollinger_bands"]:
                    bb_data = self.indicators.calculate_bollinger_bands(prices)
                    result["bb_upper"] = bb_data["upper"]
                    result["bb_middle"] = bb_data["middle"]
                    result["bb_lower"] = bb_data["lower"]
                    result["bb_width"] = self.indicators.calculate_bb_width(prices)

                elif indicator.lower() == "atr":
                    result["atr"] = self.indicators.calculate_atr(highs, lows, prices)

                elif indicator.lower() in ["ma", "moving_averages"]:
                    ma_data = self.indicators.calculate_moving_averages(prices)
                    result.update(ma_data)

                elif indicator.lower() == "volume":
                    # Volume metrics
                    avg_volume = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else 0
                    current_volume = volumes[-1] if volumes else 0
                    result["avg_volume_20d"] = round(avg_volume, 0)
                    result["current_volume"] = round(current_volume, 0)
                    result["volume_ratio"] = (
                        round(current_volume / avg_volume, 2) if avg_volume > 0 else 0
                    )

                else:
                    logger.warning(f"Unknown indicator requested: {indicator}")

            # Cache results for 5 minutes
            if self.cache and result:
                self.cache.set(cache_key, result, ttl=300)

            logger.info(f"Calculated {len(result)} indicators for {symbol}")
            return result

        except Exception as e:
            logger.error(f"Failed to calculate indicators for {symbol}: {e}")
            raise

    async def detect_market_regime(
        self,
        symbol: str,
        lookback_days: int = 90,
    ) -> dict[str, Any]:
        """
        Detect current market regime (bull/bear/sideways/high_volatility).

        Uses multiple technical indicators to classify market state:
        - Trend strength (slope of moving averages)
        - Volatility (Bollinger Band width, ATR)
        - Momentum (RSI, MACD)

        Args:
            symbol: Stock symbol to analyze
            lookback_days: Days of history to analyze

        Returns:
            Dictionary with regime classification and features:
            {
                "regime": "trending_bullish" | "trending_bearish" | "ranging" | "high_volatility",
                "confidence": 0.0-1.0,
                "features": {...},
                "timestamp": ISO timestamp
            }

        Example:
            >>> regime = await service.detect_market_regime("SPY", 90)
            >>> print(regime["regime"])  # "trending_bullish"
            >>> print(regime["confidence"])  # 0.85
        """
        try:
            # Calculate all relevant indicators
            indicators = await self.calculate_technical_indicators(
                symbol,
                indicators=["rsi", "macd", "bb", "atr", "ma", "volume"],
                lookback_days=lookback_days,
            )

            # Get trend analysis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            history = self.tradier.get_historical_quotes(
                symbol=symbol,
                interval="daily",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
            )
            prices = [float(bar.get("close", 0)) for bar in history]
            trend = self.indicators.analyze_trend(prices)

            # Extract key features
            rsi = indicators.get("rsi", 50)
            bb_width = indicators.get("bb_width", 0)
            macd_histogram = indicators.get("macd_histogram", 0)
            volume_ratio = indicators.get("volume_ratio", 1.0)
            trend_direction = trend["direction"]
            trend_strength = trend["strength"]

            # Regime classification logic
            regime = "ranging"  # Default
            confidence = 0.5

            # High volatility check (BB width > 6% or high ATR)
            if bb_width > 6.0:
                regime = "high_volatility"
                confidence = min(0.6 + (bb_width - 6.0) / 10, 0.95)

            # Trending market checks
            elif trend_direction == "bullish" and trend_strength > 0.6:
                regime = "trending_bullish"
                confidence = min(0.6 + trend_strength * 0.3, 0.95)

                # Boost confidence if RSI and MACD confirm
                if rsi > 50 and macd_histogram > 0:
                    confidence = min(confidence + 0.1, 0.95)

            elif trend_direction == "bearish" and trend_strength > 0.6:
                regime = "trending_bearish"
                confidence = min(0.6 + trend_strength * 0.3, 0.95)

                # Boost confidence if RSI and MACD confirm
                if rsi < 50 and macd_histogram < 0:
                    confidence = min(confidence + 0.1, 0.95)

            # Ranging market (low volatility, weak trend)
            else:
                regime = "ranging"
                # Higher confidence if RSI near 50 and low BB width
                if 40 <= rsi <= 60 and bb_width < 3.0:
                    confidence = 0.75
                else:
                    confidence = 0.6

            logger.info(
                f"Market regime for {symbol}: {regime} (confidence: {confidence:.2f})"
            )

            return {
                "regime": regime,
                "confidence": round(confidence, 2),
                "features": {
                    "rsi": rsi,
                    "bb_width": bb_width,
                    "macd_histogram": macd_histogram,
                    "volume_ratio": volume_ratio,
                    "trend_direction": trend_direction,
                    "trend_strength": trend_strength,
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to detect market regime for {symbol}: {e}")
            # Return unknown regime on error
            return {
                "regime": "unknown",
                "confidence": 0.0,
                "features": {},
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    async def analyze_trend(
        self,
        symbol: str,
        timeframe: str = "daily",
        lookback_days: int = 90,
    ) -> dict[str, Any]:
        """
        Analyze price trend for given timeframe.

        Args:
            symbol: Stock symbol
            timeframe: Timeframe ("daily", "weekly", "monthly")
            lookback_days: Days of history to analyze

        Returns:
            Dictionary with trend analysis:
            {
                "direction": "bullish" | "bearish" | "neutral",
                "strength": 0.0-1.0,
                "support": float,
                "resistance": float,
                "slope": float,
                "confidence": 0.0-1.0
            }
        """
        try:
            # Fetch historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            history = self.tradier.get_historical_quotes(
                symbol=symbol,
                interval=timeframe,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
            )

            if not history or len(history) < 20:
                raise ValueError(f"Insufficient data for trend analysis: {symbol}")

            prices = [float(bar.get("close", 0)) for bar in history]

            # Use technical indicators for trend analysis
            trend_data = self.indicators.analyze_trend(prices)

            # Calculate moving averages for additional context
            ma_data = self.indicators.calculate_moving_averages(prices)

            # Enhance with MA crossover signals
            current_price = prices[-1]
            confidence = trend_data["strength"]

            if "sma_50" in ma_data and "sma_200" in ma_data:
                golden_cross = ma_data["sma_50"] > ma_data["sma_200"]
                if golden_cross and trend_data["direction"] == "bullish":
                    confidence = min(confidence + 0.15, 1.0)
                elif not golden_cross and trend_data["direction"] == "bearish":
                    confidence = min(confidence + 0.15, 1.0)

            result = {
                **trend_data,
                "confidence": round(confidence, 2),
                "current_price": round(current_price, 2),
                "moving_averages": ma_data,
                "timeframe": timeframe,
                "lookback_days": lookback_days,
            }

            logger.info(
                f"Trend analysis for {symbol}: {result['direction']} "
                f"(strength: {result['strength']:.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to analyze trend for {symbol}: {e}")
            raise

    async def analyze_volume(
        self,
        symbol: str,
        lookback_days: int = 30,
    ) -> dict[str, Any]:
        """
        Analyze volume patterns and liquidity.

        Args:
            symbol: Stock symbol
            lookback_days: Days of volume history

        Returns:
            Dictionary with volume analysis:
            {
                "avg_volume": float,
                "current_volume": float,
                "volume_ratio": float,
                "volume_trend": "increasing" | "decreasing" | "stable",
                "liquidity_score": 0.0-100.0
            }
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            history = self.tradier.get_historical_quotes(
                symbol=symbol,
                interval="daily",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
            )

            if not history:
                raise ValueError(f"No volume data available for {symbol}")

            volumes = [float(bar.get("volume", 0)) for bar in history]

            # Calculate volume metrics
            avg_volume = sum(volumes) / len(volumes) if volumes else 0
            current_volume = volumes[-1] if volumes else 0
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0

            # Determine volume trend (compare recent 10 days vs previous 10 days)
            if len(volumes) >= 20:
                recent_avg = sum(volumes[-10:]) / 10
                previous_avg = sum(volumes[-20:-10]) / 10

                if recent_avg > previous_avg * 1.2:
                    volume_trend = "increasing"
                elif recent_avg < previous_avg * 0.8:
                    volume_trend = "decreasing"
                else:
                    volume_trend = "stable"
            else:
                volume_trend = "unknown"

            # Liquidity score (based on average volume)
            # High liquidity: > 1M shares/day
            # Medium: 100K - 1M
            # Low: < 100K
            if avg_volume > 1_000_000:
                liquidity_score = min(70 + (avg_volume / 1_000_000) * 3, 100)
            elif avg_volume > 100_000:
                liquidity_score = 40 + (avg_volume / 100_000) * 3
            else:
                liquidity_score = (avg_volume / 100_000) * 40

            return {
                "avg_volume": round(avg_volume, 0),
                "current_volume": round(current_volume, 0),
                "volume_ratio": round(volume_ratio, 2),
                "volume_trend": volume_trend,
                "liquidity_score": round(liquidity_score, 1),
                "lookback_days": lookback_days,
            }

        except Exception as e:
            logger.error(f"Failed to analyze volume for {symbol}: {e}")
            raise


# Singleton instance for dependency injection
_market_analysis_service: MarketAnalysisService | None = None


def get_market_analysis_service(
    tradier_client: TradierClient | None = None,
    cache_service: CacheService | None = None,
) -> MarketAnalysisService:
    """
    Get or create market analysis service instance.

    Args:
        tradier_client: Optional Tradier client (uses singleton if not provided)
        cache_service: Optional cache service (uses singleton if not provided)

    Returns:
        MarketAnalysisService instance

    Usage in routers:
        from ..services.market_analysis_service import get_market_analysis_service

        @router.get("/analyze/{symbol}")
        async def analyze_symbol(symbol: str):
            service = get_market_analysis_service()
            regime = await service.detect_market_regime(symbol)
            return regime
    """
    global _market_analysis_service

    if _market_analysis_service is None:
        # Import here to avoid circular dependencies
        from ..services.cache_service import get_cache_service
        from ..services.tradier_client import get_tradier_client

        if tradier_client is None:
            tradier_client = get_tradier_client()

        if cache_service is None:
            cache_service = get_cache_service()

        _market_analysis_service = MarketAnalysisService(
            tradier_client=tradier_client,
            cache_service=cache_service,
        )

    return _market_analysis_service
