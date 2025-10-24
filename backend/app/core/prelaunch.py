"""Pre-launch environment checks for PaiiD backend."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


def _env_flag(name: str, default: bool = False) -> bool:
    """Return truthy configuration flag from environment variables."""

    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}

logger = logging.getLogger("paiid.prelaunch")


CheckStatus = Literal["pass", "warn", "fail"]


@dataclass(slots=True)
class CheckResult:
    """Result for a single pre-launch check."""

    name: str
    status: CheckStatus
    message: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "status": self.status,
            "message": self.message,
        }
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload


class PrelaunchError(RuntimeError):
    """Raised when pre-launch checks fail."""


def _mask(value: str | None) -> str:
    if not value:
        return "<unset>"
    if len(value) <= 4:
        return "****"
    return f"****{value[-4:]}"


def _check_env_var(
    key: str,
    *,
    required: bool,
    guidance: str,
    metadata: dict[str, Any] | None = None,
) -> CheckResult:
    value = os.getenv(key, "").strip()
    status: CheckStatus
    message: str
    if value:
        status = "pass"
        message = f"{key} detected"
    elif required:
        status = "fail"
        message = f"{key} missing - {guidance}"
    else:
        status = "warn"
        message = f"{key} not configured - {guidance}"

    merged_metadata = {"value": _mask(value)}
    if metadata:
        merged_metadata.update(metadata)
    return CheckResult(name=key, status=status, message=message, metadata=merged_metadata)


def _detect_environment() -> str:
    if os.getenv("RENDER_EXTERNAL_URL"):
        return "render"
    if os.getenv("CI"):
        return "ci"
    return "local"


def _collect_checks(environment: str) -> list[CheckResult]:
    checks: list[CheckResult] = []

    env_path = Path(__file__).parent.parent / ".env"
    checks.append(
        CheckResult(
            name="env_file",
            status="pass" if env_path.exists() else "warn",
            message=(
                ".env discovered" if env_path.exists() else ".env missing - fallback to process environment"
            ),
            metadata={"path": str(env_path), "exists": env_path.exists()},
        )
    )

    # Critical env vars required for every deployment target
    checks.extend(
        [
            _check_env_var(
                "API_TOKEN",
                required=True,
                guidance="Set API_TOKEN for internal authentication (Render → Environment)",
            ),
            _check_env_var(
                "TRADIER_API_KEY",
                required=True,
                guidance="Add Tradier API key to backend environment variables",
            ),
        ]
    )

    # Tradier account ID is optional locally but required in hosted environments
    checks.append(
        _check_env_var(
            "TRADIER_ACCOUNT_ID",
            required=environment != "local",
            guidance="Populate with your Tradier account identifier",
            metadata={"environment": environment},
        )
    )

    # Database/Redis become mandatory on Render/CI where migrations will run
    checks.append(
        _check_env_var(
            "DATABASE_URL",
            required=environment in {"render", "ci"},
            guidance="Provision Render PostgreSQL and set DATABASE_URL",
            metadata={"environment": environment},
        )
    )
    checks.append(
        _check_env_var(
            "REDIS_URL",
            required=environment in {"render", "ci"},
            guidance="Enable Render Redis and copy the connection URL",
            metadata={"environment": environment},
        )
    )

    # Sentry DSN is required in hosted environments to satisfy TODO compliance
    require_sentry = environment in {"render", "ci"} and not _env_flag(
        "PRELAUNCH_ALLOW_MISSING_SENTRY",
        default=False,
    )
    checks.append(
        _check_env_var(
            "SENTRY_DSN",
            required=require_sentry,
            guidance="Create Sentry project and paste DSN (Render secret)",
            metadata={
                "environment": environment,
                "allow_missing": not require_sentry,
            },
        )
    )

    # Ensure log level sanity for automation
    checks.append(
        CheckResult(
            name="log_level",
            status="pass",
            message=f"LOG_LEVEL={os.getenv('LOG_LEVEL', 'INFO')} (default INFO)",
            metadata={"value": os.getenv("LOG_LEVEL", "INFO")},
        )
    )

    return checks


def run_prelaunch_checks(
    *,
    emit_json: bool = False,
    raise_on_error: bool = False,
    context: str = "cli",
) -> dict[str, Any]:
    """Run pre-launch validation checks.

    Args:
        emit_json: When True, print JSON payload to stdout.
        raise_on_error: Raise :class:`PrelaunchError` if any check fails.
        context: Identifier for the execution context (cli, start.sh, uvicorn-import, etc.).

    Returns:
        Dictionary payload describing the check results.
    """

    environment = _detect_environment()
    checks = _collect_checks(environment)

    status: CheckStatus = "pass"
    for check in checks:
        if check.status == "fail":
            status = "fail"
            break
        if check.status == "warn" and status != "fail":
            status = "warn"

    report = {
        "context": context,
        "environment": environment,
        "status": status,
        "checks": [check.to_dict() for check in checks],
    }

    for check in checks:
        log_method = logger.info
        if check.status == "warn":
            log_method = logger.warning
        elif check.status == "fail":
            log_method = logger.error
        log_method("[prelaunch] %s - %s", check.name, check.message, extra={"metadata": check.metadata})

    if emit_json:
        print(json.dumps(report, default=str))

    if status == "fail" and raise_on_error:
        failed = [c for c in checks if c.status == "fail"]
        raise PrelaunchError(
            "; ".join(f"{item.name}: {item.message}" for item in failed)
        )

    return report


__all__ = ["CheckResult", "PrelaunchError", "run_prelaunch_checks"]
