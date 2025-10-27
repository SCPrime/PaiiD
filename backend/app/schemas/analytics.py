"""Analytics response schemas"""

from typing import Literal

from pydantic import BaseModel, Field


class PortfolioSummary(BaseModel):
    """Real-time portfolio summary metrics"""

    total_value: float = Field(..., description="Total portfolio value")
    cash: float = Field(..., description="Cash balance")
    buying_power: float = Field(..., description="Buying power available")
    total_pl: float = Field(..., description="Total P&L (all-time)")
    total_pl_percent: float = Field(..., description="Total P&L percentage")
    day_pl: float = Field(..., description="Today's P&L")
    day_pl_percent: float = Field(..., description="Today's P&L percentage")
    num_positions: int = Field(..., description="Number of open positions")
    num_winning: int = Field(..., description="Number of winning positions")
    num_losing: int = Field(..., description="Number of losing positions")
    largest_winner: dict | None = Field(None, description="Largest winning position")
    largest_loser: dict | None = Field(None, description="Largest losing position")

    class Config:
        json_schema_extra = {
            "example": {
                "total_value": 105000.0,
                "cash": 50000.0,
                "buying_power": 80000.0,
                "total_pl": 5000.0,
                "total_pl_percent": 5.0,
                "day_pl": 500.0,
                "day_pl_percent": 0.5,
                "num_positions": 5,
                "num_winning": 3,
                "num_losing": 2,
                "largest_winner": {"symbol": "AAPL", "pl": 2500.0, "pl_percent": 16.67},
                "largest_loser": {"symbol": "TSLA", "pl": -500.0, "pl_percent": -5.0},
            }
        }


class EquityPoint(BaseModel):
    """Single equity curve data point"""

    timestamp: str = Field(..., description="Timestamp of data point")
    equity: float = Field(..., description="Total equity value")
    cash: float = Field(..., description="Cash balance")
    positions_value: float = Field(..., description="Total positions value")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-10-27T10:00:00Z",
                "equity": 105000.0,
                "cash": 50000.0,
                "positions_value": 55000.0,
            }
        }


class PortfolioHistory(BaseModel):
    """Historical portfolio equity data"""

    period: Literal["1D", "1W", "1M", "3M", "1Y", "ALL"] = Field(
        ..., description="Time period"
    )
    start_date: str = Field(..., description="Start date of period")
    end_date: str = Field(..., description="End date of period")
    data: list[EquityPoint] = Field(..., description="Equity curve data points")
    is_simulated: bool = Field(False, description="Whether data is simulated")

    class Config:
        json_schema_extra = {
            "example": {
                "period": "1M",
                "start_date": "2025-09-27T00:00:00Z",
                "end_date": "2025-10-27T23:59:59Z",
                "data": [
                    {
                        "timestamp": "2025-10-27T10:00:00Z",
                        "equity": 105000.0,
                        "cash": 50000.0,
                        "positions_value": 55000.0,
                    }
                ],
                "is_simulated": False,
            }
        }


class PerformanceMetrics(BaseModel):
    """Comprehensive performance analytics"""

    total_return: float = Field(..., description="Total return ($)")
    total_return_percent: float = Field(..., description="Total return (%)")
    sharpe_ratio: float = Field(..., description="Sharpe ratio (risk-adjusted return)")
    max_drawdown: float = Field(..., description="Maximum drawdown ($)")
    max_drawdown_percent: float = Field(..., description="Maximum drawdown (%)")
    win_rate: float = Field(..., description="Win rate (%)")
    avg_win: float = Field(..., description="Average win ($)")
    avg_loss: float = Field(..., description="Average loss ($)")
    profit_factor: float = Field(..., description="Profit factor (gross profit / gross loss)")
    num_trades: int = Field(..., description="Total number of trades")
    num_wins: int = Field(..., description="Number of winning trades")
    num_losses: int = Field(..., description="Number of losing trades")
    current_streak: int = Field(..., description="Current win/loss streak")
    best_day: float = Field(..., description="Best daily return ($)")
    worst_day: float = Field(..., description="Worst daily return ($)")

    class Config:
        json_schema_extra = {
            "example": {
                "total_return": 5000.0,
                "total_return_percent": 5.0,
                "sharpe_ratio": 1.25,
                "max_drawdown": 2000.0,
                "max_drawdown_percent": 2.0,
                "win_rate": 60.0,
                "avg_win": 1000.0,
                "avg_loss": -500.0,
                "profit_factor": 2.0,
                "num_trades": 10,
                "num_wins": 6,
                "num_losses": 4,
                "current_streak": 2,
                "best_day": 1500.0,
                "worst_day": -800.0,
            }
        }
