"""Pre-launch validation routines for the PaiiD backend.

The validator performs a series of defensive checks before the FastAPI
application is started.  Each check reports a structured result so the
caller (CLI, shell script, or the ASGI app itself) can decide whether to
continue bootstrapping the service.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Iterable, List

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ValidationCheck:
    """Represents the outcome of a validation step."""

    name: str
    passed: bool
    message: str

    def as_dict(self) -> dict[str, str | bool]:
        return {"name": self.name, "passed": self.passed, "message": self.message}


class PrelaunchValidationError(RuntimeError):
    """Raised when one or more validation checks fail."""

    def __init__(self, failed_checks: Iterable[ValidationCheck]):
        checks = list(failed_checks)
        super().__init__(
            "Pre-launch validation failed for checks: "
            + ", ".join(check.name for check in checks)
        )
        self.failed_checks: List[ValidationCheck] = checks


MINIMUM_PYTHON = (3, 10)
DEFAULT_REQUIRED_BINARIES = ("uvicorn", "alembic")


def _resolve_required_env_vars() -> tuple[str, ...]:
    base = ["API_TOKEN", "TRADIER_API_KEY"]
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment in {"production", "staging"}:
        base.append("SENTRY_DSN")
    return tuple(base)


def _resolve_ports() -> tuple[int, ...]:
    raw_ports = os.getenv("PRELAUNCH_REQUIRED_PORTS")
    if not raw_ports:
        return (8000,)
    parsed: list[int] = []
    for candidate in raw_ports.split(","):
        candidate = candidate.strip()
        if not candidate:
            continue
        try:
            parsed.append(int(candidate))
        except ValueError:
            logger.warning("Ignoring invalid port declaration in PRELAUNCH_REQUIRED_PORTS: %s", candidate)
    return tuple(parsed or (8000,))


DEFAULT_REQUIRED_ENV_VARS = _resolve_required_env_vars()
DEFAULT_PORTS = _resolve_ports()


def check_python_version(min_version: tuple[int, int] = MINIMUM_PYTHON) -> ValidationCheck:
    current = sys.version_info
    passed = (current.major, current.minor) >= min_version[:2]
    message = (
        f"Python {current.major}.{current.minor}.{current.micro} detected"
        if passed
        else (
            "Python "
            f"{current.major}.{current.minor}.{current.micro} "
            f"does not meet minimum {min_version[0]}.{min_version[1]}"
        )
    )
    return ValidationCheck(name="python_version", passed=passed, message=message)


def check_binaries(binaries: Iterable[str]) -> List[ValidationCheck]:
    checks: List[ValidationCheck] = []
    for binary in binaries:
        path = which(binary)
        passed = path is not None
        message = f"{binary} found at {path}" if passed else f"{binary} executable not found in PATH"
        checks.append(ValidationCheck(name=f"binary:{binary}", passed=passed, message=message))
    return checks


def check_environment_variables(env_vars: Iterable[str]) -> List[ValidationCheck]:
    checks: List[ValidationCheck] = []
    for key in env_vars:
        value = os.getenv(key)
        passed = bool(value)
        message = "set" if passed else "missing"
        checks.append(ValidationCheck(name=f"env:{key}", passed=passed, message=f"Environment variable {key} {message}"))
    return checks


def check_port_availability(ports: Iterable[int]) -> List[ValidationCheck]:
    checks: List[ValidationCheck] = []
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            result = sock.connect_ex(("127.0.0.1", port))
            passed = result != 0
            message = (
                f"Port {port} is available"
                if passed
                else f"Port {port} is already in use"
            )
            checks.append(ValidationCheck(name=f"port:{port}", passed=passed, message=message))
    return checks


def check_env_file() -> ValidationCheck:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    exists = env_path.exists()
    environment = os.getenv("ENVIRONMENT", "development").lower()
    required = environment in {"production", "staging"}
    passed = exists or not required
    if exists:
        message = f".env file located at {env_path}"
    elif required:
        message = ".env file missing"
    else:
        message = ".env file missing (allowed in development/testing)"
    return ValidationCheck(name="env_file", passed=passed, message=message)


def run_prelaunch_validation() -> List[ValidationCheck]:
    """Run all validation checks and return their results."""

    checks: List[ValidationCheck] = []
    checks.append(check_python_version())
    checks.extend(check_binaries(DEFAULT_REQUIRED_BINARIES))
    checks.extend(check_environment_variables(DEFAULT_REQUIRED_ENV_VARS))
    checks.extend(check_port_availability(DEFAULT_PORTS))
    checks.append(check_env_file())
    return checks


def ensure_prelaunch_validation(success_required: bool = True) -> List[ValidationCheck]:
    """Execute all validation checks and optionally raise when failures occur."""

    checks = run_prelaunch_validation()
    failed = [check for check in checks if not check.passed]

    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        logger.info("[PRELAUNCH][%s] %s :: %s", status, check.name, check.message)

    if failed and success_required:
        raise PrelaunchValidationError(failed)
    return checks


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    checks = ensure_prelaunch_validation(success_required=True)
    payload = [check.as_dict() for check in checks]
    print(json.dumps({"checks": payload}, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    try:
        raise SystemExit(main())
    except PrelaunchValidationError as exc:  # pragma: no cover - CLI entry point
        payload = [check.as_dict() for check in exc.failed_checks]
        print(json.dumps({"checks": payload}, indent=2))
        raise SystemExit(1) from exc
