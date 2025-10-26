"""
Stock Information and News Router
Provides stock lookup, company info, and news endpoints for the StockLookup feature

SECURITY: No sensitive data logged
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..core.unified_auth import get_current_user_unified
from ..core.logging_utils import get_secure_logger
from ..models.database import User
from ..services.cache import CacheService, get_cache
from ..services.tradier_client import get_tradier_client


logger = get_secure_logger(__name__)

router = APIRouter(prefix="/stock", tags=["stock"])


class CompanyInfo(BaseModel):
    """Company information model"""

    symbol: str
    name: str
    description: str | None = None
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    dividend_yield: float | None = None
    week_52_high: float | None = None
    week_52_low: float | None = None
    avg_volume: int | None = None
    current_price: float
    change: float
    change_percent: float


class NewsArticle(BaseModel):
    """News article model"""

    title: str
    summary: str | None = None
    url: str
    source: str
    published_at: str
    sentiment: str | None = None  # "positive", "negative", "neutral"


class StockInfoResponse(BaseModel):
    """Complete stock information response"""

    company: CompanyInfo
    technicals: dict
    news: list[NewsArticle] = []


@router.get("/{symbol}/info")
async def get_stock_info(
    symbol: str,
    current_user: User = Depends(get_current_user_unified),
    cache: CacheService = Depends(get_cache),
) -> CompanyInfo:
    """
    Get comprehensive company information for a symbol

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")

    Returns:
        Company info including name, sector, market cap, ratios, etc.
    """
    try:
        symbol = symbol.upper()
        client = get_tradier_client()

        # Try to get real-time quote from Tradier
        try:
            quote = client.get_quote(symbol)
        except Exception as e:
            logger.error(
                "Tradier API failed for symbol",
                symbol=symbol,
                error_type=type(e).__name__,
                error_msg=str(e)
            )
            # Try cache fallback
            cached_quote = cache.get(f"stock_info:{symbol}")
            if cached_quote:
                logger.info("Returning cached stock info", symbol=symbol)
                return CompanyInfo(**cached_quote)
            raise HTTPException(
                status_code=503,
                detail=f"Market data temporarily unavailable for {symbol}"
            ) from e

        if not quote or "symbol" not in quote:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

        # Extract data from quote
        current_price = float(quote.get("last", 0))
        change = float(quote.get("change", 0))
        change_percent = float(quote.get("change_percentage", 0))

        # Tradier provides basic info in quote
        # For more detailed company info, would need additional API or database
        company_info = CompanyInfo(
            symbol=symbol,
            name=quote.get("description", symbol),  # Tradier includes company name in "description"
            description=f"{quote.get('description', symbol)} - Real-time stock quote",
            sector=None,  # Tradier doesn't provide sector in quote
            industry=None,
            market_cap=None,  # Would need fundamental data API
            pe_ratio=None,
            dividend_yield=None,
            week_52_high=float(quote.get("week_52_high", 0)) if quote.get("week_52_high") else None,
            week_52_low=float(quote.get("week_52_low", 0)) if quote.get("week_52_low") else None,
            avg_volume=int(quote.get("average_volume", 0)) if quote.get("average_volume") else None,
            current_price=current_price,
            change=change,
            change_percent=change_percent,
        )

        # Cache for 30 seconds
        cache.set(f"stock_info:{symbol}", company_info.model_dump(), ttl=30)

        logger.info(
            "Retrieved stock info",
            symbol=symbol,
            price=current_price
        )
        return company_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get stock info",
            symbol=symbol,
            error_type=type(e).__name__,
            error_msg=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get stock info: {e!s}") from e


@router.get("/{symbol}/news")
async def get_stock_news(
    symbol: str,
    limit: int = Query(default=10, ge=1, le=50, description="Number of news articles to return"),
    current_user: User = Depends(get_current_user_unified),
) -> list[NewsArticle]:
    """
    Get recent news articles for a specific stock

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        limit: Maximum number of articles to return (1-50)

    Returns:
        List of news articles with title, summary, URL, source, and published date

    Note: This endpoint uses a news aggregation service. In production, would integrate
    with NewsAPI, Alpha Vantage, or similar service.
    """
    try:
        symbol = symbol.upper()

        # PHASE 2 INTEGRATION: Real-time news API integration pending
        # Options under evaluation:
        #   - Benzinga News API (preferred - financial focus, real-time)
        #   - NewsAPI.org (general news, slower updates)
        #   - Alpha Vantage (free tier, rate limited)
        # Current: Returns empty array with warning log (news feature disabled until Phase 2)

        # Mock news structure - in production, replace with API call
        logger.warning("News API not yet integrated", symbol=symbol)

        news_articles = []

        # Example of what the news structure would look like:
        # news_articles = [
        #     NewsArticle(
        #         title=f"{symbol} reports quarterly earnings",
        #         summary="Company beats analyst expectations...",
        #         url=f"https://example.com/news/{symbol.lower()}-earnings",
        #         source="Financial Times",
        #         published_at=datetime.now().isoformat(),
        #         sentiment="positive"
        #     )
        # ]

        logger.info(
            "Retrieved news articles",
            symbol=symbol,
            count=len(news_articles)
        )
        return news_articles

    except Exception as e:
        logger.error(
            "Failed to get news",
            symbol=symbol,
            error_type=type(e).__name__,
            error_msg=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get stock news: {e!s}") from e


@router.get("/{symbol}/complete")
async def get_complete_stock_info(
    symbol: str,
    current_user: User = Depends(get_current_user_unified),
    cache: CacheService = Depends(get_cache),
) -> StockInfoResponse:
    """
    Get complete stock information including company info, technicals, and news

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")

    Returns:
        Complete stock information package
    """
    try:
        symbol = symbol.upper()
        client = get_tradier_client()

        # Get company info (with built-in fallback)
        company = await get_stock_info(symbol, current_user, cache)

        # Get quote for technical data with fallback
        try:
            quote = client.get_quote(symbol)
        except Exception as e:
            logger.error(
                "Tradier API failed for technicals",
                symbol=symbol,
                error_type=type(e).__name__,
                error_msg=str(e)
            )
            # Try cache fallback
            cached_technicals = cache.get(f"technicals:{symbol}")
            if cached_technicals:
                logger.info("Returning cached technicals", symbol=symbol)
                news = await get_stock_news(symbol, limit=5, current_user=current_user)
                return StockInfoResponse(
                    company=company,
                    technicals=cached_technicals,
                    news=news
                )
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
        cache.set(f"technicals:{symbol}", technicals, ttl=30)

        # Get news
        news = await get_stock_news(symbol, limit=5, current_user=current_user)

        logger.info("Retrieved complete stock info", symbol=symbol)

        return StockInfoResponse(company=company, technicals=technicals, news=news)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get complete stock info",
            symbol=symbol,
            error_type=type(e).__name__,
            error_msg=str(e)
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to get complete stock info: {e!s}"
        ) from e
