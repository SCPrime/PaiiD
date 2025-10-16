"""
Backtesting API Router

Endpoints for running strategy backtests and retrieving results.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..core.auth import require_bearer
from ..services.backtesting_engine import BacktestingEngine, BacktestResult, StrategyRules
from ..services.historical_data import HistoricalDataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backtesting", tags=["backtesting"])


class BacktestRequest(BaseModel):
    """Request model for backtest execution"""

    symbol: str = Field(..., description="Stock symbol to backtest")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    initial_capital: float = Field(10000.0, ge=1000, le=1000000, description="Initial capital")

    # Strategy rules
    entry_rules: List[Dict[str, Any]] = Field(..., description="Entry conditions")
    exit_rules: List[Dict[str, Any]] = Field(..., description="Exit conditions")
    position_size_percent: float = Field(
        10.0, ge=1, le=100, description="Position size % of portfolio"
    )
    max_positions: int = Field(1, ge=1, le=10, description="Max concurrent positions")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "initial_capital": 10000,
                "entry_rules": [{"indicator": "RSI", "operator": "<", "value": 30}],
                "exit_rules": [
                    {"type": "take_profit", "value": 5},
                    {"type": "stop_loss", "value": 2},
                ],
                "position_size_percent": 10,
                "max_positions": 1,
            }
        }


class BacktestResponse(BaseModel):
    """Response model for backtest results"""

    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/run", response_model=BacktestResponse, dependencies=[Depends(require_bearer)])
async def run_backtest(request: BacktestRequest):
    """
    Execute a backtest on historical data

    This endpoint:
    1. Fetches historical OHLCV data for the symbol
    2. Simulates strategy execution bar-by-bar
    3. Calculates performance metrics
    4. Returns detailed results including equity curve and trade history

    **Entry Rules Format:**
    ```json
    [
        {"indicator": "RSI", "operator": "<", "value": 30},
        {"indicator": "SMA", "operator": ">", "period": 20}
    ]
    ```

    **Exit Rules Format:**
    ```json
    [
        {"type": "take_profit", "value": 5},
        {"type": "stop_loss", "value": 2}
    ]
    ```

    **Returns comprehensive metrics:**
    - Total return, annualized return, Sharpe ratio
    - Max drawdown, win rate, profit factor
    - Full equity curve and trade history
    """
    try:
        # Validate dates
        historical_service = HistoricalDataService()
        if not historical_service.validate_date_range(request.start_date, request.end_date):
            raise HTTPException(
                status_code=400,
                detail="Invalid date range. Ensure start_date < end_date and range <= 5 years",
            )

        # Fetch historical data
        logger.info(f"Fetching historical data for {request.symbol}")
        prices = await historical_service.get_historical_bars(
            symbol=request.symbol, start_date=request.start_date, end_date=request.end_date
        )

        if not prices or len(prices) < 20:
            raise HTTPException(
                status_code=400, detail="Insufficient historical data. Need at least 20 bars."
            )

        # Create strategy rules
        strategy = StrategyRules(
            entry_rules=request.entry_rules,
            exit_rules=request.exit_rules,
            position_size_percent=request.position_size_percent,
            max_positions=request.max_positions,
        )

        # Run backtest
        logger.info(f"Running backtest for {request.symbol} with {len(prices)} bars")
        engine = BacktestingEngine(initial_capital=request.initial_capital)
        result = engine.execute_backtest(symbol=request.symbol, prices=prices, strategy=strategy)

        # Convert dataclass to dict
        result_dict = {
            "performance": {
                "total_return": result.total_return,
                "total_return_percent": result.total_return_percent,
                "annualized_return": result.annualized_return,
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "max_drawdown_percent": result.max_drawdown_percent,
            },
            "statistics": {
                "total_trades": result.total_trades,
                "winning_trades": result.winning_trades,
                "losing_trades": result.losing_trades,
                "win_rate": result.win_rate,
                "avg_win": result.avg_win,
                "avg_loss": result.avg_loss,
                "profit_factor": result.profit_factor,
            },
            "capital": {
                "initial": result.initial_capital,
                "final": result.final_capital,
            },
            "config": {
                "symbol": result.symbol,
                "start_date": result.start_date,
                "end_date": result.end_date,
            },
            "equity_curve": result.equity_curve,
            "trade_history": result.trade_history[:100],  # Limit to 100 most recent trades
        }

        logger.info(
            f"Backtest completed: {result.total_trades} trades, {result.win_rate:.1f}% win rate"
        )

        return BacktestResponse(success=True, result=result_dict)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Backtest execution error: {str(e)}", exc_info=True)
        return BacktestResponse(success=False, error=f"Backtest failed: {str(e)}")


@router.get("/quick-test", dependencies=[Depends(require_bearer)])
async def quick_backtest(
    symbol: str = Query("SPY", description="Symbol to test"),
    months_back: int = Query(6, ge=1, le=60, description="Months of history"),
):
    """
    Run a quick backtest with default RSI strategy

    Useful for testing backtesting functionality quickly.
    Uses a simple RSI < 30 entry, 5% TP / 2% SL exit strategy.
    """
    try:
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=months_back * 30)).strftime("%Y-%m-%d")

        request = BacktestRequest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=10000,
            entry_rules=[{"indicator": "RSI", "operator": "<", "value": 30}],
            exit_rules=[{"type": "take_profit", "value": 5}, {"type": "stop_loss", "value": 2}],
            position_size_percent=10,
            max_positions=1,
        )

        return await run_backtest(request)

    except Exception as e:
        logger.error(f"Quick backtest error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategy-templates")
async def get_strategy_templates():
    """
    Get pre-built strategy templates for backtesting

    Returns common strategy configurations that users can test.
    """
    templates = [
        {
            "name": "RSI Oversold",
            "description": "Buy when RSI < 30, sell at 5% profit or 2% stop loss",
            "entry_rules": [{"indicator": "RSI", "operator": "<", "value": 30}],
            "exit_rules": [{"type": "take_profit", "value": 5}, {"type": "stop_loss", "value": 2}],
            "position_size_percent": 10,
            "max_positions": 1,
        },
        {
            "name": "RSI Overbought Short",
            "description": "Short when RSI > 70, cover at 5% profit or 2% stop loss",
            "entry_rules": [{"indicator": "RSI", "operator": ">", "value": 70}],
            "exit_rules": [{"type": "take_profit", "value": 5}, {"type": "stop_loss", "value": 2}],
            "position_size_percent": 10,
            "max_positions": 1,
        },
        {
            "name": "SMA Crossover",
            "description": "Buy when price crosses above 20-day SMA",
            "entry_rules": [{"indicator": "SMA", "operator": ">", "period": 20}],
            "exit_rules": [{"type": "take_profit", "value": 10}, {"type": "stop_loss", "value": 5}],
            "position_size_percent": 15,
            "max_positions": 1,
        },
        {
            "name": "Conservative RSI",
            "description": "More conservative RSI strategy with tighter stops",
            "entry_rules": [{"indicator": "RSI", "operator": "<", "value": 25}],
            "exit_rules": [{"type": "take_profit", "value": 3}, {"type": "stop_loss", "value": 1}],
            "position_size_percent": 5,
            "max_positions": 2,
        },
    ]

    return {"templates": templates}
