"""
ML Sentiment & Signals API Router
Real sentiment analysis and trade signal endpoints
"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..core.auth import get_current_user
from ..core.config import get_settings
from ..ml.data_pipeline import DataPipeline
from ..ml.sentiment_analyzer import get_sentiment_analyzer
from ..ml.signal_generator import SignalType, get_signal_generator
from ..models.user import User


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sentiment", tags=["ML Sentiment & Signals"])
settings = get_settings()


# Response Models
class SentimentResponse(BaseModel):
    """Sentiment analysis response"""

    symbol: str
    sentiment: str
    score: float
    confidence: float
    reasoning: str
    timestamp: datetime
    source: str


class SignalResponse(BaseModel):
    """Trade signal response"""

    symbol: str
    signal: SignalType
    strength: str
    confidence: float
    price: float
    target_price: float | None
    stop_loss: float | None
    reasoning: str
    technical_score: float
    sentiment_score: float
    combined_score: float
    timestamp: datetime


# Endpoints
@router.get("/sentiment/{symbol}", response_model=SentimentResponse)
async def get_sentiment(
    symbol: str,
    include_news: bool = Query(True, description="Include news analysis"),
    lookback_days: int = Query(7, ge=1, le=30, description="Days of news to analyze"),
    current_user: User = Depends(get_current_user),
):
    """
    Get sentiment analysis for a symbol

    Analyzes recent news and market sentiment using AI.
    """
    try:
        sentiment_analyzer = get_sentiment_analyzer()
        data_pipeline = DataPipeline()

        if include_news:
            # Fetch recent news
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=lookback_days)

            news_articles = await data_pipeline.fetch_news(
                symbol=symbol, start_date=start_date, end_date=end_date
            )

            if news_articles:
                # Analyze news sentiment
                sentiment = await sentiment_analyzer.analyze_news_batch(
                    symbol, news_articles
                )
            else:
                # No news available - return neutral
                from ..ml.sentiment_analyzer import SentimentScore

                sentiment = SentimentScore(
                    symbol=symbol,
                    sentiment="neutral",
                    score=0.0,
                    confidence=0.0,
                    reasoning="No recent news articles found",
                    timestamp=datetime.utcnow(),
                    source="news",
                )
        else:
            # Return neutral if not analyzing news
            from ..ml.sentiment_analyzer import SentimentScore

            sentiment = SentimentScore(
                symbol=symbol,
                sentiment="neutral",
                score=0.0,
                confidence=0.0,
                reasoning="News analysis disabled",
                timestamp=datetime.utcnow(),
                source="manual",
            )

        return SentimentResponse(
            symbol=sentiment.symbol,
            sentiment=sentiment.sentiment,
            score=sentiment.score,
            confidence=sentiment.confidence,
            reasoning=sentiment.reasoning,
            timestamp=sentiment.timestamp,
            source=sentiment.source,
        )

    except Exception as e:
        logger.error(f"Error getting sentiment for {symbol}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Sentiment analysis failed: {e!s}"
        ) from e


@router.get("/signals/{symbol}", response_model=SignalResponse)
async def get_trade_signal(
    symbol: str,
    include_sentiment: bool = Query(True, description="Include sentiment analysis"),
    lookback_days: int = Query(30, ge=7, le=90, description="Days of price history"),
    current_user: User = Depends(get_current_user),
):
    """
    Get AI-generated trade signal for a symbol

    Combines technical analysis with sentiment to generate BUY/SELL/HOLD signals.
    """
    try:
        signal_generator = get_signal_generator()
        data_pipeline = DataPipeline()

        # Fetch price data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=lookback_days)

        price_data = await data_pipeline.fetch_market_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval="1d",
        )

        if price_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No price data available for {symbol}",
            )

        # Fetch news if requested
        news_articles = []
        if include_sentiment:
            news_articles = await data_pipeline.fetch_news(
                symbol=symbol,
                start_date=end_date - timedelta(days=7),
                end_date=end_date,
            )

        # Generate signal
        signal = await signal_generator.generate_signal(
            symbol=symbol, price_data=price_data, news_articles=news_articles
        )

        return SignalResponse(
            symbol=signal.symbol,
            signal=signal.signal,
            strength=signal.strength.value,
            confidence=signal.confidence,
            price=signal.price,
            target_price=signal.target_price,
            stop_loss=signal.stop_loss,
            reasoning=signal.reasoning,
            technical_score=signal.technical_score,
            sentiment_score=signal.sentiment_score,
            combined_score=signal.combined_score,
            timestamp=signal.timestamp,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating signal for {symbol}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Signal generation failed: {e!s}"
        ) from e


@router.post("/signals/batch", response_model=list[SignalResponse])
async def get_batch_signals(
    symbols: list[str],
    include_sentiment: bool = Query(True, description="Include sentiment analysis"),
    lookback_days: int = Query(30, ge=7, le=90, description="Days of price history"),
    current_user: User = Depends(get_current_user),
):
    """
    Get trade signals for multiple symbols

    Batch endpoint for analyzing multiple stocks at once.
    Limited to 10 symbols per request.
    """
    if len(symbols) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 symbols allowed per batch request",
        )

    signal_generator = get_signal_generator()
    data_pipeline = DataPipeline()
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=lookback_days)

    results = []
    for symbol in symbols:
        try:
            # Fetch price data
            price_data = await data_pipeline.fetch_market_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval="1d",
            )

            if price_data.empty:
                logger.warning(f"No price data for {symbol}, skipping")
                continue

            # Fetch news if requested
            news_articles = []
            if include_sentiment:
                news_articles = await data_pipeline.fetch_news(
                    symbol=symbol,
                    start_date=end_date - timedelta(days=7),
                    end_date=end_date,
                )

            # Generate signal
            signal = await signal_generator.generate_signal(
                symbol=symbol,
                price_data=price_data,
                news_articles=news_articles,
            )

            results.append(
                SignalResponse(
                    symbol=signal.symbol,
                    signal=signal.signal,
                    strength=signal.strength.value,
                    confidence=signal.confidence,
                    price=signal.price,
                    target_price=signal.target_price,
                    stop_loss=signal.stop_loss,
                    reasoning=signal.reasoning,
                    technical_score=signal.technical_score,
                    sentiment_score=signal.sentiment_score,
                    combined_score=signal.combined_score,
                    timestamp=signal.timestamp,
                )
            )

        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            # Continue with other symbols

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No signals could be generated for the provided symbols",
        )

    return results


@router.get("/health")
async def ml_sentiment_health_check():
    """Check ML sentiment service health"""
    try:
        # Verify ML services can be instantiated
        sentiment_analyzer = get_sentiment_analyzer()
        signal_generator = get_signal_generator()

        return {
            "status": "healthy",
            "services": {
                "sentiment_analyzer": "ready",
                "signal_generator": "ready",
                "anthropic_configured": bool(settings.ANTHROPIC_API_KEY),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"ML health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
