"""
Pytest Configuration and Fixtures

Provides test fixtures for database, API client, and mocked services.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = ""  # Disable Redis for tests
os.environ["SENTRY_DSN"] = ""  # Disable Sentry for tests
os.environ["TESTING"] = "true"  # Disable rate limiting for tests
os.environ["API_TOKEN"] = "test-token-12345"
os.environ["TRADIER_API_KEY"] = "test-tradier-key"
os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"

from app.main import app
from app.db.session import Base, get_db
from app.services.cache import CacheService

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
def client(test_db):
    """
    FastAPI test client with database dependency override

    Usage:
        def test_endpoint(client):
            response = client.get("/api/health")
            assert response.status_code == 200
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
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
    from app.models.database import User

    user = User(
        email="test@example.com",
        password_hash=TEST_PASSWORD_HASH,
        alpaca_account_id="TEST123",
        preferences={"risk_tolerance": "moderate"}
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_strategy(test_db, sample_user):
    """Create a sample strategy for testing"""
    from app.models.database import Strategy

    strategy = Strategy(
        user_id=sample_user.id,
        name="Test Momentum Strategy",
        description="Buy stocks with strong momentum",
        strategy_type="momentum",
        config={
            "entry_rules": ["RSI > 60", "Price > MA50"],
            "exit_rules": ["RSI < 40", "Stop loss 2%"],
            "position_size": 0.10
        },
        is_active=True,
        is_autopilot=False
    )
    test_db.add(strategy)
    test_db.commit()
    test_db.refresh(strategy)
    return strategy


@pytest.fixture
def sample_trade(test_db, sample_user, sample_strategy):
    """Create a sample trade for testing"""
    from app.models.database import Trade

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
        filled_avg_price=150.55
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
                    "trade_date": "2025-10-13T16:00:00Z"
                },
                {
                    "symbol": "MSFT",
                    "last": 380.25,
                    "bid": 380.20,
                    "ask": 380.30,
                    "volume": 28543210,
                    "change": -1.50,
                    "change_percentage": -0.39,
                    "trade_date": "2025-10-13T16:00:00Z"
                }
            ]
        }
    }


@pytest.fixture
def mock_market_indices():
    """Mock market indices data"""
    return {
        "dow": {"last": 42500.00, "change": 125.50, "changePercent": 0.30},
        "nasdaq": {"last": 18350.00, "change": 98.75, "changePercent": 0.54},
        "source": "tradier"
    }


# ==================== HELPER FUNCTIONS ====================

def create_test_user(db, email="test@example.com"):
    """Helper to create test user"""
    from app.models.database import User
    user = User(
        email=email,
        password_hash=TEST_PASSWORD_HASH,
        preferences={}
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_strategy(db, user_id, name="Test Strategy"):
    """Helper to create test strategy"""
    from app.models.database import Strategy
    strategy = Strategy(
        user_id=user_id,
        name=name,
        description="Test strategy",
        strategy_type="custom",
        config={"test": True},
        is_active=False
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy
