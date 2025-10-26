"""
Stock Information and News Router
Provides stock lookup, company info, and news endpoints for the StockLookup feature

SECURITY: No sensitive data logged
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..core.logging_utils import get_secure_logger
from ..core.unified_auth import get_current_user_unified
from ..models.database import User
from ..services.cache import CacheService, get_cache
from ..services.stock_analysis_service import get_stock_analysis_service
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
        client = get_tradier_client()
        stock_service = get_stock_analysis_service(client, cache)

        company = stock_service.get_company_info(symbol)
        return CompanyInfo(**company.to_dict())

    except ValueError as e:
        logger.error(
            "Invalid stock symbol",
            symbol=symbol,
            error_msg=str(e)
        )
        raise HTTPException(status_code=404, detail=str(e)) from e
    except RuntimeError as e:
        logger.error(
            "Market data unavailable",
            symbol=symbol,
            error_msg=str(e)
        )
        raise HTTPException(status_code=503, detail=str(e)) from e
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
    cache: CacheService = Depends(get_cache),
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
        client = get_tradier_client()
        stock_service = get_stock_analysis_service(client, cache)

        news = stock_service.get_news(symbol, limit)
        return [NewsArticle(**article.to_dict()) for article in news]

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
        client = get_tradier_client()
        stock_service = get_stock_analysis_service(client, cache)

        complete_info = stock_service.get_complete_info(symbol)

        return StockInfoResponse(
            company=CompanyInfo(**complete_info["company"]),
            technicals=complete_info["technicals"],
            news=[NewsArticle(**article) for article in complete_info["news"]],
        )

    except ValueError as e:
        logger.error(
            "Invalid stock symbol",
            symbol=symbol,
            error_msg=str(e)
        )
        raise HTTPException(status_code=404, detail=str(e)) from e
    except RuntimeError as e:
        logger.error(
            "Market data unavailable",
            symbol=symbol,
            error_msg=str(e)
        )
        raise HTTPException(status_code=503, detail=str(e)) from e
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
