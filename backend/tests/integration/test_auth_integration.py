"""
Integration tests for Authentication API
Test ID: AUTH-001
Priority: CRITICAL
"""

import time

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Test database fixture"""
    # This would set up a test database
    # For now, using the main db connection
    db = next(get_db())
    yield db
    db.close()


@pytest.fixture
def test_timestamp():
    """Generate a unique timestamp for test emails"""
    return int(time.time())


class TestAuthenticationIntegration:
    """Integration tests for authentication flow"""

    def test_user_registration_flow(self, client, test_timestamp):
        """Test complete user registration flow"""
        # Register new user
        response = client.post(
            "/api/auth/register",
            json={
                "email": f"test-{test_timestamp}@example.com",
                "password": "SecureP@ss123",
                "name": "Test User",
                "risk_tolerance": "moderate",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert "access_token" in data
        assert data["email"] == f"test-{test_timestamp}@example.com"

    def test_user_login_flow(self, client):
        """Test user login with valid credentials"""
        # Login
        response = client.post(
            "/api/auth/login",
            json={"email": "trader@test.com", "password": "TestP@ss123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == "trader@test.com"

    def test_login_with_invalid_credentials(self, client):
        """Test login with incorrect password"""
        response = client.post(
            "/api/auth/login",
            json={"email": "trader@test.com", "password": "WrongPassword123"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid credentials" in data["detail"]

    def test_login_with_nonexistent_user(self, client):
        """Test login with non-existent email"""
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "TestP@ss123"},
        )

        assert response.status_code == 401

    def test_session_validation(self, client):
        """Test session token validation"""
        # Login first
        login_response = client.post(
            "/api/auth/login",
            json={"email": "trader@test.com", "password": "TestP@ss123"},
        )

        token = login_response.json()["access_token"]

        # Validate session
        response = client.get(
            "/api/auth/session", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert "user" in data

    def test_session_without_token(self, client):
        """Test session validation without token"""
        response = client.get("/api/auth/session")

        assert response.status_code == 401

    def test_session_with_invalid_token(self, client):
        """Test session validation with invalid token"""
        response = client.get(
            "/api/auth/session", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_logout_flow(self, client):
        """Test user logout"""
        # Login first
        login_response = client.post(
            "/api/auth/login",
            json={"email": "trader@test.com", "password": "TestP@ss123"},
        )

        token = login_response.json()["access_token"]

        # Logout
        response = client.post(
            "/api/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

        # Verify token is invalidated
        session_response = client.get(
            "/api/auth/session", headers={"Authorization": f"Bearer {token}"}
        )

        assert session_response.status_code == 401

    def test_token_refresh(self, client):
        """Test access token refresh"""
        # Login first
        login_response = client.post(
            "/api/auth/login",
            json={"email": "trader@test.com", "password": "TestP@ss123"},
        )

        refresh_token = login_response.json()["refresh_token"]

        # Refresh access token
        response = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != login_response.json()["access_token"]

    def test_duplicate_email_registration(self, client):
        """Test registration with existing email"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "trader@test.com",  # Existing user
                "password": "NewP@ss123",
                "name": "Duplicate User",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"].lower()

    def test_password_strength_validation(self, client):
        """Test password strength requirements"""
        weak_passwords = [
            "short",
            "nouppercase123",
            "NOLOWERCASE123",
            "NoNumbers",
            "NoSpecial123",
        ]

        for password in weak_passwords:
            response = client.post(
                "/api/auth/register",
                json={
                    "email": f"test-{password}@example.com",
                    "password": password,
                    "name": "Test User",
                },
            )

            assert response.status_code == 400
            assert "password" in response.json()["detail"].lower()


# Performance benchmarks
class TestAuthenticationPerformance:
    """Performance tests for authentication endpoints"""

    def test_login_response_time(self, client, benchmark):
        """Test login response time is under 200ms"""

        def login():
            return client.post(
                "/api/auth/login",
                json={"email": "trader@test.com", "password": "TestP@ss123"},
            )

        result = benchmark(login)
        assert result.status_code == 200
        assert benchmark.stats["mean"] < 0.2  # 200ms

    def test_session_validation_response_time(self, client, benchmark):
        """Test session validation is under 100ms"""
        # Get token first
        login_response = client.post(
            "/api/auth/login",
            json={"email": "trader@test.com", "password": "TestP@ss123"},
        )
        token = login_response.json()["access_token"]

        def validate_session():
            return client.get(
                "/api/auth/session", headers={"Authorization": f"Bearer {token}"}
            )

        result = benchmark(validate_session)
        assert result.status_code == 200
        assert benchmark.stats["mean"] < 0.1  # 100ms


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
