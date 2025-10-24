import uuid

import pytest
import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.jwt import create_token_pair, decode_token
from app.models.database import UserSession


@pytest.fixture
def auth_client(client: TestClient, sample_user):
    """Return client and sample user credentials."""
    return client, sample_user


def test_login_returns_token_pair(auth_client):
    client, user = auth_client
    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "TestPassword123!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    payload = decode_token(data["access_token"])
    assert payload["sub"] == str(user.id)


def test_login_invalid_password(client, sample_user):
    response = client.post(
        "/api/auth/login",
        json={"email": sample_user.email, "password": "bad-password"},
    )
    assert response.status_code == 401


def test_refresh_token_success(client, sample_user, test_db):
    tokens = create_token_pair(sample_user, test_db)
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] != tokens["access_token"]
    assert data["refresh_token"] != tokens["refresh_token"]


@pytest.mark.parametrize("refresh_token", ["invalid", f"Bearer-{uuid.uuid4()}"], ids=["garbage", "wrong-prefix"])
def test_refresh_token_invalid_input(client, refresh_token):
    response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401


def test_logout_clears_sessions(client, sample_user, test_db):
    tokens = create_token_pair(sample_user, test_db)
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 204
    remaining = test_db.query(UserSession).filter(UserSession.user_id == sample_user.id).all()
    assert remaining == []
