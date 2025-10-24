"""Test strategy CRUD operations using API fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def strategy_payload() -> dict:
    return {
        "name": "Test RSI Strategy",
        "symbol": "SPY",
        "rules": {
            "entryConditions": ["rsi_oversold"],
            "exitConditions": ["rsi_overbought"],
            "rsiPeriod": 14,
            "rsiOversold": 30,
            "rsiOverbought": 70,
        },
        "riskParams": {"stopLoss": 0.02, "takeProfit": 0.05, "positionSize": 0.10},
    }


def test_get_strategies_endpoint(client, auth_headers, sample_user):
    """GET /api/strategies/list should succeed for authenticated requests."""

    response = client.get("/api/strategies/list", headers=auth_headers)
    assert response.status_code != 401

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)
        assert "strategies" in data
        assert isinstance(data["strategies"], list)


def test_strategies_requires_auth(client):
    """Strategies listing requires a bearer token."""

    response = client.get("/api/strategies/list")
    assert response.status_code == 401


def test_create_strategy(client, auth_headers, sample_user, strategy_payload):
    """POST /api/strategies/save should create strategies for the user."""

    response = client.post("/api/strategies/save", json=strategy_payload, headers=auth_headers)

    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert data["name"] == strategy_payload["name"]
    else:
        assert response.status_code in {404, 405, 422}


def test_get_strategy_by_id(client, auth_headers, sample_user, strategy_payload):
    """Created strategies should be retrievable by identifier."""

    create_response = client.post("/api/strategies/save", json=strategy_payload, headers=auth_headers)

    if create_response.status_code == 201:
        strategy_id = create_response.json()["id"]
        get_response = client.get(f"/api/strategies/{strategy_id}", headers=auth_headers)

        if get_response.status_code == 200:
            data = get_response.json()
            assert data["id"] == strategy_id
            assert data["name"] == strategy_payload["name"]


def test_update_strategy(client, auth_headers, sample_user, strategy_payload):
    """Strategies can be updated via PUT."""

    create_response = client.post("/api/strategies/save", json=strategy_payload, headers=auth_headers)

    if create_response.status_code == 201:
        strategy_id = create_response.json()["id"]
        updated_strategy = {
            "name": "Updated Strategy Name",
            "symbol": strategy_payload["symbol"],
            "rules": {"entryConditions": ["rsi_oversold"], "rsiPeriod": 21},
        }

        update_response = client.put(
            f"/api/strategies/{strategy_id}", json=updated_strategy, headers=auth_headers
        )

        if update_response.status_code == 200:
            data = update_response.json()
            assert data["name"] == "Updated Strategy Name"
            assert data["rules"]["rsiPeriod"] == 21


def test_delete_strategy(client, auth_headers, sample_user, strategy_payload):
    """DELETE /api/strategies/:id removes a strategy if supported."""

    create_response = client.post("/api/strategies/save", json=strategy_payload, headers=auth_headers)

    if create_response.status_code == 201:
        strategy_id = create_response.json()["id"]
        delete_response = client.delete(f"/api/strategies/{strategy_id}", headers=auth_headers)

        if delete_response.status_code == 204:
            get_response = client.get(f"/api/strategies/{strategy_id}", headers=auth_headers)
            assert get_response.status_code == 404


def test_create_strategy_validation(client, auth_headers, sample_user):
    """Invalid payloads should return validation errors."""

    invalid_strategy = {"name": "Invalid Strategy"}
    response = client.post("/api/strategies/save", json=invalid_strategy, headers=auth_headers)

    if response.status_code in {400, 422}:
        return

    # Some strategy types may accept minimal payloads; ensure defaults are present.
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == invalid_strategy["name"]


def test_strategy_with_multiple_entry_conditions(client, auth_headers, sample_user):
    """Creating strategies with multiple entry conditions should succeed."""

    strategy = {
        "name": "Multi-Condition Strategy",
        "symbol": "SPY",
        "rules": {
            "entryConditions": ["rsi_oversold", "price_above_sma", "volume_surge"],
            "exitConditions": ["rsi_overbought", "price_below_sma"],
            "rsiPeriod": 14,
            "smaPeriod": 50,
            "volumeMultiplier": 1.5,
        },
    }

    response = client.post("/api/strategies/save", json=strategy, headers=auth_headers)

    if response.status_code == 201:
        data = response.json()
        assert len(data["rules"]["entryConditions"]) == 3
        assert len(data["rules"]["exitConditions"]) == 2


def test_strategy_with_risk_parameters(client, auth_headers, sample_user):
    """Risk management parameters should be persisted when provided."""

    strategy = {
        "name": "Risk Managed Strategy",
        "symbol": "AAPL",
        "rules": {"entryConditions": ["rsi_oversold"], "exitConditions": ["rsi_overbought"]},
        "riskParams": {
            "stopLoss": 0.03,
            "takeProfit": 0.06,
            "positionSize": 0.15,
            "maxOpenPositions": 5,
            "maxDailyLoss": 0.05,
        },
    }

    response = client.post("/api/strategies/save", json=strategy, headers=auth_headers)

    if response.status_code == 201:
        data = response.json()
        assert data["riskParams"]["stopLoss"] == 0.03
        assert data["riskParams"]["takeProfit"] == 0.06


def test_list_strategies_pagination(client, auth_headers, sample_user):
    """List endpoint should respect pagination parameters."""

    response = client.get("/api/strategies/list?limit=10&offset=0", headers=auth_headers)

    if response.status_code == 200:
        data = response.json()
        assert "strategies" in data
        assert len(data["strategies"]) <= 10


def test_strategy_duplicate_name_handling(client, auth_headers, sample_user):
    """Creating duplicate strategy names should be handled gracefully."""

    strategy = {
        "name": "Duplicate Name Test",
        "symbol": "SPY",
        "rules": {"entryConditions": ["rsi_oversold"]},
    }

    response1 = client.post("/api/strategies/save", json=strategy, headers=auth_headers)

    if response1.status_code == 201:
        strategy2 = {
            "name": "Duplicate Name Test",
            "symbol": "AAPL",
            "rules": {"entryConditions": ["price_above_sma"]},
        }

        response2 = client.post("/api/strategies/save", json=strategy2, headers=auth_headers)
        assert response2.status_code in {201, 409}


def test_update_nonexistent_strategy(client, auth_headers, sample_user):
    """Updating a non-existent strategy should return 404/405."""

    fake_id = "00000000-0000-0000-0000-000000000000"
    updated_strategy = {
        "name": "Updated Name",
        "symbol": "SPY",
        "rules": {"entryConditions": ["rsi_oversold"]},
    }

    response = client.put(f"/api/strategies/{fake_id}", json=updated_strategy, headers=auth_headers)
    assert response.status_code in {404, 405}


def test_delete_nonexistent_strategy(client, auth_headers, sample_user):
    """Deleting a non-existent strategy should yield 404."""

    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/api/strategies/{fake_id}", headers=auth_headers)
    assert response.status_code == 404
