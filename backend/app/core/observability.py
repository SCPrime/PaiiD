"""Observability helpers for logging, tracing, and error ingestion."""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import TYPE_CHECKING, Any

try:  # pragma: no cover - fallback path exercised in tests without dependency
    from pythonjsonlogger import jsonlogger
except ModuleNotFoundError:  # pragma: no cover - fallback implementation
    class _SimpleJsonFormatter(logging.Formatter):
        def __init__(self, fmt: str | None = None, rename_fields: dict[str, str] | None = None):
            super().__init__()
            self.rename_fields = rename_fields or {}

        def format(self, record: logging.LogRecord) -> str:
            payload: dict[str, Any] = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage(),
                "file": record.filename,
                "line": record.lineno,
            }

            reserved = {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }

            for key, value in record.__dict__.items():
                if key in reserved or key in payload:
                    continue
                payload[key] = value

            for source, target in self.rename_fields.items():
                if source in payload:
                    payload[target] = payload.pop(source)

            return json.dumps(payload, default=str)

    class jsonlogger:  # type: ignore[no-redef]
        JsonFormatter = _SimpleJsonFormatter

if TYPE_CHECKING:  # pragma: no cover - used only for static analysis
    from .config import Settings


logger = logging.getLogger("paiid.observability")

_logging_configured = False
_datadog_initialized = False


def configure_logging(log_level: str | None = None) -> None:
    """Configure structured JSON logging for the entire application."""

    global _logging_configured

    if _logging_configured:
        return

    resolved_level = (log_level or os.getenv("LOG_LEVEL", "INFO")).upper()
    logging.captureWarnings(True)

    root_logger = logging.getLogger()
    root_logger.setLevel(resolved_level)

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(filename)s %(lineno)d %(dd.trace_id)s %(dd.span_id)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "filename": "file",
            "lineno": "line",
        },
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    for noisy_logger in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logging.getLogger(noisy_logger).handlers = []
        logging.getLogger(noisy_logger).propagate = True

    logger.debug("Structured logging configured", extra={"event": "logging_configured"})
    _logging_configured = True


def init_datadog(settings: "Settings") -> bool:
    """Initialize Datadog tracing if enabled."""

    global _datadog_initialized

    if _datadog_initialized or not settings.DATADOG_TRACE_ENABLED:
        return False

    try:
        from ddtrace import config, patch_all
    except ImportError:  # pragma: no cover - safety guard when optional dep missing
        logger.warning(
            "Datadog tracing requested but ddtrace is not installed",
            extra={"event": "datadog_missing_dependency"},
        )
        return False

    os.environ.setdefault("DD_SERVICE", settings.DATADOG_SERVICE_NAME)
    os.environ.setdefault("DD_ENV", settings.DATADOG_ENVIRONMENT)
    if settings.DATADOG_TRACE_AGENT_URL:
        os.environ.setdefault("DD_TRACE_AGENT_URL", settings.DATADOG_TRACE_AGENT_URL)

    patch_all(logging=True)
    config.fastapi["service_name"] = settings.DATADOG_SERVICE_NAME
    config.asgi["service_name"] = settings.DATADOG_SERVICE_NAME

    logger.info(
        "Datadog tracing enabled",
        extra={
            "event": "datadog_initialized",
            "service": settings.DATADOG_SERVICE_NAME,
            "environment": settings.DATADOG_ENVIRONMENT,
        },
    )

    _datadog_initialized = True
    return True


def init_sentry(settings: "Settings") -> bool:
    """Initialize Sentry error tracking if a DSN is present."""

    if not settings.SENTRY_DSN:
        logger.warning(
            "Sentry DSN not configured - error tracking disabled",
            extra={"event": "sentry_disabled"},
        )
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
    except ImportError:  # pragma: no cover - optional dependency guard
        logger.exception(
            "sentry-sdk is not installed; cannot initialize Sentry",
            extra={"event": "sentry_missing_dependency"},
        )
        return False

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
        environment=settings.SENTRY_ENVIRONMENT,
        release=settings.SENTRY_RELEASE,
        send_default_pii=False,
        before_send=_redact_authorization_header,
    )

    logger.info(
        "Sentry error tracking initialized",
        extra={"event": "sentry_initialized", "environment": settings.SENTRY_ENVIRONMENT},
    )
    return True


def wrap_with_new_relic(app: Any, settings: "Settings") -> Any:
    """Wrap the ASGI app with the New Relic agent when enabled."""

    if not settings.NEW_RELIC_ENABLED:
        return app

    try:
        import newrelic.agent
    except ImportError:  # pragma: no cover - optional dependency guard
        logger.warning(
            "New Relic requested but newrelic package is not installed",
            extra={"event": "new_relic_missing_dependency"},
        )
        return app

    config_file = settings.NEW_RELIC_CONFIG_FILE
    if config_file and not os.path.exists(config_file):
        logger.error(
            "New Relic config file not found",
            extra={"event": "new_relic_missing_config", "config_file": config_file},
        )
        return app

    try:
        if config_file:
            newrelic.agent.initialize(config_file, environment=settings.NEW_RELIC_ENVIRONMENT)
        else:
            newrelic.agent.initialize()  # Relies on environment variables if present

        newrelic.agent.register_application(timeout=5.0)
        logger.info(
            "New Relic agent initialized",
            extra={
                "event": "new_relic_initialized",
                "environment": settings.NEW_RELIC_ENVIRONMENT,
                "app_name": settings.NEW_RELIC_APP_NAME,
            },
        )
        return newrelic.agent.ASGIApplicationWrapper(app)
    except Exception:  # pragma: no cover - guard against initialization failure
        logger.exception(
            "Failed to initialize New Relic agent",
            extra={"event": "new_relic_initialization_failed"},
        )
        return app


def verify_error_ingestion(settings: "Settings") -> bool:
    """Optionally emit a synthetic error for pipeline verification."""

    if not settings.OBSERVABILITY_VERIFY_ON_STARTUP:
        return False

    verification_error = RuntimeError("Observability verification exception")
    logger.info(
        "Running observability verification", extra={"event": "observability_verification_start"}
    )

    try:
        raise verification_error
    except RuntimeError as exc:
        logger.exception(
            "Synthetic verification exception generated",
            extra={"event": "observability_verification_exception"},
        )

        try:
            import sentry_sdk

            sentry_sdk.capture_exception(exc)
        except Exception:  # pragma: no cover - Sentry capture should not fail app startup
            logger.exception(
                "Failed to send verification exception to Sentry",
                extra={"event": "observability_verification_sentry_failed"},
            )

        try:
            from ddtrace import tracer

            span = tracer.current_span()
            if span:
                span.set_tag("observability.verification", True)
                span.set_tag("error.message", str(exc))
            logger.error(
                "Datadog observability verification log",
                extra={"event": "observability_verification_datadog"},
            )
        except Exception:  # pragma: no cover - ddtrace may be unavailable
            logger.debug(
                "Datadog tracer not available for verification",
                extra={"event": "observability_verification_datadog_skipped"},
            )

        try:
            import newrelic.agent

            newrelic.agent.record_custom_event(
                "ObservabilityVerification",
                {"message": str(exc), "environment": settings.NEW_RELIC_ENVIRONMENT},
            )
        except Exception:  # pragma: no cover - newrelic may be unavailable
            logger.debug(
                "New Relic agent not available for verification",
                extra={"event": "observability_verification_new_relic_skipped"},
            )

    return True


def _redact_authorization_header(event: dict[str, Any], hint: dict[str, Any] | None) -> dict[str, Any]:
    """Remove Authorization headers from outbound Sentry payloads."""

    request_data = event.get("request", {})
    headers = request_data.get("headers", {})
    if "Authorization" in headers:
        headers["Authorization"] = "[REDACTED]"
        request_data["headers"] = headers
        event["request"] = request_data
    return event

