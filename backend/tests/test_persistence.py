from datetime import datetime


def test_settings_persistence(client, auth_headers):
    payload = {
        "defaultExecutionMode": "autopilot",
        "enableSMSAlerts": False,
        "defaultSlippageBudget": 0.75,
    }

    save_response = client.post("/api/settings", json=payload, headers=auth_headers)
    assert save_response.status_code == 200
    data = save_response.json()
    for key, value in payload.items():
        assert data[key] == value

    fetch_response = client.get("/api/settings", headers=auth_headers)
    assert fetch_response.status_code == 200
    settings = fetch_response.json()
    for key, value in payload.items():
        assert settings[key] == value


def test_order_history_crud(client, auth_headers):
    order_payload = {
        "symbol": "AAPL",
        "side": "buy",
        "qty": 10,
        "type": "limit",
        "limitPrice": 150.5,
        "status": "executed",
        "dryRun": False,
        "timestamp": datetime.utcnow().isoformat(),
        "clientId": "order-test-1",
    }

    create_resp = client.post("/api/orders/history", json=order_payload, headers=auth_headers)
    assert create_resp.status_code == 201

    list_resp = client.get("/api/orders/history", headers=auth_headers)
    assert list_resp.status_code == 200
    orders = list_resp.json()["orders"]
    assert any(order["symbol"] == "AAPL" for order in orders)

    delete_resp = client.delete("/api/orders/history", headers=auth_headers)
    assert delete_resp.status_code == 204

    empty_resp = client.get("/api/orders/history", headers=auth_headers)
    assert empty_resp.status_code == 200
    assert empty_resp.json()["orders"] == []


def test_user_profile_round_trip(client, auth_headers):
    profile_payload = {
        "data": {
            "investmentSettings": {"initialCapital": 50000},
            "tradingPreferences": {"riskTolerance": "medium"},
        }
    }

    save_resp = client.post(
        "/api/users/profile/investment_profile", json=profile_payload, headers=auth_headers
    )
    assert save_resp.status_code == 200
    assert save_resp.json()["data"]["investmentSettings"]["initialCapital"] == 50000

    fetch_resp = client.get(
        "/api/users/profile/investment_profile", headers=auth_headers
    )
    assert fetch_resp.status_code == 200
    fetched = fetch_resp.json()["data"]
    assert fetched["investmentSettings"]["initialCapital"] == 50000
