"""Unit tests for the pre-launch validation helpers."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType

import pytest


def reload_prelaunch_module() -> ModuleType:
    """Reload the prelaunch module with the current environment."""

    module_name = "app.core.prelaunch"
    if module_name in sys.modules:
        del sys.modules[module_name]
    return importlib.import_module(module_name)


def test_required_env_vars_include_sentry_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("API_TOKEN", "test")
    monkeypatch.setenv("TRADIER_API_KEY", "test")
    monkeypatch.setenv("PRELAUNCH_REQUIRED_PORTS", "65500")
    monkeypatch.delenv("SENTRY_DSN", raising=False)

    prelaunch = reload_prelaunch_module()

    with pytest.raises(prelaunch.PrelaunchValidationError):
        prelaunch.ensure_prelaunch_validation(success_required=True)


def test_prelaunch_passes_with_minimal_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("API_TOKEN", "test")
    monkeypatch.setenv("TRADIER_API_KEY", "test")
    monkeypatch.setenv("PRELAUNCH_REQUIRED_PORTS", "65500")
    monkeypatch.delenv("SENTRY_DSN", raising=False)

    prelaunch = reload_prelaunch_module()

    results = prelaunch.ensure_prelaunch_validation(success_required=False)
    assert any(check.name == "port:65500" for check in results)
    assert not any(check.name == "env:SENTRY_DSN" for check in results)


def test_fixture_mode_toggle_via_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_FIXTURE_DATA", "false")
    prelaunch_services = importlib.import_module("app.services.fixture_loader")
    assert prelaunch_services.should_use_fixture_mode(False, "options") is True
    assert prelaunch_services.should_use_fixture_mode(False, "OPTIONS") is True
    assert prelaunch_services.should_use_fixture_mode(False, None) is False
    assert prelaunch_services.should_use_fixture_mode(True, None) is True
