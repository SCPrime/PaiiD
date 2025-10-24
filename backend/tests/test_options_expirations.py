"""Tests for the /options/expirations endpoint."""

from datetime import datetime, timedelta
from typing import List

import pytest

from app.routers import options as options_router
from app.services import tradier_client as tradier_module


class StubTradierClient:
    """Simple stub returning configurable expiration payloads."""

    def __init__(self, expirations: List[str] | None = None, error: Exception | None = None):
        self._expirations = expirations or []
        self._error = error
        self.calls = 0

    def get_option_expirations(self, symbol: str):
        self.calls += 1
        if self._error:
            raise self._error
        return {"expirations": {"date": self._expirations}}


@pytest.fixture(autouse=True)
def clear_options_cache():
    """Ensure cache state does not leak across tests."""

    options_router.options_cache.clear()
    yield
    options_router.options_cache.clear()


@pytest.fixture
def set_tradier_stub():
    """Helper to patch the global Tradier client singleton."""

    original_get_client = tradier_module.get_tradier_client

    def _set_stub(stub: StubTradierClient):
        tradier_module._tradier_client = stub
        tradier_module.get_tradier_client = lambda: stub  # type: ignore[assignment]
        return stub

    try:
        yield _set_stub
    finally:
        tradier_module.get_tradier_client = original_get_client
        tradier_module._tradier_client = None


def test_get_expiration_dates_success(client, auth_headers, set_tradier_stub):
    today = datetime.now().date()
    expirations = [
        (today + timedelta(days=7)).strftime("%Y-%m-%d"),
        (today + timedelta(days=30)).strftime("%Y-%m-%d"),
    ]
    stub = set_tradier_stub(StubTradierClient(expirations=expirations))

    response = client.get("/api/options/expirations/AAPL", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(expirations)
    for idx, payload in enumerate(data):
        assert payload["date"] == expirations[idx]
        expected_days = (datetime.strptime(expirations[idx], "%Y-%m-%d").date() - today).days
        assert payload["days_to_expiry"] == expected_days
    assert stub.calls == 1


def test_get_expiration_dates_empty_response(client, auth_headers, set_tradier_stub):
    stub = set_tradier_stub(StubTradierClient(expirations=[]))

    response = client.get("/api/options/expirations/MSFT", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []
    assert stub.calls == 1


def test_get_expiration_dates_handles_error(client, auth_headers, set_tradier_stub):
    stub = set_tradier_stub(StubTradierClient(error=Exception("boom")))

    response = client.get("/api/options/expirations/TSLA", headers=auth_headers)

    assert response.status_code == 500
    body = response.json()
    assert "Error fetching expirations" in body["detail"]
    assert stub.calls == 1

