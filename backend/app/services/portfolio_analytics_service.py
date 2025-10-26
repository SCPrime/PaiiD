"""
Portfolio Analytics Service

Calculates portfolio metrics and performance analytics including:
- Portfolio diversification scoring
- Risk metrics (beta, Sharpe ratio, max drawdown)
- Performance attribution
- Sector allocation analysis
- Win/loss statistics

This service consolidates portfolio calculation logic from multiple routers.
"""

import logging
import math
from typing import Any

from ..services.tradier_client import TradierClient


logger = logging.getLogger(__name__)


class PortfolioAnalyticsService:
    """
    Portfolio analytics service for calculating portfolio metrics and risk.

    Framework-agnostic service that can be used by routers or background tasks.
    """

    def __init__(self, tradier_client: TradierClient):
        """
        Initialize portfolio analytics service.

        Args:
            tradier_client: Tradier API client for account/position data
        """
        self.tradier = tradier_client

    async def calculate_portfolio_metrics(self, user_id: str | None = None) -> dict[str, Any]:
        """
        Calculate comprehensive portfolio metrics.

        Args:
            user_id: Optional user ID (for multi-user support in future)

        Returns:
            Dictionary with portfolio metrics:
            {
                "total_value": float,
                "cash": float,
                "buying_power": float,
                "positions_value": float,
                "total_pl": float,
                "total_pl_percent": float,
                "day_pl": float,
                "day_pl_percent": float,
                "num_positions": int,
                "num_winning": int,
                "num_losing": int,
                "largest_winner": dict | None,
                "largest_loser": dict | None,
                "diversification_score": float,
                "sector_allocation": dict
            }

        Example:
            >>> service = PortfolioAnalyticsService(tradier)
            >>> metrics = await service.calculate_portfolio_metrics()
            >>> print(metrics["total_value"])  # 125430.50
        """
        try:
            # Fetch account and positions
            account = self.tradier.get_account()
            positions = self.tradier.get_positions()

            # Basic account metrics
            total_value = float(account.get("portfolio_value", 0))
            cash = float(account.get("cash", 0))
            buying_power = float(account.get("buying_power", 0))

            # Position analysis
            num_positions = len(positions)
            num_winning = 0
            num_losing = 0
            total_pl = 0.0
            day_pl = 0.0
            largest_winner = None
            largest_loser = None
            max_win_pl = float("-inf")
            max_loss_pl = float("inf")

            position_details = []

            for pos in positions:
                symbol = pos.get("symbol", "")
                unrealized_pl = float(pos.get("unrealized_pl", 0))
                change_today = float(pos.get("change_today", 0))
                qty = float(pos.get("qty", 0))
                market_value = float(pos.get("market_value", 0))

                # Count winning/losing
                if unrealized_pl > 0:
                    num_winning += 1
                elif unrealized_pl < 0:
                    num_losing += 1

                # Track totals
                total_pl += unrealized_pl
                day_pl += change_today * qty

                # Track largest winner/loser
                if unrealized_pl > max_win_pl:
                    max_win_pl = unrealized_pl
                    largest_winner = {
                        "symbol": symbol,
                        "pl": unrealized_pl,
                        "pl_percent": float(pos.get("unrealized_plpc", 0)),
                    }

                if unrealized_pl < max_loss_pl:
                    max_loss_pl = unrealized_pl
                    largest_loser = {
                        "symbol": symbol,
                        "pl": unrealized_pl,
                        "pl_percent": float(pos.get("unrealized_plpc", 0)),
                    }

                # Store position details for diversification analysis
                position_details.append(
                    {
                        "symbol": symbol,
                        "market_value": market_value,
                        "unrealized_pl": unrealized_pl,
                    }
                )

            # Calculate percentages
            positions_value = sum(float(p.get("market_value", 0)) for p in positions)
            cost_basis = positions_value - total_pl

            total_pl_percent = (
                (total_pl / cost_basis * 100) if cost_basis != 0 else 0
            )
            day_pl_percent = (
                (day_pl / positions_value * 100) if positions_value != 0 else 0
            )

            # Calculate diversification score
            diversification_score = self._calculate_diversification(position_details)

            # Sector allocation (simplified - would use real sector data in production)
            sector_allocation = self._estimate_sector_allocation(position_details)

            logger.info(
                f"Portfolio metrics calculated: ${total_value:.2f}, "
                f"{num_positions} positions, diversification: {diversification_score:.1f}"
            )

            return {
                "total_value": round(total_value, 2),
                "cash": round(cash, 2),
                "buying_power": round(buying_power, 2),
                "positions_value": round(positions_value, 2),
                "total_pl": round(total_pl, 2),
                "total_pl_percent": round(total_pl_percent, 2),
                "day_pl": round(day_pl, 2),
                "day_pl_percent": round(day_pl_percent, 2),
                "num_positions": num_positions,
                "num_winning": num_winning,
                "num_losing": num_losing,
                "largest_winner": largest_winner,
                "largest_loser": largest_loser,
                "diversification_score": round(diversification_score, 1),
                "sector_allocation": sector_allocation,
            }

        except Exception as e:
            logger.error(f"Failed to calculate portfolio metrics: {e}")
            raise

    async def analyze_diversification(self, positions: list[dict]) -> dict[str, Any]:
        """
        Analyze portfolio diversification.

        Uses Herfindahl-Hirschman Index (HHI) to measure concentration:
        - HHI = sum of squared market share percentages
        - Low HHI (< 1500) = well diversified
        - High HHI (> 2500) = concentrated

        Args:
            positions: List of position dictionaries with market_value

        Returns:
            {
                "hhi": float (0-10000),
                "diversification_score": float (0-100),
                "concentration_level": "low" | "moderate" | "high",
                "largest_position_pct": float,
                "top_3_positions_pct": float,
                "num_positions": int
            }
        """
        if not positions:
            return {
                "hhi": 0,
                "diversification_score": 0,
                "concentration_level": "undefined",
                "largest_position_pct": 0,
                "top_3_positions_pct": 0,
                "num_positions": 0,
            }

        # Calculate total portfolio value
        total_value = sum(float(p.get("market_value", 0)) for p in positions)

        if total_value == 0:
            return {
                "hhi": 0,
                "diversification_score": 0,
                "concentration_level": "undefined",
                "largest_position_pct": 0,
                "top_3_positions_pct": 0,
                "num_positions": len(positions),
            }

        # Calculate position percentages
        position_pcts = [
            (float(p.get("market_value", 0)) / total_value * 100) for p in positions
        ]
        position_pcts.sort(reverse=True)

        # Calculate HHI
        hhi = sum(pct**2 for pct in position_pcts)

        # Diversification score (inverse of HHI, scaled 0-100)
        # Perfect diversification (equal weights): HHI = 10000/n
        # Max concentration (1 position): HHI = 10000
        diversification_score = max(0, 100 - (hhi / 100))

        # Concentration level
        if hhi < 1500:
            concentration_level = "low"
        elif hhi < 2500:
            concentration_level = "moderate"
        else:
            concentration_level = "high"

        # Top position metrics
        largest_position_pct = position_pcts[0] if position_pcts else 0
        top_3_positions_pct = (
            sum(position_pcts[:3]) if len(position_pcts) >= 3 else sum(position_pcts)
        )

        return {
            "hhi": round(hhi, 2),
            "diversification_score": round(diversification_score, 1),
            "concentration_level": concentration_level,
            "largest_position_pct": round(largest_position_pct, 2),
            "top_3_positions_pct": round(top_3_positions_pct, 2),
            "num_positions": len(positions),
        }

    def calculate_sharpe_ratio(
        self,
        returns: list[float],
        risk_free_rate: float = 0.02,
    ) -> float:
        """
        Calculate Sharpe ratio from daily returns.

        Sharpe Ratio = (Mean Return - Risk Free Rate) / Std Dev of Returns

        Args:
            returns: List of daily returns (as decimals, e.g., 0.015 = 1.5%)
            risk_free_rate: Annual risk-free rate (default: 2%)

        Returns:
            Annualized Sharpe ratio

        Example:
            >>> returns = [0.01, -0.005, 0.02, 0.015, -0.01]
            >>> sharpe = service.calculate_sharpe_ratio(returns)
            >>> print(sharpe)  # 1.25
        """
        if not returns or len(returns) < 2:
            return 0.0

        # Calculate mean return
        mean_return = sum(returns) / len(returns)

        # Calculate standard deviation
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return 0.0

        # Daily risk-free rate
        daily_rf = risk_free_rate / 252

        # Calculate Sharpe ratio and annualize
        sharpe = (mean_return - daily_rf) / std_dev * math.sqrt(252)

        return round(sharpe, 2)

    def calculate_max_drawdown(self, equity_curve: list[float]) -> dict[str, float]:
        """
        Calculate maximum drawdown from equity curve.

        Max Drawdown = (Trough - Peak) / Peak

        Args:
            equity_curve: List of portfolio values over time

        Returns:
            {
                "max_drawdown": float (absolute dollars),
                "max_drawdown_pct": float (percentage),
                "peak_value": float,
                "trough_value": float,
                "peak_date_idx": int,
                "trough_date_idx": int
            }
        """
        if not equity_curve or len(equity_curve) < 2:
            return {
                "max_drawdown": 0.0,
                "max_drawdown_pct": 0.0,
                "peak_value": 0.0,
                "trough_value": 0.0,
                "peak_date_idx": 0,
                "trough_date_idx": 0,
            }

        peak_value = equity_curve[0]
        peak_idx = 0
        max_dd = 0.0
        max_dd_pct = 0.0
        trough_value = equity_curve[0]
        trough_idx = 0

        for i, value in enumerate(equity_curve):
            # Update peak
            if value > peak_value:
                peak_value = value
                peak_idx = i

            # Calculate drawdown from peak
            dd = peak_value - value
            dd_pct = (dd / peak_value * 100) if peak_value > 0 else 0

            # Update max drawdown
            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct
                trough_value = value
                trough_idx = i

        return {
            "max_drawdown": round(max_dd, 2),
            "max_drawdown_pct": round(max_dd_pct, 2),
            "peak_value": round(peak_value, 2),
            "trough_value": round(trough_value, 2),
            "peak_date_idx": peak_idx,
            "trough_date_idx": trough_idx,
        }

    def calculate_win_rate(self, trades: list[dict]) -> dict[str, Any]:
        """
        Calculate win rate and trade statistics.

        Args:
            trades: List of trade dictionaries with "pl" field

        Returns:
            {
                "total_trades": int,
                "winning_trades": int,
                "losing_trades": int,
                "win_rate": float (0-100),
                "avg_win": float,
                "avg_loss": float,
                "largest_win": float,
                "largest_loss": float,
                "profit_factor": float
            }
        """
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
                "profit_factor": 0.0,
            }

        winners = [t for t in trades if float(t.get("pl", 0)) > 0]
        losers = [t for t in trades if float(t.get("pl", 0)) < 0]

        total_trades = len(trades)
        winning_trades = len(winners)
        losing_trades = len(losers)

        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # Calculate averages
        avg_win = (
            sum(float(t.get("pl", 0)) for t in winners) / winning_trades
            if winning_trades > 0
            else 0
        )
        avg_loss = (
            sum(float(t.get("pl", 0)) for t in losers) / losing_trades
            if losing_trades > 0
            else 0
        )

        # Largest win/loss
        largest_win = max((float(t.get("pl", 0)) for t in winners), default=0)
        largest_loss = min((float(t.get("pl", 0)) for t in losers), default=0)

        # Profit factor
        gross_profit = sum(float(t.get("pl", 0)) for t in winners)
        gross_loss = abs(sum(float(t.get("pl", 0)) for t in losers))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "largest_win": round(largest_win, 2),
            "largest_loss": round(largest_loss, 2),
            "profit_factor": round(profit_factor, 2),
        }

    def _calculate_diversification(self, positions: list[dict]) -> float:
        """
        Internal method to calculate diversification score.

        Uses HHI-based scoring (0-100, higher = better diversification).

        Args:
            positions: List of positions with market_value

        Returns:
            Diversification score (0-100)
        """
        if not positions or len(positions) == 0:
            return 0.0

        total_value = sum(float(p.get("market_value", 0)) for p in positions)

        if total_value == 0:
            return 0.0

        # Calculate HHI
        hhi = sum(
            (float(p.get("market_value", 0)) / total_value * 100) ** 2
            for p in positions
        )

        # Convert HHI to diversification score
        # Perfect diversification: HHI = 10000/n
        # Score = 100 - (actual_HHI - perfect_HHI) / 100
        num_positions = len(positions)
        perfect_hhi = 10000 / num_positions
        diversification_score = max(0, 100 - (hhi - perfect_hhi) / 100)

        return diversification_score

    def _estimate_sector_allocation(self, positions: list[dict]) -> dict[str, float]:
        """
        Estimate sector allocation (simplified version).

        In production, this would use real sector data from an API.
        For now, returns a placeholder structure.

        Args:
            positions: List of positions with symbol and market_value

        Returns:
            Dictionary of sector percentages
        """
        # Simplified sector mapping (would use real data in production)
        sector_map = {
            "AAPL": "Technology",
            "MSFT": "Technology",
            "GOOGL": "Technology",
            "AMZN": "Consumer Cyclical",
            "TSLA": "Consumer Cyclical",
            "SPY": "Index Fund",
            "QQQ": "Index Fund",
            "F": "Consumer Cyclical",
            "SOFI": "Financial",
            "JPM": "Financial",
        }

        total_value = sum(float(p.get("market_value", 0)) for p in positions)

        if total_value == 0:
            return {}

        sector_values: dict[str, float] = {}

        for pos in positions:
            symbol = pos.get("symbol", "")
            market_value = float(pos.get("market_value", 0))
            sector = sector_map.get(symbol, "Other")

            if sector not in sector_values:
                sector_values[sector] = 0

            sector_values[sector] += market_value

        # Convert to percentages
        sector_pcts = {
            sector: round(value / total_value * 100, 2)
            for sector, value in sector_values.items()
        }

        return sector_pcts


# Singleton instance
_portfolio_analytics_service: PortfolioAnalyticsService | None = None


def get_portfolio_analytics_service(
    tradier_client: TradierClient | None = None,
) -> PortfolioAnalyticsService:
    """
    Get or create portfolio analytics service instance.

    Args:
        tradier_client: Optional Tradier client (uses singleton if not provided)

    Returns:
        PortfolioAnalyticsService instance

    Usage in routers:
        from ..services.portfolio_analytics_service import get_portfolio_analytics_service

        @router.get("/portfolio/metrics")
        async def get_metrics():
            service = get_portfolio_analytics_service()
            metrics = await service.calculate_portfolio_metrics()
            return metrics
    """
    global _portfolio_analytics_service

    if _portfolio_analytics_service is None:
        from ..services.tradier_client import get_tradier_client

        if tradier_client is None:
            tradier_client = get_tradier_client()

        _portfolio_analytics_service = PortfolioAnalyticsService(
            tradier_client=tradier_client
        )

    return _portfolio_analytics_service
