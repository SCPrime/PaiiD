from datetime import timedelta

from datetime import timedelta

from app.models.database import User
from app.routers.ai import (
    DEFAULT_RECOMMENDATION_TTL_DAYS,
    Recommendation,
    TradeData,
    _persist_recommendation_batch,
)
from tests.conftest import TEST_PASSWORD_HASH


def _create_user(db, email: str) -> User:
    user = User(email=email, password_hash=TEST_PASSWORD_HASH, preferences={})
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_persist_recommendation_batch_handles_nullable_fields(test_db):
    user = _create_user(test_db, "user1@example.com")

    recommendations = [
        Recommendation(
            symbol="AAPL",
            action="BUY",
            confidence=82.5,
            score=7.2,
            reason="Momentum breakout",
            targetPrice=190.0,
            currentPrice=180.0,
            risk="Medium",
            entryPrice=179.0,
            stopLoss=170.0,
            takeProfit=198.0,
            tradeData=TradeData(
                symbol="AAPL",
                side="buy",
                quantity=5,
                orderType="limit",
                entryPrice=179.0,
                stopLoss=170.0,
                takeProfit=198.0,
            ),
            portfolioFit="✅ Adds diversification",
            momentum={"trend_alignment": "Bullish"},
            volatility={"atr": 2.1},
            indicators={"rsi": 61},
            explanation="Strong bullish momentum",
        ),
        Recommendation(
            symbol="MSFT",
            action="HOLD",
            confidence=55.0,
            score=5.8,
            reason="Neutral momentum",
            targetPrice=320.0,
            currentPrice=315.0,
            risk="Low",
        ),
    ]

    persisted = _persist_recommendation_batch(test_db, user.id, recommendations)

    assert len(persisted) == 2
    for record, source in zip(persisted, recommendations):
        assert record.user_id == user.id
        assert record.symbol == source.symbol
        assert record.recommendation_type == source.action.lower()
        assert record.status == "pending"
        assert record.analysis_data is not None
        assert record.analysis_data.get("momentum", {}) == (source.momentum or {})
        assert record.analysis_data.get("tradeData") is None or isinstance(
            record.analysis_data.get("tradeData"), dict
        )
        assert record.expires_at is not None
        assert record.created_at is not None
        ttl_delta = record.expires_at - record.created_at
        assert abs(ttl_delta - timedelta(days=DEFAULT_RECOMMENDATION_TTL_DAYS)) < timedelta(
            seconds=5
        )


def test_history_endpoint_scoped_to_request_user(client, test_db, auth_headers):
    user_one = _create_user(test_db, "user-one@example.com")
    user_two = _create_user(test_db, "user-two@example.com")

    _persist_recommendation_batch(
        test_db,
        user_one.id,
        [
            Recommendation(
                symbol="AAPL",
                action="BUY",
                confidence=80.0,
                score=7.5,
                reason="Great earnings",
                targetPrice=200.0,
                currentPrice=180.0,
                risk="Medium",
            )
        ],
    )

    _persist_recommendation_batch(
        test_db,
        user_two.id,
        [
            Recommendation(
                symbol="TSLA",
                action="SELL",
                confidence=65.0,
                score=6.1,
                reason="Overextended",
                targetPrice=210.0,
                currentPrice=230.0,
                risk="High",
            )
        ],
    )

    headers_user_two = {**auth_headers, "X-User-Id": str(user_two.id)}
    response = client.get("/api/ai/recommendations/history", headers=headers_user_two)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    record = payload[0]
    assert record["symbol"] == "TSLA"
    assert record["recommendation_type"] == "sell"
    assert isinstance(record["analysis_data"], dict)
    assert record["executed_at"] is None
    assert record["created_at"].endswith("Z")
    assert record["expires_at"].endswith("Z")

    # Ensure user one's data is not leaked
    symbols = {item["symbol"] for item in payload}
    assert "AAPL" not in symbols
