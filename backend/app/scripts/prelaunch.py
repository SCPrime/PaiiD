"""Pre-launch guard rails for starting the FastAPI service.

The deployment workflow calls into this module before executing
``uvicorn`` so that we can:

* ensure the configured port is not already in use; and
* provide a lightweight smoke test that verifies the application can
  boot and respond to ``/api/health``.

The implementation intentionally lives in Python so that both
PowerShell and POSIX shell wrappers can reuse the exact same logic.
"""
from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Optional

import httpx
import psutil


@dataclass
class PortProcess:
    """Represents an existing process bound to a TCP port."""

    pid: int
    name: str

    @classmethod
    def from_connection(cls, conn) -> Optional["PortProcess"]:
        if conn.pid is None:
            return None
        try:
            proc = psutil.Process(conn.pid)
        except psutil.Error:
            return None
        return cls(pid=proc.pid, name=proc.name())


def find_process_on_port(port: int) -> Optional[PortProcess]:
    """Return process information if a listener is already bound to ``port``."""

    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr and conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
            proc = PortProcess.from_connection(conn)
            if proc:
                return proc
    return None


def ensure_port_available(port: int) -> None:
    """Exit with code 1 if the provided ``port`` is already in use."""

    existing = find_process_on_port(port)
    if existing:
        message = (
            f"Port {port} is already bound by process {existing.pid} ({existing.name}).\n"
            "Either stop the process or export PORT to a free value before launching uvicorn."
        )
        raise SystemExit(message)


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def smoke_test_uvicorn(app_path: str, timeout: int = 60) -> None:
    """Boot uvicorn on an ephemeral port and assert that /api/health responds."""

    port = _find_free_port()
    env = os.environ.copy()
    env.setdefault("USE_TEST_FIXTURES", "true")
    env.setdefault("API_TOKEN", "smoke-test-token")

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        app_path,
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]

    process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    start = time.time()
    health_url = f"http://127.0.0.1:{port}/api/health"

    try:
        while time.time() - start < timeout:
            try:
                response = httpx.get(health_url, timeout=2.0)
            except httpx.TransportError:
                time.sleep(0.5)
                continue

            if response.status_code == 200:
                return
            time.sleep(0.5)
        raise SystemExit(f"Timed out waiting for uvicorn smoke test at {health_url}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        finally:
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pre-flight checks for uvicorn start-up")
    parser.add_argument(
        "action",
        choices=("check", "smoke"),
        nargs="?",
        default="check",
        help="Run port availability checks or perform a uvicorn smoke test.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Port uvicorn is expected to bind when running the real server.",
    )
    parser.add_argument(
        "--app",
        default=os.getenv("UVICORN_APP", "app.main:app"),
        help="Dotted path passed to uvicorn when running the smoke test.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv or sys.argv[1:])

    if args.action == "check":
        ensure_port_available(args.port)
        print(f"✅ Port {args.port} is available for uvicorn")
        return

    if args.action == "smoke":
        ensure_port_available(args.port)
        smoke_test_uvicorn(args.app)
        print("✅ Uvicorn smoke test completed successfully")
        return

    raise SystemExit(f"Unknown action: {args.action}")


if __name__ == "__main__":
    main()
