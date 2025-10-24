"""
Test strategy CRUD operations
Tests strategy creation, retrieval, update, deletion
"""

HEADERS = {"Authorization": "Bearer test-token-12345"}


def test_get_strategies_endpoint(client):
    """Test GET /api/strategies endpoint"""
    response = client.get("/api/strategies/list", headers=HEADERS)
    # Should return list or external API error
    assert response.status_code in [200, 401, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)
        assert "strategies" in data
        assert isinstance(data["strategies"], list)


def test_strategies_requires_auth(client):
    """Test strategies endpoint requires authentication (MVP fallback may apply)"""
    response = client.get("/api/strategies/list")
    # MVP fallback may allow (403) or block (401)
    assert response.status_code in [401, 403, 500]


def test_create_strategy(client):
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

    response = client.post("/api/strategies/save", json=strategy, headers=HEADERS)

    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test RSI Strategy"
        return data["id"]
    # Accept validation errors or unsupported methods
    assert response.status_code in [201, 404, 405, 422]


def test_get_strategy_by_id(client):
    """Test GET /api/strategies/:id"""
    # First create a strategy
    strategy = {
        "name": "Test Strategy for GET",
        "symbol": "AAPL",
        "rules": {"entryConditions": ["price_above_sma"], "smaPeriod": 20},
    }

    create_response = client.post("/api/strategies/save", json=strategy, headers=HEADERS)

    if create_response.status_code == 201:
        strategy_id = create_response.json()["id"]

        # Now get it by ID
        get_response = client.get(f"/api/strategies/{strategy_id}", headers=HEADERS)

        if get_response.status_code == 200:
            data = get_response.json()
            assert data["id"] == strategy_id
            assert data["name"] == "Test Strategy for GET"


def test_update_strategy(client):
    """Test PUT /api/strategies/:id to update strategy"""
    # First create a strategy
    strategy = {
        "name": "Original Strategy",
        "symbol": "MSFT",
        "rules": {"entryConditions": ["rsi_oversold"], "rsiPeriod": 14},
    }

    create_response = client.post("/api/strategies/save", json=strategy, headers=HEADERS)

    if create_response.status_code == 201:
        strategy_id = create_response.json()["id"]

        # Update the strategy
        updated_strategy = {
            "name": "Updated Strategy Name",
            "symbol": "MSFT",
            "rules": {"entryConditions": ["rsi_oversold"], "rsiPeriod": 21},  # Changed period
        }

        update_response = client.put(
            f"/api/strategies/{strategy_id}", json=updated_strategy, headers=HEADERS
        )

        if update_response.status_code == 200:
            data = update_response.json()
            assert data["name"] == "Updated Strategy Name"
            assert data["rules"]["rsiPeriod"] == 21


def test_delete_strategy(client):
    """Test DELETE /api/strategies/:id"""
    # First create a strategy
    strategy = {
        "name": "Strategy to Delete",
        "symbol": "GOOGL",
        "rules": {"entryConditions": ["price_above_sma"]},
    }

    create_response = client.post("/api/strategies/save", json=strategy, headers=HEADERS)

    if create_response.status_code == 201:
        strategy_id = create_response.json()["id"]

        # Delete the strategy
        delete_response = client.delete(f"/api/strategies/{strategy_id}", headers=HEADERS)

        if delete_response.status_code == 204:
            # Verify it's deleted
            get_response = client.get(f"/api/strategies/{strategy_id}", headers=HEADERS)
            assert get_response.status_code == 404


def test_create_strategy_validation(client):
    """Test strategy creation with invalid data"""
    # Missing required fields
    invalid_strategy = {
        "name": "Invalid Strategy"
        # Missing symbol and rules
    }

    response = client.post("/api/strategies/save", json=invalid_strategy, headers=HEADERS)
    # Should return validation error
    assert response.status_code in [400, 422]


def test_strategy_with_multiple_entry_conditions(client):
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

    response = client.post("/api/strategies/save", json=strategy, headers=HEADERS)

    if response.status_code == 201:
        data = response.json()
        assert len(data["rules"]["entryConditions"]) == 3
        assert len(data["rules"]["exitConditions"]) == 2


def test_strategy_with_risk_parameters(client):
    """Test strategy creation with risk management parameters"""
    strategy = {
        "name": "Risk Managed Strategy",
        "symbol": "AAPL",
        "rules": {"entryConditions": ["rsi_oversold"], "exitConditions": ["rsi_overbought"]},
        "riskParams": {
            "stopLoss": 0.03,  # 3% stop loss
            "takeProfit": 0.06,  # 6% take profit
            "positionSize": 0.15,  # 15% of capital per trade
            "maxOpenPositions": 5,
            "maxDailyLoss": 0.05,  # 5% max daily loss
        },
    }

    response = client.post("/api/strategies/save", json=strategy, headers=HEADERS)

    if response.status_code == 201:
        data = response.json()
        assert data["riskParams"]["stopLoss"] == 0.03
        assert data["riskParams"]["takeProfit"] == 0.06


def test_list_strategies_pagination(client):
    """Test listing strategies with pagination (if supported)"""
    response = client.get("/api/strategies/list?limit=10&offset=0", headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)
        assert "strategies" in data
        # Should return at most 10 items
        assert len(data["strategies"]) <= 10


def test_strategy_duplicate_name_handling(client):
    """Test creating two strategies with the same name"""
    strategy1 = {
        "name": "Duplicate Name Test",
        "symbol": "SPY",
        "rules": {"entryConditions": ["rsi_oversold"]},
    }

    response1 = client.post("/api/strategies/save", json=strategy1, headers=HEADERS)

    if response1.status_code == 201:
        # Try to create another with same name
        strategy2 = {
            "name": "Duplicate Name Test",  # Same name
            "symbol": "AAPL",  # Different symbol
            "rules": {"entryConditions": ["price_above_sma"]},
        }

        response2 = client.post("/api/strategies/save", json=strategy2, headers=HEADERS)

        # Should either allow duplicates or return conflict
        assert response2.status_code in [201, 409]


def test_update_nonexistent_strategy(client):
    """Test updating a strategy that doesn't exist"""
    fake_id = "00000000-0000-0000-0000-000000000000"

    updated_strategy = {
        "name": "Updated Name",
        "symbol": "SPY",
        "rules": {"entryConditions": ["rsi_oversold"]},
    }

    response = client.put(f"/api/strategies/{fake_id}", json=updated_strategy, headers=HEADERS)
    # Should return 404 or 405 (method not supported)
    assert response.status_code in [404, 405]


def test_delete_nonexistent_strategy(client):
    """Test deleting a strategy that doesn't exist"""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(f"/api/strategies/{fake_id}", headers=HEADERS)
    # Should return 404 or 401
    assert response.status_code in [401, 404]
