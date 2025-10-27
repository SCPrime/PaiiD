"""
Contract tests for portfolio endpoints

Validates that API responses match expected JSON schemas
"""

import json
import pytest
from jsonschema import validate, ValidationError
from pathlib import Path


@pytest.mark.asyncio
async def test_portfolio_summary_contract(client, auth_headers):
    """Test /api/portfolio/summary response contract"""
    response = await client.get("/api/portfolio/summary", headers=auth_headers)

    assert response.status_code == 200

    # Load schema
    schema_path = Path(__file__).parent / "schemas" / "portfolio_summary.json"
    with open(schema_path) as f:
        schema = json.load(f)

    # Validate response against schema
    data = response.json()
    validate(instance=data, schema=schema)

    # Additional business logic validations
    assert data["num_positions"] == data["num_winning"] + data["num_losing"]


@pytest.mark.asyncio
async def test_positions_contract(client, auth_headers):
    """Test /api/positions response contract"""
    response = await client.get("/api/positions", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate required fields
    assert "data" in data
    assert "count" in data
    assert "timestamp" in data
    assert isinstance(data["data"], list)
    assert isinstance(data["count"], int)

    # Validate each position has required fields
    for position in data["data"]:
        assert "symbol" in position
        assert "quantity" in position
        assert isinstance(position["symbol"], str)


@pytest.mark.asyncio
async def test_account_contract(client, auth_headers):
    """Test /api/account response contract"""
    response = await client.get("/api/account", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate top-level structure
    assert "data" in data
    assert "timestamp" in data
    assert isinstance(data["data"], dict)
