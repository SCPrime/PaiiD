import logging
from contextlib import contextmanager

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from app.middleware.sentry import SentryContextMiddleware


@pytest.fixture(autouse=True)
def _configure_logging():
    logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def sentry_stub(monkeypatch):
    state = {"entered": 0, "exited": 0, "captured": []}

    @contextmanager
    def push_scope():
        state["entered"] += 1

        class Scope:
            def set_context(self, *_args, **_kwargs):
                return None

            def set_tag(self, *_args, **_kwargs):
                return None

        try:
            yield Scope()
        finally:
            state["exited"] += 1

    monkeypatch.setattr("sentry_sdk.push_scope", push_scope)
    monkeypatch.setattr("sentry_sdk.add_breadcrumb", lambda *a, **k: None)
    monkeypatch.setattr("sentry_sdk.capture_exception", lambda exc: state["captured"].append(exc))

    return state


def create_app():
    app = FastAPI()
    app.add_middleware(SentryContextMiddleware)
    return app


def test_scope_closed_on_success(sentry_stub):
    app = create_app()

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/ping")

    assert response.status_code == 200
    assert sentry_stub["entered"] == 1
    assert sentry_stub["exited"] == 1


def test_scope_closed_on_exception(sentry_stub):
    app = create_app()

    @app.get("/boom")
    async def boom():  # pragma: no cover - executed via HTTP
        raise RuntimeError("middleware test")

    client = TestClient(app)

    with pytest.raises(RuntimeError):
        client.get("/boom")

    assert sentry_stub["entered"] == 1
    assert sentry_stub["exited"] == 1
    assert sentry_stub["captured"] and isinstance(sentry_stub["captured"][0], RuntimeError)
