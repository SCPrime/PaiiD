"""
Historical Data Service

Fetches historical OHLCV data for backtesting.
Supports Tradier API integration and simulated data generation.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import math

logger = logging.getLogger(__name__)


class HistoricalDataService:
    """Service for fetching historical market data"""

    def __init__(self, tradier_client=None):
        """
        Initialize historical data service

        Args:
            tradier_client: Optional Tradier API client for real data
        """
        self.tradier_client = tradier_client

    async def get_historical_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Get historical OHLCV bars

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Bar interval (daily, hourly, etc.)

        Returns:
            List of OHLCV bars: [{date, open, high, low, close, volume}]
        """
        # TODO: Implement real Tradier API integration
        # For now, generate realistic simulated data
        logger.info(f"Generating simulated data for {symbol} from {start_date} to {end_date}")
        return self._generate_realistic_prices(symbol, start_date, end_date)

    def _generate_realistic_prices(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Generate realistic price data with trends, volatility, and patterns

        This simulates realistic market behavior for backtesting.
        """
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            raise ValueError("Dates must be in YYYY-MM-DD format")

        days = (end_dt - start_dt).days
        if days <= 0:
            raise ValueError("End date must be after start date")

        # Base price depends on symbol (rough estimates)
        symbol_prices = {
            "SPY": 450.0,
            "QQQ": 380.0,
            "AAPL": 180.0,
            "MSFT": 380.0,
            "GOOGL": 140.0,
            "TSLA": 240.0,
            "AMZN": 175.0,
            "NVDA": 480.0,
            "META": 490.0,
        }
        base_price = symbol_prices.get(symbol.upper(), 150.0)

        bars = []
        current_price = base_price
        current_date = start_dt

        # Market parameters
        daily_volatility = 0.015  # 1.5% daily volatility
        trend_strength = 0.0005  # Slight upward bias
        trend_change_prob = 0.02  # 2% chance of trend reversal per day
        current_trend = 1  # 1 for uptrend, -1 for downtrend

        for i in range(days + 1):
            # Skip weekends (simplified)
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue

            # Trend changes (mean reversion)
            if random.random() < trend_change_prob:
                current_trend *= -1

            # Daily return = trend + random noise
            daily_return = (current_trend * trend_strength) + random.gauss(0, daily_volatility)

            # Calculate OHLC with validation to prevent negative prices
            open_price = current_price
            close_price = max(0.01, open_price * (1 + daily_return))  # Ensure positive

            # Intraday high/low with realistic ranges
            intraday_range = abs(close_price - open_price) + (random.random() * 0.01 * close_price)
            high_price = max(0.01, max(open_price, close_price) + (random.random() * intraday_range * 0.5))
            low_price = max(0.01, min(open_price, close_price) - (random.random() * intraday_range * 0.5))

            # Volume (random but realistic)
            avg_volume = 50_000_000 if symbol.upper() in ["SPY", "QQQ", "AAPL"] else 10_000_000
            volume = int(avg_volume * (0.5 + random.random()))

            bars.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })

            # Update for next iteration
            current_price = close_price
            current_date += timedelta(days=1)

        logger.info(f"Generated {len(bars)} bars for {symbol}")
        return bars

    async def get_latest_price(self, symbol: str) -> float:
        """Get latest price for a symbol"""
        # TODO: Implement real-time price fetch
        # For now, return simulated price
        symbol_prices = {
            "SPY": 458.20,
            "QQQ": 395.40,
            "AAPL": 182.50,
            "MSFT": 410.30,
            "GOOGL": 142.80,
            "TSLA": 245.60,
            "AMZN": 178.90,
            "NVDA": 505.20,
            "META": 512.40,
        }
        return symbol_prices.get(symbol.upper(), 150.0)

    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """Validate date range for historical data request"""
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)

            # Check if dates are valid
            if end_dt <= start_dt:
                return False

            # Check if date range is not too large (e.g., max 5 years)
            max_days = 5 * 365
            if (end_dt - start_dt).days > max_days:
                return False

            # Check if dates are not in the future
            if end_dt > datetime.now():
                return False

            return True

        except ValueError:
            return False
