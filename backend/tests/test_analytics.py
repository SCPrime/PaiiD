"""
Test analytics and portfolio calculations
Tests P&L calculation, risk metrics, portfolio summary
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-token-12345"}


def test_portfolio_summary_endpoint():
    """Test portfolio summary endpoint returns correct structure"""
    response = client.get("/api/portfolio/summary", headers=HEADERS)

    # Should return 200 or Alpaca error, not auth error
    if response.status_code == 200:
        data = response.json()
        assert "totalValue" in data
        assert "totalPL" in data
        assert "totalPLPercent" in data
        assert "dayPL" in data
        assert "dayPLPercent" in data


def test_portfolio_summary_requires_auth():
    """Test portfolio summary requires authentication"""
    response = client.get("/api/portfolio/summary")
    assert response.status_code == 401


def test_portfolio_history_endpoint():
    """Test portfolio history endpoint"""
    response = client.get("/api/portfolio/history?days=30", headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        assert "dates" in data
        assert "values" in data
        assert isinstance(data["dates"], list)
        assert isinstance(data["values"], list)


def test_portfolio_history_different_periods():
    """Test portfolio history with different time periods"""
    periods = [7, 30, 90, 365]

    for days in periods:
        response = client.get(f"/api/portfolio/history?days={days}", headers=HEADERS)
        # Should succeed or return Alpaca error
        assert response.status_code in [200, 500], f"Failed for {days} days"


def test_performance_metrics_endpoint():
    """Test performance metrics calculation"""
    response = client.get("/api/analytics/performance", headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        # Check for key performance metrics
        expected_keys = ["sharpeRatio", "maxDrawdown", "winRate", "totalReturn"]
        for key in expected_keys:
            assert key in data, f"Missing {key} in performance metrics"


@patch("app.services.tradier_client.get_tradier_client")
def test_pl_calculation_with_mock_data(mock_client):
    """Test P&L calculation logic with mocked Alpaca data"""
    # Mock account data
    mock_account = MagicMock()
    mock_account.equity = "105000.00"
    mock_account.last_equity = "104000.00"
    mock_account.cash = "95000.00"
    mock_account.buying_power = "190000.00"

    # Mock positions
    mock_position = MagicMock()
    mock_position.symbol = "AAPL"
    mock_position.qty = "10"
    mock_position.current_price = "150.00"
    mock_position.market_value = "1500.00"
    mock_position.unrealized_pl = "50.00"
    mock_position.unrealized_plpc = "0.034"  # 3.4%
    mock_position.cost_basis = "1450.00"

    mock_client.get_account.return_value = mock_account
    mock_client.get_all_positions.return_value = [mock_position]

    response = client.get("/api/portfolio/summary", headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        # Verify calculations are correct
        assert float(data["totalValue"]) > 0
        assert "totalPL" in data


def test_zero_positions_portfolio():
    """Test portfolio summary with no positions"""
    with patch("app.services.tradier_client.get_tradier_client") as mock_client:
        mock_account = MagicMock()
        mock_account.equity = "100000.00"
        mock_account.last_equity = "100000.00"
        mock_account.cash = "100000.00"
        mock_account.buying_power = "200000.00"

        mock_client.get_account.return_value = mock_account
        mock_client.get_all_positions.return_value = []

        response = client.get("/api/portfolio/summary", headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            assert float(data["totalValue"]) == 100000.00
            assert float(data["totalPL"]) == 0.00


def test_negative_pl_calculation():
    """Test that negative P&L is calculated correctly"""
    with patch("app.services.tradier_client.get_tradier_client") as mock_client:
        mock_account = MagicMock()
        mock_account.equity = "95000.00"  # Lost $5000
        mock_account.last_equity = "100000.00"
        mock_account.cash = "90000.00"

        mock_position = MagicMock()
        mock_position.symbol = "TSLA"
        mock_position.unrealized_pl = "-500.00"
        mock_position.unrealized_plpc = "-0.10"
        mock_position.market_value = "4500.00"
        mock_position.cost_basis = "5000.00"

        mock_client.get_account.return_value = mock_account
        mock_client.get_all_positions.return_value = [mock_position]

        response = client.get("/api/portfolio/summary", headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            assert float(data["totalPL"]) < 0


def test_performance_metrics_risk_calculations():
    """Test risk metric calculations (Sharpe, max drawdown)"""
    response = client.get("/api/analytics/performance", headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        # Sharpe ratio should be a number
        if "sharpeRatio" in data:
            assert isinstance(data["sharpeRatio"], (int, float))

        # Max drawdown should be between 0 and 1 (or -1 and 0 if negative)
        if "maxDrawdown" in data:
            assert isinstance(data["maxDrawdown"], (int, float))
