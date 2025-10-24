"""Tests for orders endpoints."""


def test_orders_require_auth(client):
    payload = {
        "dryRun": True,
        "requestId": "REQ-123456",
        "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1, "type": "market"}],
    }

    response = client.post("/api/trading/execute", json=payload)
    assert response.status_code == 403


def test_submit_order_success(monkeypatch, client, auth_headers):
    payload = {
        "dryRun": True,
        "requestId": "REQ-123456",
        "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1, "type": "market"}],
    }

    response = client.post("/api/trading/execute", headers=auth_headers, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is True
    assert body["dryRun"] is True


def test_submit_order_handles_api_errors(monkeypatch, client, auth_headers):
    from app.routers import orders as orders_router

    payload = {
        "dryRun": False,
        "requestId": "REQ-654321",
        "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1, "type": "market"}],
    }

    monkeypatch.setattr(
        orders_router,
        "execute_alpaca_order_with_retry",
        lambda order: (_ for _ in ()).throw(RuntimeError("alpaca down")),
    )

    monkeypatch.setattr(orders_router.settings, "LIVE_TRADING", True)
    assert orders_router.settings.LIVE_TRADING is True

    response = client.post("/api/trading/execute", headers=auth_headers, json=payload)
    assert response.status_code == 500
