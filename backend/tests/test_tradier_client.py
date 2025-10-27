"""
Tests for Tradier API client service
Tests circuit breaker, caching, error handling, and market data fetching
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, UTC
import requests

from app.services.tradier_client import TradierClient


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for Tradier"""
    monkeypatch.setenv("TRADIER_API_KEY", "test_api_key_12345")
    monkeypatch.setenv("TRADIER_ACCOUNT_ID", "VA12345678")
    monkeypatch.setenv("TRADIER_API_BASE_URL", "https://api.tradier.com/v1")


@pytest.fixture
def tradier_client(mock_env):
    """Create a Tradier client instance with mocked environment"""
    return TradierClient()


@pytest.fixture
def mock_session():
    """Mock requests session"""
    session = Mock()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"success": True}
    session.request.return_value = response
    return session


class TestTradierClientInitialization:
    """Test Tradier client initialization"""

    def test_client_initialization_success(self, mock_env):
        """Test successful client initialization"""
        client = TradierClient()
        assert client.api_key == "test_api_key_12345"
        assert client.account_id == "VA12345678"
        assert client.base_url == "https://api.tradier.com/v1"
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test_api_key_12345"

    def test_client_initialization_missing_api_key(self, monkeypatch):
        """Test initialization fails without API key"""
        monkeypatch.setenv("TRADIER_ACCOUNT_ID", "VA12345678")
        monkeypatch.delenv("TRADIER_API_KEY", raising=False)

        with pytest.raises(ValueError, match="TRADIER_API_KEY and TRADIER_ACCOUNT_ID must be set"):
            TradierClient()

    def test_client_initialization_missing_account_id(self, monkeypatch):
        """Test initialization fails without account ID"""
        monkeypatch.setenv("TRADIER_API_KEY", "test_key")
        monkeypatch.delenv("TRADIER_ACCOUNT_ID", raising=False)

        with pytest.raises(ValueError, match="TRADIER_API_KEY and TRADIER_ACCOUNT_ID must be set"):
            TradierClient()


class TestTradierCircuitBreaker:
    """Test circuit breaker pattern for Tradier API"""

    def test_circuit_breaker_closed_by_default(self, tradier_client):
        """Test circuit starts in CLOSED state"""
        assert tradier_client._state == "CLOSED"
        assert tradier_client._is_available() is True

    def test_circuit_breaker_opens_after_failures(self, tradier_client):
        """Test circuit opens after 3 consecutive failures"""
        # Record 3 failures
        tradier_client._record_failure()
        assert tradier_client._state == "CLOSED"  # Still closed after 1

        tradier_client._record_failure()
        assert tradier_client._state == "CLOSED"  # Still closed after 2

        tradier_client._record_failure()
        assert tradier_client._state == "OPEN"  # Opens after 3
        assert tradier_client._is_available() is False

    def test_circuit_breaker_half_open_after_cooldown(self, tradier_client):
        """Test circuit moves to HALF_OPEN after cooldown period"""
        # Open the circuit
        tradier_client._record_failure()
        tradier_client._record_failure()
        tradier_client._record_failure()
        assert tradier_client._state == "OPEN"

        # Simulate cooldown period passing
        tradier_client._last_failure_at = datetime.now(UTC) - timedelta(seconds=31)

        # Should now be HALF_OPEN
        assert tradier_client._is_available() is True
        assert tradier_client._state == "HALF_OPEN"

    def test_circuit_breaker_resets_on_success(self, tradier_client):
        """Test circuit resets to CLOSED on successful request"""
        # Open the circuit
        tradier_client._record_failure()
        tradier_client._record_failure()
        tradier_client._record_failure()
        assert tradier_client._state == "OPEN"

        # Record success
        tradier_client._record_success()
        assert tradier_client._state == "CLOSED"
        assert tradier_client._failures == 0
        assert tradier_client._last_failure_at is None


class TestTradierAccountMethods:
    """Test account-related methods"""

    def test_get_account_success(self, tradier_client, monkeypatch):
        """Test successful account balance retrieval"""
        mock_response = {
            "balances": {
                "total_cash": "10000.00",
                "option_buying_power": "25000.00",
                "total_equity": "15000.00",
                "long_market_value": "5000.00",
                "short_market_value": "0.00"
            }
        }

        mock_request = Mock(return_value=mock_response)
        monkeypatch.setattr(tradier_client, "_request", mock_request)

        result = tradier_client.get_account()

        assert result["account_number"] == "VA12345678"
        assert result["cash"] == 10000.00
        assert result["buying_power"] == 25000.00
        assert result["portfolio_value"] == 15000.00
        assert result["status"] == "ACTIVE"

    def test_get_profile_success(self, tradier_client, monkeypatch):
        """Test user profile retrieval"""
        mock_response = {"profile": {"id": "test_user", "name": "Test User"}}

        mock_request = Mock(return_value=mock_response)
        monkeypatch.setattr(tradier_client, "_request", mock_request)

        result = tradier_client.get_profile()
        assert result == mock_response


class TestTradierPositions:
    """Test position retrieval and normalization"""

    def test_get_positions_empty(self, tradier_client, monkeypatch):
        """Test getting positions when account has none"""
        mock_response = {"positions": "null"}

        mock_request = Mock(return_value=mock_response)
        monkeypatch.setattr(tradier_client, "_request", mock_request)

        positions = tradier_client.get_positions()
        assert positions == []

    def test_get_positions_single(self, tradier_client, monkeypatch):
        """Test getting a single position (dict format)"""
        mock_response = {
            "positions": {
                "position": {
                    "symbol": "AAPL",
                    "quantity": "10",
                    "cost_basis": "1500.00"
                }
            }
        }

        mock_request = Mock(return_value=mock_response)
        monkeypatch.setattr(tradier_client, "_request", mock_request)

        positions = tradier_client.get_positions()
        assert len(positions) == 1
        assert positions[0]["symbol"] == "AAPL"

    def test_get_positions_multiple(self, tradier_client, monkeypatch):
        """Test getting multiple positions (list format)"""
        mock_response = {
            "positions": {
                "position": [
                    {"symbol": "AAPL", "quantity": "10", "cost_basis": "1500.00"},
                    {"symbol": "MSFT", "quantity": "20", "cost_basis": "3000.00"}
                ]
            }
        }

        mock_request = Mock(return_value=mock_response)
        monkeypatch.setattr(tradier_client, "_request", mock_request)

        positions = tradier_client.get_positions()
        assert len(positions) == 2
        assert positions[0]["symbol"] == "AAPL"
        assert positions[1]["symbol"] == "MSFT"

    def test_normalize_position(self, tradier_client):
        """Test position normalization"""
        raw_position = {
            "symbol": "SPY",
            "quantity": "-5",  # Negative for short
            "cost_basis": "2000.00"
        }

        normalized = tradier_client._normalize_position(raw_position)
        assert normalized["symbol"] == "SPY"
        assert normalized["qty"] == "5.0"  # Absolute value as string


class TestTradierRequestMethod:
    """Test internal request method with error handling"""

    def test_request_success(self, tradier_client, monkeypatch):
        """Test successful API request"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_session.request.return_value = mock_response

        monkeypatch.setattr(tradier_client, "session", mock_session)

        result = tradier_client._request("GET", "/test")
        assert result == {"data": "success"}
        assert tradier_client._state == "CLOSED"

    def test_request_http_error(self, tradier_client, monkeypatch):
        """Test handling of HTTP errors"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_session.request.return_value = mock_response

        monkeypatch.setattr(tradier_client, "session", mock_session)

        with pytest.raises(Exception, match="Tradier API error"):
            tradier_client._request("GET", "/test")

        # Should increment failure count
        assert tradier_client._failures == 1

    def test_request_timeout(self, tradier_client, monkeypatch):
        """Test handling of request timeouts"""
        mock_session = Mock()
        mock_session.request.side_effect = requests.exceptions.Timeout("Request timed out")

        monkeypatch.setattr(tradier_client, "session", mock_session)

        with pytest.raises(requests.exceptions.Timeout):
            tradier_client._request("GET", "/test")

        # Should increment failure count
        assert tradier_client._failures == 1

    def test_request_circuit_open(self, tradier_client):
        """Test request blocked when circuit is open"""
        # Open the circuit
        tradier_client._state = "OPEN"
        tradier_client._last_failure_at = datetime.now(UTC)

        with pytest.raises(Exception, match="Tradier temporarily unavailable"):
            tradier_client._request("GET", "/test")

    def test_request_default_timeout(self, tradier_client, monkeypatch):
        """Test default timeout is set"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_session.request.return_value = mock_response

        monkeypatch.setattr(tradier_client, "session", mock_session)

        tradier_client._request("GET", "/test")

        # Verify timeout was set
        call_kwargs = mock_session.request.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == 5


class TestTradierErrorHandling:
    """Test error handling scenarios"""

    def test_consecutive_failures_open_circuit(self, tradier_client, monkeypatch):
        """Test that 3 consecutive failures open the circuit"""
        mock_session = Mock()
        mock_session.request.side_effect = requests.exceptions.ConnectionError("Connection failed")

        monkeypatch.setattr(tradier_client, "session", mock_session)

        # First failure
        with pytest.raises(requests.exceptions.ConnectionError):
            tradier_client._request("GET", "/test")
        assert tradier_client._state == "CLOSED"

        # Second failure
        with pytest.raises(requests.exceptions.ConnectionError):
            tradier_client._request("GET", "/test")
        assert tradier_client._state == "CLOSED"

        # Third failure - circuit opens
        with pytest.raises(requests.exceptions.ConnectionError):
            tradier_client._request("GET", "/test")
        assert tradier_client._state == "OPEN"

    def test_malformed_response(self, tradier_client, monkeypatch):
        """Test handling of malformed JSON response"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_session.request.return_value = mock_response

        monkeypatch.setattr(tradier_client, "session", mock_session)

        with pytest.raises(ValueError):
            tradier_client._request("GET", "/test")


class TestTradierSessionManagement:
    """Test connection pooling and session management"""

    def test_session_pooling_configured(self, tradier_client):
        """Test that session has connection pooling configured"""
        assert tradier_client.session is not None
        # Verify adapter is mounted
        assert "http://" in tradier_client.session.adapters
        assert "https://" in tradier_client.session.adapters

    def test_compression_headers(self, tradier_client):
        """Test that compression is enabled in headers"""
        assert "Accept-Encoding" in tradier_client.headers
        assert "gzip" in tradier_client.headers["Accept-Encoding"]
