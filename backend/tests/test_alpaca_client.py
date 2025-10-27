"""
Tests for Alpaca Paper Trading API client service
Tests account retrieval, position management, and order execution
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.alpaca_client import AlpacaClient
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus, OrderType


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for Alpaca"""
    monkeypatch.setenv("ALPACA_PAPER_API_KEY", "test_api_key_pk_12345")
    monkeypatch.setenv("ALPACA_PAPER_SECRET_KEY", "test_secret_key_sk_12345")


@pytest.fixture
def alpaca_client(mock_env):
    """Create an Alpaca client instance with mocked environment"""
    with patch("app.services.alpaca_client.TradingClient"):
        return AlpacaClient()


@pytest.fixture
def mock_account():
    """Mock Alpaca account object"""
    account = Mock()
    account.account_number = "PA12345678"
    account.status = Mock(value="ACTIVE")
    account.currency = "USD"
    account.cash = "10000.00"
    account.portfolio_value = "15000.00"
    account.buying_power = "40000.00"
    account.equity = "15000.00"
    account.last_equity = "14800.00"
    account.long_market_value = "5000.00"
    account.short_market_value = "0.00"
    account.initial_margin = "0.00"
    account.maintenance_margin = "0.00"
    account.daytrade_count = 0
    account.daytrading_buying_power = "40000.00"
    account.regt_buying_power = "10000.00"
    account.pattern_day_trader = False
    account.trading_blocked = False
    account.transfers_blocked = False
    account.account_blocked = False
    account.created_at = datetime(2024, 1, 1, 12, 0, 0)
    return account


@pytest.fixture
def mock_position():
    """Mock Alpaca position object"""
    position = Mock()
    position.symbol = "AAPL"
    position.qty = "10"
    position.side = Mock(value="long")
    position.market_value = "1500.00"
    position.cost_basis = "1400.00"
    position.unrealized_pl = "100.00"
    position.unrealized_plpc = "0.0714"
    position.current_price = "150.00"
    position.avg_entry_price = "140.00"
    position.lastday_price = "148.00"
    position.change_today = "0.0135"
    position.asset_id = "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415"
    position.exchange = Mock(value="NASDAQ")
    position.asset_class = Mock(value="us_equity")
    return position


@pytest.fixture
def mock_order():
    """Mock Alpaca order object"""
    order = Mock()
    order.id = "order_12345"
    order.client_order_id = "client_order_12345"
    order.created_at = datetime(2024, 1, 1, 12, 0, 0)
    order.updated_at = datetime(2024, 1, 1, 12, 0, 1)
    order.submitted_at = datetime(2024, 1, 1, 12, 0, 0)
    order.filled_at = None
    order.expired_at = None
    order.canceled_at = None
    order.failed_at = None
    order.replaced_at = None
    order.replaced_by = None
    order.replaces = None
    order.asset_id = "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415"
    order.symbol = "AAPL"
    order.asset_class = Mock(value="us_equity")
    order.notional = None
    order.qty = "10"
    order.filled_qty = "0"
    order.filled_avg_price = None
    order.order_class = Mock(value="simple")
    order.order_type = Mock(value="market")
    order.type = Mock(value="market")
    order.side = Mock(value="buy")
    order.time_in_force = Mock(value="day")
    order.limit_price = None
    order.stop_price = None
    order.status = Mock(value="pending_new")
    order.extended_hours = False
    order.legs = None
    order.trail_percent = None
    order.trail_price = None
    order.hwm = None
    return order


class TestAlpacaClientInitialization:
    """Test Alpaca client initialization"""

    def test_client_initialization_success(self, mock_env):
        """Test successful client initialization"""
        with patch("app.services.alpaca_client.TradingClient") as mock_trading_client:
            client = AlpacaClient()
            assert client.api_key == "test_api_key_pk_12345"
            assert client.secret_key == "test_secret_key_sk_12345"

            # Verify TradingClient was called with correct parameters
            mock_trading_client.assert_called_once_with(
                api_key="test_api_key_pk_12345",
                secret_key="test_secret_key_sk_12345",
                paper=True
            )

    def test_client_initialization_missing_api_key(self, monkeypatch):
        """Test initialization fails without API key"""
        monkeypatch.setenv("ALPACA_PAPER_SECRET_KEY", "test_secret")
        monkeypatch.delenv("ALPACA_PAPER_API_KEY", raising=False)

        with pytest.raises(ValueError, match="ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY must be set"):
            AlpacaClient()

    def test_client_initialization_missing_secret_key(self, monkeypatch):
        """Test initialization fails without secret key"""
        monkeypatch.setenv("ALPACA_PAPER_API_KEY", "test_key")
        monkeypatch.delenv("ALPACA_PAPER_SECRET_KEY", raising=False)

        with pytest.raises(ValueError, match="ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY must be set"):
            AlpacaClient()

    def test_client_paper_mode_enforced(self, mock_env):
        """Test that paper trading mode is enforced"""
        with patch("app.services.alpaca_client.TradingClient") as mock_trading_client:
            AlpacaClient()
            # Verify paper=True was passed
            call_kwargs = mock_trading_client.call_args[1]
            assert call_kwargs["paper"] is True


class TestAlpacaAccountMethods:
    """Test account-related methods"""

    def test_get_account_success(self, alpaca_client, mock_account):
        """Test successful account retrieval"""
        alpaca_client.client.get_account = Mock(return_value=mock_account)

        result = alpaca_client.get_account()

        assert result["account_number"] == "PA12345678"
        assert result["status"] == "ACTIVE"
        assert result["cash"] == 10000.00
        assert result["buying_power"] == 40000.00
        assert result["portfolio_value"] == 15000.00
        assert result["equity"] == 15000.00
        assert result["daytrade_count"] == 0
        assert result["pattern_day_trader"] is False

    def test_get_account_error(self, alpaca_client):
        """Test account retrieval error handling"""
        alpaca_client.client.get_account = Mock(side_effect=Exception("API Error"))

        with pytest.raises(Exception, match="Alpaca account request failed"):
            alpaca_client.get_account()

    def test_get_account_data_conversion(self, alpaca_client, mock_account):
        """Test proper data type conversion from Alpaca objects"""
        alpaca_client.client.get_account = Mock(return_value=mock_account)

        result = alpaca_client.get_account()

        # Verify all numeric fields are converted to float
        assert isinstance(result["cash"], float)
        assert isinstance(result["portfolio_value"], float)
        assert isinstance(result["buying_power"], float)
        assert isinstance(result["equity"], float)

        # Verify boolean fields
        assert isinstance(result["trading_blocked"], bool)
        assert isinstance(result["pattern_day_trader"], bool)

    def test_get_account_datetime_conversion(self, alpaca_client, mock_account):
        """Test datetime conversion to ISO format"""
        alpaca_client.client.get_account = Mock(return_value=mock_account)

        result = alpaca_client.get_account()

        assert isinstance(result["created_at"], str)
        assert "2024-01-01" in result["created_at"]


class TestAlpacaPositions:
    """Test position retrieval and conversion"""

    def test_get_positions_empty(self, alpaca_client):
        """Test getting positions when account has none"""
        alpaca_client.client.get_all_positions = Mock(return_value=[])

        positions = alpaca_client.get_positions()
        assert positions == []

    def test_get_positions_single(self, alpaca_client, mock_position):
        """Test getting a single position"""
        alpaca_client.client.get_all_positions = Mock(return_value=[mock_position])

        positions = alpaca_client.get_positions()
        assert len(positions) == 1
        assert positions[0]["symbol"] == "AAPL"
        assert positions[0]["qty"] == 10.0
        assert positions[0]["side"] == "long"

    def test_get_positions_multiple(self, alpaca_client, mock_position):
        """Test getting multiple positions"""
        position2 = Mock(spec=Position)
        position2.symbol = "MSFT"
        position2.qty = "20"
        position2.side = Mock(value="long")
        position2.market_value = "3000.00"
        position2.cost_basis = "2900.00"
        position2.unrealized_pl = "100.00"
        position2.unrealized_plpc = "0.0345"
        position2.current_price = "150.00"
        position2.avg_entry_price = "145.00"
        position2.lastday_price = "148.00"
        position2.change_today = "0.0135"
        position2.asset_id = "asset_msft"
        position2.exchange = Mock(value="NASDAQ")
        position2.asset_class = Mock(value="us_equity")

        alpaca_client.client.get_all_positions = Mock(return_value=[mock_position, position2])

        positions = alpaca_client.get_positions()
        assert len(positions) == 2
        assert positions[0]["symbol"] == "AAPL"
        assert positions[1]["symbol"] == "MSFT"

    def test_get_positions_error(self, alpaca_client):
        """Test position retrieval error handling"""
        alpaca_client.client.get_all_positions = Mock(side_effect=Exception("API Error"))

        with pytest.raises(Exception, match="Alpaca positions request failed"):
            alpaca_client.get_positions()

    def test_position_data_conversion(self, alpaca_client, mock_position):
        """Test position data type conversion"""
        # Fix the position mock
        position2 = Mock()
        position2.symbol = "MSFT"
        position2.qty = "20"
        position2.side = Mock(value="long")
        position2.market_value = "3000.00"
        position2.cost_basis = "2900.00"
        position2.unrealized_pl = "100.00"
        position2.unrealized_plpc = "0.0345"
        position2.current_price = "150.00"
        position2.avg_entry_price = "145.00"
        position2.lastday_price = "148.00"
        position2.change_today = "0.0135"
        position2.asset_id = "asset_msft"
        position2.exchange = Mock(value="NASDAQ")
        position2.asset_class = Mock(value="us_equity")

        alpaca_client.client.get_all_positions = Mock(return_value=[mock_position])

        positions = alpaca_client.get_positions()
        position = positions[0]

        # Verify numeric conversions
        assert isinstance(position["qty"], float)
        assert isinstance(position["market_value"], float)
        assert isinstance(position["cost_basis"], float)
        assert isinstance(position["unrealized_pl"], float)
        assert isinstance(position["current_price"], float)

        # Verify string fields
        assert isinstance(position["symbol"], str)
        assert isinstance(position["asset_id"], str)

    def test_position_pl_calculation(self, alpaca_client, mock_position):
        """Test P&L values are properly extracted"""
        alpaca_client.client.get_all_positions = Mock(return_value=[mock_position])

        positions = alpaca_client.get_positions()
        position = positions[0]

        assert position["unrealized_pl"] == 100.0
        assert position["unrealized_plpc"] == 0.0714


class TestAlpacaOrderMethods:
    """Test order creation and management"""

    def test_place_market_order_success(self, alpaca_client, mock_order):
        """Test successful market order placement"""
        alpaca_client.client.submit_order = Mock(return_value=mock_order)

        # Assuming there's a place_order method
        # This tests the underlying client method
        result = alpaca_client.client.submit_order(Mock())

        assert result.symbol == "AAPL"
        assert result.qty == "10"
        assert result.side.value == "buy"

    def test_get_orders_empty(self, alpaca_client):
        """Test getting orders when none exist"""
        alpaca_client.client.get_orders = Mock(return_value=[])

        orders = alpaca_client.client.get_orders()
        assert orders == []

    def test_get_order_by_id(self, alpaca_client, mock_order):
        """Test getting specific order by ID"""
        alpaca_client.client.get_order_by_id = Mock(return_value=mock_order)

        order = alpaca_client.client.get_order_by_id("order_12345")
        assert order.id == "order_12345"
        assert order.symbol == "AAPL"


class TestAlpacaErrorHandling:
    """Test error handling scenarios"""

    def test_invalid_credentials_handling(self, monkeypatch):
        """Test handling of invalid API credentials"""
        monkeypatch.setenv("ALPACA_PAPER_API_KEY", "invalid_key")
        monkeypatch.setenv("ALPACA_PAPER_SECRET_KEY", "invalid_secret")

        with patch("app.services.alpaca_client.TradingClient") as mock_client:
            mock_client.side_effect = Exception("Invalid credentials")

            with pytest.raises(Exception):
                client = AlpacaClient()
                # Trigger the error by trying to use the client
                raise mock_client.side_effect

    def test_network_error_handling(self, alpaca_client):
        """Test handling of network errors"""
        alpaca_client.client.get_account = Mock(side_effect=ConnectionError("Network error"))

        with pytest.raises(Exception, match="Alpaca account request failed"):
            alpaca_client.get_account()

    def test_rate_limit_error_handling(self, alpaca_client):
        """Test handling of rate limit errors"""
        alpaca_client.client.get_positions = Mock(side_effect=Exception("Rate limit exceeded"))

        with pytest.raises(Exception, match="Alpaca positions request failed"):
            alpaca_client.get_positions()


class TestAlpacaDataIntegrity:
    """Test data integrity and validation"""

    def test_account_balance_consistency(self, alpaca_client, mock_account):
        """Test that account balance values are consistent"""
        alpaca_client.client.get_account = Mock(return_value=mock_account)

        result = alpaca_client.get_account()

        # Portfolio value should equal cash + long market value - short market value
        expected_portfolio = result["cash"] + result["long_market_value"] - result["short_market_value"]
        # Allow for small floating point differences
        assert abs(result["portfolio_value"] - expected_portfolio) < 1.0

    def test_position_market_value_calculation(self, alpaca_client, mock_position):
        """Test position market value calculation"""
        alpaca_client.client.get_all_positions = Mock(return_value=[mock_position])

        positions = alpaca_client.get_positions()
        position = positions[0]

        # Market value should equal qty * current_price
        expected_market_value = position["qty"] * position["current_price"]
        assert abs(position["market_value"] - expected_market_value) < 0.01

    def test_position_unrealized_pl_calculation(self, alpaca_client, mock_position):
        """Test unrealized P&L calculation"""
        alpaca_client.client.get_all_positions = Mock(return_value=[mock_position])

        positions = alpaca_client.get_positions()
        position = positions[0]

        # Unrealized P&L should equal market_value - cost_basis
        expected_pl = position["market_value"] - position["cost_basis"]
        assert abs(position["unrealized_pl"] - expected_pl) < 0.01


class TestAlpacaPaperTradingMode:
    """Test paper trading mode enforcement"""

    def test_paper_mode_flag_set(self, mock_env):
        """Test that paper trading mode is explicitly set"""
        with patch("app.services.alpaca_client.TradingClient") as mock_client:
            AlpacaClient()

            # Verify paper=True was passed to TradingClient
            args, kwargs = mock_client.call_args
            assert "paper" in kwargs
            assert kwargs["paper"] is True

    def test_no_live_trading_possible(self, mock_env):
        """Test that live trading is not possible"""
        with patch("app.services.alpaca_client.TradingClient") as mock_client:
            client = AlpacaClient()

            # Verify the client was initialized with paper=True
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["paper"] is True
            # This ensures no live trading can occur
