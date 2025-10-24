import socket

import pytest

from app.scripts import prelaunch


def test_ensure_port_available_detects_in_use():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    port = sock.getsockname()[1]

    with pytest.raises(SystemExit):
        prelaunch.ensure_port_available(port)

    sock.close()


def test_find_process_on_free_port():
    port = prelaunch._find_free_port()
    assert prelaunch.find_process_on_port(port) is None


def test_smoke_test_uvicorn_starts_and_serves_health(monkeypatch):
    prelaunch.smoke_test_uvicorn("app.main:app", timeout=10)
