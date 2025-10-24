"""Tests for the prelaunch environment validator."""

from __future__ import annotations

import socket
import sys

import pytest

from app.core.prelaunch import PrelaunchConfig, validate_environment


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_validate_environment_success(monkeypatch: pytest.MonkeyPatch) -> None:
    port = _get_free_port()
    config = PrelaunchConfig(
        min_python=(sys.version_info.major, sys.version_info.minor),
        required_binaries=("python",),
        port_env="PRELAUNCH_PORT",
        default_port=port,
        host="127.0.0.1",
    )

    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setenv("SKIP_PORT_CHECKS", "false")
    monkeypatch.setenv("PRELAUNCH_PORT", str(port))

    result = validate_environment(config)

    assert result.ok
    assert result.errors == []


def test_validate_environment_python_version_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    port = _get_free_port()
    config = PrelaunchConfig(
        min_python=(sys.version_info.major + 1, 0),
        required_binaries=(),
        port_env="PRELAUNCH_PORT",
        default_port=port,
        host="127.0.0.1",
    )

    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setenv("SKIP_PORT_CHECKS", "false")
    monkeypatch.setenv("PRELAUNCH_PORT", str(port))

    result = validate_environment(config)

    assert not result.ok
    assert any("Python runtime" in message for message in result.errors)


def test_validate_environment_missing_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    port = _get_free_port()
    config = PrelaunchConfig(
        min_python=(sys.version_info.major, sys.version_info.minor),
        required_binaries=("definitely_missing_binary",),
        port_env="PRELAUNCH_PORT",
        default_port=port,
        host="127.0.0.1",
    )

    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setenv("SKIP_PORT_CHECKS", "false")
    monkeypatch.setenv("PRELAUNCH_PORT", str(port))

    result = validate_environment(config)

    assert not result.ok
    assert any("Required executable" in message for message in result.errors)


def test_validate_environment_port_in_use(monkeypatch: pytest.MonkeyPatch) -> None:
    port = _get_free_port()
    config = PrelaunchConfig(
        min_python=(sys.version_info.major, sys.version_info.minor),
        required_binaries=("python",),
        port_env="PRELAUNCH_PORT",
        default_port=port,
        host="127.0.0.1",
    )

    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setenv("SKIP_PORT_CHECKS", "false")
    monkeypatch.setenv("PRELAUNCH_PORT", str(port))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as blocker:
        blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        blocker.bind(("127.0.0.1", port))
        blocker.listen(1)

        result = validate_environment(config)

    assert not result.ok
    assert any("already in use" in message for message in result.errors)
