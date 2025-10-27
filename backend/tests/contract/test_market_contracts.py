"""
Contract tests for market data endpoints
"""

import json
import pytest
from jsonschema import validate
from pathlib import Path


@pytest.mark.asyncio
async def test_quote_contract(client, auth_headers):
    """Test /api/market/quote/{symbol} response contract"""
    response = await client.get("/api/market/quote/AAPL", headers=auth_headers)

    assert response.status_code == 200

    # Load schema
    schema_path = Path(__file__).parent / "schemas" / "quote.json"
    with open(schema_path) as f:
        schema = json.load(f)

    # Validate response
    data = response.json()
    validate(instance=data, schema=schema)

    # Business logic
    assert data["symbol"] == "AAPL"
    assert data["ask"] >= data["bid"]


@pytest.mark.asyncio
async def test_indices_contract(client, auth_headers):
    """Test /api/market/indices response contract"""
    response = await client.get("/api/market/indices", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate structure
    assert "dow" in data
    assert "nasdaq" in data
    assert "source" in data

    # Validate index data
    for index_data in [data["dow"], data["nasdaq"]]:
        assert "last" in index_data
        assert "change" in index_data
        assert "changePercent" in index_data


@pytest.mark.asyncio
async def test_market_conditions_contract(client, auth_headers):
    """Test /api/market/conditions response contract"""
    response = await client.get("/api/market/conditions", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate structure
    assert "conditions" in data
    assert "timestamp" in data
    assert "overallSentiment" in data
    assert "recommendedActions" in data
    assert "source" in data

    # Validate conditions
    assert isinstance(data["conditions"], list)
    for condition in data["conditions"]:
        assert "name" in condition
        assert "value" in condition
        assert "status" in condition
        assert condition["status"] in ["favorable", "neutral", "unfavorable"]


@pytest.mark.asyncio
async def test_sectors_contract(client, auth_headers):
    """Test /api/market/sectors response contract"""
    response = await client.get("/api/market/sectors", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate structure
    assert "sectors" in data
    assert "timestamp" in data
    assert "leader" in data
    assert "laggard" in data
    assert "source" in data

    # Validate sectors
    assert isinstance(data["sectors"], list)
    for sector in data["sectors"]:
        assert "name" in sector
        assert "symbol" in sector
        assert "changePercent" in sector
        assert "rank" in sector
