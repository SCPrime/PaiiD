        from ..services.equity_tracker import get_equity_tracker
        from ..services.equity_tracker import get_equity_tracker
from ..core.jwt import get_current_user
from ..models.database import User
from ..services.tradier_client import get_tradier_client
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Literal
import logging
import math

"""
Analytics and Performance Tracking Endpoints

Provides portfolio performance metrics, historical equity tracking,
and risk analytics for the P&L Dashboard.
"""




logger = logging.getLogger(__name__)

router = APIRouter(tags=["analytics"])

class PortfolioSummary(BaseModel):
    """Real-time portfolio summary metrics"""

    total_value: float
    cash: float
    buying_power: float
    total_pl: float
    total_pl_percent: float
    day_pl: float
    day_pl_percent: float
    num_positions: int
    num_winning: int
    num_losing: int
    largest_winner: dict | None = None
    largest_loser: dict | None = None

class EquityPoint(BaseModel):
    """Single equity curve data point"""

    timestamp: str
    equity: float
    cash: float
    positions_value: float

class PerformanceMetrics(BaseModel):
    """Comprehensive performance analytics"""

    total_return: float
    total_return_percent: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_percent: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    num_trades: int
    num_wins: int
    num_losses: int
    current_streak: int
    best_day: float
    worst_day: float

@router.get("/portfolio/summary")
async def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
) -> PortfolioSummary:
    """
    Get real-time portfolio summary with P&L metrics

    Returns:
        - Total portfolio value
        - Cash and buying power
        - Total P&L (all-time)
        - Day P&L (today's change)
        - Position counts (winning/losing)
        - Largest winner/loser
    """
    try:
        client = get_tradier_client()

        # Get account data
        account = client.get_account()
        positions = client.get_positions()

        total_value = float(account.get("portfolio_value", 0))
        cash = float(account.get("cash", 0))
        buying_power = float(account.get("buying_power", 0))

        # Calculate position metrics
        num_positions = len(positions)
        num_winning = 0
        num_losing = 0
        total_pl = 0.0
        day_pl = 0.0
        largest_winner = None
        largest_loser = None
        max_win_pl = float("-inf")
        max_loss_pl = float("inf")

        for pos in positions:
            unrealized_pl = float(pos.get("unrealized_pl", 0))
            change_today = float(pos.get("change_today", 0))
            qty = float(pos.get("qty", 0))

            # Count winning/losing positions
            if unrealized_pl > 0:
                num_winning += 1
            elif unrealized_pl < 0:
                num_losing += 1

            # Track total P&L
            total_pl += unrealized_pl

            # Track day P&L (change_today is price change, need to multiply by qty)
            day_pl += change_today * qty

            # Track largest winner/loser
            if unrealized_pl > max_win_pl:
                max_win_pl = unrealized_pl
                largest_winner = {
                    "symbol": pos.get("symbol"),
                    "pl": unrealized_pl,
                    "pl_percent": float(pos.get("unrealized_plpc", 0)),
                }

            if unrealized_pl < max_loss_pl:
                max_loss_pl = unrealized_pl
                largest_loser = {
                    "symbol": pos.get("symbol"),
                    "pl": unrealized_pl,
                    "pl_percent": float(pos.get("unrealized_plpc", 0)),
                }

        # Calculate percentages
        positions_value = sum(float(p.get("market_value", 0)) for p in positions)
        # Calculate P&L percentage: total_pl / cost_basis = total_pl / (positions_value - total_pl)
        # Guard against division by zero when positions_value == total_pl (break-even after gains)
        cost_basis = positions_value - total_pl
        total_pl_percent = (
            (total_pl / cost_basis * 100) if cost_basis != 0 and positions_value != 0 else 0
        )
        day_pl_percent = (day_pl / positions_value * 100) if positions_value != 0 else 0

        logger.info(f"✅ Portfolio summary: ${total_value:.2f}, P&L: ${total_pl:.2f}")

        return PortfolioSummary(
            total_value=round(total_value, 2),
            cash=round(cash, 2),
            buying_power=round(buying_power, 2),
            total_pl=round(total_pl, 2),
            total_pl_percent=round(total_pl_percent, 2),
            day_pl=round(day_pl, 2),
            day_pl_percent=round(day_pl_percent, 2),
            num_positions=num_positions,
            num_winning=num_winning,
            num_losing=num_losing,
            largest_winner=largest_winner,
            largest_loser=largest_loser,
        )

    except Exception as e:
        logger.error(f"❌ Failed to get portfolio summary: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio summary: {e!s}")

@router.get("/portfolio/history")
async def get_portfolio_history(
    period: Literal["1D", "1W", "1M", "3M", "1Y", "ALL"] = Query(default="1M"),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get historical portfolio equity data

    Args:
        period: Time period (1D, 1W, 1M, 3M, 1Y, ALL)

    Returns:
        List of equity curve data points

    Note: Uses tracked equity data from daily snapshots.
    Falls back to simulated data if insufficient history.
    """
    try:

        tracker = get_equity_tracker()
        client = get_tradier_client()
        account = client.get_account()

        current_equity = float(account.get("portfolio_value", 100000))

        # Determine time range
        now = datetime.now()
        if period == "1D":
            start_date = now - timedelta(days=1)
        elif period == "1W":
            start_date = now - timedelta(weeks=1)
        elif period == "1M":
            start_date = now - timedelta(days=30)
        elif period == "3M":
            start_date = now - timedelta(days=90)
        elif period == "1Y":
            start_date = now - timedelta(days=365)
        else:  # ALL
            start_date = now - timedelta(days=730)  # 2 years

        # Try to load historical data
        history = tracker.get_history(start_date=start_date)

        # Use real historical data only - NO simulated fallbacks
        if len(history) >= 5:  # At least 5 data points
            equity_points = [
                EquityPoint(
                    timestamp=h["timestamp"],
                    equity=h["equity"],
                    cash=h["cash"],
                    positions_value=h["positions_value"],
                ).model_dump()
                for h in history
            ]

            logger.info(
                f"✅ Loaded {len(equity_points)} equity points from history for period {period}"
            )

        else:
            # Insufficient historical data - return current point only with warning
            equity_points = [
                EquityPoint(
                    timestamp=now.isoformat(),
                    equity=round(current_equity, 2),
                    cash=round(float(account.get("cash", 0)), 2),
                    positions_value=round(current_equity - float(account.get("cash", 0)), 2),
                ).model_dump()
            ]

            logger.warning(
                f"⚠️ Insufficient historical data for period {period}. Showing current snapshot only. Data will accumulate over time."
            )

        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat(),
            "data": equity_points,
            "is_simulated": len(history) < 5,
        }

    except Exception as e:
        logger.error(f"❌ Failed to get portfolio history: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio history: {e!s}")

@router.get("/analytics/performance")
async def get_performance_metrics(
    period: Literal["1D", "1W", "1M", "3M", "1Y", "ALL"] = Query(default="1M"),
    current_user: User = Depends(get_current_user),
) -> PerformanceMetrics:
    """
    Get comprehensive performance metrics and risk analytics

    Args:
        period: Time period for calculations

    Returns:
        - Total return and Sharpe ratio
        - Max drawdown
        - Win rate and profit factor
        - Trade statistics
        - Best/worst days

    Note: Currently uses simulated data. Production would use
    tracked equity curve and completed trade history.
    """
    try:
        client = get_tradier_client()

        # Get account and positions
        account = client.get_account()
        positions = client.get_positions()
        client.get_orders()

        float(account.get("portfolio_value", 100000))

        # Simulate performance metrics based on current positions
        # PHASE 2 ENHANCEMENT: Replace with actual calculations from historical data
        # Requirements:
        #   - Store historical position snapshots in TimescaleDB
        #   - Calculate rolling Sharpe ratio from daily returns
        #   - Track win rate from closed positions history
        # Current: Estimates from current unrealized P&L (temporary)

        # Calculate from current positions
        total_pl = sum(float(p.get("unrealized_pl", 0)) for p in positions)
        total_cost = sum(float(p.get("cost_basis", 0)) for p in positions)

        winning_positions = [p for p in positions if float(p.get("unrealized_pl", 0)) > 0]
        losing_positions = [p for p in positions if float(p.get("unrealized_pl", 0)) < 0]

        num_wins = len(winning_positions)
        num_losses = len(losing_positions)
        num_trades = num_wins + num_losses

        # Win rate
        win_rate = (num_wins / num_trades * 100) if num_trades > 0 else 0

        # Average win/loss
        avg_win = (
            sum(float(p.get("unrealized_pl", 0)) for p in winning_positions) / num_wins
            if num_wins > 0
            else 0
        )
        avg_loss = (
            sum(float(p.get("unrealized_pl", 0)) for p in losing_positions) / num_losses
            if num_losses > 0
            else 0
        )

        # Profit factor
        gross_profit = sum(float(p.get("unrealized_pl", 0)) for p in winning_positions)
        gross_loss = abs(sum(float(p.get("unrealized_pl", 0)) for p in losing_positions))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Total return
        total_return = total_pl
        total_return_percent = (total_return / total_cost * 100) if total_cost > 0 else 0

        # Sharpe ratio - calculate actual volatility from equity history

        tracker = get_equity_tracker()
        now = datetime.now()
        equity_history = tracker.get_history(start_date=now - timedelta(days=365))

        if len(equity_history) > 1:
            # Calculate daily returns from actual equity data
            daily_returns = []
            for i in range(1, len(equity_history)):
                prev_equity = equity_history[i - 1]["equity"]
                curr_equity = equity_history[i]["equity"]
                if prev_equity > 0:
                    daily_return = (curr_equity - prev_equity) / prev_equity
                    daily_returns.append(daily_return)

            if len(daily_returns) > 1:
                # Calculate actual volatility (standard deviation of returns)
                mean_return = sum(daily_returns) / len(daily_returns)
                variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)
                volatility = (variance**0.5) * 100  # Convert to percentage

                # Use actual average return
                avg_return = mean_return * 100  # Convert to percentage
            else:
                # Fallback if only 1 return
                volatility = 1.5
                avg_return = total_return_percent / 252
        else:
            # Fallback if insufficient data
            volatility = 1.5
            avg_return = total_return_percent / 252

        sharpe_ratio = (avg_return / volatility * math.sqrt(252)) if volatility > 0 else 0

        # Max drawdown - calculate from actual equity history
        if len(equity_history) > 1:
            # Calculate actual max drawdown
            peak_equity = equity_history[0]["equity"]
            max_dd_amount = 0
            max_dd_percent = 0

            for point in equity_history:
                equity = point["equity"]

                # Update peak
                if equity > peak_equity:
                    peak_equity = equity

                # Calculate drawdown from peak
                dd_amount = peak_equity - equity
                dd_percent = (dd_amount / peak_equity * 100) if peak_equity > 0 else 0

                # Track maximum
                if dd_amount > max_dd_amount:
                    max_dd_amount = dd_amount
                    max_dd_percent = dd_percent

            max_drawdown = max_dd_amount
            max_drawdown_percent = max_dd_percent
        else:
            # Insufficient historical data - set to 0
            max_drawdown = 0.0
            max_drawdown_percent = 0.0
            logger.warning("⚠️ Insufficient historical data to calculate max drawdown. Returning 0.")

        # Current streak
        # Check if last position was win or loss
        current_streak = 1 if num_wins > num_losses else -1

        # Best/worst day - calculate from actual equity history
        if len(equity_history) > 1:
            # Calculate daily changes from actual equity data
            daily_changes = []
            for i in range(1, len(equity_history)):
                prev_equity = equity_history[i - 1]["equity"]
                curr_equity = equity_history[i]["equity"]
                change = curr_equity - prev_equity
                daily_changes.append(change)

            best_day = max(daily_changes) if daily_changes else 0.0
            worst_day = min(daily_changes) if daily_changes else 0.0

            logger.info(
                f"Calculated best day: ${best_day:.2f}, worst day: ${worst_day:.2f} from {len(daily_changes)} days of history"
            )
        else:
            # Insufficient historical data - set to 0
            best_day = 0.0
            worst_day = 0.0
            logger.warning(
                "⚠️ Insufficient historical data to calculate best/worst day. Returning 0."
            )

        logger.info(
            f"✅ Performance metrics: Return {total_return_percent:.2f}%, Sharpe {sharpe_ratio:.2f}"
        )

        return PerformanceMetrics(
            total_return=round(total_return, 2),
            total_return_percent=round(total_return_percent, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            max_drawdown=round(max_drawdown, 2),
            max_drawdown_percent=round(max_drawdown_percent, 2),
            win_rate=round(win_rate, 2),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            profit_factor=round(profit_factor, 2),
            num_trades=num_trades,
            num_wins=num_wins,
            num_losses=num_losses,
            current_streak=current_streak,
            best_day=round(best_day, 2),
            worst_day=round(worst_day, 2),
        )

    except Exception as e:
        logger.error(f"❌ Failed to get performance metrics: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {e!s}")
