from abc import ABC, abstractmethod
from typing import Any


class NewsArticle:
    """Standardized news article format"""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.title = kwargs.get("title")
        self.summary = kwargs.get("summary", "")
        self.source = kwargs.get("source")
        self.url = kwargs.get("url")
        self.published_at = kwargs.get("published_at")
        self.sentiment = kwargs.get("sentiment", "neutral")
        self.sentiment_score = kwargs.get("sentiment_score", 0.0)
        self.symbols = kwargs.get("symbols", [])
        self.category = kwargs.get("category", "general")
        self.image_url = kwargs.get("image_url")
        self.provider = kwargs.get("provider")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "source": self.source,
            "url": self.url,
            "published_at": self.published_at,
            "sentiment": self.sentiment,
            "sentiment_score": self.sentiment_score,
            "symbols": self.symbols,
            "category": self.category,
            "image_url": self.image_url,
            "provider": self.provider,
        }

class BaseNewsProvider(ABC):
    """Base class for all news providers"""

    @abstractmethod
    def get_company_news(self, symbol: str, days_back: int = 7) -> list[NewsArticle]:
        pass

    @abstractmethod
    def get_market_news(self, category: str = "general") -> list[NewsArticle]:
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        pass
