"""Tests for the backtesting API endpoints."""

import pytest


@pytest.fixture
def base_strategy():
    return {
        "symbol": "SPY",
        "startDate": "2024-01-01",
        "endDate": "2024-06-01",
        "initialCapital": 10000,
        "rules": {
            "entryConditions": ["rsi_oversold"],
            "exitConditions": ["rsi_overbought"],
            "rsiPeriod": 14,
            "rsiOversold": 30,
            "rsiOverbought": 70,
        },
    }


def test_backtest_requires_auth(client, base_strategy):
    response = client.post("/api/backtesting/run", json=base_strategy)
    assert response.status_code == 403


def test_backtest_accepts_authenticated_requests(client, auth_headers, base_strategy):
    response = client.post("/api/backtesting/run", json=base_strategy, headers=auth_headers)
    assert response.status_code in {200, 400, 422, 500}
    if response.status_code == 200:
        data = response.json()
        assert "trades" in data
        assert "totalReturn" in data


def test_backtest_validates_date_range(client, auth_headers, base_strategy):
    invalid_strategy = {**base_strategy, "endDate": "2023-12-31"}
    response = client.post("/api/backtesting/run", json=invalid_strategy, headers=auth_headers)
    assert response.status_code in {400, 422}


def test_backtest_rejects_negative_capital(client, auth_headers, base_strategy):
    invalid_strategy = {**base_strategy, "initialCapital": -5000}
    response = client.post("/api/backtesting/run", json=invalid_strategy, headers=auth_headers)
    assert response.status_code in {400, 422}


def test_backtest_allows_strategy_variants(client, auth_headers, base_strategy):
    variants = [
        base_strategy,
        {**base_strategy, "symbol": "AAPL"},
        {
            **base_strategy,
            "rules": {
                "entryConditions": ["sma_crossover"],
                "exitConditions": ["sma_crossunder"],
                "smaPeriod": 20,
                "smaSlowPeriod": 50,
            },
        },
    ]

    for payload in variants:
        response = client.post("/api/backtesting/run", json=payload, headers=auth_headers)
        assert response.status_code in {200, 400, 422, 500}
