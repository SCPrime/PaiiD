from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEAD = {"Authorization": "Bearer test-token-12345"}


def test_duplicate_idempotency():
    body = {
        "dryRun": True,
        "requestId": "test-request-12345",
        "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1}],
    }
    r1 = client.post("/api/trading/execute", json=body, headers=HEAD)
    r2 = client.post("/api/trading/execute", json=body, headers=HEAD)
    assert r1.status_code == 200
    assert r2.json().get("duplicate") is True


def test_preview_orders_with_bracket():
    body = {
        "orders": [
            {
                "symbol": "AAPL",
                "side": "buy",
                "qty": 10,
                "type": "limit",
                "limit_price": 150.0,
                "order_class": "bracket",
                "take_profit": {"limit_price": 160.0},
                "stop_loss": {"stop_price": 145.0},
            }
        ]
    }

    response = client.post("/api/orders/preview", json=body, headers=HEAD)
    assert response.status_code == 200
    payload = response.json()

    assert payload["total_notional"] == 1500.0
    assert payload["total_max_profit"] == 100.0
    assert payload["total_max_loss"] == 50.0
    assert payload["orders"][0]["risk_reward_ratio"] == 2.0


def test_create_template_with_advanced_fields():
    body = {
        "name": "SPY Bracket",
        "description": "Bracket template",
        "symbol": "SPY",
        "side": "buy",
        "quantity": 5,
        "order_type": "limit",
        "limit_price": 420.0,
        "order_class": "bracket",
        "take_profit": {"limit_price": 430.0},
        "stop_loss": {"stop_price": 410.0},
        "trail_percent": 1.5,
    }

    response = client.post("/api/order-templates", json=body, headers=HEAD)
    assert response.status_code == 201
    data = response.json()

    assert data["order_class"] == "bracket"
    assert data["take_profit"]["limit_price"] == 430.0
    assert data["stop_loss"]["stop_price"] == 410.0
    assert data["trail_percent"] == 1.5
