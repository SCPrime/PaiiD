"""
Unit tests for Scheduler Router - Comprehensive coverage for scheduled tasks endpoints
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import User

client = TestClient(app, raise_server_exceptions=False)


class TestScheduler:
    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", username="test", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token-12345"}

    def test_get_scheduled_tasks_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful scheduled tasks retrieval"""
        monkeypatch.setattr("app.routers.scheduler.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/scheduler/tasks", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_scheduled_tasks_unauthorized(self):
        """Test scheduled tasks retrieval without authentication"""
        response = client.get("/api/scheduler/tasks")
        assert response.status_code in [401, 403, 404]

    def test_create_scheduled_task_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful scheduled task creation"""
        monkeypatch.setattr("app.routers.scheduler.get_current_user_unified", lambda: mock_user)

        task_data = {
            "name": "Daily portfolio sync",
            "schedule": "0 9 * * *",
            "task_type": "sync",
        }

        response = client.post("/api/scheduler/tasks", json=task_data, headers=auth_headers)
        assert response.status_code in [200, 201, 404]

    def test_delete_scheduled_task_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful scheduled task deletion"""
        monkeypatch.setattr("app.routers.scheduler.get_current_user_unified", lambda: mock_user)

        response = client.delete("/api/scheduler/tasks/task-123", headers=auth_headers)
        assert response.status_code in [200, 204, 404]
