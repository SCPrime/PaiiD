import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.unified_auth import get_current_user_unified
from app.db.session import Base, get_db
from app.main import app
from app.models.database import Strategy, Trade, User


"""
Pytest Configuration and Fixtures

Provides test fixtures for database, API client, and mocked services.
"""

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = ""  # Disable Redis for tests
os.environ["SENTRY_DSN"] = ""  # Disable Sentry for tests
os.environ["TESTING"] = "true"  # Disable rate limiting for tests
os.environ["API_TOKEN"] = "test-token-12345"
os.environ["TRADIER_API_KEY"] = "test-tradier-key"
os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"

# ===========================================
# TEST AUTHENTICATION
# ===========================================
# IMPORTANT: User model requires password_hash (NOT NULL)
#
# DO NOT use real passwords in tests!
# The pre-computed TEST_PASSWORD_HASH is used for all test users.
#
# If auth tests need specific passwords, use passlib to hash them:
#   from passlib.context import CryptContext
#   pwd_context = CryptContext(schemes=["bcrypt"])
#   your_hash = pwd_context.hash("your-test-password")
# ===========================================

# Test password hash (pre-computed bcrypt hash for "TestPassword123!")
# Pre-computed to avoid hashing at module import time (which can cause bcrypt backend issues in CI)
# Original password: "TestPassword123!"
# Generated with: CryptContext(schemes=["bcrypt"]).hash("TestPassword123!")
TEST_PASSWORD_HASH = "$2b$12$LQ3JzqjX7Y8ZHnVc9r5MHOfWw8L4vQy8QWxK0X1y0HdTYJKRQ6qKK"

# ==================== DATABASE FIXTURES ====================


@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh test database for each test function

    Uses SQLite in-memory database for fast, isolated tests.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db, mock_tradier_client, mock_cache, monkeypatch):
    """
    FastAPI test client with database dependency override

    Usage:
        def test_endpoint(client):
            response = client.get("/api/health")
            assert response.status_code == 200

    Note: raise_server_exceptions=False prevents startup event failures from
    blocking test client initialization. This allows tests to run even if
    external services (Redis, Tradier, etc.) are unavailable.

    By default, this client comes with:
    - Mocked authentication (auto-creates test user)
    - Mocked Tradier client (no real API calls)
    - Mocked cache service (in-memory)
    """

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    def override_get_current_user():
        """Mock authentication for tests - creates/returns test user (id=1)"""
        user = test_db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(
                id=1,
                email="test@example.com",
                username="test_user",
                password_hash=TEST_PASSWORD_HASH,
                role="owner",
                is_active=True,
            )
            test_db.add(user)
            test_db.commit()
            test_db.refresh(user)
        return user

    def override_get_cache():
        """Mock cache service"""
        return mock_cache

    # Monkeypatch the get_tradier_client function at the module level
    # This needs to be done BEFORE importing the router modules
    monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_tradier_client)

    # Also patch in all router modules that import it
    monkeypatch.setattr("app.routers.market_data.get_tradier_client", lambda: mock_tradier_client)
    monkeypatch.setattr("app.routers.portfolio.get_tradier_client", lambda: mock_tradier_client)
    monkeypatch.setattr("app.routers.analytics.get_tradier_client", lambda: mock_tradier_client)
    monkeypatch.setattr("app.routers.options.get_tradier_client", lambda: mock_tradier_client)
    monkeypatch.setattr("app.routers.stock.get_tradier_client", lambda: mock_tradier_client)
    monkeypatch.setattr("app.routers.ai.get_tradier_client", lambda: mock_tradier_client)

    # Import dependencies to override
    from app.services.cache import get_cache

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_unified] = override_get_current_user
    app.dependency_overrides[get_cache] = override_get_cache

    # Use raise_server_exceptions=False to allow TestClient to start
    # even if startup events fail (e.g., Redis connection, external APIs)
    # This is safe because most tests don't depend on startup initialization
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers():
    """
    Authentication headers for API requests

    Usage:
        def test_protected_endpoint(client, auth_headers):
            response = client.get("/api/positions", headers=auth_headers)
            assert response.status_code == 200
    """
    return {"Authorization": "Bearer test-token-12345"}


@pytest.fixture(scope="function")
def client_no_auth(test_db):
    """
    FastAPI test client with NO authentication bypass (for testing auth failures)

    Use this client when you want to test that endpoints properly reject
    unauthenticated requests. This client overrides get_current_user_unified
    to raise 401 instead of using MVP fallback.

    Usage:
        def test_endpoint_requires_auth(client_no_auth):
            response = client_no_auth.get("/api/strategies/list")
            assert response.status_code == 401
    """

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    def override_get_current_user_strict():
        """Strict auth - no MVP fallback, raises 401 for missing auth"""
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required (test mode - no MVP fallback)"
        )

    from app.core.unified_auth import get_current_user_unified

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_unified] = override_get_current_user_strict

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ==================== MOCK CACHE FIXTURES ====================


class MockCacheService:
    """Mock cache service for testing without Redis"""

    def __init__(self):
        self.cache = {}
        self.available = True

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value, ttl: int = 60):
        self.cache[key] = value
        return True

    def delete(self, key: str):
        self.cache.pop(key, None)
        return True

    def clear_pattern(self, pattern: str):
        keys_to_delete = [k for k in self.cache.keys() if pattern.replace("*", "") in k]
        for key in keys_to_delete:
            del self.cache[key]
        return len(keys_to_delete)


@pytest.fixture(scope="function")
def mock_cache():
    """
    Mock cache service for testing cache behavior

    Usage:
        def test_caching(mock_cache):
            mock_cache.set("test_key", {"data": "value"})
            assert mock_cache.get("test_key") == {"data": "value"}
    """
    return MockCacheService()


# ==================== DATABASE MODEL FIXTURES ====================


@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing"""

    user = User(
        email="test@example.com",
        password_hash=TEST_PASSWORD_HASH,
        alpaca_account_id="TEST123",
        preferences={"risk_tolerance": "moderate"},
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_strategy(test_db, sample_user):
    """Create a sample strategy for testing"""

    strategy = Strategy(
        user_id=sample_user.id,
        name="Test Momentum Strategy",
        description="Buy stocks with strong momentum",
        strategy_type="momentum",
        config={
            "entry_rules": ["RSI > 60", "Price > MA50"],
            "exit_rules": ["RSI < 40", "Stop loss 2%"],
            "position_size": 0.10,
        },
        is_active=True,
        is_autopilot=False,
    )
    test_db.add(strategy)
    test_db.commit()
    test_db.refresh(strategy)
    return strategy


@pytest.fixture
def sample_trade(test_db, sample_user, sample_strategy):
    """Create a sample trade for testing"""

    trade = Trade(
        user_id=sample_user.id,
        strategy_id=sample_strategy.id,
        symbol="AAPL",
        side="buy",
        quantity=10,
        price=150.50,
        order_type="market",
        status="filled",
        filled_quantity=10,
        filled_avg_price=150.55,
    )
    test_db.add(trade)
    test_db.commit()
    test_db.refresh(trade)
    return trade


# ==================== MOCK API RESPONSES ====================


@pytest.fixture
def mock_tradier_quotes():
    """Mock Tradier API quote response"""
    return {
        "quotes": {
            "quote": [
                {
                    "symbol": "AAPL",
                    "last": 175.43,
                    "bid": 175.42,
                    "ask": 175.44,
                    "volume": 52341234,
                    "change": 2.15,
                    "change_percentage": 1.24,
                    "trade_date": "2025-10-13T16:00:00Z",
                },
                {
                    "symbol": "MSFT",
                    "last": 380.25,
                    "bid": 380.20,
                    "ask": 380.30,
                    "volume": 28543210,
                    "change": -1.50,
                    "change_percentage": -0.39,
                    "trade_date": "2025-10-13T16:00:00Z",
                },
            ]
        }
    }


@pytest.fixture
def mock_market_indices():
    """Mock market indices data"""
    return {
        "dow": {"last": 42500.00, "change": 125.50, "changePercent": 0.30},
        "nasdaq": {"last": 18350.00, "change": 98.75, "changePercent": 0.54},
        "source": "tradier",
    }


# ==================== COMPREHENSIVE API CLIENT MOCKS ====================


class MockTradierClient:
    """
    Comprehensive mock for Tradier API client with realistic responses.

    Mocks all commonly used Tradier endpoints with production-like data.
    """

    def get_quotes(self, symbols):
        """Mock get_quotes - returns dict keyed by symbol"""
        if isinstance(symbols, str):
            symbols = [symbols]

        result = {}
        for symbol in symbols:
            result[symbol.upper()] = {
                "symbol": symbol.upper(),
                "last": 175.0 if symbol.upper() == "AAPL" else 380.0,
                "bid": 174.95 if symbol.upper() == "AAPL" else 379.90,
                "ask": 175.05 if symbol.upper() == "AAPL" else 380.10,
                "volume": 1000000,
                "change": 2.15,
                "change_percentage": 1.24,
                "trade_date": "2025-10-27T16:00:00Z",
                "open": 172.50,
                "high": 176.00,
                "low": 172.00,
            }
        return result

    def get_historical_quotes(self, symbol, interval="daily", start=None, end=None):
        """Mock get_historical_quotes - returns list of OHLCV bars"""
        return [
            {
                "date": "2024-01-01",
                "open": 170.0,
                "high": 175.0,
                "low": 168.0,
                "close": 172.0,
                "volume": 1000000,
            },
            {
                "date": "2024-01-02",
                "open": 172.0,
                "high": 176.0,
                "low": 171.0,
                "close": 175.0,
                "volume": 1200000,
            },
        ]

    def get_options_chain(self, symbol, expiration=None):
        """Mock get_options_chain - returns options data"""
        return {
            "options": {
                "option": [
                    {
                        "symbol": f"{symbol}250117C00175000",
                        "strike": 175.0,
                        "type": "call",
                        "expiration_date": "2025-01-17",
                        "bid": 5.50,
                        "ask": 5.60,
                        "last": 5.55,
                        "volume": 1000,
                        "open_interest": 5000,
                        "greeks": {
                            "delta": 0.52,
                            "gamma": 0.03,
                            "theta": -0.05,
                            "vega": 0.15,
                        },
                    }
                ]
            }
        }

    def get_account(self):
        """Mock get_account - returns account data"""
        return {
            "cash": {"cash_available": 50000.0},
            "equities": {"market_value": 50000.0},
            "portfolio_value": 100000.0,
            "account_number": "TEST123",
            "day_trader": False,
        }

    def get_positions(self):
        """Mock get_positions - returns list of positions"""
        return [
            {
                "symbol": "AAPL",
                "quantity": 10,
                "cost_basis": 1500.0,
                "current_price": 175.0,
                "market_value": 1750.0,
                "unrealized_pl": 250.0,
                "unrealized_pl_percent": 16.67,
            },
            {
                "symbol": "MSFT",
                "quantity": 5,
                "cost_basis": 1900.0,
                "current_price": 380.0,
                "market_value": 1900.0,
                "unrealized_pl": 0.0,
                "unrealized_pl_percent": 0.0,
            },
        ]


class MockAlpacaClient:
    """
    Comprehensive mock for Alpaca API client with realistic responses.

    Mocks paper trading endpoints for order execution and account data.
    """

    def get_account(self):
        """Mock get_account - returns account data"""
        return {
            "cash": 50000.0,
            "portfolio_value": 100000.0,
            "equity": 100000.0,
            "buying_power": 50000.0,
            "daytrade_count": 0,
            "pattern_day_trader": False,
        }

    def get_positions(self):
        """Mock get_positions - returns list of positions"""
        return [
            {
                "symbol": "AAPL",
                "qty": "10",
                "avg_entry_price": "150.0",
                "current_price": "175.0",
                "market_value": "1750.0",
                "unrealized_pl": "250.0",
                "unrealized_plpc": "0.1667",
            }
        ]

    def submit_order(self, symbol, qty, side, order_type, time_in_force="day", **kwargs):
        """Mock submit_order - returns order object"""
        return {
            "id": "test-order-123",
            "client_order_id": kwargs.get("client_order_id", "test-client-123"),
            "symbol": symbol,
            "qty": str(qty),
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
            "status": "accepted",
            "filled_qty": "0",
            "filled_avg_price": None,
            "created_at": "2025-10-27T12:00:00Z",
        }

    def get_orders(self, status=None, limit=100):
        """Mock get_orders - returns list of orders"""
        return [
            {
                "id": "order-123",
                "symbol": "AAPL",
                "qty": "10",
                "side": "buy",
                "type": "market",
                "status": "filled",
                "filled_qty": "10",
                "filled_avg_price": "175.0",
            }
        ]


class MockAnthropicClient:
    """
    Comprehensive mock for Anthropic (Claude) API client.

    Mocks message creation with realistic response structure.
    """

    class Messages:
        def create(self, model, messages, max_tokens, system=None, **kwargs):
            """Mock messages.create - returns message object"""

            class MockContent:
                def __init__(self, text):
                    self.text = text
                    self.type = "text"

            class MockMessage:
                def __init__(self):
                    self.content = [MockContent("Hello! I'm Claude, your AI trading assistant. How can I help you today?")]
                    self.model = model
                    self.role = "assistant"
                    self.stop_reason = "end_turn"
                    self.usage = {"input_tokens": 10, "output_tokens": 20}

            return MockMessage()

    def __init__(self):
        self.messages = self.Messages()


@pytest.fixture
def mock_tradier_client():
    """
    Pytest fixture providing mock Tradier client.

    Usage:
        def test_market_data(mock_tradier_client, monkeypatch):
            monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_tradier_client)
            # Test code here
    """
    return MockTradierClient()


@pytest.fixture
def mock_alpaca_client():
    """
    Pytest fixture providing mock Alpaca client.

    Usage:
        def test_orders(mock_alpaca_client, monkeypatch):
            monkeypatch.setattr("app.services.alpaca_client.get_alpaca_client", lambda: mock_alpaca_client)
            # Test code here
    """
    return MockAlpacaClient()


@pytest.fixture
def mock_anthropic_client():
    """
    Pytest fixture providing mock Anthropic (Claude) client.

    Usage:
        def test_claude_chat(mock_anthropic_client, monkeypatch):
            monkeypatch.setattr("app.routers.claude.anthropic_client", mock_anthropic_client)
            # Test code here
    """
    return MockAnthropicClient()


# ==================== HELPER FUNCTIONS ====================


def create_test_user(db, email="test@example.com"):
    """Helper to create test user"""

    user = User(email=email, password_hash=TEST_PASSWORD_HASH, preferences={})
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_strategy(db, user_id, name="Test Strategy"):
    """Helper to create test strategy"""

    strategy = Strategy(
        user_id=user_id,
        name=name,
        description="Test strategy",
        strategy_type="custom",
        config={"test": True},
        is_active=False,
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy
