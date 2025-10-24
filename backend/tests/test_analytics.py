"""Tests for analytics endpoints."""

from unittest.mock import MagicMock, patch


def test_analytics_requires_auth(client):
    response = client.get("/api/portfolio/summary")
    assert response.status_code == 403


@patch("app.routers.analytics.get_tradier_client")
def test_portfolio_summary_returns_expected_shape(mock_client_factory, client, auth_headers):
    mock_client = MagicMock()
    mock_client.get_account.return_value = {
        "portfolio_value": "100000",
        "cash": "20000",
        "buying_power": "50000",
    }
    mock_client.get_positions.return_value = []
    mock_client_factory.return_value = mock_client

    response = client.get("/api/portfolio/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_value"] == 100000
    assert data["cash"] == 20000


@patch("app.routers.analytics.get_tradier_client")
def test_performance_metrics_handles_errors(mock_client_factory, client, auth_headers):
    mock_client = MagicMock()
    mock_client.get_account.return_value = {}
    mock_client.get_positions.side_effect = RuntimeError("upstream failure")
    mock_client_factory.return_value = mock_client

    response = client.get("/api/analytics/performance", headers=auth_headers)
    assert response.status_code == 500
    assert "Failed to get performance metrics" in response.json()["detail"]
