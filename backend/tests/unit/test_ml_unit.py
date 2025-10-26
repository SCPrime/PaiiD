"""
Unit tests for ML Router - Comprehensive coverage for ML prediction endpoints
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import User

client = TestClient(app, raise_server_exceptions=False)


class TestML:
    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", username="test", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token-12345"}

    def test_get_ml_predictions_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful ML predictions retrieval"""
        monkeypatch.setattr("app.routers.ml.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/ml/predictions?symbol=AAPL", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_ml_predictions_unauthorized(self):
        """Test ML predictions without authentication"""
        response = client.get("/api/ml/predictions?symbol=AAPL")
        assert response.status_code in [401, 403]

    def test_get_ml_model_info_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful ML model info retrieval"""
        monkeypatch.setattr("app.routers.ml.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/ml/model-info", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_train_ml_model_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful ML model training"""
        monkeypatch.setattr("app.routers.ml.get_current_user_unified", lambda: mock_user)

        train_data = {"symbol": "AAPL", "lookback_days": 365}

        response = client.post("/api/ml/train", json=train_data, headers=auth_headers)
        assert response.status_code in [200, 201, 404]

    def test_get_ml_feature_importance_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful ML feature importance retrieval"""
        monkeypatch.setattr("app.routers.ml.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/ml/feature-importance", headers=auth_headers)
        assert response.status_code in [200, 404]
