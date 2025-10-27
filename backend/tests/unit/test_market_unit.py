"""
Unit tests for Market Data Router (market_data.py)

Tests all endpoints in the market_data router with mocked dependencies.
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

    def test_get_quote_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful quote retrieval"""
        monkeypatch.setattr("app.routers.market_data.get_current_user_unified", lambda x: mock_user)

        mock_client = Mock()
        mock_client.get_quotes.return_value = {
            "AAPL": {
                "symbol": "AAPL",
                "last": 175.0,
                "bid": 174.95,
                "ask": 175.05,
                "volume": 1000000,
            }
        }
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        mock_cache = Mock()
        mock_cache.get.return_value = None
        monkeypatch.setattr("app.routers.market_data.get_cache", lambda: mock_cache)

        response = client.get("/api/market/quote/AAPL", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"

    def test_get_quotes_batch_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful batch quotes retrieval"""
        monkeypatch.setattr("app.routers.market_data.get_current_user_unified", lambda x: mock_user)

        mock_client = Mock()
        mock_client.get_quotes.return_value = {
            "AAPL": {"symbol": "AAPL", "last": 175.0, "bid": 174.95, "ask": 175.05},
            "MSFT": {"symbol": "MSFT", "last": 380.0, "bid": 379.90, "ask": 380.10},
        }
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        mock_cache = Mock()
        mock_cache.get.return_value = None
        monkeypatch.setattr("app.routers.market_data.get_cache", lambda: mock_cache)

        response = client.get("/api/market/quotes?symbols=AAPL,MSFT", headers=auth_headers)

        assert response.status_code == 200

    def test_get_historical_bars_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful historical bars retrieval"""
        monkeypatch.setattr("app.routers.market_data.get_current_user_unified", lambda x: mock_user)

        mock_client = Mock()
        mock_client.get_historical_quotes.return_value = [
            {"date": "2024-01-01", "open": 170.0, "high": 175.0, "low": 168.0, "close": 172.0, "volume": 1000000}
        ]
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        mock_cache = Mock()
        mock_cache.get.return_value = None
        monkeypatch.setattr("app.routers.market_data.get_cache", lambda: mock_cache)

        response = client.get("/api/market/bars/AAPL?timeframe=daily&limit=100", headers=auth_headers)

        assert response.status_code == 200

    def test_get_market_scanner_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful market scanner"""
        monkeypatch.setattr("app.routers.market_data.get_current_user_unified", lambda x: mock_user)

        mock_client = Mock()
        mock_client.get_quotes.return_value = {
            "SOFI": {"symbol": "SOFI", "last": 3.50, "bid": 3.49, "ask": 3.51, "volume": 5000000},
            "PLUG": {"symbol": "PLUG", "last": 2.75, "bid": 2.74, "ask": 2.76, "volume": 3000000},
        }
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        mock_cache = Mock()
        mock_cache.get.return_value = None
        monkeypatch.setattr("app.routers.market_data.get_cache", lambda: mock_cache)

        response = client.get("/api/market/scanner/under4", headers=auth_headers)

        assert response.status_code == 200
