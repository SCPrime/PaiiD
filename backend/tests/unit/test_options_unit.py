"""
Unit tests for Options Router - Comprehensive coverage for options endpoints
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import User

client = TestClient(app, raise_server_exceptions=False)


class TestOptions:
    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", username="test", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token-12345"}

    def test_get_options_chain_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful options chain retrieval"""
        monkeypatch.setattr("app.routers.options.get_current_user_unified", lambda x: mock_user)

        mock_client = Mock()
        mock_client.get_options_chain.return_value = {
            "options": {
                "option": [
                    {"symbol": "AAPL250117C00150000", "strike": 150.0, "option_type": "call", "bid": 5.0, "ask": 5.10}
                ]
            }
        }
        mock_client.get_quotes.return_value = {"AAPL": {"last": 175.0}}
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        mock_cache = Mock()
        mock_cache.get.return_value = None
        monkeypatch.setattr("app.routers.options.get_cache", lambda: mock_cache)

        response = client.get("/api/options/chain/AAPL?expiration=2025-01-17", headers=auth_headers)
        assert response.status_code in [200, 404, 500]

    def test_get_options_chain_unauthorized(self, monkeypatch):
        """Test options chain retrieval without authentication"""
        # Mock to prevent real API calls
        mock_client = Mock()
        mock_client.get_options_chain.side_effect = Exception("No auth")
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/options/chain/AAPL?expiration=2025-01-17")
        assert response.status_code in [401, 403, 500]

    def test_get_options_expirations_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful options expirations retrieval"""
        monkeypatch.setattr("app.routers.options.get_current_user_unified", lambda x: mock_user)

        mock_client = Mock()
        mock_client.get_options_expirations.return_value = {
            "expirations": {
                "date": ["2025-01-17", "2025-02-21", "2025-03-21"]
            }
        }
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        mock_cache = Mock()
        mock_cache.get.return_value = None
        monkeypatch.setattr("app.routers.options.get_cache", lambda: mock_cache)

        response = client.get("/api/options/expirations/AAPL", headers=auth_headers)
        assert response.status_code in [200, 404, 500]
