from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from ..core.unified_auth import get_current_user_unified
from ..models.database import User


router = APIRouter()

# Initialize news aggregator at module level
news_aggregator = None
news_cache = None

try:
    from app.services.news.news_aggregator import NewsAggregator
    from app.services.news.news_cache import get_news_cache

    news_aggregator = NewsAggregator()
    news_cache = get_news_cache()
    print("[OK] News aggregator initialized with available providers")
    print("[OK] News cache initialized")
except Exception as e:
    print(f"[WARNING] News aggregator failed to initialize: {e}")


@router.get("/news/company/{symbol}")
async def get_company_news(
    symbol: str,
    days_back: int = Query(default=7, ge=1, le=30),
    sentiment: str | None = Query(default=None, regex="^(bullish|bearish|neutral)$"),
    provider: str | None = None,
    use_cache: bool = Query(default=True),
    current_user: User = Depends(get_current_user_unified),
):
    """
    Get aggregated news for specific company

    Args:
        symbol: Stock symbol (e.g., AAPL)
        days_back: Number of days to look back (1-30)
        sentiment: Filter by sentiment (bullish, bearish, neutral)
        provider: Filter by provider name (finnhub, alpha_vantage, polygon)
        use_cache: Whether to use cached results
    """
    if not news_aggregator:
        raise HTTPException(status_code=503, detail="News service unavailable")

    try:
        # Check cache first (cache key includes filters)
        if use_cache and news_cache:
            cached_filtered = news_cache.get(
                "company",
                symbol=symbol,
                days_back=days_back,
                sentiment=sentiment,
                provider=provider,
            )
            if cached_filtered is not None:
                # Cached results are already filtered - no need to re-filter
                return {
                    "symbol": symbol,
                    "articles": cached_filtered,
                    "count": len(cached_filtered),
                    "sources": [
                        p.get_provider_name() for p in news_aggregator.providers
                    ],
                    "cached": True,
                }

        # Fetch fresh data
        articles = news_aggregator.get_company_news(symbol, days_back)

        # Apply filters to fresh data
        filtered = _apply_filters(articles, sentiment, provider)

        # Cache the filtered results (cache key includes filters for uniqueness)
        if news_cache:
            news_cache.set(
                "company",
                filtered,
                symbol=symbol,
                days_back=days_back,
                sentiment=sentiment,
                provider=provider,
            )

        return {
            "data": {
                "symbol": symbol,
                "articles": filtered,
                "sources": [p.get_provider_name() for p in news_aggregator.providers],
                "cached": False,
            },
            "count": len(filtered),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/news/market")
async def get_market_news(
    category: str = Query(default="general"),
    limit: int = Query(default=50, ge=1, le=200),
    sentiment: str | None = Query(default=None, regex="^(bullish|bearish|neutral)$"),
    provider: str | None = None,
    use_cache: bool = Query(default=True),
    current_user: User = Depends(get_current_user_unified),
):
    """
    Get aggregated market news

    Args:
        category: News category (general, forex, crypto, etc.)
        limit: Maximum number of articles to return (1-200)
        sentiment: Filter by sentiment (bullish, bearish, neutral)
        provider: Filter by provider name (finnhub, alpha_vantage, polygon)
        use_cache: Whether to use cached results
    """
    if not news_aggregator:
        raise HTTPException(status_code=503, detail="News service unavailable")

    try:
        # Check cache first (cache key includes filters)
        if use_cache and news_cache:
            cached_filtered = news_cache.get(
                "market",
                category=category,
                limit=limit,
                sentiment=sentiment,
                provider=provider,
            )
            if cached_filtered is not None:
                # Cached results are already filtered - no need to re-filter
                return {
                    "data": {
                        "category": category,
                        "articles": cached_filtered[:limit],
                        "sources": [
                            p.get_provider_name() for p in news_aggregator.providers
                        ],
                        "cached": True,
                    },
                    "count": len(cached_filtered[:limit]),
                    "timestamp": datetime.now().isoformat(),
                }

        # Fetch fresh data (fetch more to allow for filtering)
        articles = news_aggregator.get_market_news(category, limit * 2)

        # Apply filters to fresh data
        filtered = _apply_filters(articles, sentiment, provider)

        # Cache the filtered results (cache key includes filters for uniqueness)
        if news_cache:
            news_cache.set(
                "market",
                filtered,
                category=category,
                limit=limit,
                sentiment=sentiment,
                provider=provider,
            )

        return {
            "data": {
                "category": category,
                "articles": filtered[:limit],
                "sources": [p.get_provider_name() for p in news_aggregator.providers],
                "cached": False,
            },
            "count": len(filtered[:limit]),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/news/providers")
async def get_news_providers(current_user: User = Depends(get_current_user_unified)):
    """List active news providers"""
    if not news_aggregator:
        return {"providers": [], "status": "unavailable"}

    providers = [
        {"name": p.get_provider_name(), "status": "active"}
        for p in news_aggregator.providers
    ]
    return {
        "data": providers,
        "count": len(providers),
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/news/health")
async def get_news_health(current_user: User = Depends(get_current_user_unified)):
    """
    Get health status of all news providers including circuit breaker states.

    This endpoint provides observability into:
    - Provider availability (healthy/degraded/down)
    - Circuit breaker states (CLOSED/HALF_OPEN/OPEN)
    - Failure counts and timestamps
    - Overall system health percentage

    Use this for monitoring and alerting on news service degradation.
    """
    if not news_aggregator:
        return {"status": "unavailable", "message": "News aggregator not initialized"}

    try:
        health = news_aggregator.get_provider_health()
        return {
            "data": health,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get health status: {e!s}"
        )


@router.get("/news/sentiment/market")
async def get_market_sentiment(
    category: str = Query(default="general"),
    days_back: int = Query(default=7, ge=1, le=30),
    current_user: User = Depends(get_current_user_unified),
):
    """
    Get aggregated market sentiment analytics

    Returns sentiment distribution and average score across all news
    """
    if not news_aggregator:
        raise HTTPException(status_code=503, detail="News service unavailable")

    try:
        articles = news_aggregator.get_market_news(category, 200)

        # Calculate sentiment stats
        sentiments = {"bullish": 0, "bearish": 0, "neutral": 0}
        total_score = 0.0

        for article in articles:
            sentiment = article.get("sentiment", "neutral")
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
            total_score += article.get("sentiment_score", 0.0)

        total_articles = len(articles)
        avg_score = total_score / total_articles if total_articles > 0 else 0.0

        return {
            "data": {
                "category": category,
                "total_articles": total_articles,
                "avg_sentiment_score": round(avg_score, 3),
                "sentiment_distribution": {
                    "bullish": sentiments["bullish"],
                    "bearish": sentiments["bearish"],
                    "neutral": sentiments["neutral"],
                    "bullish_percent": (
                        round(sentiments["bullish"] / total_articles * 100, 1)
                        if total_articles > 0
                        else 0
                    ),
                    "bearish_percent": (
                        round(sentiments["bearish"] / total_articles * 100, 1)
                        if total_articles > 0
                        else 0
                    ),
                    "neutral_percent": (
                        round(sentiments["neutral"] / total_articles * 100, 1)
                        if total_articles > 0
                        else 0
                    ),
                },
                "overall_sentiment": (
                    "bullish"
                    if avg_score > 0.15
                    else "bearish"
                    if avg_score < -0.15
                    else "neutral"
                ),
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/news/cache/stats")
async def get_cache_stats(current_user: User = Depends(get_current_user_unified)):
    """Get news cache statistics"""
    if not news_cache:
        return {"status": "unavailable"}

    return news_cache.get_stats()


@router.post("/news/cache/clear")
async def clear_news_cache(current_user: User = Depends(get_current_user_unified)):
    """Clear all cached news"""
    if not news_cache:
        raise HTTPException(status_code=503, detail="Cache unavailable")

    news_cache.clear_all()
    return {
        "success": True,
        "message": "Cache cleared successfully",
        "timestamp": datetime.now().isoformat(),
    }


# Helper functions
def _apply_filters(
    articles: list[dict], sentiment: str | None, provider: str | None
) -> list[dict]:
    """Apply sentiment and provider filters to articles"""
    filtered = articles

    if sentiment:
        filtered = [a for a in filtered if a.get("sentiment") == sentiment]

    if provider:
        filtered = [
            a for a in filtered if provider.lower() in a.get("provider", "").lower()
        ]

    return filtered
