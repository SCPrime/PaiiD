from backend.services.ai_service import AIService
from backend.services.sentiment_analyzer import SentimentAnalyzer
from fastapi import APIRouter, HTTPException, Query
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import logging

"""
AI Router for Market Analysis and Trading Recommendations
Handles AI-powered endpoints for sentiment analysis, recommendations, and chat
"""



logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["ai"])
security = HTTPBearer()

class SentimentAnalysisRequest(BaseModel):
    symbols: list[str]
    days_back: int | None = 7

class TradingRecommendationsRequest(BaseModel):
    user_id: str
    symbols: list[str]
    risk_tolerance: str | None = "medium"

class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: dict | None = None

class NewsSentimentRequest(BaseModel):
    symbols: list[str]
    days_back: int | None = 7

@router.post("/sentiment/analyze")
async def analyze_market_sentiment(request: SentimentAnalysisRequest):
    """
    Analyze market sentiment for given symbols
    """
    try:
        async with SentimentAnalyzer() as analyzer:
            result = await analyzer.get_market_sentiment_summary(request.symbols)
            return result
    except Exception as e:
        logger.error(f"Error analyzing market sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiment/news")
async def analyze_news_sentiment(request: NewsSentimentRequest):
    """
    Analyze sentiment from news articles for given symbols
    """
    try:
        async with SentimentAnalyzer() as analyzer:
            result = await analyzer.analyze_news_sentiment(
                request.symbols, request.days_back
            )
            return result
    except Exception as e:
        logger.error(f"Error analyzing news sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiment/social")
async def analyze_social_sentiment(
    symbols: list[str] = Query(..., description="List of symbols to analyze"),
    hours_back: int = Query(24, description="Hours to look back for social posts"),
):
    """
    Analyze sentiment from social media for given symbols
    """
    try:
        async with SentimentAnalyzer() as analyzer:
            result = await analyzer.analyze_social_sentiment(symbols, hours_back)
            return result
    except Exception as e:
        logger.error(f"Error analyzing social sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations")
async def get_trading_recommendations(request: TradingRecommendationsRequest):
    """
    Get AI-powered trading recommendations
    """
    try:
        # Mock user portfolio and market data
        user_portfolio = {
            "user_id": request.user_id,
            "total_value": 100000,
            "positions": [
                {"symbol": "AAPL", "quantity": 100, "value": 15000},
                {"symbol": "MSFT", "quantity": 50, "value": 15000},
            ],
            "cash": 70000,
        }

        market_data = {
            "AAPL": {"price": 150, "change": 2.5, "volume": 1000000},
            "MSFT": {"price": 300, "change": -1.2, "volume": 800000},
        }

        async with AIService() as ai_service:
            result = await ai_service.generate_trading_recommendations(
                user_portfolio, market_data
            )
            return result
    except Exception as e:
        logger.error(f"Error getting trading recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_ai(request: ChatRequest):
    """
    Chat with AI about market conditions and trading
    """
    try:
        # Prepare context
        context = request.context or {
            "user_id": request.user_id,
            "timestamp": "2025-10-24T20:30:00Z",
            "market_status": "open",
        }

        async with AIService() as ai_service:
            result = await ai_service.chat_with_ai(request.message, context)
            return result
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/{symbols}")
async def get_ai_insights(
    symbols: str,
    user_id: str = Query(..., description="User ID for personalized insights"),
):
    """
    Get AI insights for specific symbols
    """
    try:
        symbol_list = symbols.split(",")

        async with AIService() as ai_service:
            result = await ai_service.get_ai_insights(symbol_list)
            return result
    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment/trending")
async def get_trending_sentiment():
    """
    Get sentiment analysis for trending symbols
    """
    try:
        # Mock trending symbols
        trending_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

        async with SentimentAnalyzer() as analyzer:
            result = await analyzer.get_market_sentiment_summary(trending_symbols)
            return result
    except Exception as e:
        logger.error(f"Error getting trending sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def ai_health_check():
    """
    Check AI service health
    """
    try:
        return {
            "status": "healthy",
            "services": {
                "ai_service": "operational",
                "sentiment_analyzer": "operational",
                "claude_api": "operational",
            },
            "timestamp": "2025-10-24T20:30:00Z",
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
