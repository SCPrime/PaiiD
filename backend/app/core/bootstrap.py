"""Shared startup helpers for PaiiD services."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import Settings
from .prelaunch import ValidationRecord, ValidationReport, mask_secret, run_prelaunch_validations


def _format_metadata_lines(settings: Settings, *, application: str, env_path: Path | None) -> list[str]:
    lines: list[str] = [f"===== {application.upper()} STARTUP ====="]

    if env_path is not None:
        exists = env_path.exists()
        lines.append(f".env path: {env_path}")
        lines.append(f".env exists: {exists}")

    lines.append(f"Environment profile: {settings.environment_label} ({settings.APP_ENV})")
    lines.append(f"Git commit: {settings.GIT_COMMIT or 'unknown'}")
    if settings.RELEASE_VERSION:
        lines.append(f"Release version: {settings.RELEASE_VERSION}")

    lines.append(
        "API token: "
        f"{mask_secret(settings.API_TOKEN)} | "
        f"Tradier key: {mask_secret(settings.TRADIER_API_KEY)}"
    )
    lines.append(
        "Sentry: "
        + ("ENABLED" if settings.SENTRY_DSN else "disabled")
        + " | CORS origin: "
        + (settings.ALLOW_ORIGIN or "<default>")
    )

    return lines


def _format_validation_lines(report: ValidationReport) -> Iterable[str]:
    yield "===== PRELAUNCH VALIDATION ====="

    for record in report.checks:
        status = "PASS" if record.passed else ("WARN" if record.severity == "warning" else "FAIL")
        yield f"[{status}] {record.name}: {record.detail}"
        if not record.passed:
            yield f"        Remediation: {record.remediation}"

    if report.has_errors:
        yield "❌ Prelaunch validation failed - resolve the errors above before production deploy."
    elif report.has_warnings:
        yield "⚠️  Prelaunch validation completed with warnings."
    else:
        yield "✅ All prelaunch validations passed."

    yield "==============================="


def emit_startup_summary(
    *,
    settings: Settings,
    application: str = "paiid-backend",
    env_path: Path | None = None,
) -> ValidationReport:
    """Log startup metadata and validation results for the given service."""

    metadata_lines = _format_metadata_lines(settings, application=application, env_path=env_path)
    validation_report = run_prelaunch_validations(settings)
    validation_lines = list(_format_validation_lines(validation_report))

    for line in (*metadata_lines, "", *validation_lines, ""):
        print(line, flush=True)

    return validation_report


__all__ = ["emit_startup_summary", "ValidationRecord", "ValidationReport"]
