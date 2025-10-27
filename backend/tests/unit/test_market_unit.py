"""
Unit tests for Market Data Router (market_data.py)

Tests all endpoints in the market_data router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock


class TestMarket:
    """Test suite for market endpoints"""

    def test_get_quote_success(self, client, auth_headers):
        """Test successful quote retrieval"""
        response = client.get("/api/market/quote/AAPL", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["last"] == 175.0

    def test_get_quotes_batch_success(self, client, auth_headers):
        """Test successful batch quotes retrieval"""
        response = client.get("/api/market/quotes?symbols=AAPL,MSFT", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert "AAPL" in data
        assert "MSFT" in data

    def test_get_historical_bars_success(self, client, auth_headers):
        """Test successful historical bars retrieval"""
        response = client.get("/api/market/bars/AAPL?timeframe=daily&limit=100", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_market_scanner_success(self, client, auth_headers, mock_tradier_client):
        """Test successful market scanner"""
        # Override mock for scanner-specific data
        mock_tradier_client.get_quotes = Mock(return_value={
            "SOFI": {"symbol": "SOFI", "last": 3.50, "bid": 3.49, "ask": 3.51, "volume": 5000000},
            "PLUG": {"symbol": "PLUG", "last": 2.75, "bid": 2.74, "ask": 2.76, "volume": 3000000},
        })

        response = client.get("/api/market/scanner/under4", headers=auth_headers)

        assert response.status_code == 200
