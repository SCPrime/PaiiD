"""
Unit tests for Analytics Router (analytics.py)

Tests all 3 endpoints in the analytics router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import User


client = TestClient(app, raise_server_exceptions=False)


class TestAnalytics:
    """Test suite for analytics endpoints"""

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return User(id=1, email="test@example.com", username="test_user", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {"Authorization": "Bearer test-token-12345"}

    # ===========================================
    # TEST: GET /portfolio/summary
    # ===========================================

    def test_get_portfolio_summary_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful portfolio summary retrieval"""
        monkeypatch.setattr("app.routers.analytics.get_current_user_unified", lambda: mock_user)

        # Mock Tradier client
        mock_client = Mock()
        mock_client.get_account.return_value = {
            "portfolio_value": 100000.0,
            "cash": 50000.0,
            "buying_power": 75000.0,
        }
        mock_client.get_positions.return_value = [
            {
                "symbol": "AAPL",
                "qty": 10,
                "market_value": 1750.0,
                "unrealized_pl": 100.0,
                "unrealized_plpc": 0.06,
                "change_today": 2.5,
            },
            {
                "symbol": "MSFT",
                "qty": 5,
                "market_value": 1900.0,
                "unrealized_pl": -50.0,
                "unrealized_plpc": -0.03,
                "change_today": -1.2,
            },
        ]
        monkeypatch.setattr("app.routers.analytics.get_tradier_client", lambda: mock_client)

        response = client.get("/api/portfolio/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_value" in data
        assert "cash" in data
        assert "total_pl" in data
        assert "num_positions" in data
        assert data["num_positions"] == 2
        assert data["num_winning"] == 1
        assert data["num_losing"] == 1

    def test_get_portfolio_summary_unauthorized(self):
        """Test portfolio summary without authentication"""
        response = client.get("/api/portfolio/summary")
        assert response.status_code in [401, 403]

    def test_get_portfolio_summary_empty_portfolio(self, mock_user, auth_headers, monkeypatch):
        """Test portfolio summary with no positions"""
        monkeypatch.setattr("app.routers.analytics.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_account.return_value = {
            "portfolio_value": 100000.0,
            "cash": 100000.0,
            "buying_power": 100000.0,
        }
        mock_client.get_positions.return_value = []
        monkeypatch.setattr("app.routers.analytics.get_tradier_client", lambda: mock_client)

        response = client.get("/api/portfolio/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["num_positions"] == 0
        assert data["total_pl"] == 0

    # ===========================================
    # TEST: GET /portfolio/history
    # ===========================================

    def test_get_portfolio_history_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful portfolio history retrieval"""
        monkeypatch.setattr("app.routers.analytics.get_current_user_unified", lambda: mock_user)

        # Mock Tradier client
        mock_client = Mock()
        mock_client.get_account.return_value = {"portfolio_value": 100000.0, "cash": 50000.0}
        monkeypatch.setattr("app.routers.analytics.get_tradier_client", lambda: mock_client)

        # Mock equity tracker
        from datetime import datetime

        mock_tracker = Mock()
        mock_tracker.get_history.return_value = [
            {
                "timestamp": datetime.now().isoformat(),
                "equity": 100000.0,
                "cash": 50000.0,
                "positions_value": 50000.0,
            }
            for _ in range(10)
        ]
        monkeypatch.setattr("app.services.equity_tracker.get_equity_tracker", lambda: mock_tracker)

        response = client.get("/api/portfolio/history?period=1M", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "period" in data
        assert data["period"] == "1M"
        assert isinstance(data["data"], list)

    def test_get_portfolio_history_different_periods(self, mock_user, auth_headers, monkeypatch):
        """Test portfolio history with different time periods"""
        monkeypatch.setattr("app.routers.analytics.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_account.return_value = {"portfolio_value": 100000.0, "cash": 50000.0}
        monkeypatch.setattr("app.routers.analytics.get_tradier_client", lambda: mock_client)

        mock_tracker = Mock()
        mock_tracker.get_history.return_value = []
        monkeypatch.setattr("app.services.equity_tracker.get_equity_tracker", lambda: mock_tracker)

        periods = ["1D", "1W", "1M", "3M", "1Y", "ALL"]
        for period in periods:
            response = client.get(f"/api/portfolio/history?period={period}", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["period"] == period

    def test_get_portfolio_history_insufficient_data(self, mock_user, auth_headers, monkeypatch):
        """Test portfolio history with insufficient historical data"""
        monkeypatch.setattr("app.routers.analytics.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_account.return_value = {"portfolio_value": 100000.0, "cash": 50000.0}
        monkeypatch.setattr("app.routers.analytics.get_tradier_client", lambda: mock_client)

        mock_tracker = Mock()
        mock_tracker.get_history.return_value = []  # No historical data
        monkeypatch.setattr("app.services.equity_tracker.get_equity_tracker", lambda: mock_tracker)

        response = client.get("/api/portfolio/history?period=1M", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["is_simulated"] is True

    # ===========================================
    # TEST: GET /analytics/performance
    # ===========================================

    def test_get_performance_metrics_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful performance metrics retrieval"""
        monkeypatch.setattr("app.routers.analytics.get_current_user_unified", lambda: mock_user)

        # Mock Tradier client
        mock_client = Mock()
        mock_client.get_account.return_value = {"portfolio_value": 105000.0}
        mock_client.get_positions.return_value = [
            {
                "symbol": "AAPL",
                "unrealized_pl": 500.0,
                "cost_basis": 10000.0,
            },
            {
                "symbol": "MSFT",
                "unrealized_pl": -200.0,
                "cost_basis": 8000.0,
            },
        ]
        mock_client.get_orders.return_value = []
        monkeypatch.setattr("app.routers.analytics.get_tradier_client", lambda: mock_client)

        # Mock equity tracker
        from datetime import datetime

        mock_tracker = Mock()
        mock_tracker.get_history.return_value = [
            {"equity": 100000.0 + i * 100, "timestamp": datetime.now().isoformat()}
            for i in range(50)
        ]
        monkeypatch.setattr("app.services.equity_tracker.get_equity_tracker", lambda: mock_tracker)

        response = client.get("/api/analytics/performance?period=1M", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_return" in data
        assert "sharpe_ratio" in data
        assert "max_drawdown" in data
        assert "win_rate" in data
        assert "profit_factor" in data
        assert "num_trades" in data

    def test_get_performance_metrics_different_periods(self, mock_user, auth_headers, monkeypatch):
        """Test performance metrics with different time periods"""
        monkeypatch.setattr("app.routers.analytics.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_account.return_value = {"portfolio_value": 100000.0}
        mock_client.get_positions.return_value = []
        mock_client.get_orders.return_value = []
        monkeypatch.setattr("app.routers.analytics.get_tradier_client", lambda: mock_client)

        mock_tracker = Mock()
        mock_tracker.get_history.return_value = []
        monkeypatch.setattr("app.services.equity_tracker.get_equity_tracker", lambda: mock_tracker)

        periods = ["1D", "1W", "1M", "3M", "1Y"]
        for period in periods:
            response = client.get(f"/api/analytics/performance?period={period}", headers=auth_headers)
            assert response.status_code == 200

    def test_get_performance_metrics_no_trades(self, mock_user, auth_headers, monkeypatch):
        """Test performance metrics with no trades"""
        monkeypatch.setattr("app.routers.analytics.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_account.return_value = {"portfolio_value": 100000.0}
        mock_client.get_positions.return_value = []
        mock_client.get_orders.return_value = []
        monkeypatch.setattr("app.routers.analytics.get_tradier_client", lambda: mock_client)

        mock_tracker = Mock()
        mock_tracker.get_history.return_value = []
        monkeypatch.setattr("app.services.equity_tracker.get_equity_tracker", lambda: mock_tracker)

        response = client.get("/api/analytics/performance", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["num_trades"] == 0
        assert data["win_rate"] == 0
