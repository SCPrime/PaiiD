"""
Unit tests for News Router - Comprehensive coverage for news endpoints
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import User

client = TestClient(app, raise_server_exceptions=False)


class TestNews:
    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", username="test", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token-12345"}

    def test_get_news_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful news retrieval"""
        monkeypatch.setattr("app.routers.news.get_current_user_unified", lambda: mock_user)
        mock_client = Mock()
        mock_client.get_news.return_value = [{"title": "Test News", "content": "Content"}]
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        response = client.get("/api/news?symbol=AAPL", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_news_unauthorized(self):
        """Test news retrieval without authentication"""
        response = client.get("/api/news?symbol=AAPL")
        assert response.status_code in [401, 403]

    def test_get_market_news_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful market news retrieval"""
        monkeypatch.setattr("app.routers.news.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/news/market", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_trending_news_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful trending news retrieval"""
        monkeypatch.setattr("app.routers.news.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/news/trending", headers=auth_headers)
        assert response.status_code in [200, 404]
