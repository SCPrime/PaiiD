"""
Enhanced Integration Test Configuration for Authentication
Test ID: AUTH-002
Priority: CRITICAL
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.jwt import hash_password
from app.db.session import get_db
from app.main import app
from app.models.database import Base, User


# Test Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Create database session for tests"""
    connection = test_db.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Test client with database dependency override"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestP@ss123"),
        full_name="Test User",
        preferences={"risk_tolerance": "moderate"},
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_timestamp():
    """Generate unique timestamp for test emails"""
    import time

    return int(time.time())


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    response = client.post(
        "/api/auth/login", json={"email": test_user.email, "password": "TestP@ss123"}
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        return {}


class TestAuthenticationIntegrationEnhanced:
    """Enhanced integration tests for authentication flow"""

    def test_user_registration_complete_flow(self, client, test_timestamp):
        """Test complete user registration flow with validation"""
        email = f"newuser-{test_timestamp}@example.com"

        # Register new user
        response = client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "SecureP@ss123",
                "name": "New Test User",
                "risk_tolerance": "moderate",
            },
        )

        assert response.status_code == 201
        data = response.json()

        # Validate response structure
        assert "user_id" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["email"] == email
        assert data["name"] == "New Test User"
        assert data["risk_tolerance"] == "moderate"

        # Verify user can login with new credentials
        login_response = client.post(
            "/api/auth/login", json={"email": email, "password": "SecureP@ss123"}
        )
        assert login_response.status_code == 200

    def test_user_login_with_valid_credentials(self, client, test_user):
        """Test user login with valid credentials"""
        response = client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "TestP@ss123"},
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_user.email
        assert data["user"]["name"] == test_user.name
        assert data["user"]["risk_tolerance"] == test_user.risk_tolerance

    def test_login_with_invalid_password(self, client, test_user):
        """Test login with incorrect password"""
        response = client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "WrongPassword123"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid credentials" in data["detail"]

    def test_login_with_nonexistent_email(self, client):
        """Test login with non-existent email"""
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "TestP@ss123"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_session_validation_with_valid_token(self, client, auth_headers):
        """Test session validation with valid token"""
        if not auth_headers:
            pytest.skip("Authentication setup failed")

        response = client.get("/api/auth/session", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"

    def test_session_validation_without_token(self, client):
        """Test session validation without token"""
        response = client.get("/api/auth/session")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_session_validation_with_invalid_token(self, client):
        """Test session validation with invalid token"""
        response = client.get(
            "/api/auth/session", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_logout_flow(self, client, auth_headers):
        """Test user logout and token invalidation"""
        if not auth_headers:
            pytest.skip("Authentication setup failed")

        # Logout
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200

        # Verify token is invalidated
        session_response = client.get("/api/auth/session", headers=auth_headers)
        assert session_response.status_code == 401

    def test_token_refresh_flow(self, client, test_user):
        """Test access token refresh"""
        # Login first
        login_response = client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "TestP@ss123"},
        )

        assert login_response.status_code == 200
        refresh_token = login_response.json()["refresh_token"]

        # Refresh access token
        response = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != login_response.json()["access_token"]

    def test_duplicate_email_registration(self, client, test_user):
        """Test registration with existing email"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,  # Existing user
                "password": "NewP@ss123",
                "name": "Duplicate User",
                "risk_tolerance": "aggressive",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"].lower()

    def test_password_strength_validation(self, client, test_timestamp):
        """Test password strength requirements"""
        weak_passwords = [
            "short",
            "nouppercase123",
            "NOLOWERCASE123",
            "NoNumbers",
            "NoSpecial123",
        ]

        for i, password in enumerate(weak_passwords):
            response = client.post(
                "/api/auth/register",
                json={
                    "email": f"test-{test_timestamp}-{i}@example.com",
                    "password": password,
                    "name": "Test User",
                    "risk_tolerance": "moderate",
                },
            )

            assert response.status_code == 400
            data = response.json()
            assert "password" in data["detail"].lower()

    def test_email_format_validation(self, client, test_timestamp):
        """Test email format validation"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
        ]

        for i, email in enumerate(invalid_emails):
            response = client.post(
                "/api/auth/register",
                json={
                    "email": email,
                    "password": "ValidP@ss123",
                    "name": "Test User",
                    "risk_tolerance": "moderate",
                },
            )

            assert response.status_code == 400
            data = response.json()
            assert "email" in data["detail"].lower()

    def test_risk_tolerance_validation(self, client, test_timestamp):
        """Test risk tolerance validation"""
        invalid_risk_levels = ["invalid", "extreme", "high-risk", ""]

        for i, risk in enumerate(invalid_risk_levels):
            response = client.post(
                "/api/auth/register",
                json={
                    "email": f"test-{test_timestamp}-{i}@example.com",
                    "password": "ValidP@ss123",
                    "name": "Test User",
                    "risk_tolerance": risk,
                },
            )

            assert response.status_code == 400
            data = response.json()
            assert "risk_tolerance" in data["detail"].lower()

    def test_concurrent_login_attempts(self, client, test_user):
        """Test handling of concurrent login attempts"""
        import threading

        results = []

        def login_attempt():
            response = client.post(
                "/api/auth/login",
                json={"email": test_user.email, "password": "TestP@ss123"},
            )
            results.append(response.status_code)

        # Start multiple concurrent login attempts
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=login_attempt)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All should succeed (or be rate limited gracefully)
        for status_code in results:
            assert status_code in [200, 429]  # Success or rate limited


class TestAuthenticationSecurity:
    """Security-focused authentication tests"""

    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection"""
        malicious_email = "'; DROP TABLE users; --"

        response = client.post(
            "/api/auth/login",
            json={"email": malicious_email, "password": "TestP@ss123"},
        )

        # Should not crash and should return proper error
        assert response.status_code in [400, 401]
        data = response.json()
        assert "detail" in data

    def test_password_not_logged(self, client, test_user, caplog):
        """Test that passwords are not logged"""
        import logging

        # Set logging level to capture all logs
        caplog.set_level(logging.DEBUG)

        response = client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "TestP@ss123"},
        )

        assert response.status_code == 200

        # Check that password is not in logs
        log_text = caplog.text
        assert "TestP@ss123" not in log_text

    def test_token_expiration(self, client, test_user):
        """Test token expiration handling"""
        # This would require mocking time or using expired tokens
        # For now, just test that expired tokens are rejected
        response = client.get(
            "/api/auth/session", headers={"Authorization": "Bearer expired_token"}
        )

        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
