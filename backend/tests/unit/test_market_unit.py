"""
Unit tests for Market Router (market.py)

Tests all 4+ endpoints in the market router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import User


client = TestClient(app, raise_server_exceptions=False)


class TestMarket:
    """Test suite for market endpoints"""

    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", username="test_user", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token-12345"}

    def test_get_quote_success(self, monkeypatch):
        """Test successful quote retrieval"""
        mock_client = Mock()
        mock_client.get_quote.return_value = {
            "symbol": "AAPL",
            "last": 175.0,
            "bid": 174.95,
            "ask": 175.05,
            "volume": 1000000,
        }
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/market/quote/AAPL")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"

    def test_get_quotes_batch_success(self, monkeypatch):
        """Test successful batch quotes retrieval"""
        mock_client = Mock()
        mock_client.get_quotes.return_value = {
            "quotes": {
                "quote": [
                    {"symbol": "AAPL", "last": 175.0},
                    {"symbol": "MSFT", "last": 380.0},
                ]
            }
        }
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/market/quotes?symbols=AAPL,MSFT")

        assert response.status_code == 200

    def test_get_historical_bars_success(self, monkeypatch):
        """Test successful historical bars retrieval"""
        mock_client = Mock()
        mock_client.get_historical_bars.return_value = [
            {"timestamp": "2024-01-01", "open": 170.0, "high": 175.0, "low": 168.0, "close": 172.0, "volume": 1000000}
        ]
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/market/bars/AAPL?interval=daily&start_date=2024-01-01&end_date=2024-12-31")

        assert response.status_code == 200

    def test_get_market_indices_success(self, monkeypatch):
        """Test successful market indices retrieval"""
        mock_client = Mock()
        mock_client.get_quotes.return_value = {
            "quotes": {
                "quote": [
                    {"symbol": "$DJI.IX", "last": 42500.0, "change": 125.0, "change_percentage": 0.30},
                    {"symbol": "$COMP.IX", "last": 18350.0, "change": 98.75, "change_percentage": 0.54},
                ]
            }
        }
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/market/indices")

        assert response.status_code == 200
