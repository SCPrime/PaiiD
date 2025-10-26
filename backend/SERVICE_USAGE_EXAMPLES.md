# Service Usage Examples - Wave 4

Quick reference guide for using the new service layer in routers.

---

## 1. Market Analysis Service

### Basic Usage - Get Technical Indicators

```python
from fastapi import APIRouter
from app.services import get_market_analysis_service

router = APIRouter()

@router.get("/indicators/{symbol}")
async def get_indicators(symbol: str):
    """Get technical indicators for a symbol"""
    service = get_market_analysis_service()

    indicators = await service.calculate_technical_indicators(
        symbol=symbol,
        indicators=["rsi", "macd", "bb", "volume"],
        lookback_days=90
    )

    return {
        "symbol": symbol,
        "rsi": indicators.get("rsi"),
        "macd": indicators.get("macd"),
        "bb_upper": indicators.get("bb_upper"),
        "bb_lower": indicators.get("bb_lower"),
        "volume_ratio": indicators.get("volume_ratio"),
    }
```

### Market Regime Detection

```python
@router.get("/market-regime/{symbol}")
async def get_market_regime(symbol: str):
    """Detect current market regime"""
    service = get_market_analysis_service()

    regime = await service.detect_market_regime(
        symbol=symbol,
        lookback_days=90
    )

    return {
        "symbol": symbol,
        "regime": regime["regime"],  # "trending_bullish", "trending_bearish", etc.
        "confidence": regime["confidence"],
        "features": regime["features"]
    }
```

### Trend Analysis

```python
@router.get("/trend/{symbol}")
async def analyze_trend(
    symbol: str,
    timeframe: str = "daily"
):
    """Analyze price trend"""
    service = get_market_analysis_service()

    trend = await service.analyze_trend(
        symbol=symbol,
        timeframe=timeframe,
        lookback_days=90
    )

    return {
        "symbol": symbol,
        "direction": trend["direction"],  # "bullish", "bearish", "neutral"
        "strength": trend["strength"],
        "support": trend["support"],
        "resistance": trend["resistance"],
        "confidence": trend["confidence"]
    }
```

---

## 2. Portfolio Analytics Service

### Portfolio Metrics

```python
from app.services import get_portfolio_analytics_service

@router.get("/portfolio/metrics")
async def get_portfolio_metrics():
    """Get comprehensive portfolio metrics"""
    service = get_portfolio_analytics_service()

    metrics = await service.calculate_portfolio_metrics()

    return {
        "total_value": metrics["total_value"],
        "total_pl": metrics["total_pl"],
        "total_pl_percent": metrics["total_pl_percent"],
        "num_positions": metrics["num_positions"],
        "diversification_score": metrics["diversification_score"],
        "sector_allocation": metrics["sector_allocation"]
    }
```

### Diversification Analysis

```python
@router.get("/portfolio/diversification")
async def analyze_diversification():
    """Analyze portfolio diversification"""
    service = get_portfolio_analytics_service()

    # Get positions from Tradier
    from app.services.tradier_client import get_tradier_client
    tradier = get_tradier_client()
    positions = tradier.get_positions()

    # Analyze diversification
    analysis = await service.analyze_diversification(positions)

    return {
        "hhi": analysis["hhi"],
        "diversification_score": analysis["diversification_score"],
        "concentration_level": analysis["concentration_level"],
        "largest_position_pct": analysis["largest_position_pct"],
        "top_3_positions_pct": analysis["top_3_positions_pct"]
    }
```

### Sharpe Ratio & Risk Metrics

```python
@router.get("/portfolio/risk-metrics")
async def get_risk_metrics():
    """Calculate risk-adjusted performance metrics"""
    service = get_portfolio_analytics_service()

    # Get equity history (example - would come from equity tracker)
    from app.services.equity_tracker import get_equity_tracker
    tracker = get_equity_tracker()
    history = tracker.get_history(lookback_days=365)

    # Calculate daily returns
    daily_returns = []
    for i in range(1, len(history)):
        prev = history[i-1]["equity"]
        curr = history[i]["equity"]
        daily_return = (curr - prev) / prev
        daily_returns.append(daily_return)

    # Calculate Sharpe ratio
    sharpe = service.calculate_sharpe_ratio(daily_returns, risk_free_rate=0.02)

    # Calculate max drawdown
    equity_curve = [h["equity"] for h in history]
    drawdown = service.calculate_max_drawdown(equity_curve)

    return {
        "sharpe_ratio": sharpe,
        "max_drawdown": drawdown["max_drawdown"],
        "max_drawdown_pct": drawdown["max_drawdown_pct"],
        "peak_value": drawdown["peak_value"],
        "trough_value": drawdown["trough_value"]
    }
```

---

## 3. Notification Service

### Order Fill Notification

```python
from app.services import get_notification_service

@router.post("/orders")
async def create_order(order_data: dict, user_id: str):
    """Create order and send notification"""
    # Execute order (simplified)
    order_result = {
        "symbol": order_data["symbol"],
        "qty": order_data["qty"],
        "price": 180.50,
        "side": order_data["side"]
    }

    # Send notification
    notification_service = get_notification_service()
    await notification_service.send_order_fill_notification(
        user_id=user_id,
        order=order_result
    )

    return {"status": "success", "order": order_result}
```

### Price Alert

```python
@router.post("/alerts/price")
async def create_price_alert(
    user_id: str,
    symbol: str,
    target_price: float,
    condition: str
):
    """Create price alert and notify when triggered"""
    # Monitor price (would be background task)
    current_price = 245.30  # Get from market data

    if (condition == "above" and current_price >= target_price) or \
       (condition == "below" and current_price <= target_price):

        notification_service = get_notification_service()
        await notification_service.send_price_alert(
            user_id=user_id,
            symbol=symbol,
            current_price=current_price,
            target_price=target_price,
            condition=condition
        )

        return {"status": "triggered", "notification_sent": True}

    return {"status": "monitoring"}
```

### Portfolio Alert

```python
@router.get("/monitor/portfolio")
async def monitor_portfolio(user_id: str):
    """Monitor portfolio and send alerts if thresholds breached"""
    # Get portfolio metrics
    portfolio_service = get_portfolio_analytics_service()
    metrics = await portfolio_service.calculate_portfolio_metrics()

    # Check for risk conditions
    notification_service = get_notification_service()

    if metrics["total_pl_percent"] < -5.0:  # 5% loss threshold
        await notification_service.send_portfolio_alert(
            user_id=user_id,
            alert_type="Loss Threshold",
            message=f"Portfolio down {metrics['total_pl_percent']:.1f}%",
            data={"total_pl": metrics["total_pl"], "total_pl_percent": metrics["total_pl_percent"]}
        )

    if metrics["diversification_score"] < 40:  # Poor diversification
        await notification_service.send_portfolio_alert(
            user_id=user_id,
            alert_type="Concentration Risk",
            message=f"Diversification score low: {metrics['diversification_score']:.1f}/100",
            data={"diversification_score": metrics["diversification_score"]}
        )

    return {"status": "monitored", "metrics": metrics}
```

### Get User Notifications

```python
@router.get("/notifications")
async def get_notifications(user_id: str, unread_only: bool = False):
    """Get user's notifications"""
    notification_service = get_notification_service()

    notifications = await notification_service.get_user_notifications(
        user_id=user_id,
        unread_only=unread_only,
        limit=50
    )

    return {
        "notifications": [n.model_dump() for n in notifications],
        "count": len(notifications)
    }
```

---

## 4. Cache Service

### Basic Caching

```python
from app.services import get_cache_service

@router.get("/expensive-calculation/{symbol}")
async def expensive_calculation(symbol: str):
    """Cache expensive calculations"""
    cache = get_cache_service()
    cache_key = f"calculation:{symbol}"

    # Try to get from cache
    result = await cache.get(cache_key)

    if result is None:
        # Cache miss - perform calculation
        result = perform_expensive_calculation(symbol)

        # Store in cache for 10 minutes
        await cache.set(cache_key, result, ttl=600)

    return result
```

### Get-or-Set Pattern (Recommended)

```python
@router.get("/data/{symbol}")
async def get_data(symbol: str):
    """Use get-or-set pattern for cleaner code"""
    cache = get_cache_service()

    data = await cache.get_or_set(
        key=f"data:{symbol}",
        factory=lambda: fetch_data_from_api(symbol),
        ttl=300  # 5 minutes
    )

    return data
```

### Cache Invalidation

```python
@router.post("/refresh-market-data")
async def refresh_market_data():
    """Invalidate all market data caches"""
    cache = get_cache_service()

    # Invalidate all market quote caches
    count = await cache.invalidate("market:quotes:*")

    return {"invalidated": count, "status": "success"}
```

### Cache Statistics

```python
@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache performance statistics"""
    cache = get_cache_service()

    stats = cache.get_stats()

    return {
        "hit_rate": stats["hit_rate"],
        "total_requests": stats["total_requests"],
        "hits": stats["hits"],
        "misses": stats["misses"],
        "backend": stats["backend"],  # "redis" or "memory"
        "uptime_seconds": stats["uptime_seconds"]
    }
```

### Cache Warming

```python
@router.post("/cache/warm")
async def warm_cache():
    """Warm cache with frequently accessed data"""
    cache = get_cache_service()

    keys_to_warm = {
        "market:spy:quote": (lambda: get_spy_quote(), 60),
        "market:qqq:quote": (lambda: get_qqq_quote(), 60),
        "market:dia:quote": (lambda: get_dia_quote(), 60),
    }

    count = await cache.warm_cache(keys_to_warm)

    return {"warmed": count, "total": len(keys_to_warm)}
```

---

## 5. Combined Service Usage

### AI-Powered Trade Recommendation

```python
@router.get("/ai/recommend/{symbol}")
async def get_ai_recommendation(symbol: str):
    """
    Generate AI-powered trade recommendation using multiple services
    """
    # Get services
    market_service = get_market_analysis_service()
    cache_service = get_cache_service()

    # Check cache first
    cache_key = f"ai:recommendation:{symbol}"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached

    # Get market regime
    regime = await market_service.detect_market_regime(symbol, lookback_days=90)

    # Get technical indicators
    indicators = await market_service.calculate_technical_indicators(
        symbol=symbol,
        indicators=["rsi", "macd", "bb", "volume"],
        lookback_days=90
    )

    # Get trend analysis
    trend = await market_service.analyze_trend(symbol, timeframe="daily", lookback_days=90)

    # Generate recommendation based on all signals
    recommendation = {
        "symbol": symbol,
        "regime": regime["regime"],
        "regime_confidence": regime["confidence"],
        "trend": trend["direction"],
        "trend_strength": trend["strength"],
        "rsi": indicators.get("rsi"),
        "action": None,  # Will be determined by logic
        "confidence": 0.0,
        "reasons": []
    }

    # Decision logic
    if regime["regime"] == "trending_bullish" and trend["direction"] == "bullish":
        if indicators.get("rsi", 50) < 70:  # Not overbought
            recommendation["action"] = "BUY"
            recommendation["confidence"] = min(regime["confidence"] + trend["strength"], 0.95)
            recommendation["reasons"].append("Strong bullish trend with regime confirmation")
        else:
            recommendation["action"] = "HOLD"
            recommendation["confidence"] = 0.6
            recommendation["reasons"].append("Bullish trend but RSI overbought")

    elif regime["regime"] == "trending_bearish" and trend["direction"] == "bearish":
        recommendation["action"] = "SELL"
        recommendation["confidence"] = min(regime["confidence"] + trend["strength"], 0.95)
        recommendation["reasons"].append("Strong bearish trend with regime confirmation")

    else:
        recommendation["action"] = "HOLD"
        recommendation["confidence"] = 0.5
        recommendation["reasons"].append("Mixed signals - waiting for clearer trend")

    # Cache recommendation for 10 minutes
    await cache_service.set(cache_key, recommendation, ttl=600)

    return recommendation
```

### Portfolio Health Check

```python
@router.get("/portfolio/health-check")
async def portfolio_health_check(user_id: str):
    """
    Comprehensive portfolio health check using multiple services
    """
    # Get services
    portfolio_service = get_portfolio_analytics_service()
    notification_service = get_notification_service()
    cache_service = get_cache_service()

    # Check cache
    cache_key = f"health:{user_id}"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached

    # Get portfolio metrics
    metrics = await portfolio_service.calculate_portfolio_metrics()

    # Analyze health
    health_report = {
        "overall_health": "healthy",  # healthy, warning, critical
        "issues": [],
        "recommendations": []
    }

    # Check 1: Portfolio loss threshold
    if metrics["total_pl_percent"] < -10:
        health_report["overall_health"] = "critical"
        health_report["issues"].append(f"Portfolio down {metrics['total_pl_percent']:.1f}%")
        health_report["recommendations"].append("Consider risk management strategies")

        # Send notification
        await notification_service.send_portfolio_alert(
            user_id=user_id,
            alert_type="Critical Loss",
            message=f"Portfolio has lost {abs(metrics['total_pl_percent']):.1f}%",
            data=metrics
        )

    elif metrics["total_pl_percent"] < -5:
        health_report["overall_health"] = "warning"
        health_report["issues"].append(f"Portfolio down {metrics['total_pl_percent']:.1f}%")

    # Check 2: Diversification
    if metrics["diversification_score"] < 40:
        if health_report["overall_health"] == "healthy":
            health_report["overall_health"] = "warning"
        health_report["issues"].append("Poor diversification")
        health_report["recommendations"].append("Add positions in different sectors")

    # Check 3: Concentration risk
    if metrics["num_positions"] < 5:
        health_report["issues"].append("Low number of positions")
        health_report["recommendations"].append("Consider diversifying with more positions")

    # Add metrics to report
    health_report["metrics"] = metrics

    # Cache for 5 minutes
    await cache_service.set(cache_key, health_report, ttl=300)

    return health_report
```

---

## Service Dependency Injection Patterns

### Pattern 1: Direct Import (Recommended)

```python
from app.services import get_market_analysis_service

@router.get("/endpoint")
async def endpoint():
    service = get_market_analysis_service()
    result = await service.some_method()
    return result
```

### Pattern 2: FastAPI Dependency Injection

```python
from fastapi import Depends
from app.services import get_market_analysis_service

def get_service():
    return get_market_analysis_service()

@router.get("/endpoint")
async def endpoint(service = Depends(get_service)):
    result = await service.some_method()
    return result
```

### Pattern 3: Testing with Mocks

```python
import pytest
from unittest.mock import Mock
from app.services.market_analysis_service import MarketAnalysisService

@pytest.fixture
def mock_market_service():
    mock_tradier = Mock()
    mock_cache = Mock()
    return MarketAnalysisService(
        tradier_client=mock_tradier,
        cache_service=mock_cache
    )

def test_detect_regime(mock_market_service):
    # Mock the tradier client response
    mock_market_service.tradier.get_historical_quotes.return_value = [
        {"close": 100, "high": 101, "low": 99, "volume": 1000000}
        # ... more bars
    ]

    regime = await mock_market_service.detect_market_regime("SPY", 90)

    assert regime["regime"] in ["trending_bullish", "trending_bearish", "ranging"]
```

---

## Performance Tips

1. **Always use caching for expensive operations**
   ```python
   # Good
   data = await cache.get_or_set("key", lambda: expensive_op(), ttl=300)

   # Bad
   data = expensive_op()  # No caching
   ```

2. **Use appropriate TTLs**
   - Real-time data: 15-30 seconds
   - Market data: 1-5 minutes
   - Analytics: 5-10 minutes
   - Historical data: 30-60 minutes

3. **Invalidate caches on data changes**
   ```python
   # After order execution
   await cache.invalidate(f"portfolio:{user_id}:*")
   ```

4. **Warm critical caches on startup**
   ```python
   @app.on_event("startup")
   async def startup():
       cache = get_cache_service()
       await cache.warm_cache({
           "market:spy": (get_spy_data, 60),
           "market:qqq": (get_qqq_data, 60),
       })
   ```

---

## Error Handling Best Practices

```python
@router.get("/endpoint/{symbol}")
async def endpoint(symbol: str):
    try:
        service = get_market_analysis_service()
        result = await service.detect_market_regime(symbol)
        return result

    except ValueError as e:
        # Invalid input (400)
        raise HTTPException(status_code=400, detail=str(e))

    except TimeoutError as e:
        # Service timeout (504)
        raise HTTPException(status_code=504, detail="Service timeout")

    except Exception as e:
        # Unknown error (500)
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

@router.get("/endpoint/{symbol}")
async def endpoint(symbol: str):
    logger.info(f"Endpoint called for symbol: {symbol}")

    try:
        service = get_market_analysis_service()
        result = await service.detect_market_regime(symbol)

        logger.info(f"Regime detected for {symbol}: {result['regime']}")
        return result

    except Exception as e:
        logger.error(f"Failed to detect regime for {symbol}: {e}", exc_info=True)
        raise
```

---

This guide covers the most common usage patterns for all Wave 4 services. Refer to the main documentation (`WAVE4_SERVICE_EXTRACTION_COMPLETE.md`) for more details.
