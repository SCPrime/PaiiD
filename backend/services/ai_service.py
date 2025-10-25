import json
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
import redis

from app.core.config import settings


"""
AI Service for Market Analysis and Trading Recommendations
Integrates Claude API for natural language processing and market insights
"""

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered market analysis and trading recommendations"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=3, decode_responses=True
        )
        self.claude_api_key = settings.ANTHROPIC_API_KEY
        self.claude_base_url = "https://api.anthropic.com/v1/messages"
        self.session = None
        self.rate_limiter = {
            "requests": 0,
            "last_reset": datetime.now(),
            "max_requests": 50,  # 50 requests per minute
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        if now - self.rate_limiter["last_reset"] > timedelta(minutes=1):
            self.rate_limiter["requests"] = 0
            self.rate_limiter["last_reset"] = now

        return self.rate_limiter["requests"] < self.rate_limiter["max_requests"]

    async def _increment_rate_limit(self):
        """Increment request counter"""
        self.rate_limiter["requests"] += 1

    async def analyze_market_sentiment(
        self, symbols: list[str], news_articles: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze market sentiment for given symbols using news articles"""
        try:
            if not await self._check_rate_limit():
                return {"error": "Rate limit exceeded", "retry_after": 60}

            # Prepare context for Claude
            context = f"""
            Analyze the market sentiment for these symbols: {", ".join(symbols)}

            News Articles:
            {json.dumps(news_articles[:10], indent=2)}  # Limit to 10 articles

            Provide:
            1. Overall sentiment (bullish, bearish, neutral)
            2. Confidence score (0-100)
            3. Key factors driving sentiment
            4. Risk assessment
            5. Trading recommendations
            """

            response = await self._call_claude_api(context)
            await self._increment_rate_limit()

            # Parse and structure the response
            sentiment_analysis = {
                "symbols": symbols,
                "overall_sentiment": response.get("sentiment", "neutral"),
                "confidence_score": response.get("confidence", 50),
                "key_factors": response.get("factors", []),
                "risk_assessment": response.get("risk", "medium"),
                "recommendations": response.get("recommendations", []),
                "timestamp": datetime.now().isoformat(),
            }

            # Cache the analysis
            cache_key = f"sentiment_analysis:{':'.join(symbols)}"
            self.redis_client.setex(
                cache_key, 300, json.dumps(sentiment_analysis)
            )  # 5 min cache

            return sentiment_analysis

        except Exception as e:
            logger.error(f"Error analyzing market sentiment: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def generate_trading_recommendations(
        self, user_portfolio: dict[str, Any], market_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate AI-powered trading recommendations"""
        try:
            if not await self._check_rate_limit():
                return {"error": "Rate limit exceeded", "retry_after": 60}

            # Prepare context for Claude
            context = f"""
            Generate trading recommendations based on:

            User Portfolio:
            {json.dumps(user_portfolio, indent=2)}

            Current Market Data:
            {json.dumps(market_data, indent=2)}

            Provide:
            1. Buy recommendations with reasoning
            2. Sell recommendations with reasoning
            3. Hold recommendations with reasoning
            4. Risk assessment for each recommendation
            5. Confidence scores (0-100)
            6. Time horizon for each recommendation
            """

            response = await self._call_claude_api(context)
            await self._increment_rate_limit()

            # Structure the recommendations
            recommendations = {
                "user_id": user_portfolio.get("user_id"),
                "buy_recommendations": response.get("buy", []),
                "sell_recommendations": response.get("sell", []),
                "hold_recommendations": response.get("hold", []),
                "overall_risk": response.get("overall_risk", "medium"),
                "market_outlook": response.get("outlook", "neutral"),
                "timestamp": datetime.now().isoformat(),
            }

            # Cache recommendations
            cache_key = f"recommendations:{user_portfolio.get('user_id')}"
            self.redis_client.setex(
                cache_key, 600, json.dumps(recommendations)
            )  # 10 min cache

            return recommendations

        except Exception as e:
            logger.error(f"Error generating trading recommendations: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def analyze_news_sentiment(
        self, news_articles: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze sentiment of news articles"""
        try:
            if not await self._check_rate_limit():
                return {"error": "Rate limit exceeded", "retry_after": 60}

            # Prepare context for Claude
            context = f"""
            Analyze the sentiment of these news articles:

            {json.dumps(news_articles[:20], indent=2)}  # Limit to 20 articles

            For each article, provide:
            1. Sentiment score (-100 to +100)
            2. Confidence level (0-100)
            3. Key topics mentioned
            4. Market impact assessment
            5. Overall market sentiment
            """

            response = await self._call_claude_api(context)
            await self._increment_rate_limit()

            # Structure the analysis
            sentiment_analysis = {
                "articles_analyzed": len(news_articles),
                "overall_sentiment": response.get("overall_sentiment", "neutral"),
                "sentiment_score": response.get("sentiment_score", 0),
                "confidence": response.get("confidence", 50),
                "key_topics": response.get("topics", []),
                "market_impact": response.get("market_impact", "low"),
                "article_sentiments": response.get("article_sentiments", []),
                "timestamp": datetime.now().isoformat(),
            }

            return sentiment_analysis

        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def chat_with_ai(
        self, user_message: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Chat with AI about market conditions and trading"""
        try:
            if not await self._check_rate_limit():
                return {"error": "Rate limit exceeded", "retry_after": 60}

            # Prepare context for Claude
            context_str = f"""
            You are PaiiD AI, a trading assistant. User message: {user_message}

            Current Context:
            {json.dumps(context, indent=2)}

            Provide helpful, accurate trading advice and market insights.
            Be concise but informative.
            """

            response = await self._call_claude_api(context_str)
            await self._increment_rate_limit()

            # Structure the chat response
            chat_response = {
                "user_message": user_message,
                "ai_response": response.get(
                    "response", "I'm sorry, I couldn't process that request."
                ),
                "confidence": response.get("confidence", 50),
                "suggested_actions": response.get("suggested_actions", []),
                "timestamp": datetime.now().isoformat(),
            }

            return chat_response

        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def _call_claude_api(self, context: str) -> dict[str, Any]:
        """Call Claude API with the given context"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            headers = {
                "x-api-key": self.claude_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            }

            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": context,
                    }
                ],
            }

            async with self.session.post(
                self.claude_base_url, headers=headers, json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Parse Claude's response and extract structured data
                    content = data.get("content", [{}])[0].get("text", "")

                    # Try to parse as JSON, fallback to text
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return {"response": content, "confidence": 75}
                else:
                    logger.error(f"Claude API error: {response.status}")
                    return {"error": f"API error: {response.status}"}

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return {"error": str(e)}

    async def get_ai_insights(self, symbols: list[str]) -> dict[str, Any]:
        """Get AI insights for specific symbols"""
        try:
            # Check cache first
            cache_key = f"ai_insights:{':'.join(symbols)}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)

            if not await self._check_rate_limit():
                return {"error": "Rate limit exceeded", "retry_after": 60}

            # Prepare context for Claude
            context = f"""
            Provide AI insights for these trading symbols: {", ".join(symbols)}

            Include:
            1. Technical analysis summary
            2. Fundamental analysis highlights
            3. Market sentiment indicators
            4. Risk factors
            5. Trading opportunities
            6. Time-sensitive alerts
            """

            response = await self._call_claude_api(context)
            await self._increment_rate_limit()

            # Structure the insights
            insights = {
                "symbols": symbols,
                "technical_analysis": response.get("technical", {}),
                "fundamental_analysis": response.get("fundamental", {}),
                "sentiment_indicators": response.get("sentiment", {}),
                "risk_factors": response.get("risks", []),
                "opportunities": response.get("opportunities", []),
                "alerts": response.get("alerts", []),
                "timestamp": datetime.now().isoformat(),
            }

            # Cache insights
            self.redis_client.setex(cache_key, 300, json.dumps(insights))  # 5 min cache

            return insights

        except Exception as e:
            logger.error(f"Error getting AI insights: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
