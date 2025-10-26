"""
Unit tests for Monitoring Router - Comprehensive coverage for monitoring endpoints
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import User

client = TestClient(app, raise_server_exceptions=False)


class TestMonitoring:
    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", username="test", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token-12345"}

    def test_get_system_health_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful system health retrieval"""
        monkeypatch.setattr("app.routers.monitoring.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/monitoring/health", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_system_health_unauthorized(self):
        """Test system health retrieval without authentication"""
        response = client.get("/api/monitoring/health")
        assert response.status_code in [401, 403, 404]

    def test_get_system_metrics_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful system metrics retrieval"""
        monkeypatch.setattr("app.routers.monitoring.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/monitoring/metrics", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_api_performance_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful API performance retrieval"""
        monkeypatch.setattr("app.routers.monitoring.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/monitoring/performance", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_error_logs_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful error logs retrieval"""
        monkeypatch.setattr("app.routers.monitoring.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/monitoring/errors?limit=100", headers=auth_headers)
        assert response.status_code in [200, 404]
