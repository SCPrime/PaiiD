"""Pre-launch validation checks executed during application startup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .config import Settings


SeverityLevel = Literal["error", "warning"]


@dataclass(slots=True)
class ValidationRecord:
    """Outcome for a single pre-launch validation."""

    name: str
    passed: bool
    detail: str
    remediation: str
    severity: SeverityLevel = "error"


@dataclass(slots=True)
class ValidationReport:
    """Collection of validation results with helper utilities."""

    checks: list[ValidationRecord]

    @property
    def has_errors(self) -> bool:
        return any(not record.passed and record.severity == "error" for record in self.checks)

    @property
    def has_warnings(self) -> bool:
        return any(not record.passed and record.severity == "warning" for record in self.checks)

    def to_dict(self) -> dict:
        return {
            "checks": [record.__dict__ for record in self.checks],
            "has_errors": self.has_errors,
            "has_warnings": self.has_warnings,
        }


def mask_secret(value: str | None, *, prefix: int = 4, suffix: int = 2) -> str:
    """Redact a secret while leaving a small prefix/suffix for debugging."""

    if not value:
        return "[NOT SET]"

    value = value.strip()
    if len(value) <= prefix + suffix:
        return "*" * len(value)

    return f"{value[:prefix]}…{value[-suffix:]}"


def run_prelaunch_validations(settings: Settings) -> ValidationReport:
    """Execute a collection of configuration validations."""

    checks: list[ValidationRecord] = []

    def add_check(
        name: str,
        condition: bool,
        success_detail: str,
        failure_detail: str,
        remediation: str,
        *,
        severity: SeverityLevel = "error",
    ) -> None:
        checks.append(
            ValidationRecord(
                name=name,
                passed=bool(condition),
                detail=success_detail if condition else failure_detail,
                remediation=remediation,
                severity=severity,
            )
        )

    normalized_env = settings.app_env
    recognized_envs = {"local", "development", "dev", "test", "staging", "preview", "production"}

    add_check(
        name="environment-profile",
        condition=normalized_env in recognized_envs,
        success_detail=f"Environment profile '{settings.environment_label}' recognized",
        failure_detail=f"Unknown APP_ENV profile: {settings.APP_ENV!r}",
        remediation="Set APP_ENV to one of: local, development, test, staging, preview, production.",
    )

    add_check(
        name="api-token",
        condition=settings.API_TOKEN and settings.API_TOKEN != "change-me",
        success_detail=f"API token configured ({mask_secret(settings.API_TOKEN)})",
        failure_detail="API_TOKEN is missing or still set to the placeholder value",
        remediation="Generate a strong shared secret and set API_TOKEN in the environment.",
    )

    add_check(
        name="tradier-api-key",
        condition=bool(settings.TRADIER_API_KEY),
        success_detail=f"Tradier API key present ({mask_secret(settings.TRADIER_API_KEY)})",
        failure_detail="TRADIER_API_KEY is not configured",
        remediation="Create or retrieve a Tradier API token and set TRADIER_API_KEY.",
    )

    add_check(
        name="sentry-dsn",
        condition=bool(settings.SENTRY_DSN) or normalized_env in {"local", "development", "dev", "test"},
        success_detail=(
            "Sentry DSN configured"
            if settings.SENTRY_DSN
            else "Sentry disabled for local/test environments"
        ),
        failure_detail="SENTRY_DSN must be configured for staging/preview/production",
        remediation="Provision a Sentry project and add the DSN to the environment.",
    )

    add_check(
        name="allow-origin",
        condition=bool(settings.ALLOW_ORIGIN) or normalized_env in {"local", "development", "dev", "test"},
        success_detail=(
            f"CORS origin set to {settings.ALLOW_ORIGIN}"
            if settings.ALLOW_ORIGIN
            else "CORS origin skipped for local/test"
        ),
        failure_detail="ALLOW_ORIGIN missing for remote deployment",
        remediation="Set ALLOW_ORIGIN to the trusted frontend base URL.",
        severity="warning",
    )

    add_check(
        name="alpaca-paper-credentials",
        condition=bool(settings.ALPACA_API_KEY and settings.ALPACA_SECRET_KEY),
        success_detail="Alpaca paper trading credentials detected",
        failure_detail="Alpaca paper trading credentials are incomplete",
        remediation="Set ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY for paper trading.",
        severity="warning",
    )

    return ValidationReport(checks=checks)
