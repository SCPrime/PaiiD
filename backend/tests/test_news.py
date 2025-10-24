"""Tests for news API endpoints."""

from unittest.mock import MagicMock


def test_news_requires_auth(client):
    response = client.get("/api/news/market")
    assert response.status_code == 403


def test_news_returns_articles(monkeypatch, client, auth_headers):
    from app.routers import news as news_router

    mock_aggregator = MagicMock()
    mock_aggregator.get_market_news.return_value = [
        {
            "title": "Sample",
            "url": "https://example.com",
            "source": "Example",
            "published_at": "2024-01-01T00:00:00Z",
        }
    ]
    monkeypatch.setattr(news_router, "news_aggregator", mock_aggregator)

    response = client.get("/api/news/market", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert data["articles"][0]["source"] == "Example"


def test_news_handles_provider_errors(monkeypatch, client, auth_headers):
    from app.routers import news as news_router

    mock_aggregator = MagicMock()
    mock_aggregator.get_market_news.side_effect = RuntimeError("provider down")
    monkeypatch.setattr(news_router, "news_aggregator", mock_aggregator)

    response = client.get("/api/news/market", headers=auth_headers)
    assert response.status_code == 500
    assert "provider down" in response.json()["detail"]
