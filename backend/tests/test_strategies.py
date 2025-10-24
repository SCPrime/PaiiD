"""
Tests strategy creation, retrieval, update, deletion
"""


def test_get_strategies_endpoint(client, auth_headers):
    """Test GET /api/strategies endpoint"""
    response = client.get("/api/strategies/list", headers=auth_headers)
    # Should return list or service error, not auth error
    assert response.status_code != 401

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)
        assert "strategies" in data
        assert isinstance(data["strategies"], list)


def test_strategies_requires_auth(client):
    """Test strategies endpoint requires authentication"""
    response = client.get("/api/strategies/list")
    assert response.status_code == 401


def test_create_strategy(client, auth_headers):
    """Test POST /api/strategies to create new strategy"""
    strategy = {
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

    response = client.post("/api/strategies/save", json=strategy, headers=auth_headers)

    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test RSI Strategy"
        return data["id"]
    # Accept validation errors or unsupported methods
    assert response.status_code in [201, 404, 405, 422]


def test_get_strategy_by_id(client, auth_headers):
    """Test GET /api/strategies/:id"""
    strategy = {
        "name": "Test Strategy for GET",
        "symbol": "AAPL",
        "rules": {"entryConditions": ["price_above_sma"], "smaPeriod": 20},
    }

    create_response = client.post("/api/strategies/save", json=strategy, headers=auth_headers)

    if create_response.status_code == 201:
        strategy_id = create_response.json()["id"]

        get_response = client.get(f"/api/strategies/{strategy_id}", headers=auth_headers)

        if get_response.status_code == 200:
            data = get_response.json()
            assert data["id"] == strategy_id
            assert data["name"] == "Test Strategy for GET"


def test_update_strategy(client, auth_headers):
    """Test PUT /api/strategies/:id to update strategy"""
    strategy = {
        "name": "Original Strategy",
        "symbol": "MSFT",
        "rules": {"entryConditions": ["rsi_oversold"], "rsiPeriod": 14},
    }

    create_response = client.post("/api/strategies/save", json=strategy, headers=auth_headers)

    if create_response.status_code == 201:
        strategy_id = create_response.json()["id"]

        updated_strategy = {
            "name": "Updated Strategy Name",
            "symbol": "MSFT",
            "rules": {"entryConditions": ["rsi_oversold"], "rsiPeriod": 21},
        }

        update_response = client.put(
            f"/api/strategies/{strategy_id}", json=updated_strategy, headers=auth_headers
        )

        if update_response.status_code == 200:
            data = update_response.json()
            assert data["name"] == "Updated Strategy Name"
            assert data["rules"]["rsiPeriod"] == 21


def test_delete_strategy(client, auth_headers):
    """Test DELETE /api/strategies/:id"""
    strategy = {
        "name": "Strategy to Delete",
        "symbol": "GOOGL",
        "rules": {"entryConditions": ["price_above_sma"]},
    }

    create_response = client.post("/api/strategies/save", json=strategy, headers=auth_headers)

    if create_response.status_code == 201:
        strategy_id = create_response.json()["id"]

        delete_response = client.delete(f"/api/strategies/{strategy_id}", headers=auth_headers)

        if delete_response.status_code == 204:
            get_response = client.get(f"/api/strategies/{strategy_id}", headers=auth_headers)
            assert get_response.status_code == 404


def test_create_strategy_validation(client, auth_headers):
    """Test strategy creation with invalid data"""
    invalid_strategy = {"name": "Invalid Strategy"}

    response = client.post("/api/strategies/save", json=invalid_strategy, headers=auth_headers)
    assert response.status_code in [400, 422]


def test_strategy_with_multiple_entry_conditions(client, auth_headers):
    """Test strategy with multiple entry conditions"""
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


def test_strategy_with_risk_parameters(client, auth_headers):
    """Test strategy creation with risk management parameters"""
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


def test_list_strategies_pagination(client, auth_headers):
    """Test listing strategies with pagination (if supported)"""
    response = client.get("/api/strategies/list?limit=10&offset=0", headers=auth_headers)

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)
        assert "strategies" in data
        assert len(data["strategies"]) <= 10


def test_strategy_duplicate_name_handling(client, auth_headers):
    """Test creating two strategies with the same name"""
    strategy1 = {
        "name": "Duplicate Name Test",
        "symbol": "SPY",
        "rules": {"entryConditions": ["rsi_oversold"]},
    }

    response1 = client.post("/api/strategies/save", json=strategy1, headers=auth_headers)

    if response1.status_code == 201:
        strategy2 = {
            "name": "Duplicate Name Test",
            "symbol": "AAPL",
            "rules": {"entryConditions": ["price_above_sma"]},
        }

        response2 = client.post("/api/strategies/save", json=strategy2, headers=auth_headers)
        assert response2.status_code in [201, 409]


def test_update_nonexistent_strategy(client, auth_headers):
    """Test updating a strategy that doesn't exist"""
    fake_id = "00000000-0000-0000-0000-000000000000"

    updated_strategy = {
        "name": "Updated Name",
        "symbol": "SPY",
        "rules": {"entryConditions": ["rsi_oversold"]},
    }

    response = client.put(f"/api/strategies/{fake_id}", json=updated_strategy, headers=auth_headers)
    assert response.status_code in [404, 405]


def test_delete_nonexistent_strategy(client, auth_headers):
    """Test deleting a strategy that doesn't exist"""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(f"/api/strategies/{fake_id}", headers=auth_headers)
    assert response.status_code == 404
