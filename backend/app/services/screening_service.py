"""
Screening Service - Business logic for strategy-based opportunity screening

This service encapsulates all business logic for generating trading opportunities
based on different strategies (momentum, mean reversion, options, multi-leg).
"""

import random
from typing import Literal

from pydantic import BaseModel


class Opportunity(BaseModel):
    """Trading opportunity model"""

    symbol: str
    type: Literal["stock", "option", "multileg"]
    strategy: str
    reason: str
    currentPrice: float  # noqa: N815 - API contract requires mixedCase
    targetPrice: float | None = None  # noqa: N815 - API contract requires mixedCase
    confidence: int  # 0-100
    risk: Literal["low", "medium", "high"]


class ScreeningService:
    """Service for generating and filtering trading opportunities"""

    def __init__(self):
        """Initialize screening service"""
        self._stock_universe = self._build_stock_universe()
        self._option_universe = self._build_option_universe()
        self._multileg_universe = self._build_multileg_universe()

    def _build_stock_universe(self) -> list[dict]:
        """Build the universe of stock opportunities"""
        # ruff: noqa: E501 - Long reason strings preserved for readability
        return [
            {
                "symbol": "AAPL",
                "strategy": "Momentum Breakout",
                "reason": "Breaking above 20-day MA with strong volume. RSI at 62 (bullish but not overbought). MACD showing positive crossover.",
                "current": 184.10,
                "target": 192.50,
                "confidence": 85,
                "risk": "medium",
            },
            {
                "symbol": "NVDA",
                "strategy": "Mean Reversion",
                "reason": "Oversold on daily timeframe (RSI 28), holding support at 200-day MA. High probability bounce setup.",
                "current": 485.20,
                "target": 515.00,
                "confidence": 78,
                "risk": "medium",
            },
            {
                "symbol": "MSFT",
                "strategy": "Momentum Breakout",
                "reason": "Cloud earnings beat expectations. Breaking out of consolidation with strong institutional buying.",
                "current": 405.50,
                "target": 425.00,
                "confidence": 82,
                "risk": "low",
            },
            {
                "symbol": "GOOGL",
                "strategy": "Mean Reversion",
                "reason": "Oversold after sell-off. RSI 31, holding key support. Search revenue stable.",
                "current": 142.30,
                "target": 155.00,
                "confidence": 75,
                "risk": "medium",
            },
            {
                "symbol": "AMD",
                "strategy": "Momentum Breakout",
                "reason": "Chip sector strength. Breaking resistance at $145. Data center growth accelerating.",
                "current": 143.80,
                "target": 158.00,
                "confidence": 80,
                "risk": "medium",
            },
            {
                "symbol": "JPM",
                "strategy": "Value Play",
                "reason": "Trading below fair value. Strong financials. Interest rate environment favorable.",
                "current": 162.50,
                "target": 175.00,
                "confidence": 77,
                "risk": "low",
            },
            {
                "symbol": "UNH",
                "strategy": "Defensive Breakout",
                "reason": "Healthcare demand steady. Breaking all-time highs. Optum growth strong.",
                "current": 545.00,
                "target": 580.00,
                "confidence": 83,
                "risk": "low",
            },
            {
                "symbol": "XOM",
                "strategy": "Energy Momentum",
                "reason": "Oil prices stabilizing. Strong cash flow. Share buyback program.",
                "current": 115.20,
                "target": 125.00,
                "confidence": 79,
                "risk": "medium",
            },
        ]

    def _build_option_universe(self) -> list[dict]:
        """Build the universe of option opportunities"""
        # ruff: noqa: E501 - Long reason strings preserved for readability
        return [
            {
                "symbol": "SPY 450C 30DTE",
                "strategy": "Bullish Trend Following",
                "reason": "Market in clear uptrend, low IV (18th percentile), good risk/reward ratio. Delta 0.65, Theta -0.08.",
                "current": 5.20,
                "target": 8.50,
                "confidence": 72,
                "risk": "medium",
            },
            {
                "symbol": "QQQ 425C 45DTE",
                "strategy": "Tech Momentum Play",
                "reason": "Tech leadership strong. IV at 22nd percentile. Delta 0.70, clean chart pattern.",
                "current": 6.80,
                "target": 10.50,
                "confidence": 75,
                "risk": "medium",
            },
            {
                "symbol": "AAPL 190C 60DTE",
                "strategy": "Earnings Play",
                "reason": "IV spike expected before earnings. Current IV rank low at 25%. Delta 0.55.",
                "current": 3.40,
                "target": 6.20,
                "confidence": 68,
                "risk": "high",
            },
            {
                "symbol": "IWM 210C 30DTE",
                "strategy": "Small Cap Rotation",
                "reason": "Small caps breaking out. Rate cut expectations. IV at 30th percentile.",
                "current": 4.10,
                "target": 7.00,
                "confidence": 70,
                "risk": "high",
            },
            {
                "symbol": "XLE 95C 45DTE",
                "strategy": "Energy Sector Play",
                "reason": "Energy stabilizing. Geopolitical premium. Delta 0.62, low IV.",
                "current": 2.80,
                "target": 4.50,
                "confidence": 73,
                "risk": "medium",
            },
        ]

    def _build_multileg_universe(self) -> list[dict]:
        """Build the universe of multi-leg option opportunities"""
        # ruff: noqa: E501 - Long reason strings preserved for readability
        return [
            {
                "symbol": "TSLA Iron Condor 240/250/270/280",
                "strategy": "Range-Bound Premium Collection",
                "reason": "High IV rank (75th percentile), stock consolidating between $250-$265. Theta decay favorable, max profit at current price.",
                "current": 250.00,
                "target": None,
                "confidence": 68,
                "risk": "low",
            },
            {
                "symbol": "QQQ Put Credit Spread 420/415",
                "strategy": "High Probability Income",
                "reason": "30 delta put spread, 85% probability of profit. Market trending up, selling premium at support level.",
                "current": 425.50,
                "target": None,
                "confidence": 82,
                "risk": "low",
            },
            {
                "symbol": "SPY Iron Butterfly 455/460/465",
                "strategy": "Neutral Income Play",
                "reason": "Market consolidating at 460. High IV (65th percentile). Max profit at current level.",
                "current": 460.00,
                "target": None,
                "confidence": 76,
                "risk": "low",
            },
            {
                "symbol": "NVDA Strangle 460/520",
                "strategy": "Earnings Volatility Play",
                "reason": "Earnings next week. IV expansion expected. Current IV rank 45%. Profit from big move either direction.",
                "current": 485.00,
                "target": None,
                "confidence": 65,
                "risk": "high",
            },
            {
                "symbol": "AAPL Call Debit Spread 180/190",
                "strategy": "Defined Risk Bullish",
                "reason": "Limiting upside for lower cost. Breakout setup. 70% probability of profit.",
                "current": 182.50,
                "target": 190.00,
                "confidence": 74,
                "risk": "medium",
            },
            {
                "symbol": "META Put Credit Spread 500/495",
                "strategy": "Support Level Defense",
                "reason": "Selling puts at strong support. 20 delta, 80% PoP. Collecting premium on dips.",
                "current": 510.00,
                "target": None,
                "confidence": 79,
                "risk": "low",
            },
        ]

    def _apply_price_variation(
        self, base_price: float, variance: float = 0.02
    ) -> float:
        """Apply random price variation to simulate market fluctuations"""
        price_var = random.uniform(-variance, variance)  # noqa: S311 - Not cryptographic
        return round(base_price * (1 + price_var), 2)

    def _apply_confidence_variation(self, base_confidence: int) -> int:
        """Apply random confidence variation while keeping within bounds"""
        varied = base_confidence + random.randint(-5, 5)  # noqa: S311 - Not cryptographic
        return max(60, min(95, varied))

    def _build_opportunity(
        self, data: dict, opp_type: Literal["stock", "option", "multileg"]
    ) -> Opportunity:
        """Build an Opportunity object from raw data"""
        variance = 0.02 if opp_type == "stock" else 0.03
        current_price = self._apply_price_variation(data["current"], variance)
        target_price = (
            self._apply_price_variation(data["target"], variance)
            if data["target"]
            else None
        )

        return Opportunity(
            symbol=data["symbol"],
            type=opp_type,
            strategy=data["strategy"],
            reason=data["reason"],
            currentPrice=current_price,
            targetPrice=target_price,
            confidence=self._apply_confidence_variation(data["confidence"]),
            risk=data["risk"],
        )

    def get_opportunities(
        self, max_price: float | None = None, count_per_type: int = 2
    ) -> list[Opportunity]:
        """
        Get diversified trading opportunities across all asset types

        Args:
            max_price: Optional maximum price filter
            count_per_type: Number of opportunities per type to include

        Returns:
            List of Opportunity objects with diverse investment types
        """
        # Randomly select opportunities from each category
        selected_stocks = random.sample(
            self._stock_universe, min(count_per_type, len(self._stock_universe))
        )
        selected_options = random.sample(
            self._option_universe, min(count_per_type, len(self._option_universe))
        )
        selected_multileg = random.sample(
            self._multileg_universe, min(count_per_type, len(self._multileg_universe))
        )

        # Build opportunity objects
        all_opportunities: list[Opportunity] = []

        for stock in selected_stocks:
            all_opportunities.append(self._build_opportunity(stock, "stock"))

        for option in selected_options:
            all_opportunities.append(self._build_opportunity(option, "option"))

        for multileg in selected_multileg:
            all_opportunities.append(self._build_opportunity(multileg, "multileg"))

        # Filter by max price if provided
        if max_price is not None:
            all_opportunities = [
                opp for opp in all_opportunities if opp.currentPrice <= max_price
            ]

        return all_opportunities

    def get_available_strategies(self) -> list[dict]:
        """
        Get list of available screening strategies

        Returns:
            List of strategy metadata objects
        """
        return [
            {
                "id": "momentum-breakout",
                "name": "Momentum Breakout",
                "description": "Stocks breaking above key resistance levels with strong volume",
                "assetTypes": ["stock"],
                "enabled": True,
            },
            {
                "id": "mean-reversion",
                "name": "Mean Reversion",
                "description": "Oversold stocks at support levels with bounce potential",
                "assetTypes": ["stock"],
                "enabled": True,
            },
            {
                "id": "bullish-trend-following",
                "name": "Bullish Trend Following",
                "description": "Call options in uptrending markets with favorable IV",
                "assetTypes": ["option"],
                "enabled": True,
            },
            {
                "id": "range-bound-premium",
                "name": "Range-Bound Premium Collection",
                "description": "Iron condors and credit spreads in consolidating stocks",
                "assetTypes": ["multileg"],
                "enabled": True,
            },
            {
                "id": "high-probability-income",
                "name": "High Probability Income",
                "description": "Put credit spreads with 80%+ probability of profit",
                "assetTypes": ["multileg"],
                "enabled": True,
            },
        ]


# Singleton instance
_screening_service: ScreeningService | None = None


def get_screening_service() -> ScreeningService:
    """Get or create the singleton screening service instance"""
    global _screening_service
    if _screening_service is None:
        _screening_service = ScreeningService()
    return _screening_service
