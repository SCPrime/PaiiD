"""Infrastructure health validation for MOD SQUAD."""

from __future__ import annotations

import os
import socket
import subprocess
from datetime import UTC, datetime
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "infra_health"


def run() -> None:
    """Execute infrastructure health checks."""

    config = load_extension_config()
    infra_config = config.get("infra_health")
    if not infra_config or not infra_config.get("enabled", False):
        return

    services = infra_config.get("services", [])
    timeout = int(infra_config.get("timeout_seconds", 30))

    results: list[dict[str, Any]] = []
    for entry in services:
        if isinstance(entry, dict):
            service_name = entry.get("name")
            optional = bool(entry.get("optional", False))
        else:
            service_name = entry
            optional = False

        if not service_name:
            continue

        if service_name == "postgres":
            check = _check_postgres()
        elif service_name == "redis":
            check = _check_redis()
        elif service_name == "docker":
            check = _check_docker_services(timeout)
        else:
            check = {
                "service": service_name,
                "healthy": False,
                "error": "service check not implemented",
            }

        check["optional"] = optional
        if optional and not check.get("healthy", False):
            check["status"] = "warning"
        elif not optional:
            check.setdefault(
                "status", "healthy" if check.get("healthy") else "unhealthy"
            )
        else:
            check.setdefault("status", "healthy" if check.get("healthy") else "warning")
        results.append(check)

    dump_jsonl(
        ARTIFACT_DIR / "infra_health.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "services": services,
            "results": results,
        },
    )


def _resolve_host_port(
    default_host: str, default_port: int, env_prefix: str
) -> tuple[str, int]:
    host = (
        os.getenv(f"{env_prefix}_HOST")
        or os.getenv(f"{env_prefix}_URL")
        or os.getenv(f"{env_prefix}_ADDRESS")
        or default_host
    )
    port = (
        os.getenv(f"{env_prefix}_PORT")
        or os.getenv(f"{env_prefix}_SERVICE_PORT")
        or default_port
    )
    try:
        port_value = int(port)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        port_value = default_port
    return str(host), port_value


def _check_postgres() -> dict:
    """Check Postgres connectivity on default dev port."""
    try:
        host, port = _resolve_host_port("localhost", 5433, "POSTGRES")
        host = os.getenv("PGHOST", host)
        pg_port = int(os.getenv("PGPORT", port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, pg_port))
        sock.close()
        return {
            "service": "postgres",
            "healthy": result == 0,
            "host": host,
            "port": pg_port,
        }
    except Exception as exc:  # pragma: no cover - network safety
        return {
            "service": "postgres",
            "healthy": False,
            "error": str(exc),
        }


def _check_redis() -> dict:
    """Check Redis connectivity on default dev port."""
    try:
        host, port = _resolve_host_port("localhost", 6380, "REDIS")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return {
            "service": "redis",
            "healthy": result == 0,
            "host": host,
            "port": port,
        }
    except Exception as exc:  # pragma: no cover - network safety
        return {
            "service": "redis",
            "healthy": False,
            "error": str(exc),
        }


def _check_docker_services(timeout: int) -> dict:
    """Check Docker Compose services status."""
    try:
        cmd = [
            "docker",
            "compose",
            "-f",
            "infrastructure/docker-compose.dev.yml",
            "ps",
            "--format",
            "json",
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if completed.returncode == 0:
            services = completed.stdout.strip().split("\n")
            healthy_count = sum(1 for svc in services if '"Status":"running"' in svc)
            return {
                "service": "docker_compose",
                "healthy": healthy_count > 0,
                "running_services": healthy_count,
            }
        return {
            "service": "docker_compose",
            "healthy": False,
            "returncode": completed.returncode,
        }
    except FileNotFoundError:
        return {
            "service": "docker_compose",
            "healthy": False,
            "error": "docker not installed",
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "service": "docker_compose",
            "healthy": False,
            "error": str(exc),
        }


def cli() -> None:
    run()
