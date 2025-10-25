"""
Integration tests for Trading API
Test ID: TRADE-001
Priority: CRITICAL
"""

import pytest
from backend.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def authenticated_client(client):
    """Authenticated test client fixture"""
    # Login first
    response = client.post(
        "/api/auth/login", json={"email": "trader@test.com", "password": "TestP@ss123"}
    )
    token = response.json()["access_token"]

    # Add token to headers
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


class TestTradingIntegration:
    """Integration tests for trading flow"""

    def test_order_validation_flow(self, authenticated_client):
        """Test order validation before execution"""
        response = authenticated_client.post(
            "/api/trading/validate",
            json={
                "symbol": "AAPL",
                "quantity": 10,
                "side": "buy",
                "order_type": "market",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "estimated_cost" in data
        assert "buying_power" in data
        assert data["buying_power"] >= data["estimated_cost"]

    def test_market_buy_execution(self, authenticated_client):
        """Test market buy order execution"""
        response = authenticated_client.post(
            "/api/trading/execute",
            json={
                "symbol": "AAPL",
                "quantity": 10,
                "side": "buy",
                "order_type": "market",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "order_id" in data
        assert data["status"] in ["filled", "pending"]
        assert data["symbol"] == "AAPL"
        assert data["quantity"] == 10
        assert data["side"] == "buy"

    def test_limit_order_execution(self, authenticated_client):
        """Test limit order execution"""
        response = authenticated_client.post(
            "/api/trading/execute",
            json={
                "symbol": "MSFT",
                "quantity": 5,
                "side": "buy",
                "order_type": "limit",
                "limit_price": 300.00,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["order_type"] == "limit"
        assert float(data["limit_price"]) == 300.00

    def test_sell_order_execution(self, authenticated_client):
        """Test sell order execution"""
        # First ensure we have a position
        authenticated_client.post(
            "/api/trading/execute",
            json={
                "symbol": "AAPL",
                "quantity": 10,
                "side": "buy",
                "order_type": "market",
            },
        )

        # Now sell
        response = authenticated_client.post(
            "/api/trading/execute",
            json={
                "symbol": "AAPL",
                "quantity": 5,
                "side": "sell",
                "order_type": "market",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["side"] == "sell"
        assert data["quantity"] == 5

    def test_insufficient_balance_validation(self, authenticated_client):
        """Test validation rejects orders with insufficient balance"""
        response = authenticated_client.post(
            "/api/trading/validate",
            json={
                "symbol": "AAPL",
                "quantity": 100000,  # Unrealistic quantity
                "side": "buy",
                "order_type": "market",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "insufficient" in data["detail"].lower()

    def test_invalid_symbol_validation(self, authenticated_client):
        """Test validation rejects invalid symbols"""
        response = authenticated_client.post(
            "/api/trading/validate",
            json={
                "symbol": "INVALIDSTOCK",
                "quantity": 10,
                "side": "buy",
                "order_type": "market",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert (
            "invalid" in data["detail"].lower() or "not found" in data["detail"].lower()
        )

    def test_negative_quantity_validation(self, authenticated_client):
        """Test validation rejects negative quantities"""
        response = authenticated_client.post(
            "/api/trading/validate",
            json={
                "symbol": "AAPL",
                "quantity": -10,
                "side": "buy",
                "order_type": "market",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_order_cancellation(self, authenticated_client):
        """Test order cancellation"""
        # Create limit order
        create_response = authenticated_client.post(
            "/api/trading/execute",
            json={
                "symbol": "MSFT",
                "quantity": 5,
                "side": "buy",
                "order_type": "limit",
                "limit_price": 200.00,
            },
        )

        order_id = create_response.json()["order_id"]

        # Cancel order
        response = authenticated_client.post(f"/api/trading/cancel/{order_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_trade_history_retrieval(self, authenticated_client):
        """Test retrieving trade history"""
        response = authenticated_client.get("/api/trading/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            trade = data[0]
            assert "symbol" in trade
            assert "quantity" in trade
            assert "side" in trade
            assert "executed_at" in trade
            assert "price" in trade

    def test_concurrent_order_execution(self, authenticated_client):
        """Test handling of concurrent orders"""
        import concurrent.futures

        def place_order():
            return authenticated_client.post(
                "/api/trading/execute",
                json={
                    "symbol": "AAPL",
                    "quantity": 1,
                    "side": "buy",
                    "order_type": "market",
                },
            )

        # Submit 5 orders concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(place_order) for _ in range(5)]
            responses = [f.result() for f in futures]

        # All should succeed or fail gracefully
        for response in responses:
            assert response.status_code in [
                201,
                400,
                429,
            ]  # Success, validation error, or rate limit

    def test_portfolio_update_after_trade(self, authenticated_client):
        """Test portfolio updates after trade execution"""
        # Get initial portfolio
        portfolio_before = authenticated_client.get("/api/portfolio/me").json()
        initial_value = portfolio_before["total_value"]

        # Execute trade
        authenticated_client.post(
            "/api/trading/execute",
            json={
                "symbol": "AAPL",
                "quantity": 1,
                "side": "buy",
                "order_type": "market",
            },
        )

        # Get updated portfolio
        portfolio_after = authenticated_client.get("/api/portfolio/me").json()

        # Portfolio should have changed
        assert portfolio_after["total_value"] != initial_value
        assert len(portfolio_after["positions"]) >= len(portfolio_before["positions"])


class TestTradingPerformance:
    """Performance tests for trading endpoints"""

    def test_order_validation_response_time(self, authenticated_client, benchmark):
        """Test order validation is under 500ms"""

        def validate_order():
            return authenticated_client.post(
                "/api/trading/validate",
                json={
                    "symbol": "AAPL",
                    "quantity": 10,
                    "side": "buy",
                    "order_type": "market",
                },
            )

        result = benchmark(validate_order)
        assert result.status_code == 200
        assert benchmark.stats["mean"] < 0.5  # 500ms

    def test_order_execution_response_time(self, authenticated_client, benchmark):
        """Test order execution is under 2 seconds"""

        def execute_order():
            return authenticated_client.post(
                "/api/trading/execute",
                json={
                    "symbol": "AAPL",
                    "quantity": 1,
                    "side": "buy",
                    "order_type": "market",
                },
            )

        result = benchmark(execute_order)
        assert result.status_code in [201, 400]
        assert benchmark.stats["mean"] < 2.0  # 2 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
