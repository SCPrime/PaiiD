"""Prelaunch environment validation utilities."""

from __future__ import annotations

import logging
import os
import socket
import sys
from dataclasses import dataclass, field
from shutil import which
from typing import Iterable, Tuple


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PrelaunchConfig:
    """Configuration for prelaunch validation checks."""

    min_python: tuple[int, int] = (3, 11)
    required_binaries: tuple[str, ...] = ("alembic", "uvicorn")
    port_env: str = "PORT"
    default_port: int = 8001
    host: str = "0.0.0.0"


@dataclass
class ValidationResult:
    """Aggregate result of all validation checks."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


DEFAULT_CONFIG = PrelaunchConfig()


def _format_version(version: Iterable[int]) -> str:
    return ".".join(str(part) for part in version)


def _check_python_version(min_version: Tuple[int, ...], result: ValidationResult) -> None:
    current = sys.version_info[: len(min_version)]
    minimum = tuple(min_version)

    if current < minimum:
        message = (
            "Python runtime is below the supported version. "
            f"Detected {_format_version(current)}, minimum required {_format_version(minimum)}."
        )
        result.errors.append(message)
        logger.error(
            "Prelaunch check failed: unsupported Python version",
            extra={
                "event": "prelaunch.python_version",
                "status": "error",
                "current_version": _format_version(current),
                "minimum_version": _format_version(minimum),
            },
        )
    else:
        logger.info(
            "Prelaunch check passed: Python version supported",
            extra={
                "event": "prelaunch.python_version",
                "status": "ok",
                "current_version": _format_version(current),
                "minimum_version": _format_version(minimum),
            },
        )


def _check_binaries(binaries: Iterable[str], result: ValidationResult) -> None:
    for binary in binaries:
        path = which(binary)
        if not path:
            message = f"Required executable '{binary}' is not available on PATH."
            result.errors.append(message)
            logger.error(
                "Prelaunch check failed: binary missing",
                extra={
                    "event": "prelaunch.binary",
                    "status": "error",
                    "binary": binary,
                },
            )
        else:
            logger.info(
                "Prelaunch check passed: binary available",
                extra={
                    "event": "prelaunch.binary",
                    "status": "ok",
                    "binary": binary,
                    "path": path,
                },
            )


def _resolve_port(config: PrelaunchConfig, result: ValidationResult) -> tuple[int | None, str | None]:
    raw_value = os.getenv(config.port_env)
    if raw_value in (None, ""):
        logger.info(
            "Prelaunch using default port value",
            extra={
                "event": "prelaunch.port",
                "status": "default",
                "port": config.default_port,
                "source": "default",
            },
        )
        return config.default_port, "default"

    try:
        port = int(raw_value)
    except ValueError:
        message = (
            f"Environment variable {config.port_env} must be an integer, "
            f"received '{raw_value}'."
        )
        result.errors.append(message)
        logger.error(
            "Prelaunch check failed: invalid port value",
            extra={
                "event": "prelaunch.port",
                "status": "error",
                "port_value": raw_value,
                "reason": "not_an_integer",
            },
        )
        return None, None

    if port <= 0 or port > 65535:
        message = (
            f"Environment variable {config.port_env} must be between 1 and 65535, "
            f"received {port}."
        )
        result.errors.append(message)
        logger.error(
            "Prelaunch check failed: port out of range",
            extra={
                "event": "prelaunch.port",
                "status": "error",
                "port": port,
                "reason": "out_of_range",
            },
        )
        return None, None

    logger.info(
        "Prelaunch using configured port value",
        extra={
            "event": "prelaunch.port",
            "status": "configured",
            "port": port,
            "source": config.port_env,
        },
    )
    return port, config.port_env


def _is_port_available(port: int, host: str) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def _check_port_availability(config: PrelaunchConfig, result: ValidationResult) -> None:
    skip_env = os.getenv("SKIP_PORT_CHECKS", "false").lower() == "true"
    testing_mode = os.getenv("TESTING", "false").lower() == "true"

    if skip_env or testing_mode:
        reason = "testing" if testing_mode else "disabled_via_env"
        logger.info(
            "Skipping prelaunch port availability check",
            extra={
                "event": "prelaunch.port_availability",
                "status": "skipped",
                "reason": reason,
            },
        )
        return

    port, source = _resolve_port(config, result)
    if port is None:
        return

    if _is_port_available(port, config.host):
        logger.info(
            "Prelaunch check passed: port is available",
            extra={
                "event": "prelaunch.port_availability",
                "status": "ok",
                "port": port,
                "source": source,
            },
        )
    else:
        message = f"Port {port} on host {config.host} is already in use."
        result.errors.append(message)
        logger.error(
            "Prelaunch check failed: port unavailable",
            extra={
                "event": "prelaunch.port_availability",
                "status": "error",
                "port": port,
                "source": source,
            },
        )


def validate_environment(config: PrelaunchConfig = DEFAULT_CONFIG) -> ValidationResult:
    """Run all prelaunch validation checks."""

    result = ValidationResult()
    _check_python_version(config.min_python, result)
    _check_binaries(config.required_binaries, result)
    _check_port_availability(config, result)
    return result


def run_prelaunch_checks(
    *, config: PrelaunchConfig = DEFAULT_CONFIG, raise_on_failure: bool = False
) -> ValidationResult:
    """Execute validation checks and optionally abort on failure."""

    result = validate_environment(config)

    if result.ok:
        logger.info(
            "Prelaunch validation completed successfully",
            extra={
                "event": "prelaunch.summary",
                "status": "ok",
            },
        )
    else:
        logger.error(
            "Prelaunch validation detected blocking issues",
            extra={
                "event": "prelaunch.summary",
                "status": "error",
                "error_count": len(result.errors),
            },
        )
        if raise_on_failure:
            raise SystemExit(1)

    return result


def main() -> int:
    """CLI entry point used by deployment scripts."""

    result = run_prelaunch_checks(raise_on_failure=False)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
