"""Health check endpoint tests."""


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_detailed_health_requires_auth(client):
    response = client.get("/api/health/detailed")
    assert response.status_code == 403
