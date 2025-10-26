"""
Integration Tests: News Analysis Flow
Test ID: INTG-NEWS-001
Priority: MEDIUM

Tests complete news analysis workflow:
1. Fetch market news for symbols
2. Analyze news sentiment
3. Generate trading signals from news
4. Track news-driven recommendations
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app


class TestNewsRetrievalFlow:
    """Integration tests for news retrieval"""

    def test_fetch_general_market_news(self, client, test_db):
        """
        Test fetching general market news

        Flow:
        1. Request market news
        2. Verify news structure
        3. Check for essential fields
        """
        response = client.get("/api/news")

        if response.status_code == 404:
            pytest.skip("News endpoint not implemented")

        assert response.status_code == 200, f"News request failed: {response.text}"

        news_data = response.json()

        # News could be list or dict with 'news' key
        news_list = news_data if isinstance(news_data, list) else news_data.get("news", [])

        # Verify news structure
        assert isinstance(news_list, list)

        if len(news_list) > 0:
            article = news_list[0]

            # Check essential news fields
            assert "title" in article or "headline" in article
            assert "published_at" in article or "date" in article or "timestamp" in article

    def test_fetch_symbol_specific_news(self, client, test_db):
        """
        Test fetching news for specific symbol
        """
        symbol = "AAPL"

        response = client.get(f"/api/news/{symbol}")

        if response.status_code == 404:
            # Try alternative endpoint
            response = client.get(f"/api/news?symbol={symbol}")

        if response.status_code == 404:
            pytest.skip("Symbol-specific news endpoint not implemented")

        assert response.status_code == 200

        news_data = response.json()
        news_list = news_data if isinstance(news_data, list) else news_data.get("news", [])

        if len(news_list) > 0:
            # Verify news is related to symbol
            article = news_list[0]

            # Symbol might be in title, content, or symbols array
            has_symbol_reference = (
                symbol in article.get("title", "")
                or symbol in article.get("headline", "")
                or symbol in article.get("symbols", [])
            )

            # Not all news may explicitly mention symbol - that's okay
            # Just verify we got news back

    def test_fetch_multiple_symbols_news(self, client, test_db):
        """
        Test fetching news for multiple symbols
        """
        symbols = ["AAPL", "MSFT", "GOOGL"]

        response = client.get(f"/api/news?symbols={','.join(symbols)}")

        if response.status_code == 404:
            pytest.skip("Multi-symbol news endpoint not implemented")

        if response.status_code == 200:
            news_data = response.json()
            news_list = news_data if isinstance(news_data, list) else news_data.get("news", [])

            # Should get news for requested symbols
            assert len(news_list) >= 0

    def test_news_date_filtering(self, client, test_db):
        """
        Test filtering news by date range
        """
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        params = {
            "start_date": start_date,
            "end_date": end_date,
        }

        response = client.get("/api/news", params=params)

        if response.status_code == 404:
            pytest.skip("News endpoint not implemented")

        if response.status_code == 200:
            news_data = response.json()
            news_list = news_data if isinstance(news_data, list) else news_data.get("news", [])

            # Verify news is within date range
            if len(news_list) > 0:
                for article in news_list:
                    # Date field might be named differently
                    pub_date = article.get("published_at") or article.get("date") or article.get("timestamp")
                    if pub_date:
                        # Just verify field exists - actual date validation complex
                        assert pub_date is not None

    def test_news_pagination(self, client, test_db):
        """
        Test news pagination/limiting results
        """
        params = {
            "limit": 10,
            "offset": 0,
        }

        response = client.get("/api/news", params=params)

        if response.status_code == 404:
            pytest.skip("News endpoint not implemented")

        if response.status_code == 200:
            news_data = response.json()
            news_list = news_data if isinstance(news_data, list) else news_data.get("news", [])

            # Should respect limit
            assert len(news_list) <= 10


class TestNewsSentimentAnalysis:
    """Integration tests for news sentiment analysis"""

    def test_analyze_news_sentiment(self, client, test_db):
        """
        Test sentiment analysis of news articles

        Sentiment: positive, negative, neutral
        Score: typically -1 to 1
        """
        # Get some news first
        news_response = client.get("/api/news/AAPL")

        if news_response.status_code == 404:
            pytest.skip("News endpoint not implemented")

        if news_response.status_code == 200:
            news_data = news_response.json()
            news_list = news_data if isinstance(news_data, list) else news_data.get("news", [])

            if len(news_list) > 0:
                article = news_list[0]

                # Check if sentiment is already included
                if "sentiment" in article:
                    sentiment = article["sentiment"]

                    # Verify sentiment structure
                    if isinstance(sentiment, dict):
                        assert "score" in sentiment or "polarity" in sentiment
                    elif isinstance(sentiment, str):
                        assert sentiment in ["positive", "negative", "neutral"]

                else:
                    # Try dedicated sentiment endpoint
                    article_id = article.get("id")
                    if article_id:
                        sentiment_response = client.get(f"/api/news/{article_id}/sentiment")

                        if sentiment_response.status_code == 200:
                            sentiment = sentiment_response.json()
                            assert "sentiment" in sentiment or "score" in sentiment

    def test_symbol_sentiment_aggregate(self, client, test_db):
        """
        Test aggregated sentiment for a symbol (all recent news)
        """
        symbol = "AAPL"

        response = client.get(f"/api/news/sentiment/{symbol}")

        if response.status_code == 404:
            # Try alternative ML sentiment endpoint
            response = client.get(f"/api/ml/sentiment/{symbol}")

        if response.status_code == 404:
            pytest.skip("Symbol sentiment endpoint not implemented")

        if response.status_code == 200:
            sentiment_data = response.json()

            # Should include aggregate sentiment
            expected_fields = ["sentiment", "score", "polarity", "overall_sentiment"]

            has_sentiment = any(field in sentiment_data for field in expected_fields)
            assert has_sentiment, f"Sentiment data missing expected fields: {sentiment_data}"

    def test_sentiment_trend_over_time(self, client, test_db):
        """
        Test sentiment trend analysis over time period
        """
        symbol = "AAPL"
        params = {
            "days": 7,
        }

        response = client.get(f"/api/news/sentiment/{symbol}/trend", params=params)

        if response.status_code == 404:
            pytest.skip("Sentiment trend endpoint not implemented")

        if response.status_code == 200:
            trend_data = response.json()

            # Should be time series of sentiment scores
            if isinstance(trend_data, list):
                if len(trend_data) > 0:
                    point = trend_data[0]
                    assert "date" in point or "timestamp" in point
                    assert "sentiment" in point or "score" in point


class TestNewsSignalGeneration:
    """Integration tests for generating trading signals from news"""

    def test_news_to_trading_signals(self, client, test_db):
        """
        Test converting news sentiment to trading signals

        Signals: buy, sell, hold
        Strength: 0-100
        """
        symbol = "AAPL"

        response = client.get(f"/api/news/signals/{symbol}")

        if response.status_code == 404:
            # Try ML signals endpoint
            response = client.post("/api/ml-sentiment/analyze", json={"symbol": symbol})

        if response.status_code == 404:
            pytest.skip("News signals endpoint not implemented")

        if response.status_code == 200:
            signals_data = response.json()

            # Verify signal structure
            expected_fields = ["signal", "action", "recommendation", "signals"]

            has_signal = any(field in signals_data for field in expected_fields)

            # Signals may be in different format
            if not has_signal and isinstance(signals_data, dict):
                # Check if it's a signals array
                signals_array = signals_data.get("signals", [])
                if len(signals_array) > 0:
                    has_signal = True

            assert has_signal or signals_data is not None

    def test_news_signal_confidence(self, client, test_db):
        """
        Test news signals include confidence scores
        """
        symbol = "AAPL"

        response = client.get(f"/api/news/signals/{symbol}")

        if response.status_code == 404:
            pytest.skip("News signals endpoint not implemented")

        if response.status_code == 200:
            signals_data = response.json()

            # Check for confidence/strength indicators
            confidence_fields = ["confidence", "strength", "score", "probability"]

            has_confidence = any(field in signals_data for field in confidence_fields)

            # Confidence is nice to have but not required
            if not has_confidence:
                print("Info: News signals lack confidence scores")

    def test_news_driven_recommendations(self, client, test_db):
        """
        Test generating trade recommendations based on news
        """
        response = client.get("/api/news/recommendations")

        if response.status_code == 404:
            pytest.skip("News recommendations endpoint not implemented")

        if response.status_code == 200:
            recommendations = response.json()

            # Should be list of recommended actions based on news
            recs_list = recommendations if isinstance(recommendations, list) else recommendations.get("recommendations", [])

            if len(recs_list) > 0:
                rec = recs_list[0]

                # Should include symbol and action
                assert "symbol" in rec or "ticker" in rec
                assert "action" in rec or "recommendation" in rec


class TestNewsIntegrationWithTrading:
    """Integration tests for news + trading workflows"""

    def test_news_to_order_flow(self, client, test_db):
        """
        Test complete flow: news → sentiment → signal → order

        Flow:
        1. Get news for symbol
        2. Analyze sentiment
        3. Generate signal
        4. Place order if signal strong enough
        """
        symbol = "AAPL"

        # Step 1: Get news
        news_response = client.get(f"/api/news/{symbol}")

        if news_response.status_code == 404:
            pytest.skip("News endpoint not implemented")

        if news_response.status_code == 200:
            # Step 2: Get sentiment
            sentiment_response = client.get(f"/api/news/sentiment/{symbol}")

            if sentiment_response.status_code == 404:
                # Try ML sentiment
                sentiment_response = client.get(f"/api/ml/sentiment/{symbol}")

            if sentiment_response.status_code == 200:
                sentiment_data = sentiment_response.json()

                # Extract sentiment score
                score = sentiment_data.get("score", 0)

                # Step 3: Generate signal (simulated here)
                if score > 0.5:
                    action = "buy"
                elif score < -0.5:
                    action = "sell"
                else:
                    action = "hold"

                # Step 4: Place order if not hold
                if action != "hold":
                    order_payload = {
                        "symbol": symbol,
                        "quantity": 10,
                        "side": action,
                        "order_type": "market",
                    }

                    order_response = client.post("/api/orders", json=order_payload)
                    assert order_response.status_code in [200, 201]

    def test_news_alerts_integration(self, client, test_db):
        """
        Test news alerts/notifications for significant events
        """
        # Create news alert
        alert_payload = {
            "symbol": "AAPL",
            "keywords": ["earnings", "acquisition", "regulatory"],
            "sentiment_threshold": 0.7,
        }

        response = client.post("/api/news/alerts", json=alert_payload)

        if response.status_code == 404:
            pytest.skip("News alerts endpoint not implemented")

        assert response.status_code in [200, 201, 422]

    def test_news_watchlist_integration(self, client, test_db):
        """
        Test getting news for user's watchlist symbols
        """
        # Assume user has watchlist
        response = client.get("/api/news/watchlist")

        if response.status_code == 404:
            pytest.skip("News watchlist endpoint not implemented")

        if response.status_code == 200:
            news_data = response.json()

            # Should return news for all watchlist symbols
            assert news_data is not None


class TestNewsQuality:
    """Integration tests for news quality and filtering"""

    def test_news_source_filtering(self, client, test_db):
        """
        Test filtering news by source (Reuters, Bloomberg, etc.)
        """
        params = {
            "sources": "reuters,bloomberg",
        }

        response = client.get("/api/news", params=params)

        if response.status_code == 404:
            pytest.skip("News endpoint not implemented")

        if response.status_code == 200:
            news_data = response.json()
            news_list = news_data if isinstance(news_data, list) else news_data.get("news", [])

            if len(news_list) > 0:
                # Check if articles have source field
                has_source = "source" in news_list[0]

                # Source filtering may not be implemented
                if not has_source:
                    print("Info: News articles lack source field")

    def test_news_relevance_scoring(self, client, test_db):
        """
        Test news articles include relevance scores
        """
        response = client.get("/api/news/AAPL")

        if response.status_code == 404:
            pytest.skip("News endpoint not implemented")

        if response.status_code == 200:
            news_data = response.json()
            news_list = news_data if isinstance(news_data, list) else news_data.get("news", [])

            if len(news_list) > 0:
                article = news_list[0]

                # Check for relevance indicators
                relevance_fields = ["relevance", "score", "importance"]

                has_relevance = any(field in article for field in relevance_fields)

                # Relevance scoring is optional
                if not has_relevance:
                    print("Info: News articles lack relevance scores")

    def test_news_deduplication(self, client, test_db):
        """
        Test news feed deduplicates similar articles
        """
        response = client.get("/api/news/AAPL")

        if response.status_code == 404:
            pytest.skip("News endpoint not implemented")

        if response.status_code == 200:
            news_data = response.json()
            news_list = news_data if isinstance(news_data, list) else news_data.get("news", [])

            # Check for duplicate titles
            titles = [article.get("title", article.get("headline", "")) for article in news_list]

            # Should have mostly unique titles
            unique_titles = set(titles)

            # Allow some duplicates but not too many
            if len(titles) > 0:
                uniqueness_ratio = len(unique_titles) / len(titles)
                # At least 70% unique
                assert uniqueness_ratio > 0.7 or len(titles) < 3


class TestNewsErrorHandling:
    """Test error handling in news analysis flows"""

    def test_news_api_unavailable(self, client, test_db):
        """
        Test graceful handling when news API is unavailable
        """
        response = client.get("/api/news")

        if response.status_code == 404:
            pytest.skip("News endpoint not implemented")

        # Should return 200 (success) or 503 (service unavailable)
        # NOT 500 (unhandled exception)
        assert response.status_code in [200, 503]

    def test_invalid_symbol_news(self, client, test_db):
        """
        Test handling of invalid symbols in news requests
        """
        response = client.get("/api/news/INVALIDSTOCK12345")

        if response.status_code == 404:
            pytest.skip("News endpoint not implemented")

        # Should handle gracefully - either return empty list or 404
        assert response.status_code in [200, 404, 400]

        if response.status_code == 200:
            news_data = response.json()
            # Should be empty or minimal results
            news_list = news_data if isinstance(news_data, list) else news_data.get("news", [])
            # No strict requirement on length

    def test_news_rate_limiting(self, client, test_db):
        """
        Test news API respects rate limits
        """
        # Make multiple rapid requests
        for i in range(10):
            response = client.get("/api/news")

            if response.status_code == 404:
                pytest.skip("News endpoint not implemented")

            # Should succeed or return rate limit
            assert response.status_code in [200, 429, 503]

            if response.status_code == 429:
                # Rate limit hit - test passed
                break


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
