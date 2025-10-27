"""
Unit tests for Orders Router (orders.py)

Tests order template endpoints with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock, patch
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
        return {"Authorization": "Bearer test-token-12345", "X-CSRF-Token": "test-csrf-token"}

    def test_trading_execute_dry_run(self, mock_user, auth_headers, monkeypatch):
        """Test trading execute in dry run mode"""
        monkeypatch.setattr("app.routers.orders.get_current_user_unified", lambda x: mock_user)
        monkeypatch.setattr("app.routers.orders.check_and_store", lambda x: True)
        monkeypatch.setattr("app.routers.orders.is_killed", lambda: False)

        order_data = {
            "dryRun": True,
            "requestId": "test-request-12345",
            "orders": [
                {
                    "symbol": "AAPL",
                    "qty": 10,
                    "side": "buy",
                    "type": "market",
                }
            ],
        }

        response = client.post("/api/trading/execute", json=order_data, headers=auth_headers)

        assert response.status_code in [200, 201]

    def test_trading_execute_unauthorized(self):
        """Test trading execute without authentication"""
        order_data = {
            "dryRun": True,
            "requestId": "test-request-12345",
            "orders": [{"symbol": "AAPL", "qty": 10, "side": "buy", "type": "market"}],
        }

        response = client.post("/api/trading/execute", json=order_data)
        assert response.status_code in [401, 403]

    def test_order_templates_list_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful order templates list"""
        monkeypatch.setattr("app.routers.orders.get_current_user_unified", lambda x: mock_user)

        mock_db = Mock()
        mock_query = Mock()
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value = mock_query
        monkeypatch.setattr("app.routers.orders.get_db", lambda: mock_db)

        response = client.get("/api/order-templates", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_order_template_get_by_id_not_found(self, mock_user, auth_headers, monkeypatch):
        """Test order template retrieval by ID when not found"""
        monkeypatch.setattr("app.routers.orders.get_current_user_unified", lambda x: mock_user)

        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        monkeypatch.setattr("app.routers.orders.get_db", lambda: mock_db)

        response = client.get("/api/order-templates/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_order_template_delete_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful order template deletion"""
        monkeypatch.setattr("app.routers.orders.get_current_user_unified", lambda x: mock_user)

        mock_template = Mock()
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_template
        mock_db.query.return_value = mock_query
        monkeypatch.setattr("app.routers.orders.get_db", lambda: mock_db)

        response = client.delete("/api/order-templates/1", headers=auth_headers)

        assert response.status_code in [200, 204]

    def test_trading_execute_validation_error(self, auth_headers):
        """Test trading execute with invalid data"""
        invalid_order = {
            "dryRun": True,
            "requestId": "abc",  # Too short
            "orders": [],  # Empty list
        }

        response = client.post("/api/trading/execute", json=invalid_order, headers=auth_headers)

        assert response.status_code == 422
