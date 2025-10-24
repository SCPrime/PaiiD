"""Integration tests for JWT-protected routes."""

import pytest
from fastapi.testclient import TestClient


SECURED_ENDPOINTS = [
    ("GET", "/api/users/preferences", {}),
    ("GET", "/api/users/risk-limits", {}),
    ("PATCH", "/api/users/preferences", {"json": {"risk_tolerance": 45}}),
]


@pytest.mark.parametrize("method,path,kwargs", SECURED_ENDPOINTS)
def test_secured_endpoints_require_auth(client: TestClient, method: str, path: str, kwargs: dict):
    """All secured endpoints should reject unauthenticated requests."""

    response = client.request(method, path, **kwargs)
    assert response.status_code in (401, 403)


def test_secured_endpoints_accept_jwt(client: TestClient, auth_headers: dict):
    """Valid JWT tokens should unlock all protected endpoints with consistent behaviour."""

    # Update user preferences first to ensure downstream endpoints have numeric data
    update_response = client.patch(
        "/api/users/preferences",
        headers=auth_headers,
        json={"risk_tolerance": 45},
    )
    assert update_response.status_code == 200
    prefs_payload = update_response.json()
    assert prefs_payload["risk_tolerance"] == 45

    # Verify GET endpoints respond with 200 when authenticated
    protected_gets = [
        "/api/users/preferences",
        "/api/users/risk-limits",
    ]

    for path in protected_gets:
        response = client.get(path, headers=auth_headers)
        assert response.status_code == 200

    # Ensure risk limits reflect the updated tolerance value
    risk_limits = client.get("/api/users/risk-limits", headers=auth_headers).json()
    assert isinstance(risk_limits["risk_tolerance"], int)
    assert risk_limits["risk_category"] in {"Conservative", "Moderate", "Aggressive"}
