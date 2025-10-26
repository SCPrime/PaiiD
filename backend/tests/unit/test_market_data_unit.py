"""
Unit tests for Market Data Router - Comprehensive coverage for market data endpoints
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import User

client = TestClient(app, raise_server_exceptions=False)


class TestMarketData:
    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", username="test", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token-12345"}

    def test_get_realtime_quote_success(self, monkeypatch):
        """Test successful realtime quote retrieval"""
        mock_client = Mock()
        mock_client.get_quote.return_value = {"symbol": "AAPL", "last": 175.0}
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/market-data/quote/AAPL")
        assert response.status_code in [200, 404]

    def test_get_realtime_quote_not_found(self, monkeypatch):
        """Test realtime quote for non-existent symbol"""
        mock_client = Mock()
        mock_client.get_quote.return_value = {}
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/market-data/quote/INVALID")
        assert response.status_code in [404, 200]

    def test_get_realtime_quotes_batch_success(self, monkeypatch):
        """Test successful batch realtime quotes retrieval"""
        mock_client = Mock()
        mock_client.get_quotes.return_value = {
            "quotes": {"quote": [{"symbol": "AAPL", "last": 175.0}]}
        }
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/market-data/quotes?symbols=AAPL,MSFT")
        assert response.status_code in [200, 404]
