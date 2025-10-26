"""
Stock Analysis Service - Business logic for stock information and news

This service handles stock quote retrieval, company info compilation,
technical analysis, and news aggregation.
"""


from ..core.logging_utils import get_secure_logger
from .cache import CacheService
from .tradier_client import TradierClient


logger = get_secure_logger(__name__)


class CompanyInfo:
    """Company information data class"""

    def __init__(
        self,
        symbol: str,
        name: str,
        current_price: float,
        change: float,
        change_percent: float,
        description: str | None = None,
        sector: str | None = None,
        industry: str | None = None,
        market_cap: float | None = None,
        pe_ratio: float | None = None,
        dividend_yield: float | None = None,
        week_52_high: float | None = None,
        week_52_low: float | None = None,
        avg_volume: int | None = None,
    ):
        self.symbol = symbol
        self.name = name
        self.current_price = current_price
        self.change = change
        self.change_percent = change_percent
        self.description = description
        self.sector = sector
        self.industry = industry
        self.market_cap = market_cap
        self.pe_ratio = pe_ratio
        self.dividend_yield = dividend_yield
        self.week_52_high = week_52_high
        self.week_52_low = week_52_low
        self.avg_volume = avg_volume

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "description": self.description,
            "sector": self.sector,
            "industry": self.industry,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "dividend_yield": self.dividend_yield,
            "week_52_high": self.week_52_high,
            "week_52_low": self.week_52_low,
            "avg_volume": self.avg_volume,
            "current_price": self.current_price,
            "change": self.change,
            "change_percent": self.change_percent,
        }


class NewsArticle:
    """News article data class"""

    def __init__(
        self,
        title: str,
        url: str,
        source: str,
        published_at: str,
        summary: str | None = None,
        sentiment: str | None = None,
    ):
        self.title = title
        self.summary = summary
        self.url = url
        self.source = source
        self.published_at = published_at
        self.sentiment = sentiment

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at,
            "sentiment": self.sentiment,
        }


class StockAnalysisService:
    """Service for stock information retrieval and analysis"""

    def __init__(self, tradier_client: TradierClient, cache: CacheService):
        """
        Initialize stock analysis service

        Args:
            tradier_client: Tradier API client for market data
            cache: Cache service for storing/retrieving data
        """
        self.tradier = tradier_client
        self.cache = cache

    def get_company_info(self, symbol: str) -> CompanyInfo:
        """
        Get comprehensive company information for a symbol

        Args:
            symbol: Stock ticker symbol

        Returns:
            CompanyInfo object with all available data

        Raises:
            ValueError: If symbol is invalid or not found
            RuntimeError: If market data is temporarily unavailable
        """
        symbol = symbol.upper()

        # Try to get real-time quote from Tradier
        try:
            quote = self.tradier.get_quote(symbol)
        except Exception as e:
            logger.error(
                "Tradier API failed for symbol",
                symbol=symbol,
                error_type=type(e).__name__,
                error_msg=str(e),
            )
            # Try cache fallback
            cached_info = self.cache.get(f"stock_info:{symbol}")
            if cached_info:
                logger.info("Returning cached stock info", symbol=symbol)
                return CompanyInfo(**cached_info)
            raise RuntimeError(
                f"Market data temporarily unavailable for {symbol}"
            ) from e

        if not quote or "symbol" not in quote:
            raise ValueError(f"Stock {symbol} not found")

        # Extract data from quote
        current_price = float(quote.get("last", 0))
        change = float(quote.get("change", 0))
        change_percent = float(quote.get("change_percentage", 0))

        # Build company info object
        company_info = CompanyInfo(
            symbol=symbol,
            name=quote.get(
                "description", symbol
            ),  # Tradier includes company name in "description"
            description=f"{quote.get('description', symbol)} - Real-time stock quote",
            sector=None,  # Tradier doesn't provide sector in quote
            industry=None,
            market_cap=None,  # Would need fundamental data API
            pe_ratio=None,
            dividend_yield=None,
            week_52_high=float(quote.get("week_52_high", 0))
            if quote.get("week_52_high")
            else None,
            week_52_low=float(quote.get("week_52_low", 0))
            if quote.get("week_52_low")
            else None,
            avg_volume=int(quote.get("average_volume", 0))
            if quote.get("average_volume")
            else None,
            current_price=current_price,
            change=change,
            change_percent=change_percent,
        )

        # Cache for 30 seconds
        self.cache.set(f"stock_info:{symbol}", company_info.to_dict(), ttl=30)

        logger.info("Retrieved stock info", symbol=symbol, price=current_price)
        return company_info

    def get_technical_data(self, symbol: str) -> dict:
        """
        Get technical analysis data for a symbol

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with technical indicators (bid, ask, volume, OHLC, etc.)

        Raises:
            RuntimeError: If data retrieval fails
        """
        symbol = symbol.upper()

        try:
            quote = self.tradier.get_quote(symbol)
        except Exception as e:
            logger.error(
                "Tradier API failed for technicals",
                symbol=symbol,
                error_type=type(e).__name__,
                error_msg=str(e),
            )
            # Try cache fallback
            cached_technicals = self.cache.get(f"technicals:{symbol}")
            if cached_technicals:
                logger.info("Returning cached technicals", symbol=symbol)
                return cached_technicals
            # If no cache, provide minimal technicals
            quote = {}

        # Build technical indicators data
        technicals = {
            "bid": float(quote.get("bid", 0)),
            "ask": float(quote.get("ask", 0)),
            "volume": int(quote.get("volume", 0)),
            "open": float(quote.get("open", 0)),
            "high": float(quote.get("high", 0)),
            "low": float(quote.get("low", 0)),
            "close": float(quote.get("prevclose", 0)),
            "vwap": None,  # Volume-weighted average price - would calculate from historical data
        }

        # Cache technicals for 30 seconds
        self.cache.set(f"technicals:{symbol}", technicals, ttl=30)

        return technicals

    def get_news(self, symbol: str, limit: int = 10) -> list[NewsArticle]:
        """
        Get recent news articles for a stock

        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of articles to return (1-50)

        Returns:
            List of NewsArticle objects

        Note:
            Currently returns empty list. Real-time news API integration
            is planned for Phase 2 (Benzinga, NewsAPI, or Alpha Vantage)
        """
        symbol = symbol.upper()

        # PHASE 2 INTEGRATION: Real-time news API integration pending
        logger.warning("News API not yet integrated", symbol=symbol)

        news_articles: list[NewsArticle] = []

        logger.info("Retrieved news articles", symbol=symbol, count=len(news_articles))
        return news_articles

    def get_complete_info(self, symbol: str) -> dict:
        """
        Get complete stock information including company info, technicals, and news

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with company, technicals, and news data

        Raises:
            ValueError: If symbol is invalid
            RuntimeError: If data retrieval fails
        """
        symbol = symbol.upper()

        # Get company info (with built-in fallback)
        company = self.get_company_info(symbol)

        # Get technical data
        technicals = self.get_technical_data(symbol)

        # Get news (currently empty, but structured for future)
        news = self.get_news(symbol, limit=5)

        logger.info("Retrieved complete stock info", symbol=symbol)

        return {
            "company": company.to_dict(),
            "technicals": technicals,
            "news": [article.to_dict() for article in news],
        }


def get_stock_analysis_service(
    tradier_client: TradierClient, cache: CacheService
) -> StockAnalysisService:
    """
    Factory function to create StockAnalysisService

    Args:
        tradier_client: Tradier API client
        cache: Cache service

    Returns:
        StockAnalysisService instance
    """
    return StockAnalysisService(tradier_client, cache)
