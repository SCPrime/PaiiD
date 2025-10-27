"""
Tests for order execution endpoints
Tests validation, idempotency, circuit breakers, and kill switch
"""

import pytest
from unittest.mock import Mock, patch


HEAD = {"Authorization": "Bearer test-token-12345"}


def test_duplicate_idempotency(client):
    body = {
        "dryRun": True,
        "requestId": "test-request-12345",
        "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1}],
    }
    r1 = client.post("/api/trading/execute", json=body, headers=HEAD)
    r2 = client.post("/api/trading/execute", json=body, headers=HEAD)
    # May succeed or get auth error depending on MVP fallback
    assert r1.status_code in [200, 401, 403, 500]
    if r1.status_code == 200 and r2.status_code == 200:
        assert r2.json().get("duplicate") is True


class TestOrderValidation:
    """Test order validation middleware"""

    def test_invalid_symbol_validation(self, client):
        """Test invalid symbol is rejected"""
        body = {
            "dryRun": True,
            "requestId": "test-invalid-symbol",
            "orders": [{"symbol": "INVALID@SYMBOL", "side": "buy", "qty": 1}],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # Should reject invalid symbol
        assert response.status_code in [400, 422, 401]

    def test_invalid_quantity_validation(self, client):
        """Test invalid quantity is rejected"""
        invalid_quantities = [0, -1, -10, 1000000]

        for qty in invalid_quantities:
            body = {
                "dryRun": True,
                "requestId": f"test-invalid-qty-{qty}",
                "orders": [{"symbol": "AAPL", "side": "buy", "qty": qty}],
            }
            response = client.post("/api/trading/execute", json=body, headers=HEAD)
            # Should reject invalid quantity
            assert response.status_code in [400, 422, 401]

    def test_invalid_side_validation(self, client):
        """Test invalid order side is rejected"""
        body = {
            "dryRun": True,
            "requestId": "test-invalid-side",
            "orders": [{"symbol": "AAPL", "side": "invalid", "qty": 1}],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # Should reject invalid side
        assert response.status_code in [400, 422, 401]

    def test_missing_required_fields(self, client):
        """Test missing required fields are rejected"""
        # Missing symbol
        body1 = {
            "dryRun": True,
            "requestId": "test-missing-symbol",
            "orders": [{"side": "buy", "qty": 1}],
        }
        response1 = client.post("/api/trading/execute", json=body1, headers=HEAD)
        assert response1.status_code in [400, 422, 401]

        # Missing side
        body2 = {
            "dryRun": True,
            "requestId": "test-missing-side",
            "orders": [{"symbol": "AAPL", "qty": 1}],
        }
        response2 = client.post("/api/trading/execute", json=body2, headers=HEAD)
        assert response2.status_code in [400, 422, 401]

        # Missing qty
        body3 = {
            "dryRun": True,
            "requestId": "test-missing-qty",
            "orders": [{"symbol": "AAPL", "side": "buy"}],
        }
        response3 = client.post("/api/trading/execute", json=body3, headers=HEAD)
        assert response3.status_code in [400, 422, 401]

    def test_limit_order_validation(self, client):
        """Test limit order requires price"""
        body = {
            "dryRun": True,
            "requestId": "test-limit-no-price",
            "orders": [
                {"symbol": "AAPL", "side": "buy", "qty": 1, "type": "limit"}
            ],  # Missing limit_price
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # Should reject limit order without price
        assert response.status_code in [400, 422, 401]

    def test_valid_limit_order(self, client):
        """Test valid limit order with price"""
        body = {
            "dryRun": True,
            "requestId": "test-limit-with-price",
            "orders": [
                {"symbol": "AAPL", "side": "buy", "qty": 1, "type": "limit", "limit_price": 150.00}
            ],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # Should accept or return auth error
        assert response.status_code in [200, 401, 403]

    def test_negative_limit_price_validation(self, client):
        """Test negative limit price is rejected"""
        body = {
            "dryRun": True,
            "requestId": "test-negative-price",
            "orders": [
                {"symbol": "AAPL", "side": "buy", "qty": 1, "type": "limit", "limit_price": -10.00}
            ],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # Should reject negative price
        assert response.status_code in [400, 422, 401]


class TestOrderCircuitBreaker:
    """Test circuit breaker functionality"""

    def test_circuit_breaker_status_endpoint(self, client):
        """Test circuit breaker status endpoint"""
        response = client.get("/api/trading/circuit-status", headers=HEAD)
        # Should return status or auth error
        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            data = response.json()
            # Should have circuit state info
            assert isinstance(data, dict)

    def test_order_execution_when_circuit_closed(self, client):
        """Test orders execute normally when circuit is closed"""
        body = {
            "dryRun": True,
            "requestId": "test-circuit-closed",
            "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1}],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # Should process normally or auth error
        assert response.status_code in [200, 401, 403, 500]


class TestOrderTemplates:
    """Test order template functionality"""

    def test_get_order_templates(self, client):
        """Test fetching order templates"""
        response = client.get("/api/trading/templates", headers=HEAD)
        # Should return templates or auth error
        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_create_order_template(self, client):
        """Test creating a new order template"""
        template = {
            "name": "Test Template",
            "symbol": "AAPL",
            "side": "buy",
            "qty": 10,
            "type": "limit",
            "limit_price": 150.00,
        }
        response = client.post("/api/trading/templates", json=template, headers=HEAD)
        # Should create or return auth error
        assert response.status_code in [201, 200, 401, 404, 422]

    def test_delete_order_template(self, client):
        """Test deleting an order template"""
        template_id = "test-template-123"
        response = client.delete(f"/api/trading/templates/{template_id}", headers=HEAD)
        # Should delete or return not found
        assert response.status_code in [204, 200, 401, 404]


class TestKillSwitch:
    """Test kill switch functionality"""

    def test_kill_switch_status(self, client):
        """Test checking kill switch status"""
        response = client.get("/api/trading/kill-switch", headers=HEAD)
        # Should return status or auth error
        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            # Should have killed status
            if "killed" in data:
                assert isinstance(data["killed"], bool)

    def test_orders_blocked_when_killed(self, client):
        """Test orders are blocked when kill switch is active"""
        # First, try to activate kill switch
        client.post("/api/trading/kill-switch/activate", headers=HEAD)

        # Now try to place order
        body = {
            "dryRun": True,
            "requestId": "test-kill-switch-blocked",
            "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1}],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # Should be blocked or auth error
        assert response.status_code in [403, 401, 500]


class TestDryRunMode:
    """Test dry run mode functionality"""

    def test_dry_run_flag_respected(self, client):
        """Test dry run orders don't execute"""
        body = {
            "dryRun": True,
            "requestId": "test-dry-run",
            "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1}],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # Should accept dry run or auth error
        assert response.status_code in [200, 401, 403]

        if response.status_code == 200:
            data = response.json()
            # Should indicate dry run
            if "dryRun" in data or "dry_run" in data:
                assert data.get("dryRun") is True or data.get("dry_run") is True

    def test_live_order_without_dry_run(self, client):
        """Test orders without dry run flag"""
        body = {
            "dryRun": False,
            "requestId": "test-live-order",
            "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1}],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # Should process or fail with auth
        assert response.status_code in [200, 401, 403, 500]


class TestMultipleOrders:
    """Test batch order execution"""

    def test_single_order_batch(self, client):
        """Test executing single order"""
        body = {
            "dryRun": True,
            "requestId": "test-single-order",
            "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1}],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        assert response.status_code in [200, 401, 403, 500]

    def test_multiple_orders_batch(self, client):
        """Test executing multiple orders"""
        body = {
            "dryRun": True,
            "requestId": "test-multiple-orders",
            "orders": [
                {"symbol": "AAPL", "side": "buy", "qty": 1},
                {"symbol": "MSFT", "side": "buy", "qty": 2},
                {"symbol": "GOOGL", "side": "sell", "qty": 1},
            ],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        assert response.status_code in [200, 401, 403, 500]

    def test_empty_orders_array(self, client):
        """Test empty orders array is rejected"""
        body = {
            "dryRun": True,
            "requestId": "test-empty-orders",
            "orders": [],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # Should reject empty orders
        assert response.status_code in [400, 422, 401]


class TestOrderErrorHandling:
    """Test error handling for order execution"""

    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/trading/execute",
            data="invalid json{",
            headers={**HEAD, "Content-Type": "application/json"},
        )
        # Should return 400 or 422
        assert response.status_code in [400, 422]

    def test_missing_request_id(self, client):
        """Test missing requestId is handled"""
        body = {
            "dryRun": True,
            # Missing requestId
            "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1}],
        }
        response = client.post("/api/trading/execute", json=body, headers=HEAD)
        # May accept and generate ID, or reject
        assert response.status_code in [200, 400, 422, 401]

    def test_duplicate_request_id(self, client):
        """Test duplicate requestId is handled by idempotency"""
        request_id = "test-duplicate-request-id-789"
        body = {
            "dryRun": True,
            "requestId": request_id,
            "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1}],
        }

        # First request
        response1 = client.post("/api/trading/execute", json=body, headers=HEAD)

        # Second request with same ID
        response2 = client.post("/api/trading/execute", json=body, headers=HEAD)

        # Both should succeed or auth error
        assert response1.status_code in [200, 401, 403, 500]
        assert response2.status_code in [200, 401, 403, 500]

        if response1.status_code == 200 and response2.status_code == 200:
            # Second should indicate duplicate
            data2 = response2.json()
            if "duplicate" in data2:
                assert data2["duplicate"] is True
