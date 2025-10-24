import pytest

from app.recommendations.models import RecommendationHistory


@pytest.mark.usefixtures("client")
def test_create_recommendation_history_entry(client, auth_headers, test_db):
    payload = {
        "symbol": "AAPL",
        "recommendation_type": "buy",
        "confidence_score": 82.5,
        "risk_level": "medium",
        "volatility_score": 1.2,
        "volatility_label": "medium",
        "momentum_trend": "bullish",
        "tags": ["swing", "tech"],
    }

    response = client.post(
        "/api/recommendations/history",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["recommendation_type"] == "buy"
    assert data["tags"] == ["swing", "tech"]

    record = test_db.query(RecommendationHistory).get(data["id"])
    assert record is not None
    assert record.symbol == "AAPL"
    assert record.risk_level == "medium"


def _create_sample_recommendation(client, auth_headers, symbol, **overrides):
    base_payload = {
        "symbol": symbol,
        "recommendation_type": "buy",
        "confidence_score": 70,
        "risk_level": "medium",
        "volatility_score": 1.0,
        "momentum_score": 0.5,
    }
    base_payload.update(overrides)
    response = client.post(
        "/api/recommendations/history",
        json=base_payload,
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.usefixtures("client")
def test_filter_recommendations_by_confidence_and_risk(client, auth_headers):
    _create_sample_recommendation(
        client,
        auth_headers,
        "AAPL",
        confidence_score=92,
        risk_level="low",
    )
    _create_sample_recommendation(
        client,
        auth_headers,
        "TSLA",
        confidence_score=65,
        risk_level="high",
    )

    response = client.get(
        "/api/recommendations/history",
        params={
            "min_confidence": 80,
            "risk_levels": ["low"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["symbol"] == "AAPL"


@pytest.mark.usefixtures("client")
def test_sort_recommendations_by_volatility(client, auth_headers):
    _create_sample_recommendation(
        client,
        auth_headers,
        "MSFT",
        volatility_score=0.8,
        momentum_score=0.3,
    )
    _create_sample_recommendation(
        client,
        auth_headers,
        "AMZN",
        volatility_score=2.5,
        momentum_score=1.1,
    )

    response = client.get(
        "/api/recommendations/history",
        params={
            "sort_by": "volatility",
            "sort_direction": "asc",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    symbols = [item["symbol"] for item in payload["items"]]
    assert symbols == ["MSFT", "AMZN"]
