from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_tradier_chain_response():
    return {
        "options": {
            "option": [
                {
                    "symbol": "AAPL250117C00150000",
                    "option_type": "call",
                    "strike": 150,
                    "expiration_date": "2025-01-17",
                    "bid": 5.1,
                    "ask": 5.2,
                    "last": 5.15,
                    "volume": 120,
                    "open_interest": 340,
                    "greeks": {
                        "delta": 0.45,
                        "gamma": 0.12,
                        "theta": -0.03,
                        "vega": 0.22,
                        "rho": 0.08,
                        "mid_iv": 0.32,
                    },
                }
            ]
        }
    }


class TestOptionsEndpoints:
    @patch("app.routers.options.get_tradier_client")
    def test_options_chain_success(
        self, mock_client_factory, client, auth_headers, mock_tradier_chain_response
    ):
        mock_client = MagicMock()
        mock_client.get_option_chains.return_value = mock_tradier_chain_response
        mock_client.get_option_expirations.return_value = {
            "expirations": {"date": ["2025-01-17"]}
        }
        mock_client_factory.return_value = mock_client

        response = client.get("/api/options/chains/AAPL", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["source"] == "tradier"
        assert data["total_contracts"] == 1

    @patch("app.routers.options.get_tradier_client")
    def test_options_expirations_no_error(self, mock_client_factory, client, auth_headers):
        mock_client = MagicMock()
        mock_client.get_option_expirations.return_value = {
            "expirations": {"date": ["2025-01-17", "2025-02-21"]}
        }
        mock_client_factory.return_value = mock_client

        response = client.get("/api/options/expirations/AAPL", headers=auth_headers)
        assert response.status_code == 200
        dates = response.json()
        assert len(dates) == 2
        assert dates[0]["date"] == "2025-01-17"

    @patch("app.routers.options.get_tradier_client")
    def test_options_expirations_tradier_failure(
        self, mock_client_factory, client, auth_headers
    ):
        mock_client = MagicMock()
        mock_client.get_option_expirations.side_effect = Exception("API failure")
        mock_client_factory.return_value = mock_client

        response = client.get("/api/options/expirations/AAPL", headers=auth_headers)
        assert response.status_code == 500
        assert "Error fetching expirations" in response.json()["detail"]
