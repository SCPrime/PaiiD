import pytest
from fastapi.testclient import TestClient

from app.core.jwt import create_token_pair
from app.core.kill_switch import set_kill
import pytest
from fastapi.testclient import TestClient

from app.core.jwt import create_token_pair
from app.core.kill_switch import set_kill
from app.models.database import ActivityLog, User

TEST_PASSWORD_HASH = "$2b$12$LQ3JzqjX7Y8ZHnVc9r5MHOfWw8L4vQy8QWxK0X1y0HdTYJKRQ6qKK"


@pytest.fixture
def admin_user(test_db):
    user = User(
        email="admin@example.com",
        password_hash=TEST_PASSWORD_HASH,
        full_name="Admin User",
        role="owner",
        is_active=True,
        preferences={"risk_tolerance": 50},
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def regular_user(test_db):
    user = User(
        email="trader@example.com",
        password_hash=TEST_PASSWORD_HASH,
        full_name="Trader User",
        role="personal_only",
        is_active=True,
        preferences={"risk_tolerance": 50},
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user, test_db):
    tokens = create_token_pair(
        admin_user,
        test_db,
        ip_address="127.0.0.1",
        user_agent="pytest",
    )
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
def user_headers(regular_user, test_db):
    tokens = create_token_pair(
        regular_user,
        test_db,
        ip_address="127.0.0.1",
        user_agent="pytest",
    )
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_admin_can_toggle_kill_switch(client: TestClient, test_db, admin_headers):
    set_kill(False)

    response = client.post(
        "/api/admin/kill",
        json={"halt": True, "reason": "maintenance"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tradingHalted"] is True
    assert data["reason"] == "maintenance"
    assert data["updatedBy"]["email"] == "admin@example.com"

    status_response = client.get("/api/admin/kill", headers=admin_headers)
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["tradingHalted"] is True

    logs = test_db.query(ActivityLog).all()
    assert len(logs) == 1
    assert logs[0].details["halted"] is True
    assert logs[0].details["previous"] is False
    assert logs[0].details["reason"] == "maintenance"

    # reset for other tests
    client.post(
        "/api/admin/kill",
        json={"halt": False, "reason": "resume"},
        headers=admin_headers,
    )


def test_non_admin_cannot_toggle_kill_switch(client: TestClient, test_db, user_headers):
    set_kill(False)

    response = client.post(
        "/api/admin/kill",
        json={"halt": True},
        headers=user_headers,
    )

    assert response.status_code == 403

    assert test_db.query(ActivityLog).count() == 0
