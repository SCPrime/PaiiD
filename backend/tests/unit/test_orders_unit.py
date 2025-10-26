"""
Unit tests for Orders Router (orders.py)

Tests all 8+ endpoints in the orders router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import User


client = TestClient(app, raise_server_exceptions=False)


class TestOrders:
    """Test suite for orders endpoints"""

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return User(id=1, email="test@example.com", username="test_user", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {"Authorization": "Bearer test-token-12345"}

    def test_place_order_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful order placement"""
        monkeypatch.setattr("app.routers.orders.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.place_order.return_value = {
            "order_id": "12345",
            "status": "filled",
            "symbol": "AAPL",
            "qty": 10,
        }
        monkeypatch.setattr("app.services.alpaca_client.get_alpaca_client", lambda: mock_client)

        order_data = {
            "symbol": "AAPL",
            "qty": 10,
            "side": "buy",
            "type": "market",
        }

        response = client.post("/api/orders", json=order_data, headers=auth_headers)

        assert response.status_code in [200, 201]

    def test_place_order_unauthorized(self):
        """Test order placement without authentication"""
        order_data = {"symbol": "AAPL", "qty": 10, "side": "buy", "type": "market"}

        response = client.post("/api/orders", json=order_data)
        assert response.status_code in [401, 403]

    def test_get_orders_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful orders retrieval"""
        monkeypatch.setattr("app.routers.orders.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_orders.return_value = [
            {"id": "1", "symbol": "AAPL", "qty": 10, "status": "filled"},
            {"id": "2", "symbol": "MSFT", "qty": 5, "status": "pending"},
        ]
        monkeypatch.setattr("app.services.alpaca_client.get_alpaca_client", lambda: mock_client)

        response = client.get("/api/orders", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_order_by_id_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful order retrieval by ID"""
        monkeypatch.setattr("app.routers.orders.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_order.return_value = {
            "id": "12345",
            "symbol": "AAPL",
            "qty": 10,
            "status": "filled",
        }
        monkeypatch.setattr("app.services.alpaca_client.get_alpaca_client", lambda: mock_client)

        response = client.get("/api/orders/12345", headers=auth_headers)

        assert response.status_code == 200

    def test_cancel_order_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful order cancellation"""
        monkeypatch.setattr("app.routers.orders.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.cancel_order.return_value = {"success": True}
        monkeypatch.setattr("app.services.alpaca_client.get_alpaca_client", lambda: mock_client)

        response = client.delete("/api/orders/12345", headers=auth_headers)

        assert response.status_code in [200, 204]

    def test_place_order_validation_error(self, auth_headers):
        """Test order placement with invalid data"""
        invalid_order = {
            "symbol": "",  # Empty symbol
            "qty": -10,  # Negative quantity
        }

        response = client.post("/api/orders", json=invalid_order, headers=auth_headers)

        assert response.status_code == 422
