from ..core.config import settings
from datetime import UTC, datetime, timedelta
from typing import Any
import aiohttp
import json
import logging
import pandas as pd
import redis

"""
Market Data Service for Real-Time Data Aggregation
Handles data fetching from multiple sources (Alpha Vantage, Tradier, etc.)
"""

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service for aggregating real-time market data from multiple sources"""

    def __init__(self):
        # Use environment-based Redis configuration
        if settings.REDIS_URL:
            self.redis_client = redis.from_url(
                settings.REDIS_URL, decode_responses=True
            )
        else:
            # Fallback to localhost for development
            self.redis_client = redis.Redis(
                host="localhost", port=6379, db=0, decode_responses=True
            )

        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.tradier_token = settings.TRADIER_ACCESS_TOKEN
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_real_time_quote(self, symbol: str) -> dict[str, Any] | None:
        """Get real-time quote for a symbol from multiple sources"""
        try:
            # Check cache first
            cached_data = self.redis_client.get(f"quote:{symbol}")
            if cached_data:
                data = json.loads(cached_data)
                # Check if cache is still valid (less than 30 seconds old)
                cache_time = datetime.fromisoformat(data.get("cache_timestamp", ""))
                if datetime.now(UTC) - cache_time < timedelta(seconds=30):
                    return data

            # Try multiple data sources
            quote_data = None

            # Try Alpha Vantage first
            if self.alpha_vantage_key:
                quote_data = await self._get_alpha_vantage_quote(symbol)

            # Fallback to Tradier if Alpha Vantage fails
            if not quote_data and self.tradier_token:
                quote_data = await self._get_tradier_quote(symbol)

            if quote_data:
                # Add cache timestamp
                quote_data["cache_timestamp"] = datetime.now(UTC).isoformat()

                # Cache for 30 seconds
                self.redis_client.setex(f"quote:{symbol}", 30, json.dumps(quote_data))

                return quote_data

            return None

        except Exception as e:
            logger.error(f"Error getting real-time quote for {symbol}: {e}")
            return None

    async def _get_alpha_vantage_quote(self, symbol: str) -> dict[str, Any] | None:
        """Get quote from Alpha Vantage API"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.alpha_vantage_key,
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    if "Global Quote" in data:
                        quote = data["Global Quote"]
                        return {
                            "symbol": symbol,
                            "price": float(quote.get("05. price", 0)),
                            "change": float(quote.get("09. change", 0)),
                            "change_percent": float(
                                quote.get("10. change percent", 0).replace("%", "")
                            ),
                            "volume": int(quote.get("06. volume", 0)),
                            "high": float(quote.get("03. high", 0)),
                            "low": float(quote.get("04. low", 0)),
                            "open": float(quote.get("02. open", 0)),
                            "previous_close": float(quote.get("08. previous close", 0)),
                            "timestamp": quote.get("07. latest trading day", ""),
                            "source": "alpha_vantage",
                        }

            return None

        except Exception as e:
            logger.error(f"Alpha Vantage API error for {symbol}: {e}")
            return None

    async def _get_tradier_quote(self, symbol: str) -> dict[str, Any] | None:
        """Get quote from Tradier API"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            url = "https://api.tradier.com/v1/markets/quotes"
            params = {"symbols": symbol}
            headers = {
                "Authorization": f"Bearer {self.tradier_token}",
                "Accept": "application/json",
            }

            async with self.session.get(
                url, params=params, headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    if "quotes" in data and "quote" in data["quotes"]:
                        quote = data["quotes"]["quote"]
                        return {
                            "symbol": symbol,
                            "price": float(quote.get("last", 0)),
                            "change": float(quote.get("change", 0)),
                            "change_percent": float(quote.get("change_percentage", 0)),
                            "volume": int(quote.get("volume", 0)),
                            "high": float(quote.get("high", 0)),
                            "low": float(quote.get("low", 0)),
                            "open": float(quote.get("open", 0)),
                            "previous_close": float(quote.get("close", 0)),
                            "timestamp": quote.get("date", ""),
                            "source": "tradier",
                        }

            return None

        except Exception as e:
            logger.error(f"Tradier API error for {symbol}: {e}")
            return None

    async def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1d",
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data for a symbol

        Args:
            symbol: Stock symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            timeframe: Data timeframe (1d, 1h, etc.)

        Returns:
            DataFrame with columns: open, high, low, close, volume
        """
        try:
            cache_key = (
                f"historical:{symbol}:{timeframe}:{start_date.date()}:{end_date.date()}"
            )

            # Check cache
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return pd.read_json(cached_data, orient="split")

            # Try Alpha Vantage first
            if self.alpha_vantage_key:
                df = await self._get_alpha_vantage_historical(
                    symbol, start_date, end_date, timeframe
                )
                if not df.empty:
                    # Cache for 1 hour
                    self.redis_client.setex(cache_key, 3600, df.to_json(orient="split"))
                    return df

            # Fallback to Tradier
            if self.tradier_token:
                df = await self._get_tradier_historical(
                    symbol, start_date, end_date, timeframe
                )
                if not df.empty:
                    # Cache for 1 hour
                    self.redis_client.setex(cache_key, 3600, df.to_json(orient="split"))
                    return df

            # Return empty DataFrame if no data available
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

    async def _get_alpha_vantage_historical(
        self, symbol: str, start_date: datetime, end_date: datetime, timeframe: str
    ) -> pd.DataFrame:
        """Get historical data from Alpha Vantage"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # Map timeframe to Alpha Vantage function
            function_map = {
                "1d": "TIME_SERIES_DAILY",
                "1h": "TIME_SERIES_INTRADAY",
                "5m": "TIME_SERIES_INTRADAY",
            }

            function = function_map.get(timeframe, "TIME_SERIES_DAILY")
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.alpha_vantage_key,
                "outputsize": "full",
            }

            if function == "TIME_SERIES_INTRADAY":
                params["interval"] = timeframe

            url = "https://www.alphavantage.co/query"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    # Find the time series key
                    time_series_key = next(
                        (k for k in data.keys() if "Time Series" in k), None
                    )

                    if time_series_key and time_series_key in data:
                        time_series = data[time_series_key]

                        # Convert to DataFrame
                        df = pd.DataFrame.from_dict(time_series, orient="index")
                        df.index = pd.to_datetime(df.index)

                        # Rename columns
                        df.columns = [
                            col.split(". ")[1] for col in df.columns
                        ]  # Remove number prefix
                        df.rename(
                            columns={
                                "open": "open",
                                "high": "high",
                                "low": "low",
                                "close": "close",
                                "volume": "volume",
                            },
                            inplace=True,
                        )

                        # Convert to numeric
                        for col in ["open", "high", "low", "close", "volume"]:
                            df[col] = pd.to_numeric(df[col])

                        # Filter by date range
                        df = df[(df.index >= start_date) & (df.index <= end_date)]

                        # Sort by date
                        df = df.sort_index()

                        return df

            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Alpha Vantage historical data error for {symbol}: {e}")
            return pd.DataFrame()

    async def _get_tradier_historical(
        self, symbol: str, start_date: datetime, end_date: datetime, timeframe: str
    ) -> pd.DataFrame:
        """Get historical data from Tradier"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            url = "https://api.tradier.com/v1/markets/history"
            params = {
                "symbol": symbol,
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
            }

            # Map timeframe
            if timeframe == "1d":
                params["interval"] = "daily"
            elif timeframe == "1h":
                params["interval"] = "hourly"

            headers = {
                "Authorization": f"Bearer {self.tradier_token}",
                "Accept": "application/json",
            }

            async with self.session.get(
                url, params=params, headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    if "history" in data and "day" in data["history"]:
                        history = data["history"]["day"]

                        # Convert to list if single day
                        if isinstance(history, dict):
                            history = [history]

                        # Create DataFrame
                        df = pd.DataFrame(history)
                        df["date"] = pd.to_datetime(df["date"])
                        df.set_index("date", inplace=True)

                        # Rename columns
                        df.rename(
                            columns={
                                "open": "open",
                                "high": "high",
                                "low": "low",
                                "close": "close",
                                "volume": "volume",
                            },
                            inplace=True,
                        )

                        return df

            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Tradier historical data error for {symbol}: {e}")
            return pd.DataFrame()

    async def get_market_indicators(self) -> dict[str, Any]:
        """
        Get broad market indicators (VIX, sentiment, sector performance)

        Returns:
            Dictionary with market indicator data
        """
        try:
            # Check cache
            cached_data = self.redis_client.get("market_indicators")
            if cached_data:
                return json.loads(cached_data)

            indicators = {}

            # Get VIX (volatility index)
            vix_quote = await self.get_real_time_quote("^VIX")
            if vix_quote:
                indicators["vix"] = {
                    "value": vix_quote["price"],
                    "change": vix_quote["change"],
                    "level": (
                        "low"
                        if vix_quote["price"] < 15
                        else "high"
                        if vix_quote["price"] > 25
                        else "normal"
                    ),
                }

            # Get major indices
            for symbol, name in [
                ("SPY", "S&P 500"),
                ("QQQ", "Nasdaq"),
                ("DIA", "Dow Jones"),
            ]:
                quote = await self.get_real_time_quote(symbol)
                if quote:
                    indicators[name.lower().replace(" ", "_")] = {
                        "symbol": symbol,
                        "price": quote["price"],
                        "change_percent": quote["change_percent"],
                        "trend": "bullish" if quote["change"] > 0 else "bearish",
                    }

            # Cache for 5 minutes
            self.redis_client.setex("market_indicators", 300, json.dumps(indicators))

            return indicators

        except Exception as e:
            logger.error(f"Error getting market indicators: {e}")
            return {}

    async def get_market_status(self) -> dict[str, Any]:
        """Get overall market status"""
        try:
            # Check cache first
            cached_status = self.redis_client.get("market_status")
            if cached_status:
                return json.loads(cached_status)

            # Determine market status based on time
            now = datetime.now(UTC)
            market_status = {
                "is_open": False,
                "next_open": None,
                "next_close": None,
                "timezone": "UTC",
            }

            # Simple market hours logic (9:30 AM - 4:00 PM EST, Monday-Friday)
            # This is a simplified version - in production, use proper market calendar
            weekday = now.weekday()
            hour = now.hour

            if weekday < 5:  # Monday-Friday
                if 14 <= hour < 21:  # 9:30 AM - 4:00 PM EST
                    market_status["is_open"] = True
                else:
                    market_status["is_open"] = False

            # Cache for 1 minute
            self.redis_client.setex("market_status", 60, json.dumps(market_status))

            return market_status

        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {"is_open": False, "error": str(e)}

    async def get_top_gainers(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get top gaining stocks"""
        try:
            # This would typically come from a market data provider
            # For now, return mock data
            return [
                {
                    "symbol": "AAPL",
                    "price": 150.25,
                    "change": 2.15,
                    "change_percent": 1.45,
                },
                {
                    "symbol": "MSFT",
                    "price": 300.50,
                    "change": 4.20,
                    "change_percent": 1.42,
                },
            ]
        except Exception as e:
            logger.error(f"Error getting top gainers: {e}")
            return []

    async def get_top_losers(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get top losing stocks"""
        try:
            # This would typically come from a market data provider
            # For now, return mock data
            return [
                {
                    "symbol": "TSLA",
                    "price": 200.75,
                    "change": -5.25,
                    "change_percent": -2.55,
                }
            ]
        except Exception as e:
            logger.error(f"Error getting top losers: {e}")
            return []

    async def get_market_summary(self) -> dict[str, Any]:
        """Get overall market summary"""
        try:
            # Get major indices
            indices = ["SPY", "QQQ", "DIA", "IWM"]
            index_data = []

            for symbol in indices:
                quote = await self.get_real_time_quote(symbol)
                if quote:
                    index_data.append(quote)

            return {
                "indices": index_data,
                "market_status": await self.get_market_status(),
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {"error": str(e)}
