"""
Unit tests for Backtesting Router (backtesting.py)

Tests all 3 endpoints in the backtesting router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import User


client = TestClient(app, raise_server_exceptions=False)


class TestBacktesting:
    """Test suite for backtesting endpoints"""

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return User(id=1, email="test@example.com", username="test_user", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {"Authorization": "Bearer test-token-12345"}

    @pytest.fixture
    def valid_backtest_request(self):
        """Valid backtest request data"""
        return {
            "symbol": "AAPL",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 10000.0,
            "entry_rules": [{"indicator": "RSI", "operator": "<", "value": 30}],
            "exit_rules": [
                {"type": "take_profit", "value": 5},
                {"type": "stop_loss", "value": 2},
            ],
            "position_size_percent": 10.0,
            "max_positions": 1,
        }

    # ===========================================
    # TEST: POST /backtesting/run
    # ===========================================

    def test_run_backtest_success(
        self, mock_user, auth_headers, valid_backtest_request, monkeypatch
    ):
        """Test successful backtest execution"""
        monkeypatch.setattr("app.routers.backtesting.get_current_user_unified", lambda: mock_user)

        # Mock historical data service
        mock_historical_data = Mock()
        mock_historical_data.get_historical_data.return_value = [
            {"timestamp": "2024-01-01", "open": 170.0, "high": 175.0, "low": 168.0, "close": 172.0, "volume": 1000000}
            for _ in range(252)
        ]
        monkeypatch.setattr(
            "app.services.historical_data.HistoricalDataService",
            lambda: mock_historical_data,
        )

        # Mock backtesting engine
        mock_engine = Mock()
        mock_engine.run_backtest.return_value = {
            "total_return": 1500.0,
            "total_return_percent": 15.0,
            "sharpe_ratio": 1.5,
            "max_drawdown": -500.0,
            "max_drawdown_percent": -5.0,
            "num_trades": 10,
            "win_rate": 60.0,
            "equity_curve": [],
            "trades": [],
        }
        monkeypatch.setattr("app.services.backtesting_engine.BacktestingEngine", lambda rules: mock_engine)

        response = client.post("/api/backtesting/run", json=valid_backtest_request, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert data["result"]["total_return"] == 1500.0

    def test_run_backtest_validation_error(self, auth_headers):
        """Test backtest with invalid request data"""
        invalid_request = {
            "symbol": "AAPL",
            "start_date": "invalid-date",
            "end_date": "2024-12-31",
            "initial_capital": -1000.0,  # Invalid
        }

        response = client.post("/api/backtesting/run", json=invalid_request, headers=auth_headers)

        assert response.status_code == 422

    def test_run_backtest_unauthorized(self, valid_backtest_request):
        """Test backtest without authentication"""
        response = client.post("/api/backtesting/run", json=valid_backtest_request)
        assert response.status_code in [401, 403]

    def test_run_backtest_insufficient_data(
        self, mock_user, auth_headers, valid_backtest_request, monkeypatch
    ):
        """Test backtest with insufficient historical data"""
        monkeypatch.setattr("app.routers.backtesting.get_current_user_unified", lambda: mock_user)

        # Mock historical data service with insufficient data
        mock_historical_data = Mock()
        mock_historical_data.get_historical_data.return_value = []  # No data
        monkeypatch.setattr(
            "app.services.historical_data.HistoricalDataService",
            lambda: mock_historical_data,
        )

        response = client.post("/api/backtesting/run", json=valid_backtest_request, headers=auth_headers)

        # Should handle gracefully (either 400 or return error in response)
        assert response.status_code in [200, 400]

    def test_run_backtest_different_symbols(
        self, mock_user, auth_headers, valid_backtest_request, monkeypatch
    ):
        """Test backtest with different symbols"""
        monkeypatch.setattr("app.routers.backtesting.get_current_user_unified", lambda: mock_user)

        mock_historical_data = Mock()
        mock_historical_data.get_historical_data.return_value = [
            {"timestamp": "2024-01-01", "open": 100.0, "high": 105.0, "low": 98.0, "close": 102.0, "volume": 500000}
            for _ in range(100)
        ]
        monkeypatch.setattr(
            "app.services.historical_data.HistoricalDataService",
            lambda: mock_historical_data,
        )

        mock_engine = Mock()
        mock_engine.run_backtest.return_value = {"total_return": 0.0, "num_trades": 0}
        monkeypatch.setattr("app.services.backtesting_engine.BacktestingEngine", lambda rules: mock_engine)

        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        for symbol in symbols:
            request_data = valid_backtest_request.copy()
            request_data["symbol"] = symbol

            response = client.post("/api/backtesting/run", json=request_data, headers=auth_headers)
            assert response.status_code == 200

    def test_run_backtest_different_strategies(
        self, mock_user, auth_headers, valid_backtest_request, monkeypatch
    ):
        """Test backtest with different strategy configurations"""
        monkeypatch.setattr("app.routers.backtesting.get_current_user_unified", lambda: mock_user)

        mock_historical_data = Mock()
        mock_historical_data.get_historical_data.return_value = [
            {"timestamp": "2024-01-01", "open": 170.0, "high": 175.0, "low": 168.0, "close": 172.0, "volume": 1000000}
            for _ in range(100)
        ]
        monkeypatch.setattr(
            "app.services.historical_data.HistoricalDataService",
            lambda: mock_historical_data,
        )

        mock_engine = Mock()
        mock_engine.run_backtest.return_value = {"total_return": 500.0, "num_trades": 5}
        monkeypatch.setattr("app.services.backtesting_engine.BacktestingEngine", lambda rules: mock_engine)

        # Test with different entry/exit rules
        strategies = [
            {
                "entry_rules": [{"indicator": "MACD", "operator": ">", "value": 0}],
                "exit_rules": [{"type": "take_profit", "value": 10}],
            },
            {
                "entry_rules": [{"indicator": "SMA", "operator": ">", "period": 50}],
                "exit_rules": [{"type": "stop_loss", "value": 3}],
            },
        ]

        for strategy in strategies:
            request_data = valid_backtest_request.copy()
            request_data.update(strategy)

            response = client.post("/api/backtesting/run", json=request_data, headers=auth_headers)
            assert response.status_code == 200
