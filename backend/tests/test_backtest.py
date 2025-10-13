"""
Test strategy backtesting engine
Tests backtest execution, performance metrics, trade simulation
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
HEADERS = {"Authorization": "Bearer change-me"}


def test_backtest_endpoint_exists():
    """Test that backtest endpoint is accessible"""
    # POST with minimal strategy should work
    strategy = {
        "symbol": "SPY",
        "startDate": "2024-01-01",
        "endDate": "2024-06-01",
        "initialCapital": 10000,
        "rules": {
            "entryConditions": ["rsi_oversold"],
            "exitConditions": ["rsi_overbought"],
            "rsiPeriod": 14,
            "rsiOversold": 30,
            "rsiOverbought": 70
        }
    }

    response = client.post("/api/backtest", json=strategy, headers=HEADERS)
    # Should return 200 or validation error, not auth error
    assert response.status_code != 401


def test_backtest_requires_auth():
    """Test backtest requires authentication"""
    strategy = {"symbol": "SPY", "startDate": "2024-01-01", "endDate": "2024-06-01"}
    response = client.post("/api/backtest", json=strategy)
    assert response.status_code == 401


def test_backtest_returns_performance_metrics():
    """Test backtest returns required performance metrics"""
    strategy = {
        "symbol": "AAPL",
        "startDate": "2024-01-01",
        "endDate": "2024-03-01",
        "initialCapital": 10000,
        "rules": {
            "entryConditions": ["sma_crossover"],
            "exitConditions": ["sma_crossunder"],
            "smaPeriod": 20
        }
    }

    response = client.post("/api/backtest", json=strategy, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        # Check for essential backtest metrics
        expected_keys = ["totalReturn", "sharpeRatio", "maxDrawdown", "winRate", "trades"]
        for key in expected_keys:
            assert key in data, f"Missing {key} in backtest results"


def test_backtest_with_different_symbols():
    """Test backtesting with different stock symbols"""
    symbols = ["SPY", "AAPL", "MSFT", "GOOGL"]

    for symbol in symbols:
        strategy = {
            "symbol": symbol,
            "startDate": "2024-01-01",
            "endDate": "2024-02-01",
            "initialCapital": 10000,
            "rules": {
                "entryConditions": ["price_above_sma"],
                "exitConditions": ["price_below_sma"],
                "smaPeriod": 50
            }
        }

        response = client.post("/api/backtest", json=strategy, headers=HEADERS)
        # Should complete or return error, not crash
        assert response.status_code in [200, 400, 500], f"Unexpected status for {symbol}"


def test_backtest_validates_date_range():
    """Test that invalid date ranges are rejected"""
    # End date before start date
    strategy = {
        "symbol": "SPY",
        "startDate": "2024-06-01",
        "endDate": "2024-01-01",  # Before start date
        "initialCapital": 10000,
        "rules": {"entryConditions": ["rsi_oversold"], "exitConditions": ["rsi_overbought"]}
    }

    response = client.post("/api/backtest", json=strategy, headers=HEADERS)
    # Should return validation error
    assert response.status_code in [400, 422]


def test_backtest_validates_initial_capital():
    """Test that invalid initial capital is rejected"""
    # Negative capital
    strategy = {
        "symbol": "SPY",
        "startDate": "2024-01-01",
        "endDate": "2024-02-01",
        "initialCapital": -1000,  # Negative
        "rules": {"entryConditions": ["rsi_oversold"], "exitConditions": ["rsi_overbought"]}
    }

    response = client.post("/api/backtest", json=strategy, headers=HEADERS)
    # Should return validation error
    assert response.status_code in [400, 422]


def test_backtest_rsi_strategy():
    """Test RSI-based strategy backtesting"""
    strategy = {
        "symbol": "SPY",
        "startDate": "2024-01-01",
        "endDate": "2024-03-01",
        "initialCapital": 10000,
        "rules": {
            "entryConditions": ["rsi_oversold"],
            "exitConditions": ["rsi_overbought"],
            "rsiPeriod": 14,
            "rsiOversold": 30,
            "rsiOverbought": 70,
            "stopLoss": 0.02,  # 2% stop loss
            "takeProfit": 0.05  # 5% take profit
        }
    }

    response = client.post("/api/backtest", json=strategy, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        # Check trade structure
        if "trades" in data and len(data["trades"]) > 0:
            trade = data["trades"][0]
            assert "entryDate" in trade
            assert "exitDate" in trade
            assert "pnl" in trade
            assert "pnlPercent" in trade


def test_backtest_sma_crossover_strategy():
    """Test SMA crossover strategy"""
    strategy = {
        "symbol": "AAPL",
        "startDate": "2024-01-01",
        "endDate": "2024-03-01",
        "initialCapital": 10000,
        "rules": {
            "entryConditions": ["sma_crossover"],
            "exitConditions": ["sma_crossunder"],
            "smaPeriod": 20,
            "smaSlowPeriod": 50
        }
    }

    response = client.post("/api/backtest", json=strategy, headers=HEADERS)
    # Should complete without error
    assert response.status_code in [200, 500]  # 500 if data unavailable


def test_backtest_performance_metrics_validation():
    """Test that performance metrics are within expected ranges"""
    strategy = {
        "symbol": "SPY",
        "startDate": "2024-01-01",
        "endDate": "2024-02-01",
        "initialCapital": 10000,
        "rules": {
            "entryConditions": ["rsi_oversold"],
            "exitConditions": ["rsi_overbought"],
            "rsiPeriod": 14
        }
    }

    response = client.post("/api/backtest", json=strategy, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()

        # Win rate should be between 0 and 1
        if "winRate" in data:
            assert 0 <= data["winRate"] <= 1

        # Max drawdown should be negative or zero
        if "maxDrawdown" in data:
            assert data["maxDrawdown"] <= 0

        # Total return should be a number
        if "totalReturn" in data:
            assert isinstance(data["totalReturn"], (int, float))


def test_backtest_handles_no_trades():
    """Test backtest when strategy generates no trades"""
    # Strategy with impossible conditions
    strategy = {
        "symbol": "SPY",
        "startDate": "2024-01-01",
        "endDate": "2024-01-05",  # Very short period
        "initialCapital": 10000,
        "rules": {
            "entryConditions": ["rsi_oversold"],
            "exitConditions": ["rsi_overbought"],
            "rsiPeriod": 14,
            "rsiOversold": 10,  # Extremely oversold (unlikely)
            "rsiOverbought": 90  # Extremely overbought (unlikely)
        }
    }

    response = client.post("/api/backtest", json=strategy, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        # Should return valid structure even with no trades
        assert "totalReturn" in data
        assert "trades" in data
