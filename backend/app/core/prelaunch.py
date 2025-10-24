"""Prelaunch environment validation for the PaiiD backend."""

from __future__ import annotations

import logging
import os
import shutil
import socket
import sys
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence


logger = logging.getLogger("app.prelaunch")

MIN_PYTHON_VERSION: tuple[int, int, int] = (3, 11, 0)
REQUIRED_BINARIES: tuple[str, ...] = ("alembic", "uvicorn")
PORT_ENV_VAR = "PORT"
DEFAULT_PORT = 8000


@dataclass(slots=True)
class CheckResult:
    """Represents the outcome of an individual validation step."""

    name: str
    ok: bool
    message: str
    details: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "ok": self.ok,
            "message": self.message,
            "details": self.details,
        }


class PrelaunchCheckError(RuntimeError):
    """Raised when one or more prelaunch checks fail."""

    def __init__(self, failures: Sequence[CheckResult]):
        super().__init__("Prelaunch validation failed")
        self.failures = list(failures)


def _normalize_version_info(version_info: object) -> tuple[int, int, int]:
    """Normalize Python's ``sys.version_info`` for flexible testing."""

    if hasattr(version_info, "major"):
        major = getattr(version_info, "major")
        minor = getattr(version_info, "minor", 0)
        micro = getattr(version_info, "micro", 0)
        return int(major), int(minor), int(micro)

    try:
        major, minor, micro = version_info  # type: ignore[misc]
    except Exception as exc:  # pragma: no cover - defensive
        raise TypeError("Unsupported version_info format") from exc

    return int(major), int(minor), int(micro)


def validate_python_version(
    *,
    minimum: tuple[int, int, int] = MIN_PYTHON_VERSION,
    version_info: object | None = None,
) -> CheckResult:
    """Ensure the interpreter meets the minimum supported version."""

    version_info = version_info or sys.version_info
    current = _normalize_version_info(version_info)
    ok = current >= minimum

    message = (
        "Python version is compatible"
        if ok
        else "Python version is lower than the supported minimum"
    )

    details = {
        "current": ".".join(str(part) for part in current),
        "required": ".".join(str(part) for part in minimum),
    }

    return CheckResult("python_version", ok, message, details)


def validate_binary_dependencies(
    binaries: Iterable[str] = REQUIRED_BINARIES,
    *,
    which: Callable[[str], str | None] | None = None,
) -> list[CheckResult]:
    """Verify that critical command-line tools are available."""

    results: list[CheckResult] = []

    resolver = which or shutil.which

    for binary in binaries:
        resolved_path = resolver(binary)
        ok = resolved_path is not None
        message = (
            "Binary dependency available"
            if ok
            else "Binary dependency is missing from PATH"
        )
        details = {"binary": binary, "resolved_path": resolved_path}
        results.append(CheckResult(f"binary:{binary}", ok, message, details))

    return results


def _resolve_port(
    port: int | None,
    env: Mapping[str, str] | None,
) -> tuple[int | None, dict[str, object]]:
    env_value = (env or os.environ).get(PORT_ENV_VAR)
    metadata: dict[str, object] = {"env_var": PORT_ENV_VAR, "env_value": env_value}

    if port is not None:
        metadata["source"] = "explicit"
        return port, metadata

    if env_value:
        metadata["source"] = "environment"
        try:
            parsed = int(env_value)
        except ValueError:
            metadata["error"] = "non_integer_port"
            return None, metadata
        return parsed, metadata

    metadata["source"] = "default"
    return DEFAULT_PORT, metadata


def validate_port_availability(
    *,
    port: int | None = None,
    env: Mapping[str, str] | None = None,
) -> CheckResult:
    """Confirm that the TCP port required by Uvicorn is available."""

    resolved_port, details = _resolve_port(port, env)

    if resolved_port is None:
        return CheckResult(
            "port_availability",
            False,
            "Port value is not a valid integer",
            details,
        )

    details["port"] = resolved_port

    if not 0 < resolved_port < 65536:
        details["error"] = "out_of_range"
        return CheckResult(
            "port_availability",
            False,
            "Port must be between 1 and 65535",
            details,
        )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", resolved_port))
    except OSError as exc:
        details["error"] = str(exc)
        return CheckResult(
            "port_availability",
            False,
            "Port is already in use or not accessible",
            details,
        )
    finally:
        sock.close()

    return CheckResult(
        "port_availability",
        True,
        "Required port is available",
        details,
    )


def run_prelaunch_checks(
    *,
    raise_on_error: bool = False,
    version_info: object | None = None,
    required_binaries: Iterable[str] | None = None,
    which: Callable[[str], str | None] | None = None,
    port: int | None = None,
    env: Mapping[str, str] | None = None,
) -> list[CheckResult]:
    """Execute all prelaunch validations and optionally raise on failure."""

    logger.info("Starting prelaunch validation", extra={"event": "prelaunch.start"})

    results: list[CheckResult] = []

    results.append(validate_python_version(version_info=version_info))
    resolver = which or shutil.which

    results.extend(
        validate_binary_dependencies(
            tuple(required_binaries) if required_binaries is not None else REQUIRED_BINARIES,
            which=resolver,
        )
    )
    results.append(validate_port_availability(port=port, env=env))

    failures = [result for result in results if not result.ok]

    if failures:
        logger.error(
            "Prelaunch validation failed",
            extra={
                "event": "prelaunch.complete",
                "status": "failed",
                "failures": [failure.to_dict() for failure in failures],
            },
        )
        if raise_on_error:
            raise PrelaunchCheckError(failures)
    else:
        logger.info(
            "Prelaunch validation succeeded",
            extra={
                "event": "prelaunch.complete",
                "status": "passed",
                "checks": [result.to_dict() for result in results],
            },
        )

    return results


def ensure_prelaunch_ready() -> None:
    """Run validations and raise ``PrelaunchCheckError`` on failure."""

    run_prelaunch_checks(raise_on_error=True)


def main() -> int:
    """CLI entry-point used by deployment scripts."""

    try:
        ensure_prelaunch_ready()
    except PrelaunchCheckError:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via CLI hook
    raise SystemExit(main())
