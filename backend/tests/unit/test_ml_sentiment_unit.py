"""
Unit tests for ML Sentiment Router - Comprehensive coverage for sentiment analysis endpoints

NOTE: Sentiment endpoints REQUIRE authentication.
Endpoints tested: /api/sentiment/sentiment/{symbol}, /api/sentiment/signals/{symbol}, /api/sentiment/health
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, UTC


class TestMLSentiment:
    def test_get_sentiment_analysis_success(self, client, auth_headers, monkeypatch):
        """Test successful sentiment analysis retrieval"""
        # Mock Redis to avoid caching issues
        from unittest.mock import AsyncMock
        mock_redis = Mock()
        mock_redis.get = AsyncMock(return_value=None)  # Cache miss
        mock_redis.set = AsyncMock(return_value=True)
        monkeypatch.setattr("app.routers.ml_sentiment.get_redis", lambda: mock_redis)

        # Mock sentiment analyzer
        from app.ml.sentiment_analyzer import SentimentScore

        mock_analyzer = Mock()
        mock_sentiment = SentimentScore(
            symbol="AAPL",
            sentiment="bullish",
            score=0.75,
            confidence=0.85,
            reasoning="Positive news coverage",
            timestamp=datetime.now(UTC),
            source="news",
        )
        mock_analyzer.analyze_news_batch = AsyncMock(return_value=mock_sentiment)
        monkeypatch.setattr("app.routers.ml_sentiment.get_sentiment_analyzer", lambda: mock_analyzer)

        # Mock data pipeline
        from unittest.mock import AsyncMock
        mock_pipeline = Mock()
        mock_pipeline.fetch_news = AsyncMock(return_value=[
            {"title": "AAPL earnings beat", "content": "Strong results", "date": datetime.now(UTC)}
        ])
        monkeypatch.setattr("app.routers.ml_sentiment.MLDataPipeline", lambda: mock_pipeline)

        response = client.get("/api/api/sentiment/sentiment/AAPL", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["sentiment"] == "bullish"
        assert data["score"] == 0.75

    def test_get_sentiment_analysis_unauthorized(self, client):
        """Test sentiment analysis without authentication"""
        from app.main import app
        from app.core.unified_auth import get_current_user_unified

        # Clear auth override
        original_override = app.dependency_overrides.get(get_current_user_unified)
        if get_current_user_unified in app.dependency_overrides:
            del app.dependency_overrides[get_current_user_unified]

        response = client.get("/api/api/sentiment/sentiment/AAPL")

        # Restore override
        if original_override:
            app.dependency_overrides[get_current_user_unified] = original_override

        assert response.status_code in [401, 403, 500]

    def test_get_trade_signals_success(self, client, auth_headers, monkeypatch):
        """Test successful trade signal retrieval"""
        # Mock Redis
        from unittest.mock import AsyncMock
        mock_redis = Mock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)
        monkeypatch.setattr("app.routers.ml_sentiment.get_redis", lambda: mock_redis)

        # Mock signal generator
        from app.ml.signal_generator import SignalType, TradeSignal

        mock_generator = Mock()
        mock_signal = TradeSignal(
            symbol="AAPL",
            signal=SignalType.BUY,
            strength="strong",
            confidence=0.85,
            price=175.0,
            target_price=185.0,
            stop_loss=170.0,
            reasoning="Strong bullish pattern detected",
            technical_score=0.8,
            sentiment_score=0.9,
            combined_score=0.85,
            timestamp=datetime.now(UTC),
        )
        mock_generator.generate_signal = AsyncMock(return_value=mock_signal)
        monkeypatch.setattr("app.routers.ml_sentiment.get_signal_generator", lambda: mock_generator)

        response = client.get("/api/api/sentiment/signals/AAPL", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["signal"] == "buy"
        assert data["confidence"] == 0.85

    def test_ml_sentiment_health_check(self, client):
        """Test ML sentiment health check endpoint"""
        response = client.get("/api/api/sentiment/health")

        # Health endpoint should be public
        assert response.status_code == 200
        data = response.json()
        # Response is wrapped with 'data' and 'timestamp'
        assert "data" in data
        assert "status" in data["data"]
