"""Tests for strategies endpoints."""

def test_strategies_require_auth(client):
    response = client.get("/api/strategies/list")
    assert response.status_code == 403


def test_list_strategies_returns_payload(client, auth_headers, tmp_path, monkeypatch):
    from app.routers import strategies as strategies_router

    monkeypatch.setattr(strategies_router, "STRATEGIES_DIR", tmp_path)

    response = client.get("/api/strategies/list", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "strategies" in data
    assert any(item["strategy_type"] == "under4-multileg" for item in data["strategies"])


def test_save_strategy_validates_payload(client, auth_headers, tmp_path, monkeypatch):
    from app.routers import strategies as strategies_router

    monkeypatch.setattr(strategies_router, "STRATEGIES_DIR", tmp_path)

    response = client.post(
        "/api/strategies/save",
        headers=auth_headers,
        json={"strategy_type": "custom", "config": {}},
    )
    assert response.status_code == 400
    assert "Unknown strategy type" in response.json()["detail"]
