"""
Test authentication and authorization
Tests Bearer token validation, missing tokens, invalid formats
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

# Valid token from config (matches conftest.py line 18)
VALID_TOKEN = "test-token-12345"
INVALID_TOKEN = "wrong-token-123"


def test_valid_bearer_token():
    """Test that valid Bearer token is accepted"""
    headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
    response = client.get("/api/account", headers=headers)
    # Should succeed or return Alpaca error, not 401
    assert response.status_code != 401


def test_missing_authorization_header():
    """Test that missing Authorization header returns 401"""
    response = client.get("/api/account")
    assert response.status_code == 401
    assert "Missing authorization header" in response.json()["detail"]


def test_invalid_bearer_token():
    """Test that invalid Bearer token returns 401"""
    headers = {"Authorization": f"Bearer {INVALID_TOKEN}"}
    response = client.get("/api/account", headers=headers)
    assert response.status_code == 401


def test_malformed_authorization_header():
    """Test that malformed Authorization header returns 401"""
    # Missing "Bearer" prefix
    headers = {"Authorization": VALID_TOKEN}
    response = client.get("/api/account", headers=headers)
    assert response.status_code == 401


def test_empty_bearer_token():
    """Test that empty Bearer token returns 401"""
    headers = {"Authorization": "Bearer "}
    response = client.get("/api/account", headers=headers)
    assert response.status_code == 401


def test_auth_on_protected_endpoints():
    """Test authentication is required on all protected endpoints"""
    protected_endpoints = [
        "/api/account",
        "/api/positions",
        "/api/order-templates",
        "/api/portfolio/summary",
        "/api/strategies/list",
    ]

    for endpoint in protected_endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401, f"Endpoint {endpoint} should require auth"


def test_public_endpoints_no_auth():
    """Test that public endpoints don't require authentication"""
    public_endpoints = [
        "/api/health",
    ]

    for endpoint in public_endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, f"Endpoint {endpoint} should be public"


def test_case_sensitive_bearer_prefix():
    """Test that Bearer prefix is case-sensitive"""
    # Lowercase "bearer" should be rejected
    headers = {"Authorization": f"bearer {VALID_TOKEN}"}
    response = client.get("/api/account", headers=headers)
    assert response.status_code == 401
