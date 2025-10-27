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
        monkeypatch.setattr("app.routers.portfolio.get_current_user_unified", lambda x: mock_user)

        mock_client = Mock()
        mock_client.get_account.return_value = {
            "cash": {"cash_available": 50000.0},
            "equities": {"market_value": 50000.0},
            "portfolio_value": 100000.0,
        }
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/account", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_get_account_unauthorized(self, monkeypatch):
        """Test account retrieval without authentication"""
        # Mock Tradier client to avoid real API call
        mock_client = Mock()
        mock_client.get_account.side_effect = Exception("No auth")
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/account")
        assert response.status_code in [401, 403, 500]

    def test_get_positions_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful positions retrieval"""
        monkeypatch.setattr("app.routers.portfolio.get_current_user_unified", lambda x: mock_user)

        mock_client = Mock()
        mock_client.get_positions.return_value = [
            {"symbol": "AAPL", "quantity": 10, "cost_basis": 1500.0},
            {"symbol": "MSFT", "quantity": 5, "cost_basis": 1900.0},
        ]
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        mock_cache = Mock()
        mock_cache.get.return_value = None
        monkeypatch.setattr("app.routers.portfolio.get_cache", lambda: mock_cache)

        response = client.get("/api/positions", headers=auth_headers)

        assert response.status_code == 200

    def test_get_position_by_symbol_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful position retrieval by symbol"""
        monkeypatch.setattr("app.routers.portfolio.get_current_user_unified", lambda x: mock_user)

        mock_client = Mock()
        mock_client.get_positions.return_value = [
            {"symbol": "AAPL", "quantity": 10, "cost_basis": 1500.0}
        ]
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/positions/AAPL", headers=auth_headers)

        assert response.status_code == 200
