"""Observability and monitoring configuration for MOD SQUAD."""

from __future__ import annotations

import logging
import os
from typing import Any

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .config import settings


logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """Initialize Sentry error tracking and performance monitoring."""

    if not settings.SENTRY_DSN:
        logger.info("Sentry DSN not configured; skipping Sentry initialization")
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        integrations=[
            FastApiIntegration(
                transaction_style="endpoint",
                failed_request_status_codes=[400, 499],
            ),
            SqlalchemyIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
        ],
        # Custom tag enrichment
        before_send=_enrich_sentry_event,
        # Release tracking
        release=os.getenv("RENDER_GIT_COMMIT") or "dev",
    )

    logger.info(
        "Sentry initialized",
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=0.1,
    )


def _enrich_sentry_event(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any]:
    """Attach MOD SQUAD context to Sentry events."""

    event.setdefault("tags", {})
    event["tags"]["modsquad_enabled"] = "true"
    event["tags"]["market_modules"] = os.getenv("MODSQUAD_ACTIVE_MARKET", "stocks_options")

    # Add user context if available
    if "user" in event:
        event["tags"]["user_role"] = event["user"].get("role", "unknown")

    return event


def capture_execution_error(
    strategy_type: str,
    market_key: str,
    user_id: int,
    error: Exception,
    context: dict[str, Any] | None = None,
) -> None:
    """Capture strategy execution errors with rich context."""

    sentry_sdk.set_context(
        "strategy_execution",
        {
            "strategy_type": strategy_type,
            "market_key": market_key,
            "user_id": user_id,
            **(context or {}),
        },
    )
    sentry_sdk.capture_exception(error)


def configure_structured_logging() -> None:
    """Configure structured JSON logging for production."""

    import logging.config

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default" if settings.SENTRY_ENVIRONMENT == "development" else "json",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"],
        },
    }

    try:
        logging.config.dictConfig(logging_config)
        logger.info("Structured logging configured", environment=settings.SENTRY_ENVIRONMENT)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to configure structured logging: %s", exc)


__all__ = ["capture_execution_error", "configure_structured_logging", "init_sentry"]

