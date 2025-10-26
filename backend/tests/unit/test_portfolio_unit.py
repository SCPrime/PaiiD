"""
Unit tests for Portfolio Router (portfolio.py)

Tests all 3 endpoints in the portfolio router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import User


client = TestClient(app, raise_server_exceptions=False)


class TestPortfolio:
    """Test suite for portfolio endpoints"""

    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", username="test_user", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token-12345"}

    def test_get_account_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful account retrieval"""
        monkeypatch.setattr("app.routers.portfolio.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_account.return_value = {
            "portfolio_value": 100000.0,
            "cash": 50000.0,
            "buying_power": 75000.0,
        }
        monkeypatch.setattr("app.services.alpaca_client.get_alpaca_client", lambda: mock_client)

        response = client.get("/api/account", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "portfolio_value" in data

    def test_get_account_unauthorized(self):
        """Test account retrieval without authentication"""
        response = client.get("/api/account")
        assert response.status_code in [401, 403]

    def test_get_portfolio_value_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful portfolio value retrieval"""
        monkeypatch.setattr("app.routers.portfolio.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_account.return_value = {"portfolio_value": 105000.0}
        monkeypatch.setattr("app.services.alpaca_client.get_alpaca_client", lambda: mock_client)

        response = client.get("/api/portfolio/value", headers=auth_headers)

        assert response.status_code == 200

    def test_get_portfolio_history_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful portfolio history retrieval"""
        monkeypatch.setattr("app.routers.portfolio.get_current_user_unified", lambda: mock_user)

        mock_tracker = Mock()
        mock_tracker.get_history.return_value = [
            {"timestamp": "2024-01-01", "equity": 100000.0, "cash": 50000.0, "positions_value": 50000.0}
        ]
        monkeypatch.setattr("app.services.equity_tracker.get_equity_tracker", lambda: mock_tracker)

        response = client.get("/api/portfolio/history?period=1M", headers=auth_headers)

        assert response.status_code == 200
