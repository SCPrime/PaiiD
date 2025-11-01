"""Stocks/options market module aligned with PaiiD core services."""

from __future__ import annotations

from collections.abc import Iterable

from ..base import MarketBootstrapResult, MarketContext, MarketStrategy
from ..registry import register_market_strategy


class StocksOptionsStrategy(MarketStrategy):
    market_key = "stocks_options"
    supported_modes = ("paper", "live")

    def bootstrap(self, context: MarketContext) -> MarketBootstrapResult:
        services = {
            "order_executor": "services.order_execution.OrderExecutionService",
            "portfolio_tracker": "services.portfolio_analytics_service.PortfolioAnalyticsService",
        }
        notes: Iterable[str] = (
            "TODO: bind actual service instances for dependency injection",
            "Available engines: Alpaca paper/live, Tradier options",
        )
        return MarketBootstrapResult(
            services=services,
            background_tasks=("alpaca-stream",),
            notes=notes,
        )

    def readiness_checks(self, context: MarketContext) -> Iterable[str]:
        return (
            "alpaca.paper.health" if context.mode == "paper" else "alpaca.live.health",
            "tradier.options.health",
        )


register_market_strategy(StocksOptionsStrategy.market_key, StocksOptionsStrategy)
