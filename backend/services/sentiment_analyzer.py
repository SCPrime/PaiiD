"""
Sentiment Analysis Service
Analyzes news articles, social media, and market data for sentiment indicators
"""

import json
import logging
import re
from datetime import datetime
from typing import Any

import aiohttp
import redis
from backend.config import settings


logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Service for analyzing market sentiment from various sources"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=4, decode_responses=True
        )
        self.news_api_key = settings.NEWS_API_KEY
        self.twitter_bearer_token = settings.TWITTER_BEARER_TOKEN
        self.session = None

        # Sentiment keywords and weights
        self.bullish_keywords = {
            "strong": 2,
            "growth": 2,
            "positive": 2,
            "bullish": 3,
            "buy": 2,
            "outperform": 2,
            "beat": 2,
            "surge": 3,
            "rally": 3,
            "gain": 2,
            "rise": 2,
            "up": 1,
            "increase": 2,
            "profit": 2,
            "earnings": 1,
            "revenue": 1,
            "success": 2,
            "breakthrough": 3,
            "innovation": 2,
            "expansion": 2,
        }

        self.bearish_keywords = {
            "weak": -2,
            "decline": -2,
            "negative": -2,
            "bearish": -3,
            "sell": -2,
            "underperform": -2,
            "miss": -2,
            "drop": -2,
            "fall": -2,
            "loss": -2,
            "down": -1,
            "decrease": -2,
            "loss": -2,
            "earnings": -1,
            "revenue": -1,
            "failure": -2,
            "crisis": -3,
            "recession": -3,
            "crash": -3,
            "correction": -2,
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def analyze_news_sentiment(
        self, symbols: list[str], days_back: int = 7
    ) -> dict[str, Any]:
        """Analyze sentiment from news articles for given symbols"""
        try:
            # Check cache first
            cache_key = f"news_sentiment:{':'.join(symbols)}:{days_back}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)

            # Fetch news articles
            news_articles = await self._fetch_news_articles(symbols, days_back)

            if not news_articles:
                return {
                    "symbols": symbols,
                    "sentiment_score": 0,
                    "confidence": 0,
                    "articles_analyzed": 0,
                    "timestamp": datetime.now().isoformat(),
                }

            # Analyze sentiment for each article
            sentiment_scores = []
            for article in news_articles:
                score = self._calculate_sentiment_score(article.get("content", ""))
                sentiment_scores.append(
                    {
                        "title": article.get("title", ""),
                        "sentiment_score": score,
                        "url": article.get("url", ""),
                        "published_at": article.get("published_at", ""),
                    }
                )

            # Calculate overall sentiment
            overall_sentiment = self._calculate_overall_sentiment(sentiment_scores)

            result = {
                "symbols": symbols,
                "sentiment_score": overall_sentiment["score"],
                "confidence": overall_sentiment["confidence"],
                "articles_analyzed": len(sentiment_scores),
                "article_sentiments": sentiment_scores,
                "trend": overall_sentiment["trend"],
                "timestamp": datetime.now().isoformat(),
            }

            # Cache the result
            self.redis_client.setex(cache_key, 1800, json.dumps(result))  # 30 min cache

            return result

        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def analyze_social_sentiment(
        self, symbols: list[str], hours_back: int = 24
    ) -> dict[str, Any]:
        """Analyze sentiment from social media for given symbols"""
        try:
            # Check cache first
            cache_key = f"social_sentiment:{':'.join(symbols)}:{hours_back}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)

            # Fetch social media posts (simulated for now)
            social_posts = await self._fetch_social_posts(symbols, hours_back)

            if not social_posts:
                return {
                    "symbols": symbols,
                    "sentiment_score": 0,
                    "confidence": 0,
                    "posts_analyzed": 0,
                    "timestamp": datetime.now().isoformat(),
                }

            # Analyze sentiment for each post
            sentiment_scores = []
            for post in social_posts:
                score = self._calculate_sentiment_score(post.get("text", ""))
                sentiment_scores.append(
                    {
                        "text": post.get("text", "")[:100]
                        + "...",  # Truncate for display
                        "sentiment_score": score,
                        "platform": post.get("platform", "unknown"),
                        "created_at": post.get("created_at", ""),
                    }
                )

            # Calculate overall sentiment
            overall_sentiment = self._calculate_overall_sentiment(sentiment_scores)

            result = {
                "symbols": symbols,
                "sentiment_score": overall_sentiment["score"],
                "confidence": overall_sentiment["confidence"],
                "posts_analyzed": len(sentiment_scores),
                "post_sentiments": sentiment_scores,
                "trend": overall_sentiment["trend"],
                "timestamp": datetime.now().isoformat(),
            }

            # Cache the result
            self.redis_client.setex(cache_key, 900, json.dumps(result))  # 15 min cache

            return result

        except Exception as e:
            logger.error(f"Error analyzing social sentiment: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def get_market_sentiment_summary(self, symbols: list[str]) -> dict[str, Any]:
        """Get comprehensive market sentiment summary"""
        try:
            # Check cache first
            cache_key = f"market_sentiment_summary:{':'.join(symbols)}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)

            # Get news sentiment
            news_sentiment = await self.analyze_news_sentiment(symbols, days_back=7)

            # Get social sentiment
            social_sentiment = await self.analyze_social_sentiment(
                symbols, hours_back=24
            )

            # Calculate combined sentiment
            news_score = news_sentiment.get("sentiment_score", 0)
            social_score = social_sentiment.get("sentiment_score", 0)

            # Weighted average (news 70%, social 30%)
            combined_score = (news_score * 0.7) + (social_score * 0.3)

            # Determine overall sentiment
            if combined_score > 20:
                overall_sentiment = "bullish"
            elif combined_score < -20:
                overall_sentiment = "bearish"
            else:
                overall_sentiment = "neutral"

            result = {
                "symbols": symbols,
                "overall_sentiment": overall_sentiment,
                "combined_score": combined_score,
                "news_sentiment": news_sentiment,
                "social_sentiment": social_sentiment,
                "confidence": min(
                    news_sentiment.get("confidence", 0),
                    social_sentiment.get("confidence", 0),
                ),
                "timestamp": datetime.now().isoformat(),
            }

            # Cache the result
            self.redis_client.setex(cache_key, 600, json.dumps(result))  # 10 min cache

            return result

        except Exception as e:
            logger.error(f"Error getting market sentiment summary: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score for given text"""
        if not text:
            return 0.0

        text_lower = text.lower()
        bullish_score = 0
        bearish_score = 0

        # Count bullish keywords
        for keyword, weight in self.bullish_keywords.items():
            count = len(re.findall(rf"\b{keyword}\b", text_lower))
            bullish_score += count * weight

        # Count bearish keywords
        for keyword, weight in self.bearish_keywords.items():
            count = len(re.findall(rf"\b{keyword}\b", text_lower))
            bearish_score += count * weight

        # Calculate net score
        net_score = bullish_score - bearish_score

        # Normalize to -100 to +100 range
        max_possible_score = len(text.split()) * 3  # Rough estimate
        if max_possible_score > 0:
            normalized_score = (net_score / max_possible_score) * 100
            return max(-100, min(100, normalized_score))

        return 0.0

    def _calculate_overall_sentiment(
        self, sentiment_scores: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate overall sentiment from individual scores"""
        if not sentiment_scores:
            return {"score": 0, "confidence": 0, "trend": "neutral"}

        scores = [item["sentiment_score"] for item in sentiment_scores]
        avg_score = sum(scores) / len(scores)

        # Calculate confidence based on score distribution
        variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
        confidence = max(0, 100 - (variance / 10))  # Higher variance = lower confidence

        # Determine trend
        if avg_score > 20:
            trend = "bullish"
        elif avg_score < -20:
            trend = "bearish"
        else:
            trend = "neutral"

        return {
            "score": round(avg_score, 2),
            "confidence": round(confidence, 2),
            "trend": trend,
        }

    async def _fetch_news_articles(
        self, symbols: list[str], days_back: int
    ) -> list[dict[str, Any]]:
        """Fetch news articles for given symbols"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # Simulate news API call (replace with actual News API)
            articles = []
            for symbol in symbols:
                # Mock news articles for demonstration
                mock_articles = [
                    {
                        "title": f"{symbol} shows strong performance in Q4",
                        "content": f"{symbol} has demonstrated strong growth with positive earnings and market expansion.",
                        "url": f"https://example.com/news/{symbol.lower()}-strong-performance",
                        "published_at": datetime.now().isoformat(),
                    },
                    {
                        "title": f"Analysts bullish on {symbol} outlook",
                        "content": f"Market analysts are optimistic about {symbol}'s future prospects and recommend buy.",
                        "url": f"https://example.com/news/{symbol.lower()}-bullish-outlook",
                        "published_at": datetime.now().isoformat(),
                    },
                ]
                articles.extend(mock_articles)

            return articles

        except Exception as e:
            logger.error(f"Error fetching news articles: {e}")
            return []

    async def _fetch_social_posts(
        self, symbols: list[str], hours_back: int
    ) -> list[dict[str, Any]]:
        """Fetch social media posts for given symbols"""
        try:
            # Simulate social media posts (replace with actual Twitter API)
            posts = []
            for symbol in symbols:
                # Mock social posts for demonstration
                mock_posts = [
                    {
                        "text": f"Just bought more {symbol}! Feeling bullish about this one 🚀",
                        "platform": "twitter",
                        "created_at": datetime.now().isoformat(),
                    },
                    {
                        "text": f"{symbol} is looking strong today. Great earnings report!",
                        "platform": "twitter",
                        "created_at": datetime.now().isoformat(),
                    },
                ]
                posts.extend(mock_posts)

            return posts

        except Exception as e:
            logger.error(f"Error fetching social posts: {e}")
            return []
