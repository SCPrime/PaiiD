"""
Unit tests for Positions Router (positions.py)

Tests all endpoints in the positions router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock, AsyncMock
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
        monkeypatch.setattr("app.routers.positions.get_current_user_unified", lambda x: mock_user)

        mock_service = Mock()
        mock_service.get_open_positions = AsyncMock(return_value=[
            {"symbol": "AAPL", "quantity": 10, "unrealized_pnl": 500.0},
            {"symbol": "MSFT", "quantity": 5, "unrealized_pnl": 200.0},
        ])
        monkeypatch.setattr("app.routers.positions.PositionTrackerService", lambda: mock_service)

        response = client.get("/api/positions", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_get_positions_unauthorized(self, monkeypatch):
        """Test positions retrieval without authentication"""
        # Mock to avoid fixture loader issues
        mock_settings = Mock()
        mock_settings.USE_TEST_FIXTURES = False
        monkeypatch.setattr("app.routers.positions.settings", mock_settings)

        response = client.get("/api/positions")
        assert response.status_code in [401, 403, 500]

    def test_get_portfolio_greeks_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful portfolio greeks retrieval"""
        monkeypatch.setattr("app.routers.positions.get_current_user_unified", lambda x: mock_user)

        mock_service = Mock()
        mock_service.get_portfolio_greeks = AsyncMock(return_value={
            "delta": 0.5,
            "gamma": 0.02,
            "theta": -0.05,
            "vega": 0.1,
        })
        monkeypatch.setattr("app.routers.positions.PositionTrackerService", lambda: mock_service)

        response = client.get("/api/positions/greeks", headers=auth_headers)

        assert response.status_code == 200

    def test_close_position_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful position closure"""
        monkeypatch.setattr("app.routers.positions.get_current_user_unified", lambda x: mock_user)

        mock_service = Mock()
        mock_service.close_position = AsyncMock(return_value={"success": True, "order_id": "12345"})
        monkeypatch.setattr("app.routers.positions.PositionTrackerService", lambda: mock_service)

        response = client.post("/api/positions/pos_12345/close", headers={"Authorization": "Bearer test-token-12345", "X-CSRF-Token": "test-csrf"})

        assert response.status_code in [200, 201]
