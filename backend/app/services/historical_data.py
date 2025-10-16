"""
Historical Data Service

Fetches historical OHLCV data for backtesting using Tradier API.
NO mock data - all data comes from real market sources.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class HistoricalDataService:
    """Service for fetching historical market data from Tradier"""

    def __init__(self, tradier_client):
        """
        Initialize historical data service

        Args:
            tradier_client: Tradier API client for real market data (REQUIRED)
        """
        if tradier_client is None:
            raise ValueError("Tradier client is required - no mock data fallbacks allowed")
        self.tradier_client = tradier_client

    async def get_historical_bars(
        self, symbol: str, start_date: str, end_date: str, interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Get historical OHLCV bars from Tradier API

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Bar interval (daily, weekly, monthly)

        Returns:
            List of OHLCV bars: [{date, open, high, low, close, volume}]

        Raises:
            ValueError: If date format is invalid or date range is invalid
            Exception: If Tradier API call fails
        """
        # Validate date range
        if not self.validate_date_range(start_date, end_date):
            raise ValueError(f"Invalid date range: {start_date} to {end_date}")

        logger.info(f"Fetching real market data for {symbol} from {start_date} to {end_date}")

        # Call Tradier API (synchronous method, not async)
        bars = self.tradier_client.get_historical_bars(
            symbol=symbol, interval=interval, start_date=start_date, end_date=end_date
        )

        if not bars:
            logger.warning(
                f"No historical data available for {symbol} in date range {start_date} to {end_date}"
            )
            return []

        logger.info(f"Retrieved {len(bars)} real market bars for {symbol}")
        return bars

    async def get_latest_price(self, symbol: str) -> float:
        """
        Get latest price for a symbol from Tradier

        Args:
            symbol: Stock symbol

        Returns:
            Current price

        Raises:
            Exception: If Tradier API call fails or no price available
        """
        logger.info(f"Fetching latest price for {symbol}")

        # Call Tradier quote endpoint
        quote = self.tradier_client.get_quote(symbol)

        if not quote or "last" not in quote:
            logger.error(f"No price data available for {symbol}")
            raise Exception(f"Unable to fetch price for {symbol}")

        price = float(quote["last"])
        logger.info(f"Latest price for {symbol}: ${price:.2f}")
        return price

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
