"""
Unit tests for Orders Router (orders.py)

Tests order template endpoints with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock


class TestOrders:
    """Test suite for orders endpoints"""

    def test_trading_execute_dry_run(self, client, auth_headers, monkeypatch):
        """Test trading execute in dry run mode"""
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

    def test_trading_execute_unauthorized(self, client_no_auth):
        """Test trading execute without authentication"""
        order_data = {
            "dryRun": True,
            "requestId": "test-request-12345",
            "orders": [{"symbol": "AAPL", "qty": 10, "side": "buy", "type": "market"}],
        }

        response = client_no_auth.post("/api/trading/execute", json=order_data)
        assert response.status_code in [401, 403]

    def test_order_templates_list_success(self, client, auth_headers, test_db, monkeypatch):
        """Test successful order templates list"""
        # Use real DB query with empty result
        response = client.get("/api/order-templates", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_order_template_get_by_id_not_found(self, client, auth_headers, test_db):
        """Test order template retrieval by ID when not found"""
        response = client.get("/api/order-templates/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_order_template_delete_success(self, client, auth_headers, test_db):
        """Test successful order template deletion"""
        # First create a template
        from app.models.database import OrderTemplate

        template = OrderTemplate(
            user_id=1,
            name="Test Template",
            symbol="AAPL",
            side="buy",
            qty=10,
            order_type="market",
        )
        test_db.add(template)
        test_db.commit()
        test_db.refresh(template)

        response = client.delete(f"/api/order-templates/{template.id}", headers=auth_headers)

        assert response.status_code in [200, 204]

    def test_trading_execute_validation_error(self, client, auth_headers):
        """Test trading execute with invalid data"""
        invalid_order = {
            "dryRun": True,
            "requestId": "abc",  # Too short
            "orders": [],  # Empty list
        }

        response = client.post("/api/trading/execute", json=invalid_order, headers=auth_headers)

        assert response.status_code == 422
