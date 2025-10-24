import pytest


class MockTradierClient:
    def __init__(self, chain=None, expirations=None, raise_error=False):
        self._chain = chain or {
            "options": {
                "option": [
                    {
                        "symbol": "SPY250117C00590000",
                        "option_type": "call",
                        "strike": 590.0,
                        "expiration_date": "2025-01-17",
                        "bid": 1.0,
                        "ask": 1.2,
                        "last": 1.1,
                        "volume": 10,
                        "open_interest": 100,
                        "greeks": {
                            "delta": 0.5,
                            "gamma": 0.1,
                            "theta": -0.02,
                            "vega": 0.12,
                            "rho": 0.01,
                            "mid_iv": 0.25,
                        },
                    }
                ]
            }
        }
        self._expirations = expirations or {"expirations": {"date": ["2025-01-17"]}}
        self._raise_error = raise_error

    def get_option_chains(self, symbol, expiration):
        if self._raise_error:
            raise Exception("Tradier failure")
        return self._chain

    def get_option_expirations(self, symbol):
        if self._raise_error:
            raise Exception("Tradier failure")
        return self._expirations


@pytest.fixture
def mock_tradier(monkeypatch):
    client = MockTradierClient()
    monkeypatch.setattr("app.routers.options._get_tradier_client", lambda: client)
    return client


def test_options_chain_includes_source(client, auth_headers, mock_tradier):
    response = client.get("/api/options/chains/SPY", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "tradier"
    assert data["total_contracts"] == 1


def test_expiration_dates_returns_list(client, auth_headers, monkeypatch):
    mock = MockTradierClient(expirations={"expirations": {"date": "2025-01-17"}})
    monkeypatch.setattr("app.routers.options._get_tradier_client", lambda: mock)
    response = client.get("/api/options/expirations/SPY", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data[0]["date"] == "2025-01-17"
    assert data[0]["days_to_expiry"] >= 0


def test_options_chain_tradier_error_returns_500(client, auth_headers, monkeypatch):
    mock = MockTradierClient(raise_error=True)
    monkeypatch.setattr("app.routers.options._get_tradier_client", lambda: mock)
    response = client.get("/api/options/chains/SPY", headers=auth_headers)
    assert response.status_code == 500
    assert "Error fetching options chain" in response.json()["detail"]
