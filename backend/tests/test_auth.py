import pytest

from app.models.database import UserSession


@pytest.fixture
def login_payload(sample_user):
    return {"email": sample_user.email, "password": "TestPassword123!"}


def test_login_returns_token_pair(client, test_db, sample_user, login_payload):
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Ensure session persisted
    sessions = test_db.query(UserSession).filter(UserSession.user_id == sample_user.id).all()
    assert len(sessions) == 1


def test_login_rejects_invalid_password(client, sample_user):
    payload = {"email": sample_user.email, "password": "WrongPassword!"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401


def test_refresh_token_rotates_session(client, test_db, sample_user, login_payload):
    login_response = client.post("/api/auth/login", json=login_payload)
    tokens = login_response.json()

    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()

    assert refreshed["access_token"] != tokens["access_token"]
    assert refreshed["refresh_token"] != tokens["refresh_token"]

    # Old session should be removed and replaced
    sessions = test_db.query(UserSession).filter(UserSession.user_id == sample_user.id).all()
    assert len(sessions) == 1
    assert sessions[0].refresh_token_jti is not None


def test_refresh_rejects_invalid_token(client, auth_headers):
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": "invalid-token"},
        headers=auth_headers,
    )
    assert response.status_code == 401


def test_protected_route_requires_auth(client):
    response = client.get("/api/users/preferences")
    assert response.status_code in (401, 403)


def test_protected_route_with_valid_token(client, auth_headers):
    response = client.get("/api/users/preferences", headers=auth_headers)
    assert response.status_code == 200
