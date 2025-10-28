def test_readiness_returns_503_on_dependency_unavailable(monkeypatch, client):
    from app.routers import health as health_module

    async def fake_check_tradier():
        return health_module.DependencyStatus(
            status="unavailable", message="auth failed"
        )

    async def fake_check_alpaca():
        return health_module.DependencyStatus(status="healthy")

    monkeypatch.setattr(health_module, "_check_tradier", fake_check_tradier)
    monkeypatch.setattr(health_module, "_check_alpaca", fake_check_alpaca)

    resp = client.get("/api/health/readiness")
    assert resp.status_code == 503
    body = resp.json()
    assert body.get("status") in {"degraded", "error"}


def test_market_quote_maps_provider_404(monkeypatch, client):
    from app.routers import market_data as market_data_module
    from app.services.tradier_client import ProviderHTTPError

    class FakeClient:
        def get_quotes(self, symbols):
            raise ProviderHTTPError(404, "not found")

    monkeypatch.setattr(market_data_module, "get_tradier_client", lambda: FakeClient())

    resp = client.get("/api/market/quote/UNKNOWN")
    assert resp.status_code == 404


def test_market_bars_maps_provider_401_to_503(monkeypatch, client):
    from app.routers import market_data as market_data_module
    from app.services.tradier_client import ProviderHTTPError

    class FakeClient:
        def get_historical_quotes(self, **kwargs):
            raise ProviderHTTPError(401, "unauthorized")

    monkeypatch.setattr(market_data_module, "get_tradier_client", lambda: FakeClient())

    resp = client.get("/api/market/bars/SPY")
    assert resp.status_code == 503
