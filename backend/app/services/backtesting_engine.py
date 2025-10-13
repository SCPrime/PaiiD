"""
Backtesting Engine Service

Simulates strategy execution on historical market data to evaluate performance.
Calculates key metrics: Sharpe ratio, max drawdown, win rate, profit factor.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Represents a single trade"""
    entry_date: str
    exit_date: Optional[str]
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    side: str  # 'long' or 'short'
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    status: str = "open"  # 'open', 'closed'


@dataclass
class StrategyRules:
    """Defines strategy entry/exit rules"""
    entry_rules: List[Dict[str, Any]]  # e.g., [{"indicator": "RSI", "operator": "<", "value": 30}]
    exit_rules: List[Dict[str, Any]]  # e.g., [{"type": "take_profit", "value": 5}, {"type": "stop_loss", "value": 2}]
    position_size_percent: float = 10.0  # % of portfolio per trade
    max_positions: int = 1  # Max concurrent positions
    rsi_period: int = 14  # Configurable RSI period (default 14)


@dataclass
class BacktestResult:
    """Comprehensive backtest results"""
    # Performance metrics
    total_return: float
    total_return_percent: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_percent: float

    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float

    # Time series data
    equity_curve: List[Dict[str, Any]]  # [{date, value, drawdown}]
    trade_history: List[Dict[str, Any]]

    # Configuration
    initial_capital: float
    final_capital: float
    start_date: str
    end_date: str
    symbol: str


class BacktestingEngine:
    """Core backtesting engine"""

    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: List[Trade] = []
        self.closed_trades: List[Trade] = []
        self.equity_curve: List[Dict[str, Any]] = []
        self.peak_capital = initial_capital

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate RSI for strategy signals"""
        if len(prices) < period + 1:
            return 50.0

        changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        gains = [max(c, 0) for c in changes]
        losses = [abs(min(c, 0)) for c in changes]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period

    def check_entry_signal(
        self,
        rules: List[Dict[str, Any]],
        prices: List[float],
        current_price: float,
        rsi_period: int = 14
    ) -> bool:
        """
        Check if entry conditions are met

        Rules format: [{"indicator": "RSI", "operator": "<", "value": 30}]
        """
        if not rules:
            return False

        for rule in rules:
            indicator = rule.get("indicator", "").upper()
            operator = rule.get("operator", "=")
            value = rule.get("value", 0)

            if indicator == "RSI":
                if len(prices) < rsi_period + 1:
                    return False
                rsi = self.calculate_rsi(prices, period=rsi_period)

                if operator == "<" and not (rsi < value):
                    return False
                elif operator == ">" and not (rsi > value):
                    return False
                elif operator == "=" and not (abs(rsi - value) < 1):
                    return False

            elif indicator == "SMA":
                period = rule.get("period", 20)
                sma = self.calculate_sma(prices, period)
                if sma is None:
                    return False

                if operator == ">" and not (current_price > sma):
                    return False
                elif operator == "<" and not (current_price < sma):
                    return False

            elif indicator == "PRICE":
                if operator == ">" and not (current_price > value):
                    return False
                elif operator == "<" and not (current_price < value):
                    return False

        return True

    def check_exit_signal(
        self,
        trade: Trade,
        current_price: float,
        exit_rules: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Check if exit conditions are met

        Returns: (should_exit, reason)
        """
        if trade.entry_price is None:
            return False, ""

        pnl_percent = ((current_price - trade.entry_price) / trade.entry_price) * 100

        for rule in exit_rules:
            rule_type = rule.get("type", "")
            value = rule.get("value", 0)

            if rule_type == "take_profit":
                if pnl_percent >= value:
                    return True, f"Take profit hit: {pnl_percent:.2f}%"

            elif rule_type == "stop_loss":
                if pnl_percent <= -value:
                    return True, f"Stop loss hit: {pnl_percent:.2f}%"

            elif rule_type == "trailing_stop":
                # Simplified trailing stop
                if pnl_percent <= -value:
                    return True, f"Trailing stop: {pnl_percent:.2f}%"

        return False, ""

    def execute_backtest(
        self,
        symbol: str,
        prices: List[Dict[str, Any]],  # [{date, open, high, low, close, volume}]
        strategy: StrategyRules
    ) -> BacktestResult:
        """
        Execute backtest on historical data

        Args:
            symbol: Stock symbol
            prices: List of OHLCV bars
            strategy: Strategy rules

        Returns:
            BacktestResult with all metrics
        """
        if not prices or len(prices) < 20:
            raise ValueError("Insufficient price data for backtesting")

        # Reset state
        self.capital = self.initial_capital
        self.positions = []
        self.closed_trades = []
        self.equity_curve = []
        self.peak_capital = self.initial_capital

        # Track price history for indicators
        price_history = []

        # Iterate through each bar
        for i, bar in enumerate(prices):
            date = bar["date"]
            close_price = bar["close"]
            price_history.append(close_price)

            # Check exits for open positions first
            for position in self.positions[:]:  # Iterate over copy
                should_exit, reason = self.check_exit_signal(
                    position,
                    close_price,
                    strategy.exit_rules
                )

                if should_exit:
                    # Close position
                    position.exit_date = date
                    position.exit_price = close_price
                    position.pnl = (close_price - position.entry_price) * position.quantity
                    position.pnl_percent = ((close_price - position.entry_price) / position.entry_price) * 100
                    position.status = "closed"

                    # Return capital: original cost basis + profit/loss
                    # This equals: entry_price * quantity + (exit_price - entry_price) * quantity = exit_price * quantity
                    self.capital += position.entry_price * position.quantity + position.pnl

                    # Move to closed trades
                    self.closed_trades.append(position)
                    self.positions.remove(position)

                    logger.debug(f"Closed position: {symbol} at {close_price}, PnL: {position.pnl:.2f}, Reason: {reason}")

            # Check entry signals if we have capacity
            if len(self.positions) < strategy.max_positions:
                should_enter = self.check_entry_signal(
                    strategy.entry_rules,
                    price_history,
                    close_price,
                    rsi_period=strategy.rsi_period
                )

                if should_enter:
                    # Calculate position size
                    position_capital = self.capital * (strategy.position_size_percent / 100)
                    quantity = int(position_capital / close_price)

                    # Calculate exact cost before checking capital
                    exact_cost = quantity * close_price

                    if quantity > 0 and exact_cost <= self.capital:
                        # Open new position
                        trade = Trade(
                            entry_date=date,
                            exit_date=None,
                            entry_price=close_price,
                            exit_price=None,
                            quantity=quantity,
                            side="long",
                            status="open"
                        )

                        self.positions.append(trade)
                        self.capital -= close_price * quantity

                        logger.debug(f"Opened position: {symbol} at {close_price}, Qty: {quantity}")

            # Calculate current equity (capital + open positions value)
            # Formula: current_value = close_price * quantity = unrealized_pnl + cost_basis
            open_positions_value = sum(
                (close_price - p.entry_price) * p.quantity + (p.entry_price * p.quantity)
                for p in self.positions
                if p.entry_price > 0  # Guard against zero entry prices
            )
            current_equity = self.capital + open_positions_value

            # Update peak capital for drawdown calculation
            if current_equity > self.peak_capital:
                self.peak_capital = current_equity

            # Calculate drawdown
            drawdown = self.peak_capital - current_equity
            drawdown_percent = (drawdown / self.peak_capital) * 100 if self.peak_capital > 0 else 0

            # Record equity curve point
            self.equity_curve.append({
                "date": date,
                "value": round(current_equity, 2),
                "drawdown": round(drawdown, 2),
                "drawdown_percent": round(drawdown_percent, 2)
            })

        # Close any remaining open positions at final price
        final_price = prices[-1]["close"]
        final_date = prices[-1]["date"]
        for position in self.positions:
            position.exit_date = final_date
            position.exit_price = final_price
            position.pnl = (final_price - position.entry_price) * position.quantity
            position.pnl_percent = ((final_price - position.entry_price) / position.entry_price) * 100
            position.status = "closed"
            self.closed_trades.append(position)

        self.positions = []

        # Calculate final metrics
        return self._calculate_metrics(symbol, prices[0]["date"], prices[-1]["date"])

    def _calculate_metrics(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> BacktestResult:
        """Calculate all performance metrics from closed trades"""

        if not self.equity_curve:
            raise ValueError("No equity curve data available")

        final_capital = self.equity_curve[-1]["value"]
        total_return = final_capital - self.initial_capital
        total_return_percent = (total_return / self.initial_capital) * 100

        # Calculate annualized return
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        days = (end_dt - start_dt).days
        years = days / 365.0 if days > 0 else 1.0
        annualized_return = ((final_capital / self.initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0

        # Trade statistics
        winning_trades = [t for t in self.closed_trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in self.closed_trades if t.pnl and t.pnl < 0]
        total_trades = len(self.closed_trades)

        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0

        total_wins = sum(t.pnl for t in winning_trades)
        total_losses = abs(sum(t.pnl for t in losing_trades))
        # Profit factor: total_wins / total_losses
        # If no losses, factor is infinity (perfect strategy) or 0 (no trades)
        if total_losses > 0:
            profit_factor = total_wins / total_losses
        elif total_wins > 0:
            profit_factor = 999.99  # Display as "∞" equivalent (backend uses float, not actual inf)
        else:
            profit_factor = 0  # No wins, no losses = neutral

        # Max drawdown
        max_drawdown = max((point["drawdown"] for point in self.equity_curve), default=0)
        max_drawdown_percent = max((point["drawdown_percent"] for point in self.equity_curve), default=0)

        # Sharpe ratio (simplified - assumes daily returns)
        if len(self.equity_curve) > 1:
            returns = [
                (self.equity_curve[i]["value"] - self.equity_curve[i-1]["value"]) / self.equity_curve[i-1]["value"]
                for i in range(1, len(self.equity_curve))
            ]
            avg_return = sum(returns) / len(returns) if returns else 0
            std_return = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / len(returns)) if returns else 1
            sharpe_ratio = (avg_return / std_return * math.sqrt(252)) if std_return > 0 else 0  # Annualized
        else:
            sharpe_ratio = 0

        # Format trade history
        trade_history = [
            {
                "entry_date": t.entry_date,
                "exit_date": t.exit_date,
                "entry_price": round(t.entry_price, 2),
                "exit_price": round(t.exit_price, 2) if t.exit_price else None,
                "quantity": t.quantity,
                "side": t.side,
                "pnl": round(t.pnl, 2) if t.pnl else 0,
                "pnl_percent": round(t.pnl_percent, 2) if t.pnl_percent else 0,
                "status": t.status
            }
            for t in self.closed_trades
        ]

        return BacktestResult(
            total_return=round(total_return, 2),
            total_return_percent=round(total_return_percent, 2),
            annualized_return=round(annualized_return, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            max_drawdown=round(max_drawdown, 2),
            max_drawdown_percent=round(max_drawdown_percent, 2),
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=round(win_rate, 2),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            profit_factor=round(profit_factor, 2),
            equity_curve=self.equity_curve,
            trade_history=trade_history,
            initial_capital=self.initial_capital,
            final_capital=round(final_capital, 2),
            start_date=start_date,
            end_date=end_date,
            symbol=symbol
        )
