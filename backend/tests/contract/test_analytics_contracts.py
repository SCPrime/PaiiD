"""
Contract tests for analytics endpoints
"""

import json
import pytest
from jsonschema import validate
from pathlib import Path


@pytest.mark.asyncio
async def test_performance_metrics_contract(client, auth_headers):
    """Test /api/analytics/performance response contract"""
    response = await client.get("/api/analytics/performance", headers=auth_headers)

    assert response.status_code == 200

    # Load schema
    schema_path = Path(__file__).parent / "schemas" / "performance_metrics.json"
    with open(schema_path) as f:
        schema = json.load(f)

    # Validate response
    data = response.json()
    validate(instance=data, schema=schema)

    # Business logic validations
    assert data["num_trades"] == data["num_wins"] + data["num_losses"]
    assert 0 <= data["win_rate"] <= 100


@pytest.mark.asyncio
async def test_portfolio_history_contract(client, auth_headers):
    """Test /api/portfolio/history response contract"""
    response = await client.get("/api/portfolio/history?period=1M", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate required fields
    assert "period" in data
    assert "start_date" in data
    assert "end_date" in data
    assert "data" in data
    assert "is_simulated" in data

    # Validate data points
    assert isinstance(data["data"], list)
    for point in data["data"]:
        assert "timestamp" in point
        assert "equity" in point
        assert "cash" in point
        assert "positions_value" in point
