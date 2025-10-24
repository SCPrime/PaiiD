import importlib
import sys

import pytest


@pytest.fixture(autouse=True)
def cleanup_main_module():
    sys.modules.pop("app.main", None)
    sys.modules.pop("app.core.config", None)
    yield
    sys.modules.pop("app.main", None)
    sys.modules.pop("app.core.config", None)


def _load_main(monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LIVE_TRADING", "false")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("API_TOKEN", "test-token")
    monkeypatch.setenv("TRADIER_API_KEY", "")
    return importlib.import_module("app.main")


def test_sentry_enabled_when_dsn(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "https://example.com/123")
    monkeypatch.setenv("SENTRY_TRACES_SAMPLE_RATE", "0.5")
    monkeypatch.setenv("SENTRY_PROFILES_SAMPLE_RATE", "0.5")

    import sentry_sdk

    init_calls: list[tuple[tuple, dict]] = []
    monkeypatch.setattr(sentry_sdk, "init", lambda *a, **k: init_calls.append((a, k)))

    module = _load_main(monkeypatch)

    middleware_names = [middleware.cls.__name__ for middleware in module.app.user_middleware]

    assert "SentryContextMiddleware" in middleware_names
    assert init_calls, "Expected Sentry to initialize when DSN present"
    assert init_calls[0][1]["dsn"] == "https://example.com/123"


def test_sentry_disabled_without_dsn(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    monkeypatch.delenv("RENDER_SENTRY_DSN", raising=False)
    monkeypatch.delenv("SENTRY_BACKEND_DSN", raising=False)

    import sentry_sdk

    monkeypatch.setattr(sentry_sdk, "init", pytest.fail)

    module = _load_main(monkeypatch)

    middleware_names = [middleware.cls.__name__ for middleware in module.app.user_middleware]

    assert "SentryContextMiddleware" not in middleware_names
