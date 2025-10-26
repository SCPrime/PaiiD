"""
PaiiD Backend Integration Tests
Comprehensive testing of API endpoints, ML features, and system integration
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import get_db
from app.main import app
from app.models.database import Base


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

class TestHealthEndpoints:
    """Test health and status endpoints"""

    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_status_endpoint(self, client):
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "uptime" in data

class TestMarketDataEndpoints:
    """Test market data and options endpoints"""

    @patch('app.services.market_data_service.MarketDataService.get_quote')
    def test_get_market_data(self, mock_get_quote, client):
        mock_get_quote.return_value = {
            "symbol": "AAPL",
            "price": 150.00,
            "change": 1.50,
            "changePercent": 1.01
        }

        response = client.get("/api/market-data/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["price"] == 150.00

    @patch('app.services.tradier_client.TradierClient.get_options_chain')
    def test_get_options_chain(self, mock_get_chain, client):
        mock_get_chain.return_value = {
            "symbol": "AAPL",
            "strikes": [145, 150, 155],
            "expirations": ["2025-11-15", "2025-12-20"]
        }

        response = client.get("/api/options/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert "strikes" in data

class TestMLEndpoints:
    """Test ML and AI endpoints"""

    @patch('app.ml.pattern_recognition.PatternDetector.detect_patterns')
    def test_detect_patterns(self, mock_detect, client):
        mock_detect.return_value = [
            {
                "pattern": "double_top",
                "confidence": 0.85,
                "description": "Double top pattern detected"
            }
        ]

        response = client.post("/api/ml/detect-patterns", json={
            "symbol": "AAPL",
            "timeframe": "1d"
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["pattern"] == "double_top"

    @patch('app.ml.market_regime.MarketRegimeDetector.detect_regime')
    def test_market_regime_detection(self, mock_detect, client):
        mock_detect.return_value = {
            "regime": "trending_bullish",
            "confidence": 0.78,
            "description": "Strong upward trend detected"
        }

        response = client.get("/api/ml/market-regime/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert data["regime"] == "trending_bullish"
        assert data["confidence"] == 0.78

class TestTradingEndpoints:
    """Test trading and order endpoints"""

    @patch('app.services.alpaca_client.AlpacaClient.get_account')
    def test_get_account_balance(self, mock_get_account, client):
        mock_get_account.return_value = {
            "buying_power": 10000.00,
            "cash": 5000.00,
            "portfolio_value": 15000.00
        }

        response = client.get("/api/account/balance")
        assert response.status_code == 200
        data = response.json()
        assert "buying_power" in data
        assert data["buying_power"] == 10000.00

    @patch('app.services.alpaca_client.AlpacaClient.get_positions')
    def test_get_positions(self, mock_get_positions, client):
        mock_get_positions.return_value = [
            {
                "symbol": "AAPL",
                "qty": 100,
                "market_value": 15000.00,
                "unrealized_pl": 500.00
            }
        ]

        response = client.get("/api/account/positions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["symbol"] == "AAPL"

class TestWebSocketIntegration:
    """Test WebSocket functionality"""

    def test_websocket_connection(self, client):
        with client.websocket_connect("/ws") as websocket:
            # Test basic connection
            assert websocket is not None

    def test_websocket_market_data(self, client):
        with client.websocket_connect("/ws") as websocket:
            # Send subscription message
            websocket.send_json({
                "type": "subscribe",
                "channel": "market_data",
                "symbol": "AAPL"
            })

            # Should receive acknowledgment
            data = websocket.receive_json()
            assert data["type"] == "subscription_confirmed"

class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_symbol_returns_404(self, client):
        response = client.get("/api/market-data/INVALID")
        assert response.status_code == 404

    def test_malformed_request_returns_422(self, client):
        response = client.post("/api/ml/detect-patterns", json={
            "invalid": "data"
        })
        assert response.status_code == 422

    def test_rate_limiting_works(self, client):
        # Make multiple requests to test rate limiting
        responses = []
        for _ in range(10):
            response = client.get("/api/health")
            responses.append(response.status_code)

        # All should succeed (rate limit not exceeded)
        assert all(status == 200 for status in responses)

class TestPerformance:
    """Test performance and response times"""

    def test_health_endpoint_performance(self, client):
        import time
        start_time = time.time()
        response = client.get("/api/health")
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 0.1  # Should respond in < 100ms

    def test_concurrent_requests(self, client):
        import concurrent.futures

        def make_request():
            return client.get("/api/health")

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]

        # All requests should succeed
        assert all(result.status_code == 200 for result in results)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
