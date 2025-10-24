"""Unit tests for the prelaunch environment validation module."""

from __future__ import annotations

import socket
from types import SimpleNamespace

import pytest

from app.core import prelaunch


def _version(major: int, minor: int, micro: int) -> SimpleNamespace:
    return SimpleNamespace(major=major, minor=minor, micro=micro)


def _get_available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_run_prelaunch_checks_success(monkeypatch: pytest.MonkeyPatch) -> None:
    port = _get_available_port()
    env = {prelaunch.PORT_ENV_VAR: str(port)}

    monkeypatch.setattr(prelaunch.shutil, "which", lambda name: f"/usr/bin/{name}")

    results = prelaunch.run_prelaunch_checks(
        version_info=_version(3, 11, 4),
        required_binaries=("alpha", "beta"),
        env=env,
    )

    assert all(result.ok for result in results)


def test_run_prelaunch_checks_python_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    env = {prelaunch.PORT_ENV_VAR: str(_get_available_port())}
    monkeypatch.setattr(prelaunch.shutil, "which", lambda name: f"/usr/bin/{name}")

    with pytest.raises(prelaunch.PrelaunchCheckError) as exc:
        prelaunch.run_prelaunch_checks(
            raise_on_error=True,
            version_info=_version(3, 10, 9),
            required_binaries=(),
            env=env,
        )

    assert any(result.name == "python_version" for result in exc.value.failures)


def test_run_prelaunch_checks_missing_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    env = {prelaunch.PORT_ENV_VAR: str(_get_available_port())}

    def fake_which(name: str) -> str | None:
        return None if name == "missing" else f"/usr/bin/{name}"

    monkeypatch.setattr(prelaunch.shutil, "which", fake_which)

    with pytest.raises(prelaunch.PrelaunchCheckError) as exc:
        prelaunch.run_prelaunch_checks(
            raise_on_error=True,
            version_info=_version(3, 11, 1),
            required_binaries=("missing",),
            env=env,
        )

    assert any(result.name == "binary:missing" for result in exc.value.failures)


def test_run_prelaunch_checks_port_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    busy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    busy_socket.bind(("127.0.0.1", 0))
    busy_socket.listen(1)
    port = busy_socket.getsockname()[1]

    env = {prelaunch.PORT_ENV_VAR: str(port)}
    monkeypatch.setattr(prelaunch.shutil, "which", lambda name: f"/usr/bin/{name}")

    try:
        with pytest.raises(prelaunch.PrelaunchCheckError) as exc:
            prelaunch.run_prelaunch_checks(
                raise_on_error=True,
                version_info=_version(3, 11, 2),
                required_binaries=(),
                env=env,
            )

        assert any(result.name == "port_availability" for result in exc.value.failures)
    finally:
        busy_socket.close()
