"""
Unit tests for ML Router - Comprehensive coverage for ML prediction endpoints

NOTE: ML router endpoints are PUBLIC (no authentication required).
Endpoints tested: /api/ml/market-regime, /api/ml/health, /api/ml/recommend-strategy
"""
import pytest
from unittest.mock import Mock


class TestML:
    def test_get_market_regime_success(self, client, monkeypatch):
        """Test successful market regime detection"""
        # Mock regime detector
        mock_detector = Mock()
        mock_detector.predict.return_value = {
            "regime": "trending_bullish",
            "confidence": 0.85,
            "features": {"volatility": 0.2, "trend": 0.8},
            "cluster_id": 1,
        }
        mock_detector.get_recommended_strategies.return_value = ["momentum", "breakout"]
        monkeypatch.setattr("app.routers.ml.get_regime_detector", lambda: mock_detector)

        response = client.get("/api/api/ml/market-regime?symbol=AAPL&lookback_days=90")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["regime"] == "trending_bullish"
        assert data["confidence"] == 0.85
        assert "recommended_strategies" in data

    def test_get_market_regime_failure(self, client, monkeypatch):
        """Test market regime detection when model fails"""
        mock_detector = Mock()
        mock_detector.predict.return_value = {
            "regime": "unknown",
            "error": "Insufficient data",
        }
        monkeypatch.setattr("app.routers.ml.get_regime_detector", lambda: mock_detector)

        response = client.get("/api/api/ml/market-regime?symbol=AAPL")

        assert response.status_code == 500

    def test_ml_health_check(self, client, monkeypatch):
        """Test ML health check endpoint"""
        mock_detector = Mock()
        mock_detector.is_fitted = True
        mock_detector.regime_labels = {0: "trending_bullish", 1: "ranging"}
        mock_detector.n_clusters = 4
        monkeypatch.setattr("app.routers.ml.get_regime_detector", lambda: mock_detector)

        response = client.get("/api/api/ml/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["regime_detector_ready"] is True
        assert "regime_labels" in data

    # NOTE: test_train_regime_detector - Skipped (POST endpoint, CSRF protected)

    def test_recommend_strategy_success(self, client, monkeypatch):
        """Test successful strategy recommendation"""
        # Mock strategy selector
        mock_selector = Mock()
        mock_selector.recommend.return_value = [
            {"strategy_id": "momentum", "probability": 0.75, "confidence": 0.80},
            {"strategy_id": "breakout", "probability": 0.65, "confidence": 0.70},
        ]
        monkeypatch.setattr("app.routers.ml.get_strategy_selector", lambda: mock_selector)

        # Mock regime detector for context
        mock_detector = Mock()
        mock_detector.predict.return_value = {
            "regime": "trending_bullish",
            "confidence": 0.85,
        }
        monkeypatch.setattr("app.routers.ml.get_regime_detector", lambda: mock_detector)

        response = client.get("/api/api/ml/recommend-strategy?symbol=AAPL&top_n=2")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
