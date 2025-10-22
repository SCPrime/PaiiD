"""Tests for the options expirations endpoint."""
from datetime import datetime

import pytest
import requests

from app.core.config import settings
from app.routers import options as options_router


class FakeResponse:
    """Simple response stub for mocking requests."""

    def __init__(self, *, status_code=200, payload=None, text="", raise_http_error=False):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text
        self._raise_http_error = raise_http_error

    def raise_for_status(self):
        if self._raise_http_error:
            error = requests.exceptions.HTTPError(self.text or "error")
            error.response = self
            raise error

    def json(self):
        return self._payload


@pytest.fixture(autouse=True)
def restore_settings(monkeypatch):
    """Ensure sensitive settings are reset after each test."""

    monkeypatch.setattr(settings, "TRADIER_API_KEY", "test-tradier-key", raising=False)
    monkeypatch.setattr(settings, "TRADIER_API_BASE_URL", "https://api.tradier.com/v1", raising=False)
    yield


def test_get_expirations_success(client, auth_headers, monkeypatch):
    payload = {"expirations": {"date": ["2025-10-24", "2025-10-31"]}}
    fake_response = FakeResponse(payload=payload)

    def fake_get(url, *, headers, params, timeout):  # noqa: D401 - signature mirrors requests.get
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-tradier-key"
        assert params == {"symbol": "AAPL", "includeAllRoots": "false"}
        return fake_response

    monkeypatch.setattr(options_router.requests, "get", fake_get)

    response = client.get("/api/expirations/AAPL", headers=auth_headers)
    assert response.status_code == 200

    expected = []
    today = datetime.utcnow().date()
    for date_str in payload["expirations"]["date"]:
        expiry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        expected.append({
            "date": date_str,
            "days_to_expiry": (expiry_date - today).days,
        })

    assert response.json() == expected


def test_get_expirations_handles_http_error(client, auth_headers, monkeypatch):
    fake_response = FakeResponse(status_code=401, text="Unauthorized", raise_http_error=True)

    def fake_get(*args, **kwargs):
        return fake_response

    monkeypatch.setattr(options_router.requests, "get", fake_get)

    response = client.get("/api/expirations/AAPL", headers=auth_headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Tradier API error: Unauthorized"}


def test_get_expirations_handles_request_exception(client, auth_headers, monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.exceptions.RequestException("network down")

    monkeypatch.setattr(options_router.requests, "get", fake_get)

    response = client.get("/api/expirations/AAPL", headers=auth_headers)
    assert response.status_code == 502
    assert response.json() == {"detail": "Unable to reach Tradier API: network down"}


def test_get_expirations_missing_credentials(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "TRADIER_API_KEY", "", raising=False)

    def fake_get(*args, **kwargs):  # pragma: no cover - should not be called
        raise AssertionError("requests.get should not be invoked when credentials are missing")

    monkeypatch.setattr(options_router.requests, "get", fake_get)

    response = client.get("/api/expirations/AAPL", headers=auth_headers)
    assert response.status_code == 500
    assert response.json() == {"detail": "Tradier API credentials not configured"}
