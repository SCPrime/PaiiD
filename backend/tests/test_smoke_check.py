"""Unit tests for the Alpaca smoke check script."""

from __future__ import annotations

from types import SimpleNamespace

from scripts import smoke_check


def test_smoke_check_missing_keys(monkeypatch):
    """If required Alpaca keys are absent the script should fail fast."""
    monkeypatch.setattr(
        smoke_check,
        "settings",
        SimpleNamespace(ALPACA_API_KEY="", ALPACA_SECRET_KEY="", TESTING=False),
    )

    exit_code = smoke_check.main()

    assert exit_code == 1


def test_smoke_check_testing_mode_short_circuit(monkeypatch):
    """When TESTING is true the script should skip live Alpaca calls."""
    monkeypatch.setattr(
        smoke_check,
        "settings",
        SimpleNamespace(ALPACA_API_KEY="key", ALPACA_SECRET_KEY="secret", TESTING=True),
    )

    def _unexpected_call():  # pragma: no cover - defensive guard
        raise AssertionError("get_alpaca_client should not be called in testing mode")

    monkeypatch.setattr(smoke_check, "get_alpaca_client", _unexpected_call)

    exit_code = smoke_check.main()

    assert exit_code == 0
