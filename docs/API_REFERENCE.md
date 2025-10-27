# PaiiD API Reference

**Version:** 1.0.0
**Base URL:** `https://paiid-backend.onrender.com`
**Local Development:** `http://localhost:8001`

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Response Format](#response-format)
5. [Error Handling](#error-handling)
6. [Endpoint Reference](#endpoint-reference)
   - [Authentication](#authentication-endpoints)
   - [Health & Monitoring](#health--monitoring-endpoints)
   - [Portfolio Management](#portfolio-management-endpoints)
   - [Order Execution](#order-execution-endpoints)
   - [Market Data](#market-data-endpoints)
   - [AI & ML](#ai--ml-endpoints)
   - [Strategies](#strategy-endpoints)
   - [News & Sentiment](#news--sentiment-endpoints)
   - [Options Trading](#options-endpoints)
   - [User Management](#user-management-endpoints)
   - [Streaming](#streaming-endpoints)
7. [OpenAPI Documentation](#openapi-documentation)
8. [Postman Collection](#postman-collection)

---

## Overview

The PaiiD API provides 137 endpoints across 26 functional areas for AI-powered trading operations. Built with FastAPI, it delivers high-performance, real-time market data, intelligent trade execution, and comprehensive portfolio management.

### Data Sources

- **Market Data:** Tradier API (Real-time, NO delay)
- **Trade Execution:** Alpaca Paper Trading API (Paper trading only)
- **AI Analysis:** Anthropic Claude API
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Caching:** Redis (optional, falls back to in-memory)

### Key Features

- Real-time WebSocket streaming for market data
- JWT-based authentication with refresh tokens
- CSRF protection for state-changing operations
- Rate limiting to prevent abuse
- Intelligent caching for performance optimization
- Comprehensive error handling with detailed messages
- Machine learning models for pattern recognition and regime detection

---

## Authentication

The API supports two authentication methods:

### 1. JWT Authentication (Recommended)

All authenticated endpoints require a JWT Bearer token in the Authorization header.

**Obtaining a Token:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Using the Token:**
```http
GET /api/positions
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. API Token Authentication (Legacy)

For server-to-server communication, use the API token from environment variables.

```http
GET /api/positions
Authorization: Bearer rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
```

### CSRF Protection

State-changing operations (POST, PUT, DELETE, PATCH) require a CSRF token in addition to JWT authentication.

**Obtaining CSRF Token:**
```http
GET /api/auth/csrf-token
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "csrf_token": "1a2b3c4d5e6f7g8h9i0j"
}
```

**Using CSRF Token:**
```http
POST /api/orders
Authorization: Bearer <jwt_token>
X-CSRF-Token: 1a2b3c4d5e6f7g8h9i0j
Content-Type: application/json

{
  "symbol": "AAPL",
  "quantity": 10,
  "side": "buy"
}
```

### Exempt Endpoints

The following endpoints do NOT require authentication:
- `/api/health` - Basic health check
- `/api/health/ping` - Liveness probe
- `/api/monitor/health` - Monitoring health check
- `/api/auth/login` - User login
- `/api/auth/register` - User registration
- `/docs` - Swagger UI documentation
- `/redoc` - ReDoc documentation

---

## Rate Limiting

Rate limits are enforced to ensure fair usage and prevent abuse. Limits are applied per IP address.

### Limits by Category

| Category | Endpoints | Limit | Window |
|----------|-----------|-------|--------|
| **Authentication** | `/api/auth/*` | 10 requests | 1 minute |
| **Market Data** | `/api/market/*`, `/api/quotes/*` | 200 requests | 1 hour |
| **Trading** | `/api/orders/*`, `/api/positions/*` | 60 requests | 1 hour |
| **AI/ML** | `/api/ai/*`, `/api/ml/*` | 50 requests | 1 hour |
| **General** | All other endpoints | 100 requests | 1 hour |

### Rate Limit Headers

All responses include rate limit headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634567890
```

### Exceeding Rate Limits

When rate limits are exceeded, you'll receive a `429 Too Many Requests` response:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Please retry after 60 seconds.",
  "retry_after": 60
}
```

---

## Response Format

All API responses follow a consistent JSON format for both success and error cases.

### Success Response

```json
{
  "status": "success",
  "data": {
    // Response data varies by endpoint
  },
  "timestamp": "2025-10-27T14:30:00Z",
  "request_id": "req_1a2b3c4d5e6f"
}
```

### List Response (Paginated)

```json
{
  "status": "success",
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 125,
    "total_pages": 3
  },
  "timestamp": "2025-10-27T14:30:00Z"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request succeeded |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid request parameters |
| `401` | Unauthorized | Authentication required or failed |
| `403` | Forbidden | Authenticated but not authorized |
| `404` | Not Found | Resource not found |
| `422` | Unprocessable Entity | Validation error |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error |
| `503` | Service Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid order quantity",
    "details": {
      "field": "quantity",
      "constraint": "must be greater than 0"
    }
  },
  "timestamp": "2025-10-27T14:30:00Z",
  "request_id": "req_1a2b3c4d5e6f",
  "path": "/api/orders"
}
```

### Common Error Codes

| Code | Description | Typical Status |
|------|-------------|----------------|
| `AUTHENTICATION_REQUIRED` | No authentication provided | 401 |
| `INVALID_TOKEN` | JWT token is invalid or expired | 401 |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions | 403 |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist | 404 |
| `VALIDATION_ERROR` | Request validation failed | 422 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `EXTERNAL_API_ERROR` | Third-party API error (Tradier, Alpaca) | 503 |
| `DATABASE_ERROR` | Database operation failed | 500 |

---

## Endpoint Reference

### Authentication Endpoints

#### POST `/api/auth/register`
Register a new user account.

**Tags:** `auth`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "invite_code": "PAIID_BETA_2025"
}
```

**Response (201):**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Validation:**
- Email must be valid format
- Password minimum 8 characters
- Invite code required for beta access

---

#### POST `/api/auth/login`
Authenticate user and obtain JWT tokens.

**Tags:** `auth`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

**Errors:**
- `401` - Invalid email or password
- `429` - Too many login attempts

---

#### POST `/api/auth/refresh`
Refresh access token using refresh token.

**Tags:** `auth`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

#### POST `/api/auth/logout`
Logout user and invalidate session.

**Tags:** `auth`
**Auth Required:** Yes

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

#### GET `/api/auth/csrf-token`
Obtain CSRF token for state-changing operations.

**Tags:** `auth`
**Auth Required:** Yes

**Response (200):**
```json
{
  "csrf_token": "1a2b3c4d5e6f7g8h9i0j",
  "expires_at": "2025-10-27T15:30:00Z"
}
```

---

### Health & Monitoring Endpoints

#### GET `/api/health`
Basic health check - always returns 200 if app is running.

**Tags:** `health`
**Auth Required:** No

**Response (200):**
```json
{
  "status": "healthy",
  "time": "2025-10-27T14:30:00Z"
}
```

---

#### GET `/api/health/detailed`
Detailed health check with dependency status.

**Tags:** `health`
**Auth Required:** Yes (admin only)

**Response (200):**
```json
{
  "status": "healthy",
  "uptime_seconds": 86400,
  "version": "1.0.0",
  "dependencies": {
    "database": {
      "status": "healthy",
      "latency_ms": 5.2
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1.8
    },
    "tradier_api": {
      "status": "healthy",
      "latency_ms": 120.5
    },
    "alpaca_api": {
      "status": "healthy",
      "latency_ms": 95.3
    }
  }
}
```

---

#### GET `/api/health/ready`
Kubernetes readiness probe - checks if app can serve traffic.

**Tags:** `health`
**Auth Required:** No

**Response (200):**
```json
{
  "ready": true,
  "checks": {
    "database": "pass",
    "cache": "pass"
  }
}
```

---

#### GET `/api/health/live`
Kubernetes liveness probe - checks if app is alive.

**Tags:** `health`
**Auth Required:** No

**Response (200):**
```json
{
  "alive": true
}
```

---

#### GET `/api/monitor/health`
Monitoring endpoint for external health checks.

**Tags:** `health`
**Auth Required:** No

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-27T14:30:00Z"
}
```

---

#### GET `/api/monitor/ping`
Simple ping endpoint for uptime monitoring.

**Tags:** `health`
**Auth Required:** No

**Response (200):**
```json
{
  "message": "pong"
}
```

---

#### GET `/api/monitor/version`
Get API version information.

**Tags:** `health`
**Auth Required:** No

**Response (200):**
```json
{
  "version": "1.0.0",
  "build": "2025-10-27",
  "environment": "production"
}
```

---

### Portfolio Management Endpoints

#### GET `/api/portfolio`
Get complete portfolio summary.

**Tags:** `portfolio`
**Auth Required:** Yes

**Response (200):**
```json
{
  "account_value": 100000.00,
  "cash": 50000.00,
  "buying_power": 200000.00,
  "positions_value": 50000.00,
  "total_pl": 5000.00,
  "total_pl_percent": 5.26,
  "positions_count": 5
}
```

---

#### GET `/api/portfolio/summary`
Get portfolio analytics summary.

**Tags:** `analytics`
**Auth Required:** Yes

**Response (200):**
```json
{
  "total_value": 100000.00,
  "daily_pl": 1500.00,
  "daily_pl_percent": 1.5,
  "ytd_pl": 15000.00,
  "ytd_pl_percent": 17.65,
  "sharpe_ratio": 1.8,
  "max_drawdown": -0.12
}
```

---

#### GET `/api/portfolio/history`
Get historical portfolio value.

**Tags:** `analytics`
**Auth Required:** Yes

**Query Parameters:**
- `start_date` (optional): ISO date string (default: 30 days ago)
- `end_date` (optional): ISO date string (default: today)
- `interval` (optional): `1d`, `1h`, `15m` (default: `1d`)

**Response (200):**
```json
{
  "history": [
    {
      "timestamp": "2025-10-01T00:00:00Z",
      "value": 95000.00,
      "pl": 0.00
    },
    {
      "timestamp": "2025-10-02T00:00:00Z",
      "value": 96500.00,
      "pl": 1500.00
    }
  ]
}
```

---

### Position Management Endpoints

#### GET `/api/positions`
Get all open positions.

**Tags:** `portfolio`
**Auth Required:** Yes

**Response (200):**
```json
{
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 100,
      "avg_entry_price": 150.00,
      "current_price": 155.00,
      "market_value": 15500.00,
      "cost_basis": 15000.00,
      "unrealized_pl": 500.00,
      "unrealized_pl_percent": 3.33,
      "side": "long"
    }
  ]
}
```

---

#### GET `/api/positions/{symbol}`
Get position for specific symbol.

**Tags:** `portfolio`
**Auth Required:** Yes

**Path Parameters:**
- `symbol` (required): Stock symbol (e.g., AAPL)

**Response (200):**
```json
{
  "symbol": "AAPL",
  "quantity": 100,
  "avg_entry_price": 150.00,
  "current_price": 155.00,
  "market_value": 15500.00,
  "cost_basis": 15000.00,
  "unrealized_pl": 500.00,
  "unrealized_pl_percent": 3.33,
  "side": "long",
  "trades": [
    {
      "timestamp": "2025-10-20T10:00:00Z",
      "quantity": 50,
      "price": 148.00,
      "side": "buy"
    },
    {
      "timestamp": "2025-10-21T14:30:00Z",
      "quantity": 50,
      "price": 152.00,
      "side": "buy"
    }
  ]
}
```

---

### Order Execution Endpoints

#### POST `/api/orders`
Submit a new order.

**Tags:** `orders`
**Auth Required:** Yes
**CSRF Required:** Yes

**Request Body:**
```json
{
  "symbol": "AAPL",
  "quantity": 10,
  "side": "buy",
  "type": "market",
  "time_in_force": "day"
}
```

**Limit Order:**
```json
{
  "symbol": "AAPL",
  "quantity": 10,
  "side": "buy",
  "type": "limit",
  "limit_price": 150.00,
  "time_in_force": "gtc"
}
```

**Response (201):**
```json
{
  "order_id": "abc123-def456",
  "symbol": "AAPL",
  "quantity": 10,
  "side": "buy",
  "type": "market",
  "status": "submitted",
  "submitted_at": "2025-10-27T14:30:00Z"
}
```

**Validation:**
- `symbol`: 1-5 uppercase letters
- `quantity`: Integer > 0, <= 10000
- `side`: "buy" or "sell"
- `type`: "market", "limit", "stop", "stop_limit"
- `time_in_force`: "day", "gtc", "ioc", "fok"

---

#### GET `/api/orders`
Get all orders (open and closed).

**Tags:** `orders`
**Auth Required:** Yes

**Query Parameters:**
- `status` (optional): "open", "closed", "all" (default: "all")
- `limit` (optional): Max results (default: 50, max: 500)
- `since` (optional): ISO timestamp for orders after this time

**Response (200):**
```json
{
  "orders": [
    {
      "order_id": "abc123",
      "symbol": "AAPL",
      "quantity": 10,
      "filled_quantity": 10,
      "side": "buy",
      "type": "market",
      "status": "filled",
      "avg_fill_price": 155.23,
      "submitted_at": "2025-10-27T14:30:00Z",
      "filled_at": "2025-10-27T14:30:05Z"
    }
  ]
}
```

---

#### GET `/api/orders/{order_id}`
Get specific order details.

**Tags:** `orders`
**Auth Required:** Yes

**Path Parameters:**
- `order_id` (required): Order ID from order submission

**Response (200):**
```json
{
  "order_id": "abc123",
  "symbol": "AAPL",
  "quantity": 10,
  "filled_quantity": 10,
  "side": "buy",
  "type": "market",
  "status": "filled",
  "avg_fill_price": 155.23,
  "submitted_at": "2025-10-27T14:30:00Z",
  "filled_at": "2025-10-27T14:30:05Z",
  "fills": [
    {
      "timestamp": "2025-10-27T14:30:05Z",
      "quantity": 10,
      "price": 155.23
    }
  ]
}
```

---

#### DELETE `/api/orders/{order_id}`
Cancel an open order.

**Tags:** `orders`
**Auth Required:** Yes
**CSRF Required:** Yes

**Path Parameters:**
- `order_id` (required): Order ID to cancel

**Response (200):**
```json
{
  "order_id": "abc123",
  "status": "canceled",
  "canceled_at": "2025-10-27T14:35:00Z"
}
```

**Errors:**
- `404` - Order not found
- `400` - Order already filled or canceled

---

#### POST `/api/orders/batch`
Submit multiple orders in a single request.

**Tags:** `orders`
**Auth Required:** Yes
**CSRF Required:** Yes

**Request Body:**
```json
{
  "orders": [
    {
      "symbol": "AAPL",
      "quantity": 10,
      "side": "buy",
      "type": "limit",
      "limit_price": 150.00
    },
    {
      "symbol": "MSFT",
      "quantity": 5,
      "side": "buy",
      "type": "limit",
      "limit_price": 300.00
    }
  ]
}
```

**Response (201):**
```json
{
  "orders": [
    {
      "order_id": "abc123",
      "symbol": "AAPL",
      "status": "submitted"
    },
    {
      "order_id": "def456",
      "symbol": "MSFT",
      "status": "submitted"
    }
  ]
}
```

---

#### GET `/api/order-templates`
Get saved order templates.

**Tags:** `orders`
**Auth Required:** Yes

**Response (200):**
```json
{
  "templates": [
    {
      "id": 1,
      "name": "Buy Tech Dip",
      "symbols": ["AAPL", "MSFT", "GOOGL"],
      "quantity": 10,
      "side": "buy",
      "type": "limit",
      "limit_offset": -2.00
    }
  ]
}
```

---

#### POST `/api/order-templates`
Create a new order template.

**Tags:** `orders`
**Auth Required:** Yes
**CSRF Required:** Yes

**Request Body:**
```json
{
  "name": "Buy Tech Dip",
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "quantity": 10,
  "side": "buy",
  "type": "limit",
  "limit_offset": -2.00
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Buy Tech Dip",
  "created_at": "2025-10-27T14:30:00Z"
}
```

---

### Market Data Endpoints

#### GET `/api/market/quote/{symbol}`
Get real-time quote for a symbol.

**Tags:** `market-data`
**Auth Required:** Yes

**Path Parameters:**
- `symbol` (required): Stock symbol (e.g., AAPL)

**Response (200):**
```json
{
  "symbol": "AAPL",
  "last": 155.25,
  "bid": 155.20,
  "ask": 155.30,
  "volume": 45234567,
  "open": 153.00,
  "high": 156.00,
  "low": 152.50,
  "close": 154.75,
  "change": 0.50,
  "change_percent": 0.32,
  "timestamp": "2025-10-27T14:30:00Z"
}
```

---

#### POST `/api/market/quotes`
Get quotes for multiple symbols.

**Tags:** `market-data`
**Auth Required:** Yes

**Request Body:**
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA"]
}
```

**Response (200):**
```json
{
  "quotes": {
    "AAPL": {
      "symbol": "AAPL",
      "last": 155.25,
      "change_percent": 0.32
    },
    "MSFT": {
      "symbol": "MSFT",
      "last": 305.50,
      "change_percent": 1.25
    }
  }
}
```

---

#### GET `/api/market/bars/{symbol}`
Get historical price bars (OHLCV data).

**Tags:** `market-data`
**Auth Required:** Yes

**Path Parameters:**
- `symbol` (required): Stock symbol

**Query Parameters:**
- `interval` (required): Bar interval - `1m`, `5m`, `15m`, `1h`, `1d`
- `start_date` (optional): ISO date string (default: 30 days ago)
- `end_date` (optional): ISO date string (default: today)

**Response (200):**
```json
{
  "symbol": "AAPL",
  "interval": "1d",
  "bars": [
    {
      "timestamp": "2025-10-27T00:00:00Z",
      "open": 153.00,
      "high": 156.00,
      "low": 152.50,
      "close": 155.25,
      "volume": 45234567
    }
  ]
}
```

---

#### GET `/api/market/conditions`
Get current market conditions.

**Tags:** `market-data`
**Auth Required:** Yes

**Response (200):**
```json
{
  "market_open": true,
  "next_open": "2025-10-28T09:30:00Z",
  "next_close": "2025-10-27T16:00:00Z",
  "indices": {
    "SPY": {
      "last": 455.50,
      "change_percent": 0.85
    },
    "QQQ": {
      "last": 385.25,
      "change_percent": 1.20
    }
  }
}
```

---

#### GET `/api/market/indices`
Get major market indices.

**Tags:** `market-data`
**Auth Required:** No

**Response (200):**
```json
{
  "indices": [
    {
      "symbol": "SPY",
      "name": "S&P 500 ETF",
      "last": 455.50,
      "change": 3.85,
      "change_percent": 0.85
    },
    {
      "symbol": "QQQ",
      "name": "Nasdaq 100 ETF",
      "last": 385.25,
      "change": 4.56,
      "change_percent": 1.20
    }
  ]
}
```

---

#### GET `/api/market/scanner`
Scan market for stocks matching criteria.

**Tags:** `screening`
**Auth Required:** Yes

**Query Parameters:**
- `min_volume` (optional): Minimum volume
- `min_price` (optional): Minimum price
- `max_price` (optional): Maximum price
- `min_change_percent` (optional): Minimum % change
- `sector` (optional): Sector filter

**Response (200):**
```json
{
  "results": [
    {
      "symbol": "AAPL",
      "last": 155.25,
      "volume": 45234567,
      "change_percent": 2.5,
      "sector": "Technology"
    }
  ],
  "count": 25
}
```

---

#### GET `/api/market/movers`
Get top gainers, losers, and most active stocks.

**Tags:** `screening`
**Auth Required:** Yes

**Response (200):**
```json
{
  "gainers": [
    {
      "symbol": "NVDA",
      "change_percent": 8.5,
      "last": 495.00
    }
  ],
  "losers": [
    {
      "symbol": "INTC",
      "change_percent": -5.2,
      "last": 35.50
    }
  ],
  "most_active": [
    {
      "symbol": "TSLA",
      "volume": 125000000,
      "last": 245.00
    }
  ]
}
```

---

### AI & ML Endpoints

#### GET `/api/ai/recommendations`
Get AI-generated trading recommendations.

**Tags:** `ai`
**Auth Required:** Yes

**Response (200):**
```json
{
  "recommendations": [
    {
      "symbol": "AAPL",
      "action": "buy",
      "confidence": 0.85,
      "target_price": 160.00,
      "stop_loss": 148.00,
      "rationale": "Strong technical setup with bullish divergence on RSI",
      "risk_rating": "moderate",
      "timestamp": "2025-10-27T14:30:00Z"
    }
  ]
}
```

---

#### GET `/api/ai/recommendations/{symbol}`
Get AI recommendations for specific symbol.

**Tags:** `ai`
**Auth Required:** Yes

**Path Parameters:**
- `symbol` (required): Stock symbol

**Response (200):**
```json
{
  "symbol": "AAPL",
  "action": "buy",
  "confidence": 0.85,
  "target_price": 160.00,
  "stop_loss": 148.00,
  "rationale": "Strong technical setup with bullish divergence on RSI. Price broke above 50-day MA with increasing volume.",
  "risk_rating": "moderate",
  "technical_indicators": {
    "rsi": 65.5,
    "macd": "bullish",
    "moving_averages": "bullish"
  },
  "timestamp": "2025-10-27T14:30:00Z"
}
```

---

#### POST `/api/ai/analyze-portfolio`
Get AI analysis of current portfolio.

**Tags:** `ai`
**Auth Required:** Yes

**Response (200):**
```json
{
  "overall_score": 7.5,
  "risk_level": "moderate",
  "diversification_score": 6.0,
  "sector_allocation": {
    "Technology": 45.0,
    "Healthcare": 25.0,
    "Finance": 20.0,
    "Energy": 10.0
  },
  "recommendations": [
    "Consider reducing technology exposure to below 40%",
    "Add more international exposure for diversification"
  ],
  "strengths": [
    "Well-balanced sector allocation",
    "Strong performing stocks"
  ],
  "weaknesses": [
    "Over-concentration in technology",
    "Limited international exposure"
  ]
}
```

---

#### POST `/api/ai/analyze-news`
Analyze news article for sentiment.

**Tags:** `ai`
**Auth Required:** Yes

**Request Body:**
```json
{
  "text": "Apple announces record quarterly earnings, beating analyst expectations...",
  "symbol": "AAPL"
}
```

**Response (200):**
```json
{
  "sentiment": "positive",
  "sentiment_score": 0.85,
  "key_topics": ["earnings", "revenue", "growth"],
  "impact": "high",
  "summary": "Very positive news indicating strong company performance"
}
```

---

#### GET `/api/ml/patterns/{symbol}`
Detect chart patterns using ML.

**Tags:** `ml`
**Auth Required:** Yes

**Path Parameters:**
- `symbol` (required): Stock symbol

**Response (200):**
```json
{
  "symbol": "AAPL",
  "patterns": [
    {
      "pattern": "ascending_triangle",
      "confidence": 0.82,
      "timeframe": "daily",
      "bullish": true,
      "target_price": 160.00
    },
    {
      "pattern": "golden_cross",
      "confidence": 0.91,
      "timeframe": "daily",
      "bullish": true
    }
  ]
}
```

---

#### GET `/api/ml/regime`
Get current market regime detection.

**Tags:** `ml`
**Auth Required:** Yes

**Response (200):**
```json
{
  "regime": "trending_bullish",
  "confidence": 0.78,
  "volatility": "moderate",
  "trend_strength": 0.85,
  "recommended_strategy": "trend_following",
  "indicators": {
    "vix": 18.5,
    "adx": 35.2,
    "market_breadth": 0.65
  }
}
```

---

#### POST `/api/ml/sentiment/analyze`
Analyze market sentiment for symbols.

**Tags:** `ml-sentiment`
**Auth Required:** Yes

**Request Body:**
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"]
}
```

**Response (200):**
```json
{
  "sentiments": {
    "AAPL": {
      "score": 0.75,
      "label": "bullish",
      "sources": ["news", "social", "analyst_ratings"]
    },
    "MSFT": {
      "score": 0.60,
      "label": "neutral",
      "sources": ["news", "social"]
    }
  }
}
```

---

#### GET `/api/ml/predictions/{symbol}`
Get ML price predictions.

**Tags:** `ml`
**Auth Required:** Yes

**Path Parameters:**
- `symbol` (required): Stock symbol

**Query Parameters:**
- `horizon` (optional): Prediction horizon in days (default: 5, max: 30)

**Response (200):**
```json
{
  "symbol": "AAPL",
  "current_price": 155.25,
  "predictions": [
    {
      "date": "2025-10-28",
      "predicted_price": 156.50,
      "confidence_interval": {
        "lower": 154.00,
        "upper": 159.00
      }
    },
    {
      "date": "2025-10-29",
      "predicted_price": 157.25,
      "confidence_interval": {
        "lower": 153.50,
        "upper": 161.00
      }
    }
  ],
  "model": "lstm_ensemble",
  "accuracy_score": 0.72
}
```

---

### Strategy Endpoints

#### GET `/api/strategies`
Get all saved trading strategies.

**Tags:** `strategies`
**Auth Required:** Yes

**Response (200):**
```json
{
  "strategies": [
    {
      "id": 1,
      "name": "Momentum Breakout",
      "type": "technical",
      "active": true,
      "created_at": "2025-10-20T10:00:00Z",
      "performance": {
        "total_trades": 45,
        "win_rate": 0.62,
        "avg_return": 2.5
      }
    }
  ]
}
```

---

#### POST `/api/strategies`
Create a new trading strategy.

**Tags:** `strategies`
**Auth Required:** Yes
**CSRF Required:** Yes

**Request Body:**
```json
{
  "name": "Momentum Breakout",
  "type": "technical",
  "rules": [
    {
      "indicator": "rsi",
      "condition": "greater_than",
      "value": 60
    },
    {
      "indicator": "volume",
      "condition": "greater_than",
      "value": "avg_volume"
    }
  ],
  "entry_action": "buy",
  "exit_rules": [
    {
      "type": "profit_target",
      "value": 5.0
    },
    {
      "type": "stop_loss",
      "value": 2.0
    }
  ]
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Momentum Breakout",
  "created_at": "2025-10-27T14:30:00Z"
}
```

---

#### GET `/api/strategies/{strategy_id}`
Get specific strategy details.

**Tags:** `strategies`
**Auth Required:** Yes

**Path Parameters:**
- `strategy_id` (required): Strategy ID

**Response (200):**
```json
{
  "id": 1,
  "name": "Momentum Breakout",
  "type": "technical",
  "active": true,
  "rules": [...],
  "performance": {
    "total_trades": 45,
    "winning_trades": 28,
    "losing_trades": 17,
    "win_rate": 0.62,
    "avg_return": 2.5,
    "sharpe_ratio": 1.8,
    "max_drawdown": -8.5
  }
}
```

---

#### PUT `/api/strategies/{strategy_id}`
Update a strategy.

**Tags:** `strategies`
**Auth Required:** Yes
**CSRF Required:** Yes

**Path Parameters:**
- `strategy_id` (required): Strategy ID

**Request Body:**
```json
{
  "name": "Momentum Breakout v2",
  "active": true,
  "rules": [...]
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Momentum Breakout v2",
  "updated_at": "2025-10-27T14:30:00Z"
}
```

---

#### DELETE `/api/strategies/{strategy_id}`
Delete a strategy.

**Tags:** `strategies`
**Auth Required:** Yes
**CSRF Required:** Yes

**Path Parameters:**
- `strategy_id` (required): Strategy ID

**Response (200):**
```json
{
  "message": "Strategy deleted successfully"
}
```

---

### Backtesting Endpoints

#### POST `/api/backtesting/run`
Run backtest for a strategy.

**Tags:** `backtesting`
**Auth Required:** Yes

**Request Body:**
```json
{
  "strategy_id": 1,
  "symbols": ["AAPL", "MSFT"],
  "start_date": "2024-01-01",
  "end_date": "2025-10-27",
  "initial_capital": 100000
}
```

**Response (200):**
```json
{
  "backtest_id": "bt_123",
  "status": "completed",
  "results": {
    "total_return": 15.5,
    "sharpe_ratio": 1.8,
    "max_drawdown": -12.5,
    "total_trades": 85,
    "win_rate": 0.62,
    "avg_trade_return": 1.8,
    "final_equity": 115500
  },
  "trades": [...]
}
```

---

#### GET `/api/backtesting/{backtest_id}`
Get backtest results.

**Tags:** `backtesting`
**Auth Required:** Yes

**Path Parameters:**
- `backtest_id` (required): Backtest ID

**Response (200):**
```json
{
  "backtest_id": "bt_123",
  "strategy_id": 1,
  "start_date": "2024-01-01",
  "end_date": "2025-10-27",
  "results": {...},
  "equity_curve": [
    {
      "date": "2024-01-01",
      "equity": 100000
    },
    {
      "date": "2024-01-02",
      "equity": 101500
    }
  ]
}
```

---

#### GET `/api/backtesting/list`
List all backtests.

**Tags:** `backtesting`
**Auth Required:** Yes

**Response (200):**
```json
{
  "backtests": [
    {
      "backtest_id": "bt_123",
      "strategy_name": "Momentum Breakout",
      "created_at": "2025-10-27T14:30:00Z",
      "status": "completed",
      "total_return": 15.5
    }
  ]
}
```

---

### News & Sentiment Endpoints

#### GET `/api/news`
Get latest market news.

**Tags:** `news`
**Auth Required:** Yes

**Query Parameters:**
- `symbol` (optional): Filter by symbol
- `limit` (optional): Max results (default: 20, max: 100)

**Response (200):**
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Apple Announces Record Earnings",
      "summary": "Apple reported better than expected quarterly earnings...",
      "source": "Reuters",
      "url": "https://...",
      "published_at": "2025-10-27T14:00:00Z",
      "symbols": ["AAPL"],
      "sentiment": "positive",
      "sentiment_score": 0.85
    }
  ]
}
```

---

#### GET `/api/news/{article_id}`
Get specific news article.

**Tags:** `news`
**Auth Required:** Yes

**Path Parameters:**
- `article_id` (required): Article ID

**Response (200):**
```json
{
  "id": 1,
  "title": "Apple Announces Record Earnings",
  "content": "Full article content...",
  "summary": "Summary...",
  "source": "Reuters",
  "author": "John Doe",
  "published_at": "2025-10-27T14:00:00Z",
  "symbols": ["AAPL"],
  "sentiment": "positive",
  "sentiment_score": 0.85,
  "key_topics": ["earnings", "revenue", "growth"]
}
```

---

#### GET `/api/news/trending`
Get trending news topics.

**Tags:** `news`
**Auth Required:** Yes

**Response (200):**
```json
{
  "trending": [
    {
      "topic": "AI Technology",
      "article_count": 45,
      "sentiment": "positive",
      "top_symbols": ["NVDA", "MSFT", "GOOGL"]
    }
  ]
}
```

---

### Options Endpoints

#### GET `/api/options/chain/{symbol}`
Get options chain for a symbol.

**Tags:** `options`
**Auth Required:** Yes

**Path Parameters:**
- `symbol` (required): Stock symbol

**Query Parameters:**
- `expiration` (optional): Expiration date (YYYY-MM-DD)
- `strike_min` (optional): Minimum strike price
- `strike_max` (optional): Maximum strike price

**Response (200):**
```json
{
  "symbol": "AAPL",
  "underlying_price": 155.25,
  "expirations": ["2025-11-15", "2025-12-20"],
  "calls": [
    {
      "strike": 155.0,
      "expiration": "2025-11-15",
      "last": 5.25,
      "bid": 5.20,
      "ask": 5.30,
      "volume": 1234,
      "open_interest": 5678,
      "implied_volatility": 0.35,
      "delta": 0.52,
      "gamma": 0.05,
      "theta": -0.15,
      "vega": 0.25
    }
  ],
  "puts": [...]
}
```

---

#### POST `/api/options/greeks`
Calculate Greeks for an option.

**Tags:** `options`
**Auth Required:** Yes

**Request Body:**
```json
{
  "symbol": "AAPL",
  "strike": 155.0,
  "expiration": "2025-11-15",
  "option_type": "call",
  "underlying_price": 155.25,
  "interest_rate": 0.05
}
```

**Response (200):**
```json
{
  "delta": 0.52,
  "gamma": 0.05,
  "theta": -0.15,
  "vega": 0.25,
  "rho": 0.08,
  "implied_volatility": 0.35,
  "theoretical_value": 5.25
}
```

---

#### POST `/api/proposals`
Create options trade proposal.

**Tags:** `options`
**Auth Required:** Yes

**Request Body:**
```json
{
  "strategy_type": "vertical_spread",
  "symbol": "AAPL",
  "expiration": "2025-11-15",
  "legs": [
    {
      "option_type": "call",
      "strike": 155.0,
      "quantity": 1,
      "side": "buy"
    },
    {
      "option_type": "call",
      "strike": 160.0,
      "quantity": 1,
      "side": "sell"
    }
  ]
}
```

**Response (200):**
```json
{
  "proposal_id": "prop_123",
  "max_profit": 500.0,
  "max_loss": 500.0,
  "breakeven": 157.50,
  "net_debit": 250.0,
  "probability_of_profit": 0.65
}
```

---

#### GET `/api/options/strategies`
Get options strategy templates.

**Tags:** `options`
**Auth Required:** Yes

**Response (200):**
```json
{
  "strategies": [
    {
      "name": "Bull Call Spread",
      "description": "Limited risk bullish strategy",
      "legs": 2,
      "max_profit": "limited",
      "max_loss": "limited"
    },
    {
      "name": "Iron Condor",
      "description": "Neutral income strategy",
      "legs": 4,
      "max_profit": "limited",
      "max_loss": "limited"
    }
  ]
}
```

---

### User Management Endpoints

#### GET `/api/users/me`
Get current user profile.

**Tags:** `users`
**Auth Required:** Yes

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-10-01T10:00:00Z",
  "risk_tolerance": "moderate",
  "preferences": {
    "notifications": true,
    "newsletter": false
  }
}
```

---

#### PUT `/api/users/me`
Update current user profile.

**Tags:** `users`
**Auth Required:** Yes
**CSRF Required:** Yes

**Request Body:**
```json
{
  "full_name": "John A. Doe",
  "risk_tolerance": "aggressive",
  "preferences": {
    "notifications": false
  }
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John A. Doe",
  "updated_at": "2025-10-27T14:30:00Z"
}
```

---

#### DELETE `/api/users/me`
Delete current user account.

**Tags:** `users`
**Auth Required:** Yes
**CSRF Required:** Yes

**Response (200):**
```json
{
  "message": "Account deleted successfully"
}
```

---

### Streaming Endpoints

#### WebSocket `/api/stream/quotes`
Stream real-time quote updates.

**Tags:** `streaming`
**Auth Required:** Yes (via query param: `?token=<jwt>`)

**Subscribe Message:**
```json
{
  "action": "subscribe",
  "symbols": ["AAPL", "MSFT", "GOOGL"]
}
```

**Quote Update Message:**
```json
{
  "type": "quote",
  "symbol": "AAPL",
  "last": 155.25,
  "bid": 155.20,
  "ask": 155.30,
  "volume": 45234567,
  "timestamp": "2025-10-27T14:30:15Z"
}
```

**Unsubscribe Message:**
```json
{
  "action": "unsubscribe",
  "symbols": ["MSFT"]
}
```

---

#### WebSocket `/api/stream/trades`
Stream real-time trade updates.

**Tags:** `streaming`
**Auth Required:** Yes

**Trade Update Message:**
```json
{
  "type": "trade",
  "symbol": "AAPL",
  "price": 155.25,
  "size": 100,
  "timestamp": "2025-10-27T14:30:15.123Z"
}
```

---

#### WebSocket `/api/stream/orders`
Stream order status updates.

**Tags:** `streaming`
**Auth Required:** Yes

**Order Update Message:**
```json
{
  "type": "order_update",
  "order_id": "abc123",
  "status": "filled",
  "filled_quantity": 10,
  "avg_fill_price": 155.23,
  "timestamp": "2025-10-27T14:30:05Z"
}
```

---

#### GET `/api/stream/status`
Get WebSocket connection status.

**Tags:** `streaming`
**Auth Required:** Yes

**Response (200):**
```json
{
  "connected": true,
  "subscriptions": ["AAPL", "MSFT"],
  "uptime_seconds": 3600
}
```

---

### Settings Endpoints

#### GET `/api/settings`
Get user trading settings.

**Tags:** `settings`
**Auth Required:** Yes

**Response (200):**
```json
{
  "risk_tolerance": "moderate",
  "max_position_size": 10000,
  "max_loss_per_trade": 500,
  "default_order_type": "limit",
  "notifications_enabled": true
}
```

---

#### PUT `/api/settings`
Update trading settings.

**Tags:** `settings`
**Auth Required:** Yes
**CSRF Required:** Yes

**Request Body:**
```json
{
  "risk_tolerance": "aggressive",
  "max_position_size": 15000,
  "default_order_type": "market"
}
```

**Response (200):**
```json
{
  "message": "Settings updated successfully",
  "settings": {...}
}
```

---

#### GET `/api/settings/config`
Get platform configuration (public).

**Tags:** `settings`
**Auth Required:** No

**Response (200):**
```json
{
  "market_open": "09:30",
  "market_close": "16:00",
  "timezone": "America/New_York",
  "supported_order_types": ["market", "limit", "stop", "stop_limit"],
  "max_symbols_per_request": 50
}
```

---

### Analytics Endpoints

#### GET `/api/analytics/performance`
Get performance analytics.

**Tags:** `analytics`
**Auth Required:** Yes

**Query Parameters:**
- `period` (optional): `1d`, `1w`, `1m`, `3m`, `1y`, `ytd`, `all` (default: `1m`)

**Response (200):**
```json
{
  "period": "1m",
  "total_return": 8.5,
  "total_return_percent": 8.5,
  "sharpe_ratio": 1.8,
  "sortino_ratio": 2.1,
  "max_drawdown": -5.2,
  "volatility": 12.5,
  "win_rate": 0.62,
  "avg_win": 2.5,
  "avg_loss": -1.8,
  "profit_factor": 1.8
}
```

---

### Scheduler Endpoints

#### GET `/api/scheduler/jobs`
Get scheduled jobs status.

**Tags:** `scheduler`
**Auth Required:** Yes (admin only)

**Response (200):**
```json
{
  "jobs": [
    {
      "id": "market_data_refresh",
      "name": "Market Data Refresh",
      "trigger": "cron",
      "next_run": "2025-10-27T15:00:00Z",
      "last_run": "2025-10-27T14:00:00Z",
      "status": "running"
    }
  ]
}
```

---

#### POST `/api/scheduler/jobs/{job_id}/run`
Trigger job execution manually.

**Tags:** `scheduler`
**Auth Required:** Yes (admin only)
**CSRF Required:** Yes

**Path Parameters:**
- `job_id` (required): Job ID

**Response (200):**
```json
{
  "job_id": "market_data_refresh",
  "status": "triggered",
  "started_at": "2025-10-27T14:30:00Z"
}
```

---

### Telemetry Endpoints

#### POST `/api/telemetry/event`
Log a telemetry event.

**Tags:** `telemetry`
**Auth Required:** Yes

**Request Body:**
```json
{
  "event_type": "order_placed",
  "properties": {
    "symbol": "AAPL",
    "quantity": 10,
    "order_type": "market"
  }
}
```

**Response (200):**
```json
{
  "event_id": "evt_123",
  "recorded_at": "2025-10-27T14:30:00Z"
}
```

---

#### GET `/api/telemetry/events`
Get telemetry events.

**Tags:** `telemetry`
**Auth Required:** Yes

**Query Parameters:**
- `event_type` (optional): Filter by event type
- `limit` (optional): Max results (default: 50)

**Response (200):**
```json
{
  "events": [
    {
      "event_id": "evt_123",
      "event_type": "order_placed",
      "properties": {...},
      "timestamp": "2025-10-27T14:30:00Z"
    }
  ]
}
```

---

## OpenAPI Documentation

### Interactive Documentation

The API provides interactive documentation using Swagger UI and ReDoc:

**Swagger UI (Recommended):**
```
Production: https://paiid-backend.onrender.com/api/docs
Local: http://localhost:8001/api/docs
```

**ReDoc (Alternative):**
```
Production: https://paiid-backend.onrender.com/api/redoc
Local: http://localhost:8001/api/redoc
```

### OpenAPI Schema Export

Download the OpenAPI 3.0 schema in JSON format:

```bash
# Production
curl https://paiid-backend.onrender.com/api/openapi.json > paiid-openapi.json

# Local
curl http://localhost:8001/api/openapi.json > paiid-openapi.json
```

### Using OpenAPI Schema

The OpenAPI schema can be used to:
- Generate client SDKs in various languages
- Import into API testing tools (Postman, Insomnia)
- Generate API documentation
- Validate API requests/responses

**Generate Python Client:**
```bash
openapi-generator-cli generate \
  -i paiid-openapi.json \
  -g python \
  -o ./paiid-python-client
```

**Generate TypeScript Client:**
```bash
openapi-generator-cli generate \
  -i paiid-openapi.json \
  -g typescript-fetch \
  -o ./paiid-ts-client
```

---

## Postman Collection

### Generate from OpenAPI

**Method 1: Import from URL**
1. Open Postman
2. Click "Import"
3. Select "Link"
4. Enter: `https://paiid-backend.onrender.com/api/openapi.json`
5. Click "Import"

**Method 2: Import from File**
1. Download OpenAPI schema:
   ```bash
   curl https://paiid-backend.onrender.com/api/openapi.json > paiid-openapi.json
   ```
2. Open Postman
3. Click "Import"
4. Select "Upload Files"
5. Choose `paiid-openapi.json`
6. Click "Import"

### Environment Setup

Create a Postman environment with the following variables:

| Variable | Value (Production) | Value (Local) |
|----------|-------------------|---------------|
| `base_url` | `https://paiid-backend.onrender.com` | `http://localhost:8001` |
| `jwt_token` | (Obtained from login) | (Obtained from login) |
| `csrf_token` | (Obtained from /api/auth/csrf-token) | (Obtained from /api/auth/csrf-token) |

**Using Variables in Requests:**
```
URL: {{base_url}}/api/positions
Authorization: Bearer {{jwt_token}}
X-CSRF-Token: {{csrf_token}}
```

### Pre-request Script for Authentication

Add this to collection pre-request script to auto-refresh tokens:

```javascript
// Check if token is about to expire
const tokenExp = pm.environment.get("token_expiry");
const now = new Date().getTime();

if (!tokenExp || now >= tokenExp - 60000) {
    // Token expired or expiring soon, refresh it
    pm.sendRequest({
        url: pm.environment.get("base_url") + "/api/auth/refresh",
        method: "POST",
        header: {
            "Content-Type": "application/json"
        },
        body: {
            mode: "raw",
            raw: JSON.stringify({
                refresh_token: pm.environment.get("refresh_token")
            })
        }
    }, (err, res) => {
        if (!err && res.code === 200) {
            const data = res.json();
            pm.environment.set("jwt_token", data.access_token);
            pm.environment.set("token_expiry", now + (data.expires_in * 1000));
        }
    });
}
```

---

## Rate Limit Handling

### Exponential Backoff

When receiving `429` responses, implement exponential backoff:

```python
import time
import requests

def api_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            wait_time = retry_after * (2 ** attempt)  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue

        return response

    raise Exception("Max retries exceeded")
```

---

## Caching Strategy

The API implements intelligent caching to optimize performance:

### Cache TTL by Endpoint

| Endpoint Category | TTL | Cache-Control Header |
|------------------|-----|---------------------|
| Market quotes | 5 seconds | `max-age=5, stale-while-revalidate=10` |
| Historical bars | 1 hour | `max-age=3600, immutable` |
| Positions | 30 seconds | `max-age=30, must-revalidate` |
| News articles | 5 minutes | `max-age=300` |
| User profile | Until changed | `max-age=3600, must-revalidate` |

### Cache Invalidation

Caches are automatically invalidated when:
- User places an order (positions cache cleared)
- User updates settings (user cache cleared)
- Market data refreshes (quotes cache cleared)

**Force Fresh Data:**
```http
GET /api/positions
Cache-Control: no-cache
```

---

## Webhook Support

### Coming Soon

The following webhooks will be supported in future releases:
- Order fills
- Position changes
- Price alerts
- Strategy signals
- Account updates

---

## SDK Examples

### Python SDK

```python
from paiid import PaiiDClient

# Initialize client
client = PaiiDClient(
    base_url="https://paiid-backend.onrender.com",
    api_token="your-jwt-token"
)

# Get positions
positions = client.positions.list()
for position in positions:
    print(f"{position.symbol}: {position.quantity} @ {position.avg_entry_price}")

# Place order
order = client.orders.create(
    symbol="AAPL",
    quantity=10,
    side="buy",
    type="limit",
    limit_price=150.00
)
print(f"Order placed: {order.order_id}")

# Get AI recommendations
recommendations = client.ai.get_recommendations()
for rec in recommendations:
    print(f"{rec.symbol}: {rec.action} (confidence: {rec.confidence})")
```

### TypeScript SDK

```typescript
import { PaiiDClient } from '@paiid/sdk';

// Initialize client
const client = new PaiiDClient({
  baseUrl: 'https://paiid-backend.onrender.com',
  apiToken: 'your-jwt-token'
});

// Get positions
const positions = await client.positions.list();
positions.forEach(position => {
  console.log(`${position.symbol}: ${position.quantity} @ ${position.avgEntryPrice}`);
});

// Place order
const order = await client.orders.create({
  symbol: 'AAPL',
  quantity: 10,
  side: 'buy',
  type: 'limit',
  limitPrice: 150.00
});
console.log(`Order placed: ${order.orderId}`);

// Get AI recommendations
const recommendations = await client.ai.getRecommendations();
recommendations.forEach(rec => {
  console.log(`${rec.symbol}: ${rec.action} (confidence: ${rec.confidence})`);
});
```

---

## Support

For API support:
- **Documentation Issues:** Create issue on GitHub
- **API Questions:** Email support@paiid.com
- **Bug Reports:** Use GitHub Issues with `bug` label
- **Feature Requests:** Use GitHub Issues with `enhancement` label

---

**Document Version:** 1.0.0
**Last Updated:** October 27, 2025
**Total Endpoints:** 137 across 26 routers
**Maintained By:** PaiiD Development Team
