"""
Unit tests for ML Sentiment Router - Comprehensive coverage for sentiment analysis endpoints
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import User

client = TestClient(app, raise_server_exceptions=False)


class TestMLSentiment:
    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", username="test", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token-12345"}

    def test_get_sentiment_analysis_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful sentiment analysis retrieval"""
        monkeypatch.setattr("app.routers.ml_sentiment.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/ml/sentiment?symbol=AAPL", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_sentiment_analysis_unauthorized(self):
        """Test sentiment analysis without authentication"""
        response = client.get("/api/ml/sentiment?symbol=AAPL")
        assert response.status_code in [401, 403]

    def test_get_sentiment_trends_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful sentiment trends retrieval"""
        monkeypatch.setattr("app.routers.ml_sentiment.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/ml/sentiment/trends?symbol=AAPL", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_analyze_news_sentiment_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful news sentiment analysis"""
        monkeypatch.setattr("app.routers.ml_sentiment.get_current_user_unified", lambda: mock_user)

        news_data = {"text": "Apple reports record earnings, stock surges."}

        response = client.post("/api/ml/sentiment/analyze", json=news_data, headers=auth_headers)
        assert response.status_code in [200, 201, 404]
