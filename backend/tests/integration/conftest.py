"""
Integration Test Configuration and Fixtures

This conftest provides fixtures specific to integration tests,
including mock external API responses for Tradier and Alpaca.
"""

import os

# ==================== ENVIRONMENT SETUP (MUST BE FIRST) ====================
# Set environment variables BEFORE importing app modules to ensure they are
# picked up by Pydantic settings

os.environ["TESTING"] = "true"
os.environ["USE_TEST_FIXTURES"] = "true"  # Enable fixture mode for deterministic tests
os.environ["TRADIER_API_KEY"] = "test-tradier-key"
os.environ["TRADIER_ACCOUNT_ID"] = "TEST123"
os.environ["ALPACA_PAPER_API_KEY"] = "test-alpaca-key"
os.environ["ALPACA_PAPER_SECRET_KEY"] = "test-alpaca-secret"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = ""  # Disable Redis for tests
os.environ["SENTRY_DSN"] = ""  # Disable Sentry for tests
os.environ["API_TOKEN"] = "test-token-12345"
os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"

# Now safe to import
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


# ==================== MOCK TRADIER API RESPONSES ====================


class MockTradierClient:
    """Mock Tradier API client that returns fixture data"""

    def __init__(self):
        self.api_key = "test-tradier-key"
        self.account_id = "TEST123"
        self.base_url = "https://api.tradier.com/v1"

    def get_quote(self, symbol: str) -> dict:
        """Return mock quote data matching REAL Tradier API schema"""
        return {
            "symbol": symbol,
            "last": self._get_mock_price(symbol),
            "bid": self._get_mock_price(symbol) - 0.02,
            "ask": self._get_mock_price(symbol) + 0.02,
            "volume": 5234123,
            "open": self._get_mock_price(symbol) - 1.50,
            "high": self._get_mock_price(symbol) + 0.75,
            "low": self._get_mock_price(symbol) - 2.00,
            "close": self._get_mock_price(symbol),
            "prevclose": self._get_mock_price(symbol) - 1.25,
            "change": 1.25,
            "change_percentage": 0.72,
            "timestamp": datetime.now().isoformat(),
            "description": f"{symbol} Inc",
        }

    def get_quotes(self, symbols: list[str]) -> list[dict]:
        """Return multiple quotes"""
        return [self.get_quote(symbol) for symbol in symbols]

    def _get_mock_price(self, symbol: str) -> float:
        """Generate realistic mock price based on symbol"""
        prices = {
            "AAPL": 175.43,
            "MSFT": 380.25,
            "GOOGL": 138.50,
            "TSLA": 242.84,
            "NVDA": 485.20,
            "AMZN": 145.30,
            "META": 325.75,
            "NFLX": 445.60,
            "SPY": 450.25,
            "QQQ": 385.40,
        }
        return prices.get(symbol, 100.00)

    def get_account(self) -> dict:
        """Return mock account data matching REAL Tradier API schema"""
        return {
            "account_number": self.account_id,
            "cash": 100000.00,
            "buying_power": 200000.00,
            "portfolio_value": 150000.00,
            "equity": 150000.00,
            "long_market_value": 50000.00,
            "short_market_value": 0.00,
            "status": "ACTIVE",
        }

    def get_positions(self) -> list[dict]:
        """Return mock positions matching REAL Tradier API schema"""
        return []  # Empty by default - tests can add positions as needed

    def get_options_chain(self, symbol: str, expiration: str = None) -> dict:
        """Return mock options chain matching REAL Tradier API schema"""
        if not expiration:
            expiration = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        return {
            "options": {
                "option": [
                    {
                        "symbol": f"{symbol}250117C00150000",
                        "description": f"{symbol} Jan 17 2025 $150.00 Call",
                        "exch": "Z",
                        "type": "call",
                        "last": 5.25,
                        "change": 0.15,
                        "volume": 1234,
                        "open": 5.10,
                        "high": 5.40,
                        "low": 5.00,
                        "close": 5.25,
                        "bid": 5.20,
                        "ask": 5.30,
                        "underlying": symbol,
                        "strike": 150.00,
                        "greeks": {
                            "delta": 0.55,
                            "gamma": 0.02,
                            "theta": -0.05,
                            "vega": 0.15,
                            "rho": 0.01,
                        },
                        "change_percentage": 2.94,
                        "average_volume": 2500,
                        "last_volume": 10,
                        "trade_date": datetime.now().timestamp() * 1000,
                        "prevclose": 5.10,
                        "week_52_high": 12.50,
                        "week_52_low": 2.00,
                        "bidsize": 50,
                        "bidexch": "Z",
                        "bid_date": datetime.now().timestamp() * 1000,
                        "asksize": 75,
                        "askexch": "Z",
                        "ask_date": datetime.now().timestamp() * 1000,
                        "open_interest": 5000,
                        "contract_size": 100,
                        "expiration_date": expiration,
                        "expiration_type": "standard",
                        "option_type": "call",
                    }
                ]
            }
        }

    def get_expirations(self, symbol: str) -> list[str]:
        """Return mock expiration dates"""
        base_date = datetime.now()
        return [
            (base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
            (base_date + timedelta(days=14)).strftime("%Y-%m-%d"),
            (base_date + timedelta(days=30)).strftime("%Y-%m-%d"),
            (base_date + timedelta(days=60)).strftime("%Y-%m-%d"),
        ]


# ==================== MOCK ALPACA API RESPONSES ====================


class MockAlpacaClient:
    """Mock Alpaca API client that returns fixture data"""

    def __init__(self):
        self.api_key = "test-alpaca-key"
        self.secret_key = "test-alpaca-secret"
        self.base_url = "https://paper-api.alpaca.markets"
        self._order_counter = 1000

    def submit_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str = "market",
        time_in_force: str = "day",
        limit_price: float = None,
        **kwargs,
    ) -> dict:
        """Return mock order response matching REAL Alpaca API schema"""
        order_id = f"test-order-{self._order_counter}"
        self._order_counter += 1

        return {
            "id": order_id,
            "client_order_id": kwargs.get("client_order_id", f"client-{order_id}"),
            "created_at": datetime.now().isoformat() + "Z",
            "updated_at": datetime.now().isoformat() + "Z",
            "submitted_at": datetime.now().isoformat() + "Z",
            "filled_at": datetime.now().isoformat() + "Z",
            "expired_at": None,
            "canceled_at": None,
            "failed_at": None,
            "replaced_at": None,
            "replaced_by": None,
            "replaces": None,
            "asset_id": f"test-asset-{symbol}",
            "symbol": symbol,
            "asset_class": "us_equity",
            "qty": str(qty),
            "filled_qty": str(qty),
            "type": order_type,
            "side": side,
            "time_in_force": time_in_force,
            "limit_price": str(limit_price) if limit_price else None,
            "stop_price": None,
            "filled_avg_price": str(self._get_fill_price(symbol)),
            "status": "filled",
            "extended_hours": False,
            "legs": None,
        }

    def get_order(self, order_id: str) -> dict:
        """Return mock order status"""
        return {
            "id": order_id,
            "status": "filled",
            "filled_qty": "10",
            "filled_avg_price": "175.50",
        }

    def cancel_order(self, order_id: str) -> None:
        """Mock order cancellation"""
        pass  # Successfully cancelled

    def get_account(self) -> dict:
        """Return mock account data matching REAL Alpaca API schema"""
        return {
            "id": "test-account-id",
            "account_number": "PA123456789",
            "status": "ACTIVE",
            "currency": "USD",
            "buying_power": "200000.00",
            "regt_buying_power": "200000.00",
            "daytrading_buying_power": "400000.00",
            "cash": "100000.00",
            "portfolio_value": "150000.00",
            "pattern_day_trader": False,
            "trading_blocked": False,
            "transfers_blocked": False,
            "account_blocked": False,
            "created_at": "2024-01-01T00:00:00Z",
            "trade_suspended_by_user": False,
            "multiplier": "4",
            "shorting_enabled": True,
            "equity": "150000.00",
            "last_equity": "149500.00",
            "long_market_value": "50000.00",
            "short_market_value": "0",
            "initial_margin": "25000.00",
            "maintenance_margin": "15000.00",
            "last_maintenance_margin": "15000.00",
            "sma": "0",
            "daytrade_count": 0,
        }

    def get_positions(self) -> list[dict]:
        """Return mock positions matching REAL Alpaca API schema"""
        return []  # Empty by default

    def _get_fill_price(self, symbol: str) -> float:
        """Generate mock fill price"""
        prices = {
            "AAPL": 175.50,
            "MSFT": 380.30,
            "GOOGL": 138.55,
            "TSLA": 242.90,
            "NVDA": 485.25,
        }
        return prices.get(symbol, 100.00)


# ==================== PYTEST FIXTURES ====================


@pytest.fixture(scope="function")
def mock_tradier_client():
    """Provide mock Tradier client for integration tests"""
    return MockTradierClient()


@pytest.fixture(scope="function")
def mock_alpaca_client():
    """Provide mock Alpaca client for integration tests"""
    return MockAlpacaClient()


@pytest.fixture(scope="function", autouse=True)
def mock_external_apis(mock_tradier_client, mock_alpaca_client, monkeypatch):
    """
    Auto-patch external API clients for all integration tests

    This fixture runs automatically for all tests in the integration/ directory.
    It replaces real API clients with mocks that return fixture data.
    """

    # Mock get_tradier_client() to return our mock instance
    def mock_get_tradier_client():
        return mock_tradier_client

    monkeypatch.setattr(
        "app.services.tradier_client.get_tradier_client", mock_get_tradier_client
    )

    # Mock Alpaca HTTP requests (orders router uses direct HTTP calls)
    def mock_requests_post(url, **kwargs):
        """Mock HTTP POST requests to Alpaca API"""
        mock_response = MagicMock()
        mock_response.status_code = 200

        if "/orders" in url:
            # Order submission
            data = kwargs.get("json", {})
            order = mock_alpaca_client.submit_order(
                symbol=data.get("symbol", "UNKNOWN"),
                qty=int(data.get("qty", 1)),
                side=data.get("side", "buy"),
                order_type=data.get("type", "market"),
                time_in_force=data.get("time_in_force", "day"),
                limit_price=float(data.get("limit_price")) if data.get("limit_price") else None,
            )
            mock_response.json.return_value = order
        else:
            mock_response.json.return_value = {}

        return mock_response

    def mock_requests_get(url, **kwargs):
        """Mock HTTP GET requests to Alpaca API"""
        mock_response = MagicMock()
        mock_response.status_code = 200

        if "/account" in url:
            mock_response.json.return_value = mock_alpaca_client.get_account()
        elif "/positions" in url:
            mock_response.json.return_value = mock_alpaca_client.get_positions()
        elif "/orders/" in url:
            order_id = url.split("/")[-1]
            mock_response.json.return_value = mock_alpaca_client.get_order(order_id)
        else:
            mock_response.json.return_value = {}

        return mock_response

    def mock_requests_delete(url, **kwargs):
        """Mock HTTP DELETE requests to Alpaca API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        return mock_response

    # Patch requests module
    monkeypatch.setattr("requests.post", mock_requests_post)
    monkeypatch.setattr("requests.get", mock_requests_get)
    monkeypatch.setattr("requests.delete", mock_requests_delete)

    yield {
        "tradier": mock_tradier_client,
        "alpaca": mock_alpaca_client,
    }
