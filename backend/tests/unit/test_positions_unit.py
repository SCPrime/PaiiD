"""
Unit tests for Positions Router (positions.py)

Tests all 3 endpoints in the positions router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import User


client = TestClient(app, raise_server_exceptions=False)


class TestPositions:
    """Test suite for positions endpoints"""

    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", username="test_user", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token-12345"}

    def test_get_positions_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful positions retrieval"""
        monkeypatch.setattr("app.routers.positions.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.list_positions.return_value = [
            {"symbol": "AAPL", "qty": 10, "market_value": 1750.0},
            {"symbol": "MSFT", "qty": 5, "market_value": 1900.0},
        ]
        monkeypatch.setattr("app.services.alpaca_client.get_alpaca_client", lambda: mock_client)

        response = client.get("/api/positions", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_positions_unauthorized(self):
        """Test positions retrieval without authentication"""
        response = client.get("/api/positions")
        assert response.status_code in [401, 403]

    def test_get_position_by_symbol_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful position retrieval by symbol"""
        monkeypatch.setattr("app.routers.positions.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_position.return_value = {"symbol": "AAPL", "qty": 10, "market_value": 1750.0}
        monkeypatch.setattr("app.services.alpaca_client.get_alpaca_client", lambda: mock_client)

        response = client.get("/api/positions/AAPL", headers=auth_headers)

        assert response.status_code == 200

    def test_close_position_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful position closure"""
        monkeypatch.setattr("app.routers.positions.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.close_position.return_value = {"success": True}
        monkeypatch.setattr("app.services.alpaca_client.get_alpaca_client", lambda: mock_client)

        response = client.delete("/api/positions/AAPL", headers=auth_headers)

        assert response.status_code in [200, 204]
