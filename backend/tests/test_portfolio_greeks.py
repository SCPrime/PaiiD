from __future__ import annotations

from unittest.mock import MagicMock

import sys
import types

import pytest
from fastapi.testclient import TestClient

if "cachetools" not in sys.modules:
    cachetools_stub = types.ModuleType("cachetools")

    def _cached(*args, **kwargs):  # type: ignore[override]
        def decorator(func):
            return func

        return decorator

    cachetools_stub.TTLCache = dict  # type: ignore[attr-defined]
    cachetools_stub.cached = _cached  # type: ignore[attr-defined]
    sys.modules["cachetools"] = cachetools_stub

from app.main import app
from app.portfolio import aggregate_greeks


client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-token-12345"}


def test_aggregate_greeks_combines_positions():
    positions = [
        {
            "symbol": "AAPL",
            "qty": "50",
            "side": "long",
            "asset_type": "equity",
        },
        {
            "symbol": "AAPL250118C00200000",
            "qty": "2",
            "side": "long",
            "asset_type": "option",
            "multiplier": 100,
            "greeks": {"delta": 0.55, "gamma": 0.02, "theta": -0.08, "vega": 0.12, "rho": 0.04},
        },
        {
            "symbol": "SPY250118P00430000",
            "qty": "1",
            "side": "short",
            "asset_type": "option",
            "greeks": {"delta": -0.40, "gamma": 0.01, "theta": -0.05, "vega": 0.09, "rho": 0.03},
        },
    ]

    analytics = aggregate_greeks(positions)

    assert pytest.approx(analytics.totals.delta, rel=1e-4) == 50 + (0.55 * 2 * 100) + (-0.40 * 1 * 100 * -1)
    assert pytest.approx(analytics.totals.gamma, rel=1e-4) == (0.02 * 2 * 100) + (0.01 * 1 * 100 * -1)
    assert len(analytics.breakdown) == 3
    assert analytics.breakdown[0].greeks["delta"] == 1.0


def test_portfolio_greeks_endpoint(monkeypatch):
    mock_client = MagicMock()
    mock_client.get_positions.return_value = [
        {
            "symbol": "TSLA",
            "qty": "10",
            "side": "long",
            "asset_type": "equity",
        },
        {
            "symbol": "TSLA250321C00350000",
            "qty": "1",
            "side": "long",
            "asset_type": "option",
            "multiplier": 100,
            "greeks": {"delta": 0.62, "gamma": 0.03, "theta": -0.07, "vega": 0.11, "rho": 0.05},
        },
    ]

    monkeypatch.setattr("app.routers.analytics.get_tradier_client", lambda: mock_client)

    response = client.get("/api/portfolio/greeks", headers=HEADERS)

    assert response.status_code == 200
    payload = response.json()
    assert "totals" in payload
    assert payload["totals"]["delta"] > 0
    assert len(payload["breakdown"]) == 2
