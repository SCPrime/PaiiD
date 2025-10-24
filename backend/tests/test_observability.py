import json
import logging

from app.core import observability
from app.core.config import Settings


def reset_logging_state() -> None:
    observability._logging_configured = False  # type: ignore[attr-defined]
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)


def test_configure_logging_uses_json_formatter():
    reset_logging_state()

    observability.configure_logging("DEBUG")

    root = logging.getLogger()
    assert root.handlers, "Root logger should have handlers after configuration"
    formatter = root.handlers[0].formatter

    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="test-message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["message"] == "test-message"
    assert data["level"] == "INFO"


def test_init_sentry_without_dsn_returns_false():
    settings = Settings(SENTRY_DSN=None)

    assert observability.init_sentry(settings) is False


def test_wrap_with_new_relic_disabled_returns_same_app():
    dummy_app = object()
    settings = Settings(NEW_RELIC_ENABLED=False)

    assert observability.wrap_with_new_relic(dummy_app, settings) is dummy_app


def test_verify_error_ingestion_disabled_returns_false():
    settings = Settings(OBSERVABILITY_VERIFY_ON_STARTUP=False)

    assert observability.verify_error_ingestion(settings) is False

