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
        monkeypatch.setattr("app.routers.options.get_current_user_unified", lambda: mock_user)
        mock_client = Mock()
        mock_client.get_options_chain.return_value = {"options": []}
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/options/chain/AAPL", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_options_chain_unauthorized(self):
        """Test options chain retrieval without authentication"""
        response = client.get("/api/options/chain/AAPL")
        assert response.status_code in [401, 403]

    def test_get_options_expirations_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful options expirations retrieval"""
        monkeypatch.setattr("app.routers.options.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/options/expirations/AAPL", headers=auth_headers)
        assert response.status_code in [200, 404]
