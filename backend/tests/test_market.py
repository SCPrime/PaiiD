"""Tests for market data API endpoints."""

from unittest.mock import MagicMock, patch


def test_market_indices_requires_auth(client):
    response = client.get("/api/market/indices")
    assert response.status_code == 403


@patch("app.routers.market.requests.get")
def test_market_indices_returns_expected_payload(mock_get, client, auth_headers):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "quotes": {
            "quote": [
                {"symbol": "$DJI", "last": 35000, "change": 150, "change_percentage": 0.42},
                {"symbol": "COMP:GIDS", "last": 15000, "change": 75, "change_percentage": 0.5},
            ]
        }
    }
    mock_get.return_value = mock_response

    response = client.get("/api/market/indices", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "tradier"
    assert "dow" in data and "nasdaq" in data


@patch("app.routers.market.requests.get")
def test_market_quote_handles_upstream_errors(mock_get, client, auth_headers):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "upstream failure"}
    mock_get.return_value = mock_response

    response = client.get("/api/market/quote/SPY", headers=auth_headers)
    assert response.status_code in {500, 502}


def test_market_quote_invalid_token(client):
    response = client.get("/api/market/quote/SPY", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
