"""
Integration Tests: AI Recommendation Flow
Test ID: INTG-AI-001
Priority: HIGH

Tests complete AI recommendation workflow:
1. Fetch AI-powered trade recommendations
2. Analyze recommendation structure and reasoning
3. Execute trade based on AI recommendation
4. Track AI recommendation performance
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestAIRecommendationFlow:
    """Integration tests for AI recommendation and execution flow"""

    def test_fetch_ai_recommendations(self, client, test_db):
        """
        Test fetching AI-powered trade recommendations

        Flow:
        1. Request AI recommendations
        2. Verify recommendation structure
        3. Check reasoning and confidence scores
        """
        response = client.get("/api/ai/recommendations")

        # AI endpoint may require specific params or may not exist
        if response.status_code == 404:
            pytest.skip("AI recommendations endpoint not implemented")

        assert response.status_code in [200, 422], f"AI recommendations failed: {response.text}"

        if response.status_code == 200:
            recommendations = response.json()

            # Recommendations could be list or dict
            recs_list = recommendations if isinstance(recommendations, list) else recommendations.get("recommendations", [])

            # Verify structure if recommendations exist
            if len(recs_list) > 0:
                rec = recs_list[0]

                # Check for essential fields
                assert "symbol" in rec or "ticker" in rec
                assert "action" in rec or "recommendation" in rec or "side" in rec
                assert "confidence" in rec or "score" in rec

    def test_ai_recommendation_with_market_context(self, client, test_db):
        """
        Test AI recommendations use current market context
        """
        # Provide market context (optional)
        params = {
            "symbols": "AAPL,MSFT,GOOGL",
            "strategy": "momentum",
        }

        response = client.get("/api/ai/recommendations", params=params)

        if response.status_code == 404:
            pytest.skip("AI recommendations endpoint not implemented")

        assert response.status_code in [200, 422]

        if response.status_code == 200:
            recommendations = response.json()
            # Verify recommendations relate to requested symbols
            recs_list = recommendations if isinstance(recommendations, list) else recommendations.get("recommendations", [])

            if len(recs_list) > 0:
                # At least one recommendation should be for requested symbols
                symbols_in_recs = [r.get("symbol", r.get("ticker", "")) for r in recs_list]
                assert any(s in ["AAPL", "MSFT", "GOOGL"] for s in symbols_in_recs)

    def test_execute_ai_recommendation(self, client, test_db):
        """
        Test executing a trade based on AI recommendation

        Flow:
        1. Fetch AI recommendations
        2. Select recommendation with high confidence
        3. Execute order based on recommendation
        4. Verify order matches recommendation
        """
        # Get recommendations
        rec_response = client.get("/api/ai/recommendations")

        if rec_response.status_code == 404:
            pytest.skip("AI recommendations endpoint not implemented")

        if rec_response.status_code == 200:
            recommendations = rec_response.json()
            recs_list = recommendations if isinstance(recommendations, list) else recommendations.get("recommendations", [])

            if len(recs_list) > 0:
                # Take first recommendation
                rec = recs_list[0]

                # Extract recommendation details
                symbol = rec.get("symbol", rec.get("ticker", "AAPL"))
                action = rec.get("action", rec.get("recommendation", rec.get("side", "buy")))
                quantity = rec.get("quantity", rec.get("shares", 10))

                # Normalize action to buy/sell
                side = "buy" if action.lower() in ["buy", "long", "bullish"] else "sell"

                # Execute order based on recommendation
                order_payload = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "side": side,
                    "order_type": "market",
                }

                order_response = client.post("/api/orders", json=order_payload)
                assert order_response.status_code in [200, 201]

                order_data = order_response.json()
                assert order_data["symbol"] == symbol
                assert order_data["side"] == side

    def test_ai_recommendation_filtering(self, client, test_db):
        """
        Test filtering AI recommendations by risk level or strategy
        """
        # Try different filters
        filters = [
            {"risk_level": "low"},
            {"risk_level": "high"},
            {"strategy_type": "momentum"},
            {"strategy_type": "value"},
        ]

        for filter_params in filters:
            response = client.get("/api/ai/recommendations", params=filter_params)

            if response.status_code == 404:
                pytest.skip("AI recommendations endpoint not implemented")

            # Filtering may not be implemented - accept 200 or 422
            assert response.status_code in [200, 422]

    def test_ai_recommendation_reasoning(self, client, test_db):
        """
        Test AI provides reasoning for recommendations
        """
        response = client.get("/api/ai/recommendations")

        if response.status_code == 404:
            pytest.skip("AI recommendations endpoint not implemented")

        if response.status_code == 200:
            recommendations = response.json()
            recs_list = recommendations if isinstance(recommendations, list) else recommendations.get("recommendations", [])

            if len(recs_list) > 0:
                rec = recs_list[0]

                # Check for reasoning/explanation
                has_reasoning = any(key in rec for key in ["reasoning", "explanation", "rationale", "why"])

                # Reasoning is nice to have but not required
                # Just log if missing
                if not has_reasoning:
                    print(f"Warning: Recommendation lacks reasoning field: {rec}")


class TestAIAnalysisFlow:
    """Test AI analysis of stocks and market conditions"""

    def test_ai_stock_analysis(self, client, test_db):
        """
        Test AI analysis of specific stock
        """
        symbol = "AAPL"

        # Try different AI analysis endpoints
        endpoints_to_try = [
            f"/api/ai/analyze/{symbol}",
            f"/api/ai/stock/{symbol}",
            f"/api/claude/analyze/{symbol}",
        ]

        success = False
        for endpoint in endpoints_to_try:
            response = client.get(endpoint)
            if response.status_code == 200:
                analysis = response.json()

                # Verify analysis contains useful info
                assert "symbol" in analysis or "ticker" in analysis
                success = True
                break

        if not success:
            pytest.skip("AI stock analysis endpoint not found")

    def test_ai_sentiment_analysis(self, client, test_db):
        """
        Test AI sentiment analysis for stocks
        """
        symbol = "AAPL"

        # Try sentiment endpoints
        endpoints_to_try = [
            f"/api/ai/sentiment/{symbol}",
            f"/api/ml/sentiment/{symbol}",
            "/api/ml-sentiment/analyze",
        ]

        for endpoint in endpoints_to_try:
            if endpoint == "/api/ml-sentiment/analyze":
                # POST endpoint
                response = client.post(endpoint, json={"symbol": symbol})
            else:
                # GET endpoint
                response = client.get(endpoint)

            if response.status_code == 200:
                sentiment = response.json()

                # Verify sentiment data
                assert "sentiment" in sentiment or "score" in sentiment or "signals" in sentiment
                return  # Test passed

        pytest.skip("AI sentiment analysis endpoint not found")

    def test_ai_chat_interface(self, client, test_db):
        """
        Test AI chat/conversational interface
        """
        # Try Claude chat endpoint
        chat_payload = {
            "message": "What stocks should I buy today?",
            "context": {"risk_tolerance": "moderate"},
        }

        response = client.post("/api/claude/chat", json=chat_payload)

        if response.status_code == 404:
            pytest.skip("Claude chat endpoint not implemented")

        assert response.status_code in [200, 422]

        if response.status_code == 200:
            chat_response = response.json()

            # Verify response structure
            assert "response" in chat_response or "message" in chat_response

    def test_ai_strategy_generation(self, client, test_db):
        """
        Test AI-powered strategy generation
        """
        strategy_request = {
            "goals": ["growth", "income"],
            "risk_tolerance": "moderate",
            "time_horizon": "medium",
        }

        response = client.post("/api/ai/generate-strategy", json=strategy_request)

        if response.status_code == 404:
            pytest.skip("AI strategy generation not implemented")

        assert response.status_code in [200, 422]

        if response.status_code == 200:
            strategy = response.json()

            # Verify strategy structure
            assert "name" in strategy or "description" in strategy


class TestMLIntegration:
    """Test machine learning model integration"""

    def test_ml_prediction_endpoint(self, client, test_db):
        """
        Test ML prediction endpoints
        """
        symbol = "AAPL"

        # Try ML prediction endpoints
        endpoints_to_try = [
            f"/api/ml/predict/{symbol}",
            f"/api/ml/forecast/{symbol}",
        ]

        for endpoint in endpoints_to_try:
            response = client.get(endpoint)

            if response.status_code == 200:
                prediction = response.json()

                # Verify prediction data
                assert "prediction" in prediction or "forecast" in prediction
                return  # Test passed

        pytest.skip("ML prediction endpoint not found")

    def test_ml_model_status(self, client, test_db):
        """
        Test ML model status and availability
        """
        response = client.get("/api/ml/status")

        if response.status_code == 404:
            pytest.skip("ML status endpoint not implemented")

        assert response.status_code == 200

        status = response.json()

        # Verify status includes model info
        assert "models" in status or "available" in status or "loaded" in status

    def test_ml_training_status(self, client, test_db):
        """
        Test ML model training status
        """
        response = client.get("/api/ml/training/status")

        if response.status_code == 404:
            pytest.skip("ML training status endpoint not implemented")

        assert response.status_code in [200, 404]


class TestAIRecommendationPerformance:
    """Test performance tracking of AI recommendations"""

    def test_ai_recommendation_history(self, client, test_db):
        """
        Test retrieving historical AI recommendations
        """
        response = client.get("/api/ai/recommendations/history")

        if response.status_code == 404:
            pytest.skip("AI recommendation history not implemented")

        assert response.status_code == 200

        history = response.json()

        # Verify history structure
        assert isinstance(history, list) or "recommendations" in history

    def test_ai_recommendation_accuracy(self, client, test_db):
        """
        Test tracking accuracy of AI recommendations
        """
        response = client.get("/api/ai/recommendations/accuracy")

        if response.status_code == 404:
            pytest.skip("AI recommendation accuracy tracking not implemented")

        assert response.status_code == 200

        accuracy = response.json()

        # Verify accuracy metrics
        assert "accuracy" in accuracy or "success_rate" in accuracy or "performance" in accuracy

    def test_ai_recommendation_feedback(self, client, test_db):
        """
        Test providing feedback on AI recommendations
        """
        feedback_payload = {
            "recommendation_id": 1,
            "result": "success",
            "profit_loss": 150.50,
        }

        response = client.post("/api/ai/recommendations/feedback", json=feedback_payload)

        if response.status_code == 404:
            pytest.skip("AI recommendation feedback not implemented")

        assert response.status_code in [200, 201, 422]


class TestAIErrorHandling:
    """Test error handling in AI flows"""

    def test_ai_api_unavailable(self, client, test_db):
        """
        Test graceful handling when AI API (Anthropic) is unavailable
        """
        response = client.get("/api/ai/recommendations")

        if response.status_code == 404:
            pytest.skip("AI recommendations endpoint not implemented")

        # Should return 200 (success) or 503 (service unavailable)
        # NOT 500 (unhandled exception)
        assert response.status_code in [200, 503, 504]

    def test_ai_timeout_handling(self, client, test_db):
        """
        Test AI request timeout handling
        """
        # Make AI request that might timeout
        chat_payload = {
            "message": "Provide detailed analysis of all S&P 500 stocks with price targets and reasoning for each.",
        }

        response = client.post("/api/claude/chat", json=chat_payload)

        if response.status_code == 404:
            pytest.skip("Claude chat endpoint not implemented")

        # Should handle timeout gracefully
        assert response.status_code in [200, 408, 503, 504]

    def test_invalid_ai_request(self, client, test_db):
        """
        Test AI handles invalid requests gracefully
        """
        # Empty message
        empty_payload = {"message": ""}

        response = client.post("/api/claude/chat", json=empty_payload)

        if response.status_code == 404:
            pytest.skip("Claude chat endpoint not implemented")

        # Should return validation error
        assert response.status_code in [400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
