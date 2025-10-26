# PaiiD Backend API Reference

**Base URL (Production):** `https://paiid-backend.onrender.com`
**Base URL (Local Development):** `http://localhost:8001`
**Version:** 1.0.0
**Authentication:** Bearer token (JWT) unless otherwise noted

## Table of Contents

1. [Authentication](#authentication)
2. [Health Check](#health-check)
3. [Portfolio & Positions](#portfolio--positions)
4. [Orders & Trading](#orders--trading)
5. [Market Data](#market-data)
6. [AI Recommendations](#ai-recommendations)
7. [Claude AI Chat](#claude-ai-chat)
8. [Strategies](#strategies)
9. [Analytics](#analytics)
10. [Backtesting](#backtesting)
11. [News](#news)
12. [Options](#options)
13. [Machine Learning](#machine-learning)
14. [ML Sentiment](#ml-sentiment)
15. [Screening](#screening)
16. [Streaming](#streaming)
17. [Scheduler](#scheduler)
18. [Settings](#settings)
19. [Monitoring](#monitoring)
20. [Telemetry](#telemetry)
21. [Users](#users)
22. [Proposals](#proposals)

---

## Authentication

All endpoints (except health checks and some public endpoints) require authentication via JWT Bearer token.

### Authentication Headers

```http
Authorization: Bearer <JWT_ACCESS_TOKEN>
X-CSRF-Token: <CSRF_TOKEN>  (required for state-changing operations: POST/PUT/DELETE/PATCH)
```

### POST /api/auth/register

Register a new user account.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "full_name": "John Doe",
  "invite_code": "PAIID_BETA_2025"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one digit
- At least one uppercase letter

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `400`: Email already registered, invalid invite code, or password validation failed
- `500`: Server error

---

### POST /api/auth/login

Authenticate user and receive JWT tokens.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token Expiry:**
- **Access Token:** 15 minutes
- **Refresh Token:** 7 days

**Errors:**
- `401`: Incorrect email or password
- `403`: Account is disabled
- `500`: Server error

---

### POST /api/auth/refresh

Exchange refresh token for new access + refresh token pair.

**Authentication:** Not required (but requires valid refresh token)

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Process:**
1. Validates refresh token
2. Checks session exists in database
3. Invalidates old session
4. Generates new token pair
5. Stores new session

**Errors:**
- `401`: Invalid or expired refresh token, session expired, user not found
- `403`: Account is disabled
- `500`: Server error

---

### POST /api/auth/logout

Logout user and invalidate all sessions.

**Authentication:** Required

**Request Body:** None

**Response (204 No Content)**

**Behavior:**
- Deletes all active sessions for the current user
- Invalidates all access and refresh tokens

---

### GET /api/auth/me

Get current authenticated user's profile.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "beta_tester",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z",
  "last_login_at": "2025-01-20T14:25:00Z",
  "preferences": {
    "risk_tolerance": 50
  }
}
```

---

### GET /api/auth/csrf-token

Generate a CSRF token for the authenticated user.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "csrf_token": "abc123...",
  "expires_in": 3600,
  "message": "Include this token in X-CSRF-Token header for state-changing requests"
}
```

**Usage:**
1. Call this endpoint after login to get a CSRF token
2. Include the token in `X-CSRF-Token` header for POST/PUT/DELETE/PATCH requests
3. Token expires after 1 hour - call this endpoint again to refresh

---

## Health Check

### GET /api/health

Basic health check endpoint (no auth required).

**Authentication:** Not required

**Response (200 OK):**
```json
{
  "status": "ok",
  "time": "2025-10-26T14:30:00.000Z"
}
```

---

### GET /api/health/detailed

Detailed health check with system metrics.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-26T14:30:00.000Z",
  "version": "1.0.0",
  "dependencies": {
    "database": "healthy",
    "tradier_api": "healthy",
    "alpaca_api": "healthy",
    "redis": "healthy"
  },
  "metrics": {
    "cache_hit_rate": 85.2,
    "avg_response_time_ms": 120
  }
}
```

---

### GET /api/health/readiness

Kubernetes-style readiness probe.

**Authentication:** Not required

**Response (200 OK):**
```json
{
  "ready": true
}
```

**Errors:**
- `503`: System degraded or not ready

---

### GET /api/health/liveness

Kubernetes-style liveness probe.

**Authentication:** Not required

**Response (200 OK):**
```json
{
  "alive": true
}
```

---

### GET /api/health/ready/full

Comprehensive readiness probe with all dependencies.

**Authentication:** Not required

**Response (200 OK):**
```json
{
  "status": "up",
  "checks": {
    "database": {"status": "up"},
    "redis": {"status": "up"},
    "streaming": {
      "status": "up",
      "active_symbols": 2
    },
    "anthropic": {"status": "up"}
  },
  "time": "2025-10-26T14:30:00.000Z"
}
```

---

### GET /api/health/sentry-test

Test endpoint that raises an exception for Sentry testing.

**Authentication:** Not required

**Response:** Intentionally throws exception for error tracking verification

---

## Portfolio & Positions

### GET /api/account

Get Tradier account information.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "data": {
    "account_number": "ABC123456",
    "total_equity": 125000.50,
    "total_cash": 45000.25,
    "option_buying_power": 80000.00,
    "day_trade_count": 2
  },
  "timestamp": "2025-10-26T14:30:00.000Z"
}
```

**Data Source:** Tradier API (Live account)

---

### GET /api/positions

Get all open positions from Tradier.

**Authentication:** Required

**Caching:** 30 seconds

**Response (200 OK):**
```json
{
  "data": [
    {
      "symbol": "AAPL",
      "quantity": 100,
      "cost_basis": 15000.00,
      "close_price": 155.50,
      "date_acquired": "2025-10-15T00:00:00Z"
    }
  ],
  "count": 1,
  "timestamp": "2025-10-26T14:30:00.000Z"
}
```

**Data Source:** Tradier API (Live account)

---

### GET /api/positions/{symbol}

Get a specific position by symbol.

**Authentication:** Required

**Path Parameters:**
- `symbol` (string, required): Stock symbol (e.g., "AAPL")

**Response (200 OK):**
```json
{
  "data": {
    "symbol": "AAPL",
    "quantity": 100,
    "cost_basis": 15000.00,
    "close_price": 155.50,
    "date_acquired": "2025-10-15T00:00:00Z"
  },
  "timestamp": "2025-10-26T14:30:00.000Z"
}
```

**Errors:**
- `404`: No position found for symbol
- `500`: Failed to fetch position

---

## Orders & Trading

### POST /api/trading/execute

Execute trading orders with idempotency and dry-run support.

**Authentication:** Required
**CSRF Protection:** Required

**Request Body:**
```json
{
  "dryRun": true,
  "requestId": "req-20251026-143000-abc123",
  "orders": [
    {
      "symbol": "AAPL",
      "side": "buy",
      "qty": 10,
      "type": "limit",
      "limit_price": 150.00,
      "asset_class": "stock"
    }
  ]
}
```

**Order Fields:**
- `symbol` (string, required): 1-5 uppercase letters (e.g., "AAPL")
- `side` (string, required): "buy" or "sell"
- `qty` (number, required): 0.01 to 10,000 shares/contracts
- `type` (string, optional): "market", "limit", "stop", "stop_limit" (default: "market")
- `limit_price` (number, optional): Required for limit/stop_limit orders
- `asset_class` (string, optional): "stock" or "option" (default: "stock")
- **Options-specific:**
  - `option_type` (string): "call" or "put" (required for options)
  - `strike_price` (number): Strike price (required for options)
  - `expiration_date` (string): YYYY-MM-DD format (required for options)

**Request Validation:**
- `requestId`: 8-64 alphanumeric characters + hyphens/underscores for idempotency
- `orders`: Max 10 orders per request

**Response (200 OK) - Dry Run:**
```json
{
  "accepted": true,
  "dryRun": true,
  "orders": [
    {
      "symbol": "AAPL",
      "side": "buy",
      "qty": 10,
      "type": "limit",
      "limit_price": 150.00
    }
  ]
}
```

**Response (200 OK) - Live Execution:**
```json
{
  "accepted": true,
  "dryRun": false,
  "orders": [
    {
      "symbol": "AAPL",
      "side": "buy",
      "qty": 10,
      "type": "limit",
      "limit_price": 150.00,
      "alpaca_order_id": "abc-123-def",
      "status": "pending_new"
    }
  ]
}
```

**Circuit Breaker:**
- Opens after 3 consecutive failures
- Cooldown: 60 seconds
- Returns `503` when circuit is open

**Retry Logic:**
- 3 attempts with exponential backoff (1s, 2s, 4s)
- Only retries on connection/timeout errors

**Errors:**
- `400`: Invalid request data
- `423`: Trading halted (kill switch active)
- `500`: Order execution failed
- `503`: Alpaca API temporarily unavailable (circuit breaker open)

---

### POST /api/admin/kill

Activate/deactivate trading kill switch.

**Authentication:** Required
**CSRF Protection:** Required

**Request Body:**
```json
{
  "state": true
}
```

**Response (200 OK):**
```json
{
  "tradingHalted": true
}
```

**Behavior:**
- When `state: true`, all trading is halted
- Existing orders are not cancelled
- New order submissions return `423 Locked`

---

### POST /api/order-templates

Create a new order template.

**Authentication:** Required
**CSRF Protection:** Required

**Request Body:**
```json
{
  "name": "AAPL Buy Template",
  "description": "Standard AAPL long position",
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 10,
  "order_type": "limit",
  "limit_price": 150.00
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": null,
  "name": "AAPL Buy Template",
  "description": "Standard AAPL long position",
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 10,
  "order_type": "limit",
  "limit_price": 150.00,
  "created_at": "2025-10-26T14:30:00Z",
  "updated_at": "2025-10-26T14:30:00Z",
  "last_used_at": null
}
```

---

### GET /api/order-templates

List all order templates.

**Authentication:** Required

**Query Parameters:**
- `skip` (integer, optional): Pagination offset (default: 0)
- `limit` (integer, optional): Max results (default: 100)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "AAPL Buy Template",
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 10,
    "order_type": "limit",
    "limit_price": 150.00,
    "created_at": "2025-10-26T14:30:00Z"
  }
]
```

---

### GET /api/order-templates/{template_id}

Get a specific order template by ID.

**Authentication:** Required

**Path Parameters:**
- `template_id` (integer, required): Template ID

**Response (200 OK):** Same as POST response

**Errors:**
- `404`: Order template not found

---

### PUT /api/order-templates/{template_id}

Update an existing order template.

**Authentication:** Required
**CSRF Protection:** Required

**Request Body:** (all fields optional)
```json
{
  "name": "Updated Template Name",
  "limit_price": 155.00
}
```

**Response (200 OK):** Updated template object

**Errors:**
- `404`: Order template not found

---

### DELETE /api/order-templates/{template_id}

Delete an order template.

**Authentication:** Required
**CSRF Protection:** Required

**Response (204 No Content)**

**Errors:**
- `404`: Order template not found

---

### POST /api/order-templates/{template_id}/use

Mark template as used (updates last_used_at timestamp).

**Authentication:** Required
**CSRF Protection:** Required

**Response (200 OK):** Template object with updated timestamp

---

## Market Data

All market data endpoints use Tradier API for real-time quotes, historical data, and analysis.

### GET /api/market/quote/{symbol}

Get real-time quote for a symbol.

**Authentication:** Required

**Caching:** Configurable TTL (default: 5 seconds)

**Path Parameters:**
- `symbol` (string, required): Stock symbol (1-10 characters)

**Response (200 OK):**
```json
{
  "symbol": "AAPL",
  "bid": 154.25,
  "ask": 154.50,
  "last": 154.35,
  "volume": 45678910,
  "timestamp": "2025-10-26T14:30:00.000Z",
  "cached": false
}
```

**Data Source:** Tradier API (Real-time, NO delay)

**Errors:**
- `404`: No quote found for symbol
- `500`: Failed to fetch quote

---

### GET /api/market/quotes

Get quotes for multiple symbols (batch request).

**Authentication:** Required

**Query Parameters:**
- `symbols` (string, required): Comma-separated symbols (max 200 chars, e.g., "AAPL,MSFT,GOOGL")

**Response (200 OK):**
```json
{
  "AAPL": {
    "bid": 154.25,
    "ask": 154.50,
    "last": 154.35,
    "timestamp": "2025-10-26T14:30:00.000Z"
  },
  "MSFT": {
    "bid": 380.10,
    "ask": 380.25,
    "last": 380.15,
    "timestamp": "2025-10-26T14:30:00.000Z"
  }
}
```

**Performance:** Intelligent caching - checks cache per symbol, batches API calls for cache misses

---

### GET /api/market/bars/{symbol}

Get historical price bars (OHLCV data).

**Authentication:** Required

**Caching:** 1 hour (historical data doesn't change)

**Path Parameters:**
- `symbol` (string, required): Stock symbol

**Query Parameters:**
- `timeframe` (string, optional): "1Min", "5Min", "15Min", "1Hour", "1Day", "daily", "weekly", "monthly" (default: "daily")
- `limit` (integer, optional): Number of bars (1-1000, default: 100)

**Response (200 OK):**
```json
{
  "symbol": "AAPL",
  "bars": [
    {
      "timestamp": "2025-10-26T00:00:00Z",
      "open": 154.00,
      "high": 156.50,
      "low": 153.25,
      "close": 155.75,
      "volume": 78954210
    }
  ],
  "cached": false
}
```

**Data Source:** Tradier API

---

### GET /api/market/scanner/under4

Scan for stocks under $4 with volume.

**Authentication:** Required

**Caching:** 3 minutes

**Response (200 OK):**
```json
{
  "candidates": [
    {
      "symbol": "SOFI",
      "price": 3.85,
      "bid": 3.84,
      "ask": 3.86,
      "volume": 15678920,
      "timestamp": "2025-10-26T14:30:00.000Z"
    }
  ],
  "count": 12,
  "cached": false
}
```

**Scan Criteria:**
- Price: $0.50 - $4.00
- Liquid stocks with high volume
- Pre-defined list of candidates

---

### GET /api/market/cache/stats

Get cache performance statistics.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "cache_hits": 1250,
  "cache_misses": 325,
  "total_requests": 1575,
  "hit_rate_percent": 79.4,
  "timestamp": "2025-10-26T14:30:00.000Z"
}
```

---

### POST /api/market/cache/clear

Clear all market data caches.

**Authentication:** Required
**CSRF Protection:** Required

**Response (200 OK):**
```json
{
  "success": true,
  "entries_cleared": 487,
  "timestamp": "2025-10-26T14:30:00.000Z"
}
```

**Clears:**
- All quote caches
- Bar data caches
- Scanner result caches

---

## AI Recommendations

AI-powered trading recommendations using real market data and technical analysis.

### GET /api/ai/recommendations

Generate AI-powered trading recommendations.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "recommendations": [
    {
      "symbol": "AAPL",
      "action": "BUY",
      "confidence": 85.5,
      "score": 8.5,
      "reason": "Strong bullish momentum with high volume confirmation",
      "targetPrice": 165.00,
      "currentPrice": 154.35,
      "timeframe": "1-2 weeks",
      "risk": "Low",
      "entryPrice": 153.50,
      "stopLoss": 146.50,
      "takeProfit": 165.00,
      "riskRewardRatio": 2.3,
      "indicators": {
        "rsi": 62.5,
        "macd_histogram": 0.75,
        "sma_20": 152.00,
        "sma_50": 148.50
      },
      "tradeData": {
        "symbol": "AAPL",
        "side": "buy",
        "quantity": 10,
        "orderType": "limit",
        "entryPrice": 153.50,
        "stopLoss": 146.50,
        "takeProfit": 165.00
      },
      "portfolioFit": "New position - Adds diversification",
      "momentum": {
        "sma_20": 152.00,
        "sma_50": 148.50,
        "sma_200": 145.00,
        "price_vs_sma_20": 1.54,
        "price_vs_sma_50": 3.94,
        "price_vs_sma_200": 6.45,
        "avg_volume_20d": 65000000,
        "volume_strength": "High",
        "volume_ratio": 1.8,
        "trend_alignment": "Bullish"
      },
      "volatility": {
        "atr": 3.25,
        "atr_percent": 2.1,
        "bb_width": 4.5,
        "volatility_class": "Medium",
        "volatility_score": 5.5
      },
      "sector": "Technology",
      "sectorPerformance": {
        "name": "Technology",
        "changePercent": 2.5,
        "rank": 1,
        "isLeader": true,
        "isLaggard": false
      },
      "explanation": "**BUY Recommendation** (85% confidence)..."
    }
  ],
  "portfolioAnalysis": {
    "totalPositions": 5,
    "totalValue": 125000.50,
    "topSectors": [
      {"name": "Technology", "percentage": 35.0}
    ],
    "riskScore": 4.5,
    "diversificationScore": 80.0,
    "recommendations": [
      "Portfolio is well-diversified across sectors"
    ]
  },
  "generated_at": "2025-10-26T14:30:00.000Z",
  "model_version": "v2.0.0-portfolio-aware"
}
```

**Data Sources:**
- Real-time quotes: Tradier API
- Historical data: Tradier API (200 days for technical analysis)
- Portfolio positions: Alpaca Paper Trading API
- Technical indicators: RSI, MACD, Bollinger Bands, SMA (20, 50, 200)

**Analysis Includes:**
- Momentum analysis (SMAs, volume, trend alignment)
- Volatility analysis (ATR, Bollinger Band width)
- Sector correlation and performance
- Portfolio fit analysis
- Risk/reward calculations
- 1-click trade execution data

---

### GET /api/ai/recommendations/{symbol}

Get AI recommendation for a specific symbol.

**Authentication:** Required

**Path Parameters:**
- `symbol` (string, required): Stock symbol (1-10 characters, pattern: `^[A-Z0-9$.:^-]+$`)

**Response (200 OK):**
```json
{
  "symbol": "AAPL",
  "action": "BUY",
  "confidence": 75.5,
  "reason": "AI analysis suggests favorable risk/reward",
  "targetPrice": 165.00,
  "currentPrice": 154.35,
  "timeframe": "1-2 months",
  "risk": "Medium"
}
```

**Errors:**
- `404`: No price data available for symbol

---

### GET /api/ai/signals

Generate ML-based trading signals with technical analysis.

**Authentication:** Required

**Query Parameters:**
- `symbols` (string, optional): Comma-separated symbols (default: watchlist from env)
- `min_confidence` (number, optional): Minimum confidence threshold 0-100 (default: 60.0)
- `use_technical` (boolean, optional): Use real technical analysis (default: true)

**Response (200 OK):**
```json
{
  "recommendations": [...],
  "generated_at": "2025-10-26T14:30:00.000Z",
  "model_version": "v2.0.0-technical"
}
```

**Technical Analysis:**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (SMA 20, 50, 200)
- Trend detection
- Support/resistance levels

---

### GET /api/ai/analyze-symbol/{symbol}

Comprehensive AI analysis of a stock symbol.

**Authentication:** Required

**Path Parameters:**
- `symbol` (string, required): Stock symbol

**Response (200 OK):**
```json
{
  "symbol": "AAPL",
  "current_price": 154.35,
  "analysis": "**Current Status**: AAPL is trading at $154.35...",
  "momentum": "Bullish",
  "trend": "Strong Uptrend",
  "support_level": 148.50,
  "resistance_level": 160.00,
  "risk_assessment": "Low - Strong signal with high confidence",
  "entry_suggestion": "Consider entering near $154.35 if price holds above $148.50...",
  "exit_suggestion": "Take partial profits at $165.00...",
  "stop_loss_suggestion": 146.50,
  "take_profit_suggestion": 165.00,
  "confidence_score": 85.5,
  "key_indicators": {
    "rsi": 62.5,
    "macd_histogram": 0.75,
    "sma_20": 152.00,
    "sma_50": 148.50,
    "sma_200": 145.00,
    "current_vs_sma20": 1.54,
    "current_vs_sma50": 3.94
  },
  "summary": "BUY signal with 85.5% confidence. Strong Uptrend with bullish momentum..."
}
```

**Data Requirements:**
- Minimum 50 days of historical data
- Uses 200 days for comprehensive analysis

---

### POST /api/ai/recommendations/save

Save an AI recommendation to history for tracking.

**Authentication:** Required
**CSRF Protection:** Required

**Request Body:**
```json
{
  "symbol": "AAPL",
  "recommendation_type": "buy",
  "confidence_score": 85.5,
  "analysis_data": {},
  "suggested_entry_price": 153.50,
  "suggested_stop_loss": 146.50,
  "suggested_take_profit": 165.00,
  "suggested_position_size": 10,
  "reasoning": "Strong bullish momentum...",
  "market_context": "Technology sector leading..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "recommendation_id": 123,
  "message": "Saved BUY recommendation for AAPL"
}
```

**Purpose:**
- Performance tracking (how accurate were predictions?)
- Strategy refinement (which signals work best?)
- User analysis (review past recommendations and outcomes)

**Expiry:** Recommendations expire after 7 days

---

### GET /api/ai/recommendations/history

Get recommendation history with optional filters.

**Authentication:** Required

**Query Parameters:**
- `symbol` (string, optional): Filter by symbol
- `status` (string, optional): Filter by status ("pending", "executed", "ignored", "expired")
- `limit` (integer, optional): Max results (1-200, default: 50)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response (200 OK):**
```json
[
  {
    "id": 123,
    "symbol": "AAPL",
    "recommendation_type": "buy",
    "confidence_score": 85.5,
    "analysis_data": {},
    "suggested_entry_price": 153.50,
    "suggested_stop_loss": 146.50,
    "suggested_take_profit": 165.00,
    "reasoning": "Strong bullish momentum...",
    "market_context": "Technology sector leading...",
    "status": "pending",
    "created_at": "2025-10-26T14:30:00Z",
    "expires_at": "2025-11-02T14:30:00Z",
    "executed_at": null,
    "execution_price": null,
    "actual_pnl": null,
    "actual_pnl_percent": null
  }
]
```

---

### GET /api/ai/recommended-templates

Get AI-recommended strategy templates based on user's risk profile and market conditions.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "templates": [
    {
      "template_id": "trend-following-macd",
      "name": "Trend Following (MACD)",
      "description": "Trend-following strategy using MACD crossovers",
      "strategy_type": "momentum",
      "risk_level": "Moderate",
      "compatibility_score": 92.5,
      "expected_win_rate": 65.0,
      "avg_return_percent": 2.5,
      "max_drawdown_percent": 8.0,
      "recommended_for": "Moderate risk tolerance, trending markets",
      "ai_rationale": "Ideal for your moderate risk tolerance...",
      "clone_url": "/api/strategies/templates/trend-following-macd/clone"
    }
  ],
  "user_risk_tolerance": 50,
  "market_volatility": "Medium",
  "portfolio_value": 125000.50,
  "generated_at": "2025-10-26T14:30:00.000Z",
  "message": "Found 5 strategies compatible with your risk profile"
}
```

---

### GET /api/ai/analyze-portfolio

AI-powered portfolio analysis using Claude API.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "health_score": 82.5,
  "risk_level": "Medium",
  "total_value": 125000.50,
  "cash_balance": 45000.25,
  "buying_power": 80000.00,
  "positions_count": 5,
  "diversification_score": 80.0,
  "recommendations": [
    "Maintain current diversification strategy",
    "Consider rebalancing quarterly",
    "Monitor positions regularly for changes"
  ],
  "risk_factors": [
    "Monitor market volatility",
    "High concentration risk in few positions",
    "Low cash reserves - limited ability to handle drawdowns"
  ],
  "opportunities": [
    "High buying power available for new positions",
    "Room to add complementary positions",
    "Regularly review for tax-loss harvesting opportunities"
  ],
  "ai_summary": "Portfolio health score: 82/100. Maintain current diversification strategy.",
  "generated_at": "2025-10-26T14:30:00Z"
}
```

**Data Sources:**
- Account data: Tradier API
- Positions: Tradier API
- AI Analysis: Claude API (claude-sonnet-4-20250514)

**Fallback:** Rule-based analysis when Claude API unavailable

---

### POST /api/ai/analyze-news

AI-powered news article analysis.

**Authentication:** Required
**CSRF Protection:** Required

**Request Body:**
```json
{
  "title": "Tech Stocks Rally on Strong Earnings",
  "content": "Apple and Microsoft report record profits...",
  "source": "CNBC",
  "published_at": "2025-10-20T10:30:00Z"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "article_info": {
    "title": "Tech Stocks Rally on Strong Earnings",
    "source": "CNBC",
    "published_at": "2025-10-20T10:30:00Z"
  },
  "ai_analysis": {
    "sentiment": "bullish",
    "sentiment_score": 0.75,
    "confidence": 85.0,
    "tickers_mentioned": ["AAPL", "MSFT"],
    "portfolio_impact": "high",
    "affected_positions": ["AAPL"],
    "key_points": [
      "Record earnings for tech giants",
      "Positive guidance for next quarter",
      "Strong consumer demand"
    ],
    "trading_implications": "Consider adding to tech positions...",
    "urgency": "medium",
    "summary": "Strong tech earnings drive positive sentiment..."
  },
  "user_context": {
    "has_positions": true,
    "position_count": 5,
    "tickers": ["AAPL", "MSFT", "GOOGL"]
  }
}
```

**AI Model:** Claude Sonnet 4 (claude-sonnet-4-20250514)

---

### POST /api/ai/analyze-news-batch

Analyze multiple news articles in batch.

**Authentication:** Required
**CSRF Protection:** Required

**Request Body:**
```json
[
  {
    "title": "Article 1",
    "content": "Tech stocks surge...",
    "source": "CNBC"
  },
  {
    "title": "Article 2",
    "content": "Fed announces rate decision...",
    "source": "Reuters"
  }
]
```

**Limit:** Maximum 5 articles per batch

**Response (200 OK):**
```json
{
  "success": true,
  "results": [
    {...},
    {...}
  ],
  "analyzed_count": 2
}
```

---

## Claude AI Chat

*(This section would continue with Claude chat endpoints - continuing due to length...)*

## Strategies

### POST /api/strategies/save

Save strategy configuration.

**Authentication:** Required
**CSRF Protection:** Required

**Request Body:**
```json
{
  "strategy_type": "under4-multileg",
  "config": {
    "max_position_size": 1000,
    "stop_loss_percent": 5.0,
    "take_profit_percent": 10.0
  }
}
```

**Allowed Strategy Types:**
- `under4-multileg`
- `trend-following`
- `mean-reversion`
- `momentum`
- `custom`

**Response (200 OK):**
```json
{
  "success": true,
  "strategy_id": 123,
  "message": "Strategy saved successfully"
}
```

---

### GET /api/strategies/load/{strategy_type}

Load strategy configuration.

**Authentication:** Required

**Path Parameters:**
- `strategy_type` (string, required): Strategy type identifier

**Response (200 OK):**
```json
{
  "strategy_type": "under4-multileg",
  "config": {
    "max_position_size": 1000,
    "stop_loss_percent": 5.0,
    "take_profit_percent": 10.0
  },
  "created_at": "2025-10-26T14:30:00Z"
}
```

**Errors:**
- `404`: Strategy not found

---

### GET /api/strategies/list

List all available strategies for the user.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "strategies": [
    {
      "id": 123,
      "name": "Under $4 Multi-Leg",
      "strategy_type": "under4-multileg",
      "is_active": true,
      "created_at": "2025-10-26T14:30:00Z"
    }
  ]
}
```

---

### POST /api/strategies/run

Run a strategy (execute morning routine).

**Authentication:** Required
**CSRF Protection:** Required

**Request Body:**
```json
{
  "strategy_type": "under4-multileg",
  "dry_run": true
}
```

**Response (200 OK) - Dry Run:**
```json
{
  "success": true,
  "dry_run": true,
  "signals": [...],
  "execution_plan": [...]
}
```

**Errors:**
- `400`: Unknown strategy type
- `501`: Live execution not yet implemented

---

### DELETE /api/strategies/{strategy_type}

Delete a saved strategy configuration.

**Authentication:** Required
**CSRF Protection:** Required

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Strategy deleted successfully"
}
```

**Errors:**
- `404`: Strategy not found

---

### GET /api/strategies/templates

Get all available strategy templates.

**Authentication:** Required

**Query Parameters:**
- `filter_by_risk` (boolean, optional): Filter by user's risk tolerance (default: true)

**Response (200 OK):**
```json
{
  "templates": [
    {
      "id": "trend-following-macd",
      "name": "Trend Following (MACD)",
      "description": "Trend-following strategy using MACD crossovers",
      "strategy_type": "momentum",
      "risk_level": "Moderate",
      "expected_win_rate": 65.0,
      "avg_return_percent": 2.5,
      "max_drawdown_percent": 8.0,
      "recommended_for": "Moderate risk tolerance, trending markets",
      "compatibility_score": 92.5,
      "config": {...}
    }
  ],
  "user_risk_tolerance": 50,
  "market_volatility": "Medium"
}
```

---

### GET /api/strategies/templates/{template_id}

Get a specific strategy template by ID.

**Authentication:** Required

**Path Parameters:**
- `template_id` (string, required): Template identifier

**Query Parameters:**
- `customize` (boolean, optional): Customize based on user's risk tolerance (default: true)

**Response (200 OK):**
```json
{
  "id": "trend-following-macd",
  "name": "Trend Following (MACD)",
  "description": "Trend-following strategy using MACD crossovers",
  "strategy_type": "momentum",
  "risk_level": "Moderate",
  "expected_win_rate": 65.0,
  "avg_return_percent": 2.5,
  "max_drawdown_percent": 8.0,
  "recommended_for": "Moderate risk tolerance, trending markets",
  "config": {...},
  "customized": true
}
```

**Errors:**
- `404`: Template not found

---

### POST /api/strategies/templates/{template_id}/clone

Clone a strategy template to user's strategies.

**Authentication:** Required
**CSRF Protection:** Required

**Request Body:**
```json
{
  "custom_name": "My Trend Strategy",
  "customize_config": true,
  "config_overrides": {
    "position_size_percent": 8.0
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Template 'Trend Following (MACD)' cloned successfully",
  "strategy": {
    "id": 456,
    "name": "My Trend Strategy",
    "description": "Trend-following strategy using MACD crossovers",
    "strategy_type": "momentum",
    "config": {...},
    "is_active": false,
    "created_at": "2025-10-26T14:30:00Z"
  }
}
```

**Errors:**
- `404`: Template not found, user not found

---

## Response Codes Summary

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request successful, no response body |
| 400 | Bad Request - Invalid request data/validation failed |
| 401 | Unauthorized - Missing or invalid authentication token |
| 403 | Forbidden - Valid token but insufficient permissions |
| 404 | Not Found - Resource does not exist |
| 423 | Locked - Trading halted (kill switch active) |
| 500 | Internal Server Error - Server error |
| 501 | Not Implemented - Feature not yet implemented |
| 503 | Service Unavailable - Service temporarily unavailable (circuit breaker) |

---

## Rate Limiting

Rate limiting is enabled in production (disabled in test mode).

**Limits:**
- General endpoints: Configured per endpoint
- Trading endpoints: Stricter limits to prevent abuse

**Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)

---

## Caching Strategy

The API implements intelligent caching to optimize performance:

| Data Type | TTL | Cache Key Pattern |
|-----------|-----|-------------------|
| Quotes | 5s | `quote:{symbol}` |
| Historical Bars | 1 hour | `bars:{symbol}:{timeframe}:{limit}` |
| Positions | 30s | `portfolio:positions` |
| Scanner Results | 3 min | `scanner:under4` |

**Cache Clear:** Use `POST /api/market/cache/clear` to invalidate all caches

---

## Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters long",
      "type": "value_error"
    }
  ]
}
```

---

## Data Sources

**Market Data:**
- **Tradier API** (Live account) - ALL market data, quotes, bars, options
- Real-time quotes (NO delay)
- Historical OHLCV bars
- Options chains and Greeks
- Market data and news

**Trade Execution:**
- **Alpaca API** (Paper Trading account) - Order execution ONLY
- Paper trade orders and fills
- Paper account positions
- Paper account balance
- NOT used for market data/quotes/analysis

**AI Analysis:**
- **Anthropic Claude API** (claude-sonnet-4-20250514)
- Portfolio analysis
- News sentiment analysis
- Trading recommendations

---

## Authentication Flow

1. **Register/Login** → Receive access token (15min) + refresh token (7 days)
2. **Get CSRF Token** → Call `/api/auth/csrf-token` after login
3. **Make Authenticated Requests:**
   - Include `Authorization: Bearer <access_token>` header
   - For state-changing operations (POST/PUT/DELETE/PATCH), also include `X-CSRF-Token: <csrf_token>` header
4. **Refresh Token** → When access token expires, call `/api/auth/refresh` with refresh token
5. **Logout** → Call `/api/auth/logout` to invalidate all sessions

---

## Interactive API Documentation

Once the backend is running, you can access interactive API documentation:

- **Swagger UI:** http://localhost:8001/api/docs
- **ReDoc:** http://localhost:8001/api/redoc
- **OpenAPI JSON:** http://localhost:8001/api/openapi.json

---

## WebSocket Streaming (TBD)

Real-time market data streaming via WebSocket (documentation coming soon).

---

## Support

For API support, issues, or feature requests:
- GitHub Issues: [PaiiD Repository](https://github.com/your-repo/paiid)
- Email: support@paiid.com

---

**Last Updated:** October 26, 2025
**API Version:** 1.0.0
**Documentation Version:** 1.0
