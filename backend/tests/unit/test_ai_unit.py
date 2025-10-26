"""
Unit tests for AI Recommendations Router (ai.py)

Tests all 14+ endpoints in the AI router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import User


client = TestClient(app, raise_server_exceptions=False)


class TestAIRecommendations:
    """Test suite for AI recommendations endpoints"""

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return User(id=1, email="test@example.com", username="test_user", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {"Authorization": "Bearer test-token-12345"}

    @pytest.fixture
    def mock_tradier_quotes(self):
        """Mock Tradier quotes response"""
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
                    }
                ]
            }
        }

    @pytest.fixture
    def mock_portfolio_data(self):
        """Mock portfolio data from Alpaca"""
        return {
            "total_value": 100000.0,
            "cash": 50000.0,
            "positions": [
                {"symbol": "AAPL", "qty": 10, "market_value": 1754.30, "pct_of_portfolio": 1.75}
            ],
            "num_positions": 1,
        }

    # ===========================================
    # TEST: GET /ai/recommendations
    # ===========================================

    def test_get_recommendations_success(self, mock_user, auth_headers, monkeypatch):
        """Test successful recommendations retrieval"""
        # Mock authentication
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        # Mock Tradier client
        mock_client = Mock()
        mock_client.get_quotes.return_value = {
            "quotes": {
                "quote": [
                    {
                        "symbol": "AAPL",
                        "last": 175.0,
                        "volume": 1000000,
                        "change_percentage": 1.5,
                    }
                ]
            }
        }
        monkeypatch.setattr("app.routers.ai.get_tradier_client", lambda: mock_client)

        # Mock portfolio fetch
        async def mock_fetch_portfolio():
            return {"total_value": 100000.0, "cash": 50000.0, "positions": [], "num_positions": 0}

        monkeypatch.setattr("app.routers.ai._fetch_portfolio_data", mock_fetch_portfolio)

        # Mock sector performance
        async def mock_sector_perf():
            return {"sectors": [], "leader": "Technology", "laggard": "Energy"}

        monkeypatch.setattr("app.routers.ai._fetch_sector_performance", mock_sector_perf)

        # Mock momentum analysis
        async def mock_momentum(symbol, price, volume):
            return {
                "sma_20": 170.0,
                "sma_50": 165.0,
                "sma_200": 160.0,
                "price_vs_sma_20": 2.94,
                "price_vs_sma_50": 6.06,
                "price_vs_sma_200": 9.38,
                "avg_volume_20d": 800000,
                "volume_strength": "High",
                "volume_ratio": 1.25,
                "trend_alignment": "Bullish",
            }

        monkeypatch.setattr("app.routers.ai._calculate_momentum_analysis", mock_momentum)

        # Mock volatility analysis
        async def mock_volatility(symbol, price):
            return {
                "atr": 3.5,
                "atr_percent": 2.0,
                "bb_width": 4.0,
                "volatility_class": "Medium",
                "volatility_score": 5.0,
            }

        monkeypatch.setattr("app.routers.ai._calculate_volatility_analysis", mock_volatility)

        response = client.get("/api/ai/recommendations", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "generated_at" in data
        assert isinstance(data["recommendations"], list)

    def test_get_recommendations_unauthorized(self):
        """Test recommendations without authentication"""
        response = client.get("/api/ai/recommendations")
        assert response.status_code in [401, 403]

    # ===========================================
    # TEST: GET /ai/recommendations/{symbol}
    # ===========================================

    def test_get_symbol_recommendation_success(self, monkeypatch):
        """Test successful single symbol recommendation"""
        # Mock Tradier client
        mock_client = Mock()
        mock_client.get_quote.return_value = {"last": 175.0, "volume": 1000000}
        monkeypatch.setattr("app.routers.ai.get_tradier_client", lambda: mock_client)

        response = client.get("/api/ai/recommendations/AAPL")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert "action" in data
        assert "confidence" in data
        assert "currentPrice" in data

    def test_get_symbol_recommendation_invalid_symbol(self):
        """Test recommendation with invalid symbol format"""
        response = client.get("/api/ai/recommendations/INVALID@SYMBOL")
        assert response.status_code == 422

    def test_get_symbol_recommendation_not_found(self, monkeypatch):
        """Test recommendation when symbol data not available"""
        mock_client = Mock()
        mock_client.get_quote.return_value = {}
        monkeypatch.setattr("app.routers.ai.get_tradier_client", lambda: mock_client)

        response = client.get("/api/ai/recommendations/AAPL")
        assert response.status_code == 404

    # ===========================================
    # TEST: GET /ai/signals
    # ===========================================

    def test_get_ml_signals_success(self, mock_user, auth_headers, monkeypatch):
        """Test ML signals generation with technical analysis"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        # Mock technical signal generation
        async def mock_tech_signal(symbol):
            from app.routers.ai import Recommendation

            return Recommendation(
                symbol=symbol,
                action="BUY",
                confidence=75.0,
                score=7.5,
                reason="Strong technical signal",
                currentPrice=175.0,
                targetPrice=185.0,
            )

        monkeypatch.setattr("app.routers.ai._generate_technical_signal", mock_tech_signal)

        response = client.get(
            "/api/ai/signals?symbols=AAPL,MSFT&min_confidence=70&use_technical=true",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0

    def test_get_ml_signals_no_symbols(self, mock_user, auth_headers, monkeypatch):
        """Test ML signals with default watchlist"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        async def mock_tech_signal(symbol):
            return None  # No signals meet criteria

        monkeypatch.setattr("app.routers.ai._generate_technical_signal", mock_tech_signal)

        response = client.get("/api/ai/signals", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data

    # ===========================================
    # TEST: GET /ai/analyze-symbol/{symbol}
    # ===========================================

    def test_analyze_symbol_success(self, mock_user, auth_headers, monkeypatch):
        """Test comprehensive symbol analysis"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_quote.return_value = {"last": 175.0}
        mock_client.get_historical_bars.return_value = [
            {"close": 170.0, "high": 172.0, "low": 168.0} for _ in range(200)
        ]
        monkeypatch.setattr("app.routers.ai.get_tradier_client", lambda: mock_client)

        # Mock TechnicalIndicators
        mock_signal = {
            "symbol": "AAPL",
            "action": "BUY",
            "confidence": 80.0,
            "current_price": 175.0,
            "entry_price": 174.0,
            "stop_loss": 170.0,
            "take_profit": 180.0,
            "risk_reward_ratio": 2.5,
            "reasons": ["Strong momentum", "RSI oversold"],
            "indicators": {"rsi": 35, "macd_histogram": 0.5, "sma_20": 170.0, "sma_50": 165.0},
        }
        monkeypatch.setattr(
            "app.routers.ai.TechnicalIndicators.generate_signal", lambda symbol, prices: mock_signal
        )

        response = client.get("/api/ai/analyze-symbol/AAPL", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert "analysis" in data
        assert "momentum" in data
        assert "trend" in data
        assert "confidence_score" in data

    def test_analyze_symbol_insufficient_data(self, mock_user, auth_headers, monkeypatch):
        """Test symbol analysis with insufficient historical data"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_quote.return_value = {"last": 175.0}
        mock_client.get_historical_bars.return_value = []  # No data
        monkeypatch.setattr("app.routers.ai.get_tradier_client", lambda: mock_client)

        response = client.get("/api/ai/analyze-symbol/AAPL", headers=auth_headers)

        assert response.status_code == 400

    # ===========================================
    # TEST: GET /ai/recommended-templates
    # ===========================================

    def test_get_recommended_templates_success(self, mock_user, auth_headers, monkeypatch, test_db):
        """Test strategy template recommendations"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        # Mock portfolio fetch
        async def mock_fetch_portfolio():
            return {"total_value": 100000.0, "cash": 50000.0, "positions": [], "num_positions": 0}

        monkeypatch.setattr("app.routers.ai._fetch_portfolio_data", mock_fetch_portfolio)

        # Mock strategy templates
        from app.services.strategy_templates import StrategyTemplate

        mock_templates = [
            StrategyTemplate(
                id="momentum_1",
                name="Momentum Strategy",
                description="Buy strong momentum stocks",
                strategy_type="momentum",
                risk_level="Moderate",
                expected_win_rate=65,
                avg_return_percent=2.5,
                max_drawdown_percent=10.0,
                recommended_for=["Moderate risk traders"],
            )
        ]
        monkeypatch.setattr(
            "app.services.strategy_templates.filter_templates_by_risk", lambda risk: mock_templates
        )
        monkeypatch.setattr(
            "app.services.strategy_templates.get_template_compatibility_score",
            lambda template, risk, volatility, value: 85.0,
        )

        response = client.get("/api/ai/recommended-templates", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "user_risk_tolerance" in data
        assert "market_volatility" in data

    # ===========================================
    # TEST: POST /ai/recommendations/save
    # ===========================================

    def test_save_recommendation_success(self, mock_user, auth_headers, monkeypatch, test_db):
        """Test saving recommendation to history"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        request_data = {
            "symbol": "AAPL",
            "recommendation_type": "buy",
            "confidence_score": 85.0,
            "analysis_data": {"rsi": 35},
            "suggested_entry_price": 175.0,
            "suggested_stop_loss": 170.0,
            "suggested_take_profit": 185.0,
            "reasoning": "Strong momentum signal",
        }

        response = client.post("/api/ai/recommendations/save", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommendation_id" in data

    def test_save_recommendation_validation_error(self, auth_headers):
        """Test saving recommendation with invalid data"""
        request_data = {
            "symbol": "AAPL",
            "recommendation_type": "invalid",  # Invalid type
            "confidence_score": 150.0,  # Out of range
        }

        response = client.post("/api/ai/recommendations/save", json=request_data, headers=auth_headers)

        assert response.status_code == 422

    # ===========================================
    # TEST: GET /ai/recommendations/history
    # ===========================================

    def test_get_recommendation_history_success(self, mock_user, auth_headers, monkeypatch, test_db):
        """Test retrieving recommendation history"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        response = client.get("/api/ai/recommendations/history?limit=50", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_recommendation_history_filtered(self, mock_user, auth_headers, monkeypatch, test_db):
        """Test recommendation history with filters"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        response = client.get(
            "/api/ai/recommendations/history?symbol=AAPL&status=pending", headers=auth_headers
        )

        assert response.status_code == 200

    # ===========================================
    # TEST: GET /ai/analyze-portfolio
    # ===========================================

    def test_analyze_portfolio_success(self, mock_user, auth_headers, monkeypatch):
        """Test AI-powered portfolio analysis"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_account.return_value = {
            "total_equity": 100000.0,
            "total_cash": 50000.0,
            "option_buying_power": 75000.0,
        }
        mock_client.get_positions.return_value = []
        monkeypatch.setattr("app.routers.ai.get_tradier_client", lambda: mock_client)

        # Mock Anthropic client
        mock_anthropic = Mock()
        mock_message = Mock()
        mock_message.content = [
            Mock(
                text='{"health_score": 75, "risk_level": "Medium", "recommendations": ["rec1", "rec2", "rec3"], "risk_factors": ["risk1", "risk2", "risk3"], "opportunities": ["opp1", "opp2", "opp3"], "ai_summary": "Portfolio is healthy."}'
            )
        ]
        mock_anthropic.messages.create.return_value = mock_message

        with patch("app.routers.ai.Anthropic", return_value=mock_anthropic):
            response = client.get("/api/ai/analyze-portfolio", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "health_score" in data
        assert "risk_level" in data
        assert "recommendations" in data

    def test_analyze_portfolio_no_api_key(self, mock_user, auth_headers, monkeypatch):
        """Test portfolio analysis fallback when API key not configured"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_account.return_value = {
            "total_equity": 100000.0,
            "total_cash": 50000.0,
            "option_buying_power": 75000.0,
        }
        mock_client.get_positions.return_value = []
        monkeypatch.setattr("app.routers.ai.get_tradier_client", lambda: mock_client)

        # Set ANTHROPIC_API_KEY to None
        monkeypatch.setenv("ANTHROPIC_API_KEY", "")

        response = client.get("/api/ai/analyze-portfolio", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "health_score" in data  # Should use rule-based fallback

    # ===========================================
    # TEST: POST /ai/analyze-news
    # ===========================================

    def test_analyze_news_success(self, mock_user, auth_headers, monkeypatch):
        """Test AI news article analysis"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_positions.return_value = [{"symbol": "AAPL"}]
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        # Mock Anthropic
        mock_anthropic = Mock()
        mock_message = Mock()
        mock_message.content = [
            Mock(
                text='{"sentiment": "bullish", "sentiment_score": 0.8, "confidence": 85, "tickers_mentioned": ["AAPL"], "portfolio_impact": "high", "affected_positions": ["AAPL"], "key_points": ["point1"], "trading_implications": "Positive news", "urgency": "high", "summary": "Tech stocks rally"}'
            )
        ]
        mock_anthropic.messages.create.return_value = mock_message

        article = {
            "title": "Apple Reports Strong Earnings",
            "content": "Apple exceeded expectations...",
            "source": "CNBC",
        }

        with patch("app.routers.ai.Anthropic", return_value=mock_anthropic):
            response = client.post("/api/ai/analyze-news", json=article, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ai_analysis" in data

    def test_analyze_news_missing_content(self, auth_headers):
        """Test news analysis with missing article content"""
        article = {}

        response = client.post("/api/ai/analyze-news", json=article, headers=auth_headers)

        assert response.status_code == 400

    # ===========================================
    # TEST: POST /ai/analyze-news-batch
    # ===========================================

    def test_analyze_news_batch_success(self, mock_user, auth_headers, monkeypatch):
        """Test batch news analysis"""
        monkeypatch.setattr("app.routers.ai.get_current_user_unified", lambda: mock_user)

        mock_client = Mock()
        mock_client.get_positions.return_value = []
        monkeypatch.setattr("app.services.tradier_client.get_tradier_client", lambda: mock_client)

        # Mock Anthropic
        mock_anthropic = Mock()
        mock_message = Mock()
        mock_message.content = [
            Mock(
                text='{"sentiment": "neutral", "sentiment_score": 0.0, "confidence": 70, "tickers_mentioned": [], "portfolio_impact": "low", "affected_positions": [], "key_points": ["point1"], "trading_implications": "No impact", "urgency": "low", "summary": "Market update"}'
            )
        ]
        mock_anthropic.messages.create.return_value = mock_message

        articles = [
            {"title": "Article 1", "content": "Content 1", "source": "CNBC"},
            {"title": "Article 2", "content": "Content 2", "source": "Reuters"},
        ]

        with patch("app.routers.ai.Anthropic", return_value=mock_anthropic):
            response = client.post("/api/ai/analyze-news-batch", json=articles, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data
        assert data["analyzed_count"] > 0
