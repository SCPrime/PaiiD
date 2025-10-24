"""Tests for the options router covering chain caching and greeks endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest

from app.routers import options as options_router


@pytest.fixture(autouse=True)
def clear_options_cache():
    """Ensure each test has an empty options cache."""
    options_router.options_cache.clear()
    yield
    options_router.options_cache.clear()


def _build_mock_option(symbol: str, option_type: str, strike: float, expiration: str) -> dict[str, Any]:
    return {
        "symbol": f"{symbol}-{expiration.replace('-', '')}-{option_type[0].upper()}-{int(strike)}",
        "option_type": option_type,
        "strike": strike,
        "expiration_date": expiration,
        "bid": 1.05,
        "ask": 1.45,
        "last": 1.25,
        "volume": 1200,
        "open_interest": 5600,
        "greeks": {
            "delta": 0.55 if option_type == "call" else -0.45,
            "gamma": 0.012,
            "theta": -0.045,
            "vega": 0.08,
            "rho": 0.04 if option_type == "call" else -0.04,
            "mid_iv": 0.24,
        },
    }


def test_options_chain_returns_mock_data(client, auth_headers):
    """The chain endpoint should return mock contracts in testing mode."""
    response = client.get(
        "/api/options/chain",
        params={"symbol": "AAPL"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "AAPL"
    assert payload["total_contracts"] > 0
    assert payload["calls"]
    assert payload["puts"]


def test_options_chain_uses_cache(client, auth_headers, monkeypatch):
    """Repeated requests should reuse the cached payload instead of hitting Tradier."""

    expiration = (datetime.utcnow() + timedelta(days=14)).date().isoformat()

    class DummyTradier:
        def __init__(self) -> None:
            self.chain_calls = 0
            self.quote_calls = 0

        def get_option_chains(self, symbol: str, expiry: str | None = None):
            self.chain_calls += 1
            return {
                "underlying_price": 210.0,
                "options": {
                    "option": [
                        _build_mock_option(symbol, "call", 200.0, expiration),
                        _build_mock_option(symbol, "put", 200.0, expiration),
                    ]
                },
            }

        def get_quote(self, symbol: str):
            self.quote_calls += 1
            return {"symbol": symbol, "last": 210.0, "close": 210.0}

    dummy_client = DummyTradier()
    monkeypatch.setattr(options_router, "_get_tradier_client", lambda: dummy_client)

    first = client.get(
        "/api/options/chain",
        params={"symbol": "TSLA", "expiration": expiration},
        headers=auth_headers,
    )
    assert first.status_code == 200
    assert dummy_client.chain_calls == 1
    assert dummy_client.quote_calls == 1

    second = client.get(
        "/api/options/chain",
        params={"symbol": "TSLA", "expiration": expiration},
        headers=auth_headers,
    )
    assert second.status_code == 200
    assert dummy_client.chain_calls == 1  # Cache hit skips new Tradier call
    assert dummy_client.quote_calls == 1


def test_greeks_endpoint_returns_expected_fields(client, auth_headers, monkeypatch):
    """The Greeks endpoint should return theoretical metrics for the requested contract."""

    expiration = (datetime.utcnow() + timedelta(days=30)).date().isoformat()
    strike = 200.0

    class DummyTradier:
        def get_option_chains(self, symbol: str, expiry: str | None = None):
            return {
                "underlying_price": 205.0,
                "options": {
                    "option": [
                        _build_mock_option(symbol, "call", strike, expiration),
                        _build_mock_option(symbol, "put", strike, expiration),
                    ]
                },
            }

        def get_quote(self, symbol: str):
            return {"symbol": symbol, "last": 205.0, "close": 205.0}

        def get_option_expirations(self, symbol: str):
            return {"expirations": {"date": [expiration]}}

    monkeypatch.setattr(options_router, "_get_tradier_client", lambda: DummyTradier())

    response = client.get(
        "/api/options/greeks",
        params={
            "symbol": "MSFT",
            "expiration": expiration,
            "strike": strike,
            "option_type": "call",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"].startswith("MSFT")
    assert payload["option_type"] == "call"
    assert payload["strike"] == pytest.approx(strike)
    for field in (
        "delta",
        "gamma",
        "theta",
        "vega",
        "rho",
        "theoretical_price",
        "intrinsic_value",
        "extrinsic_value",
        "probability_itm",
    ):
        assert field in payload

    assert payload["market_price"] is not None
    assert payload["implied_volatility"] == pytest.approx(0.24)
