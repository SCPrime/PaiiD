"""AI recommendation response schemas"""

from typing import Literal

from pydantic import BaseModel, Field


class TradeData(BaseModel):
    """Pre-filled trade execution data for 1-click trading"""

    symbol: str = Field(..., description="Stock symbol")
    side: Literal["buy", "sell"] = Field(..., description="Trade side")
    quantity: int = Field(..., description="Suggested quantity")
    orderType: Literal["market", "limit"] = Field("limit", description="Order type")
    entryPrice: float | None = Field(None, description="Suggested entry price")
    stopLoss: float | None = Field(None, description="Suggested stop loss")
    takeProfit: float | None = Field(None, description="Suggested take profit")


class Recommendation(BaseModel):
    """AI trading recommendation"""

    symbol: str = Field(..., description="Stock symbol")
    action: Literal["BUY", "SELL", "HOLD"] = Field(..., description="Recommended action")
    confidence: float = Field(..., description="Confidence score (0-100)")
    score: float = Field(..., description="AI recommendation score (1-10)")
    reason: str = Field(..., description="Reason for recommendation")
    targetPrice: float = Field(..., description="Target price")
    currentPrice: float = Field(..., description="Current market price")
    timeframe: str = Field("1-3 months", description="Recommended timeframe")
    risk: Literal["Low", "Medium", "High"] = Field("Medium", description="Risk level")
    entryPrice: float | None = Field(None, description="Suggested entry price")
    stopLoss: float | None = Field(None, description="Suggested stop loss price")
    takeProfit: float | None = Field(None, description="Suggested take profit price")
    riskRewardRatio: float | None = Field(None, description="Risk/reward ratio")
    indicators: dict | None = Field(None, description="Technical indicators data")
    tradeData: TradeData | None = Field(None, description="1-click execution data")
    portfolioFit: str | None = Field(None, description="Portfolio fit analysis")
    momentum: dict | None = Field(None, description="Momentum analysis")
    volatility: dict | None = Field(None, description="Volatility analysis")
    sector: str | None = Field(None, description="Stock sector")
    sectorPerformance: dict | None = Field(None, description="Sector performance data")
    explanation: str | None = Field(None, description="Detailed explanation")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "action": "BUY",
                "confidence": 85.0,
                "score": 8.5,
                "reason": "Strong bullish momentum with high volume confirmation",
                "targetPrice": 185.00,
                "currentPrice": 175.28,
                "timeframe": "1-2 weeks",
                "risk": "Low",
                "entryPrice": 174.50,
                "stopLoss": 166.50,
                "takeProfit": 185.00,
                "tradeData": {
                    "symbol": "AAPL",
                    "side": "buy",
                    "quantity": 10,
                    "orderType": "limit",
                    "entryPrice": 174.50,
                },
            }
        }


class PortfolioAnalysis(BaseModel):
    """Portfolio-level risk and diversification analysis"""

    totalPositions: int = Field(..., description="Total number of positions")
    totalValue: float = Field(..., description="Total portfolio value")
    topSectors: list[dict] = Field(..., description="Top sectors by allocation")
    riskScore: float = Field(..., description="Portfolio risk score (1-10)")
    diversificationScore: float = Field(
        ..., description="Diversification score (1-10)"
    )
    recommendations: list[str] = Field(
        ..., description="Portfolio-level recommendations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "totalPositions": 5,
                "totalValue": 105000.0,
                "topSectors": [
                    {"name": "Technology", "percentage": 35.0},
                    {"name": "Healthcare", "percentage": 25.0},
                ],
                "riskScore": 4.5,
                "diversificationScore": 7.5,
                "recommendations": [
                    "Consider adding 2 more positions for better diversification",
                    "Technology sector is 35% of portfolio - consider rebalancing",
                ],
            }
        }


class RecommendationsResponse(BaseModel):
    """AI recommendations list response"""

    recommendations: list[Recommendation] = Field(..., description="List of recommendations")
    portfolioAnalysis: PortfolioAnalysis | None = Field(
        None, description="Portfolio analysis"
    )
    generated_at: str = Field(..., description="Generation timestamp")
    model_version: str = Field("v1.0.0", description="AI model version")

    class Config:
        json_schema_extra = {
            "example": {
                "recommendations": [
                    {
                        "symbol": "AAPL",
                        "action": "BUY",
                        "confidence": 85.0,
                        "score": 8.5,
                        "reason": "Strong bullish momentum",
                        "targetPrice": 185.00,
                        "currentPrice": 175.28,
                    }
                ],
                "portfolioAnalysis": {
                    "totalPositions": 5,
                    "totalValue": 105000.0,
                    "topSectors": [{"name": "Technology", "percentage": 35.0}],
                    "riskScore": 4.5,
                    "diversificationScore": 7.5,
                    "recommendations": ["Maintain current diversification strategy"],
                },
                "generated_at": "2025-10-27T15:30:00Z",
                "model_version": "v2.0.0-portfolio-aware",
            }
        }


class SymbolAnalysis(BaseModel):
    """Comprehensive symbol analysis response"""

    symbol: str = Field(..., description="Stock symbol")
    current_price: float = Field(..., description="Current price")
    analysis: str = Field(..., description="Detailed analysis text")
    momentum: str = Field(..., description="Momentum classification")
    trend: str = Field(..., description="Trend classification")
    support_level: float = Field(..., description="Support price level")
    resistance_level: float = Field(..., description="Resistance price level")
    risk_assessment: str = Field(..., description="Risk assessment text")
    entry_suggestion: str = Field(..., description="Entry suggestion text")
    exit_suggestion: str = Field(..., description="Exit suggestion text")
    stop_loss_suggestion: float = Field(..., description="Suggested stop loss price")
    take_profit_suggestion: float = Field(..., description="Suggested take profit price")
    confidence_score: float = Field(..., description="Confidence score (0-100)")
    key_indicators: dict = Field(..., description="Key technical indicators")
    summary: str = Field(..., description="Brief summary")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "current_price": 175.28,
                "analysis": "AAPL is showing strong bullish momentum...",
                "momentum": "Bullish",
                "trend": "Strong Uptrend",
                "support_level": 170.00,
                "resistance_level": 180.00,
                "risk_assessment": "Low - Strong signal with high confidence",
                "entry_suggestion": "Consider entering near $174.50",
                "exit_suggestion": "Take partial profits at $185.00",
                "stop_loss_suggestion": 166.50,
                "take_profit_suggestion": 185.00,
                "confidence_score": 85.0,
                "key_indicators": {
                    "rsi": 65.0,
                    "macd_histogram": 0.25,
                    "sma_20": 173.50,
                },
                "summary": "BUY signal with 85% confidence. Strong uptrend.",
            }
        }
