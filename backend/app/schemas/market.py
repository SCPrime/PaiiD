"""Market data response schemas"""

from typing import Literal

from pydantic import BaseModel, Field


class QuoteResponse(BaseModel):
    """Real-time stock quote response"""

    symbol: str = Field(..., description="Stock symbol")
    bid: float = Field(..., description="Bid price")
    ask: float = Field(..., description="Ask price")
    last: float = Field(..., description="Last trade price")
    volume: int = Field(..., description="Trading volume")
    timestamp: str = Field(..., description="Quote timestamp")
    cached: bool = Field(False, description="Whether quote is from cache")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "bid": 175.25,
                "ask": 175.30,
                "last": 175.28,
                "volume": 45000000,
                "timestamp": "2025-10-27T15:45:00Z",
                "cached": False,
            }
        }


class HistoricalBarsResponse(BaseModel):
    """Historical OHLCV bars response"""

    symbol: str = Field(..., description="Stock symbol")
    interval: Literal["daily", "weekly", "monthly"] = Field(..., description="Bar interval")
    start_date: str = Field(..., description="Start date of data")
    end_date: str = Field(..., description="End date of data")
    bars: list[dict] = Field(..., description="OHLCV bar data")
    count: int = Field(..., description="Number of bars returned")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "interval": "daily",
                "start_date": "2025-09-27",
                "end_date": "2025-10-27",
                "bars": [
                    {
                        "date": "2025-10-27",
                        "open": 174.50,
                        "high": 176.25,
                        "low": 173.80,
                        "close": 175.28,
                        "volume": 45000000,
                    }
                ],
                "count": 1,
            }
        }


class IndicesResponse(BaseModel):
    """Major market indices response"""

    dow: dict = Field(..., description="Dow Jones Industrial Average data")
    nasdaq: dict = Field(..., description="NASDAQ Composite data")
    source: str = Field(..., description="Data source (tradier, claude_ai, fallback)")
    cached: bool = Field(False, description="Whether data is from cache")

    class Config:
        json_schema_extra = {
            "example": {
                "dow": {"last": 42500.0, "change": 125.50, "changePercent": 0.30},
                "nasdaq": {"last": 18350.0, "change": 98.75, "changePercent": 0.54},
                "source": "tradier",
                "cached": False,
            }
        }


class MarketCondition(BaseModel):
    """Single market condition indicator"""

    name: str = Field(..., description="Condition name")
    value: str = Field(..., description="Condition value")
    status: Literal["favorable", "neutral", "unfavorable"] = Field(
        ..., description="Condition status"
    )
    details: str | None = Field(None, description="Additional details")


class MarketConditionsResponse(BaseModel):
    """Market conditions analysis response"""

    conditions: list[MarketCondition] = Field(..., description="List of market conditions")
    timestamp: str = Field(..., description="Analysis timestamp")
    overallSentiment: Literal["bullish", "neutral", "bearish"] = Field(
        ..., description="Overall market sentiment"
    )
    recommendedActions: list[str] = Field(
        ..., description="Recommended trading actions"
    )
    source: str = Field(..., description="Data source (tradier, fallback)")

    class Config:
        json_schema_extra = {
            "example": {
                "conditions": [
                    {
                        "name": "VIX (Volatility)",
                        "value": "15.50",
                        "status": "favorable",
                        "details": "Low volatility (15.50) - stable market conditions",
                    }
                ],
                "timestamp": "2025-10-27T15:30:00Z",
                "overallSentiment": "bullish",
                "recommendedActions": [
                    "Consider directional bullish strategies",
                    "Look for momentum plays in strong sectors",
                ],
                "source": "tradier",
            }
        }


class SectorPerformanceResponse(BaseModel):
    """Sector performance analysis response"""

    sectors: list[dict] = Field(..., description="Sector performance data")
    timestamp: str = Field(..., description="Analysis timestamp")
    leader: str = Field(..., description="Best performing sector")
    laggard: str = Field(..., description="Worst performing sector")
    source: str = Field(..., description="Data source (tradier, fallback)")

    class Config:
        json_schema_extra = {
            "example": {
                "sectors": [
                    {
                        "name": "Technology",
                        "symbol": "XLK",
                        "changePercent": 1.25,
                        "last": 185.50,
                        "rank": 1,
                    }
                ],
                "timestamp": "2025-10-27T15:30:00Z",
                "leader": "Technology",
                "laggard": "Energy",
                "source": "tradier",
            }
        }
