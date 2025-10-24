"""
Sentiment Analysis Service using Anthropic Claude
Analyzes market news and social media sentiment for trading insights
"""

import logging
from datetime import datetime

import anthropic
from pydantic import BaseModel

from ..core.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


class SentimentScore(BaseModel):
    """Sentiment analysis result"""

    symbol: str
    sentiment: str  # 'bullish', 'bearish', 'neutral'
    score: float  # -1.0 (very bearish) to +1.0 (very bullish)
    confidence: float  # 0.0 to 1.0
    reasoning: str
    timestamp: datetime
    source: str  # 'news', 'social', 'combined'


class SentimentAnalyzer:
    """Analyzes market sentiment using Anthropic Claude"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

    async def analyze_text(self, symbol: str, text: str, source: str = "news") -> SentimentScore:
        """
        Analyze sentiment from text (news article, social media post, etc.)

        Args:
            symbol: Stock/asset symbol
            text: Text to analyze
            source: Source type ('news', 'social', 'combined')

        Returns:
            SentimentScore with analysis results
        """
        try:
            prompt = self._build_sentiment_prompt(symbol, text)

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse Claude's response
            response_text = message.content[0].text
            return self._parse_sentiment_response(symbol, response_text, source)

        except Exception as e:
            logger.error(f"Sentiment analysis error for {symbol}: {e}")
            # Return neutral sentiment on error
            return SentimentScore(
                symbol=symbol,
                sentiment="neutral",
                score=0.0,
                confidence=0.0,
                reasoning=f"Analysis failed: {e!s}",
                timestamp=datetime.utcnow(),
                source=source,
            )

    async def analyze_news_batch(self, symbol: str, news_articles: list[dict]) -> SentimentScore:
        """
        Analyze multiple news articles and aggregate sentiment

        Args:
            symbol: Stock/asset symbol
            news_articles: List of news article dicts with 'title', 'content', 'source'

        Returns:
            Aggregated SentimentScore
        """
        if not news_articles:
            return SentimentScore(
                symbol=symbol,
                sentiment="neutral",
                score=0.0,
                confidence=0.0,
                reasoning="No news articles available",
                timestamp=datetime.utcnow(),
                source="news",
            )

        # Combine all news into one analysis for efficiency
        combined_text = self._combine_news_articles(news_articles)

        try:
            prompt = self._build_batch_sentiment_prompt(symbol, combined_text)

            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text
            return self._parse_sentiment_response(symbol, response_text, "news")

        except Exception as e:
            logger.error(f"Batch sentiment analysis error for {symbol}: {e}")
            return SentimentScore(
                symbol=symbol,
                sentiment="neutral",
                score=0.0,
                confidence=0.0,
                reasoning=f"Batch analysis failed: {e!s}",
                timestamp=datetime.utcnow(),
                source="news",
            )

    def _build_sentiment_prompt(self, symbol: str, text: str) -> str:
        """Build prompt for sentiment analysis"""
        return f"""Analyze the market sentiment for {symbol} based on this text:

{text}

Provide a structured sentiment analysis with:
1. Overall sentiment (BULLISH, BEARISH, or NEUTRAL)
2. Sentiment score from -1.0 (very bearish) to +1.0 (very bullish)
3. Confidence level from 0.0 to 1.0
4. Brief reasoning (2-3 sentences)

Format your response EXACTLY as:
SENTIMENT: [BULLISH|BEARISH|NEUTRAL]
SCORE: [number between -1.0 and 1.0]
CONFIDENCE: [number between 0.0 and 1.0]
REASONING: [your reasoning here]

Be objective and focus on actionable market indicators."""

    def _build_batch_sentiment_prompt(self, symbol: str, combined_text: str) -> str:
        """Build prompt for batch news analysis"""
        return f"""Analyze the overall market sentiment for {symbol} based on these recent news articles:

{combined_text}

Synthesize all the information and provide:
1. Overall market sentiment (BULLISH, BEARISH, or NEUTRAL)
2. Aggregate sentiment score from -1.0 (very bearish) to +1.0 (very bullish)
3. Confidence level from 0.0 to 1.0
4. Key themes and reasoning (3-4 sentences)

Format your response EXACTLY as:
SENTIMENT: [BULLISH|BEARISH|NEUTRAL]
SCORE: [number between -1.0 and 1.0]
CONFIDENCE: [number between 0.0 and 1.0]
REASONING: [your synthesized analysis here]

Focus on the most recent and impactful information."""

    def _parse_sentiment_response(self, symbol: str, response: str, source: str) -> SentimentScore:
        """Parse Claude's structured response"""
        try:
            lines = response.strip().split("\n")
            sentiment_line = ""
            score_line = ""
            confidence_line = ""
            reasoning_lines = []

            # Parse structured response
            for line in lines:
                if line.startswith("SENTIMENT:"):
                    sentiment_line = line.split(":", 1)[1].strip()
                elif line.startswith("SCORE:"):
                    score_line = line.split(":", 1)[1].strip()
                elif line.startswith("CONFIDENCE:"):
                    confidence_line = line.split(":", 1)[1].strip()
                elif line.startswith("REASONING:"):
                    reasoning_lines.append(line.split(":", 1)[1].strip())
                elif reasoning_lines:  # Continue reasoning from previous line
                    reasoning_lines.append(line.strip())

            # Extract values
            sentiment = sentiment_line.lower()
            if sentiment not in ["bullish", "bearish", "neutral"]:
                sentiment = "neutral"

            score = float(score_line) if score_line else 0.0
            score = max(-1.0, min(1.0, score))  # Clamp to [-1, 1]

            confidence = float(confidence_line) if confidence_line else 0.5
            confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]

            reasoning = " ".join(reasoning_lines) or "No reasoning provided"

            return SentimentScore(
                symbol=symbol,
                sentiment=sentiment,
                score=score,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=datetime.utcnow(),
                source=source,
            )

        except Exception as e:
            logger.error(f"Error parsing sentiment response: {e}")
            # Return neutral on parse error
            return SentimentScore(
                symbol=symbol,
                sentiment="neutral",
                score=0.0,
                confidence=0.0,
                reasoning=f"Parse error: {e!s}",
                timestamp=datetime.utcnow(),
                source=source,
            )

    def _combine_news_articles(self, articles: list[dict]) -> str:
        """Combine multiple news articles into one text"""
        combined = []
        for i, article in enumerate(articles[:10], 1):  # Limit to 10 articles
            title = article.get("title", "")
            content = article.get("content", article.get("summary", ""))
            source = article.get("source", "Unknown")

            combined.append(f"Article {i} ({source}):")
            combined.append(f"Title: {title}")
            if content:
                combined.append(f"Content: {content[:500]}...")  # Limit length
            combined.append("")

        return "\n".join(combined)


# Global instance
_sentiment_analyzer: SentimentAnalyzer | None = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get or create sentiment analyzer instance"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer
