"""
Response schemas for PaiiD Trading Platform API

This module provides Pydantic models for all API responses,
ensuring consistent typing and OpenAPI documentation.
"""

from .analytics import (
    EquityPoint,
    PerformanceMetrics,
    PortfolioHistory,
    PortfolioSummary,
)
from .ai import (
    PortfolioAnalysis,
    Recommendation,
    RecommendationsResponse,
    SymbolAnalysis,
)
from .health import DetailedHealthResponse, HealthResponse
from .market import (
    HistoricalBarsResponse,
    IndicesResponse,
    MarketConditionsResponse,
    QuoteResponse,
    SectorPerformanceResponse,
)
from .orders import OrderResponse, OrderTemplateResponse
from .portfolio import AccountResponse, PositionResponse, PositionsResponse


__all__ = [
    # Analytics
    "PortfolioSummary",
    "EquityPoint",
    "PerformanceMetrics",
    "PortfolioHistory",
    # AI
    "Recommendation",
    "RecommendationsResponse",
    "PortfolioAnalysis",
    "SymbolAnalysis",
    # Health
    "HealthResponse",
    "DetailedHealthResponse",
    # Market
    "QuoteResponse",
    "HistoricalBarsResponse",
    "IndicesResponse",
    "MarketConditionsResponse",
    "SectorPerformanceResponse",
    # Orders
    "OrderResponse",
    "OrderTemplateResponse",
    # Portfolio
    "AccountResponse",
    "PositionResponse",
    "PositionsResponse",
]
