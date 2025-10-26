# PaiiD API Documentation

## Overview

The PaiiD API is a comprehensive financial trading platform that provides real-time market data, sentiment analysis, portfolio management, and automated trading capabilities. Built with FastAPI, it offers high-performance, scalable endpoints with comprehensive authentication and monitoring.

## Base URL

```
Production: https://api.paiid.com
Development: http://localhost:8000
```

## Authentication

The API supports multiple authentication methods:

### 1. JWT Authentication (Recommended)
```http
Authorization: Bearer <jwt_token>
```

### 2. API Token Authentication
```http
Authorization: Bearer <api_token>
```

### 3. Single User MVP Mode
No authentication required for development/testing.

## Rate Limiting

- **Standard Endpoints**: 100 requests per hour
- **ML Endpoints**: 50 requests per hour
- **Market Data**: 200 requests per hour
- **Portfolio Management**: 60 requests per hour

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "data": { ... },
  "message": "Success",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "error": "ERROR_CODE",
  "message": "Human readable error message",
  "details": "Additional error details",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## API Endpoints

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "name": "John Doe",
  "risk_tolerance": "moderate"
}
```

**Response:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "access_token": "jwt_token",
  "refresh_token": "refresh_token"
}
```

#### Login User
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "risk_tolerance": "moderate"
  }
}
```

#### Refresh Token
```http
POST /api/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "refresh_token"
}
```

#### Logout
```http
POST /api/auth/logout
```

**Headers:**
```
Authorization: Bearer <jwt_token>
```

#### Get Session
```http
GET /api/auth/session
```

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "authenticated": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "risk_tolerance": "moderate"
  }
}
```

### Market Data Endpoints

#### Get Stock Quote
```http
GET /api/market-data/quote/{symbol}
```

**Parameters:**
- `symbol` (path): Stock symbol (e.g., AAPL, MSFT)

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 185.50,
  "change": 2.15,
  "change_percent": 1.17,
  "volume": 45000000,
  "market_cap": 2900000000000,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Get Historical Data
```http
GET /api/market-data/historical/{symbol}
```

**Query Parameters:**
- `period`: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
- `interval`: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

**Response:**
```json
{
  "symbol": "AAPL",
  "period": "1mo",
  "interval": "1d",
  "data": [
    {
      "timestamp": "2024-01-15T00:00:00Z",
      "open": 183.50,
      "high": 186.20,
      "low": 182.80,
      "close": 185.50,
      "volume": 45000000
    }
  ]
}
```

#### Get Market Status
```http
GET /api/market-data/status
```

**Response:**
```json
{
  "market_status": "open",
  "next_open": "2024-01-16T09:30:00Z",
  "next_close": "2024-01-15T16:00:00Z",
  "timezone": "America/New_York"
}
```

### ML Sentiment Endpoints

#### Get Sentiment Analysis
```http
GET /api/sentiment/{symbol}
```

**Query Parameters:**
- `include_news` (boolean): Include news analysis (default: true)
- `lookback_days` (integer): Days of news to analyze (1-30, default: 7)

**Response:**
```json
{
  "symbol": "AAPL",
  "sentiment_score": 0.75,
  "sentiment_label": "positive",
  "confidence": 0.85,
  "news_count": 15,
  "analysis_timestamp": "2024-01-15T10:30:00Z",
  "cached": false,
  "news_summary": "Recent news shows strong earnings growth...",
  "technical_indicators": {
    "rsi": 65.2,
    "macd": 0.15,
    "bollinger_position": "upper"
  }
}
```

#### Get Trade Signals
```http
GET /api/sentiment/{symbol}/signals
```

**Query Parameters:**
- `signal_type` (string): Filter by signal type (buy, sell, hold)
- `confidence_threshold` (float): Minimum confidence level (0.0-1.0, default: 0.7)

**Response:**
```json
{
  "symbol": "AAPL",
  "signals": [
    {
      "signal_type": "buy",
      "confidence": 0.82,
      "reasoning": "Strong positive sentiment combined with bullish technical indicators",
      "timestamp": "2024-01-15T10:30:00Z",
      "price_target": 185.50,
      "stop_loss": 175.00
    }
  ],
  "overall_sentiment": "positive",
  "market_regime": "bullish"
}
```

### Portfolio Management Endpoints

#### Get Portfolio
```http
GET /api/portfolio
```

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "total_value": 100000.00,
  "total_cost": 95000.00,
  "total_gain_loss": 5000.00,
  "total_gain_loss_percent": 5.26,
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 100,
      "current_price": 185.50,
      "cost_basis": 180.00,
      "market_value": 18550.00,
      "gain_loss": 550.00,
      "gain_loss_percent": 3.06
    }
  ]
}
```

#### Get Portfolio Performance
```http
GET /api/portfolio/performance
```

**Query Parameters:**
- `period`: 1d, 1w, 1m, 3m, 6m, 1y, all

**Response:**
```json
{
  "period": "1m",
  "total_return": 5.26,
  "benchmark_return": 3.15,
  "alpha": 2.11,
  "beta": 1.05,
  "sharpe_ratio": 1.85,
  "max_drawdown": -2.15,
  "volatility": 12.5
}
```

### Order Management Endpoints

#### Place Order
```http
POST /api/orders
```

**Request Body:**
```json
{
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 100,
  "order_type": "market",
  "time_in_force": "day"
}
```

**Response:**
```json
{
  "order_id": "uuid",
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 100,
  "order_type": "market",
  "status": "pending",
  "submitted_at": "2024-01-15T10:30:00Z"
}
```

#### Get Orders
```http
GET /api/orders
```

**Query Parameters:**
- `status`: pending, filled, cancelled, rejected
- `symbol`: Filter by symbol
- `limit`: Number of orders to return (default: 50)

**Response:**
```json
{
  "orders": [
    {
      "order_id": "uuid",
      "symbol": "AAPL",
      "side": "buy",
      "quantity": 100,
      "filled_quantity": 100,
      "order_type": "market",
      "status": "filled",
      "filled_price": 185.50,
      "submitted_at": "2024-01-15T10:30:00Z",
      "filled_at": "2024-01-15T10:30:15Z"
    }
  ],
  "total": 1
}
```

#### Cancel Order
```http
DELETE /api/orders/{order_id}
```

**Response:**
```json
{
  "order_id": "uuid",
  "status": "cancelled",
  "cancelled_at": "2024-01-15T10:35:00Z"
}
```

### News Endpoints

#### Get News
```http
GET /api/news
```

**Query Parameters:**
- `symbol`: Filter by symbol
- `limit`: Number of articles (default: 20)
- `category`: general, earnings, analyst, merger

**Response:**
```json
{
  "articles": [
    {
      "id": "uuid",
      "title": "Apple Reports Strong Q4 Earnings",
      "summary": "Apple Inc. reported better-than-expected earnings...",
      "url": "https://example.com/article",
      "source": "Reuters",
      "published_at": "2024-01-15T09:00:00Z",
      "sentiment": "positive",
      "symbols": ["AAPL"]
    }
  ],
  "total": 1
}
```

### Analytics Endpoints

#### Get Market Analytics
```http
GET /api/analytics/market
```

**Query Parameters:**
- `symbol`: Stock symbol
- `period`: Analysis period

**Response:**
```json
{
  "symbol": "AAPL",
  "technical_analysis": {
    "trend": "bullish",
    "support_levels": [180.00, 175.00],
    "resistance_levels": [190.00, 195.00],
    "moving_averages": {
      "sma_20": 182.50,
      "sma_50": 178.75,
      "ema_12": 184.25
    }
  },
  "fundamental_analysis": {
    "pe_ratio": 28.5,
    "pb_ratio": 5.2,
    "dividend_yield": 0.45,
    "market_cap": 2900000000000
  }
}
```

### Monitoring Endpoints

#### Health Check
```http
GET /api/monitor/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime": "2d 5h 30m",
  "version": "1.0.0"
}
```

#### System Metrics
```http
GET /api/monitor/metrics/system
```

**Response:**
```json
{
  "cpu_usage_percent": 45.2,
  "memory_usage_percent": 62.8,
  "disk_usage_percent": 35.5,
  "active_connections": 150,
  "requests_per_minute": 45.5,
  "average_response_time_ms": 125.0
}
```

#### ML Model Health
```http
GET /api/monitor/metrics/ml-models
```

**Response:**
```json
{
  "models": [
    {
      "model_name": "sentiment_analyzer",
      "status": "healthy",
      "accuracy": 0.85,
      "last_training": "2024-01-08T00:00:00Z",
      "inference_time_ms": 50.0,
      "memory_usage_mb": 512.0
    }
  ]
}
```

#### Monitoring Dashboard
```http
GET /api/monitor/dashboard
```

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "system_health": { ... },
  "services": [ ... ],
  "system_metrics": { ... },
  "ml_models": [ ... ],
  "cache_metrics": [ ... ],
  "alerts": [ ... ],
  "performance_trends": { ... }
}
```

## Error Codes

### Authentication Errors
- `AUTHENTICATION_FAILED`: Invalid credentials
- `TOKEN_EXPIRED`: JWT token has expired
- `TOKEN_INVALID`: Invalid token format
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions

### Validation Errors
- `INVALID_INPUT`: Request body validation failed
- `MISSING_REQUIRED_FIELD`: Required field is missing
- `INVALID_FORMAT`: Field format is invalid
- `VALUE_OUT_OF_RANGE`: Value exceeds allowed range

### Business Logic Errors
- `INSUFFICIENT_FUNDS`: Not enough funds for order
- `INVALID_SYMBOL`: Stock symbol not found
- `MARKET_CLOSED`: Market is currently closed
- `ORDER_NOT_FOUND`: Order ID not found

### System Errors
- `INTERNAL_SERVER_ERROR`: Unexpected server error
- `SERVICE_UNAVAILABLE`: External service unavailable
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `DATABASE_ERROR`: Database operation failed

## SDKs and Libraries

### Python SDK
```python
from paiid_sdk import PaiiDClient

client = PaiiDClient(api_key="your_api_key")

# Get market data
quote = client.market_data.get_quote("AAPL")

# Get sentiment analysis
sentiment = client.sentiment.get_analysis("AAPL")

# Place order
order = client.orders.place_order(
    symbol="AAPL",
    side="buy",
    quantity=100,
    order_type="market"
)
```

### JavaScript SDK
```javascript
import { PaiiDClient } from 'paiid-sdk';

const client = new PaiiDClient('your_api_key');

// Get market data
const quote = await client.marketData.getQuote('AAPL');

// Get sentiment analysis
const sentiment = await client.sentiment.getAnalysis('AAPL');

// Place order
const order = await client.orders.placeOrder({
  symbol: 'AAPL',
  side: 'buy',
  quantity: 100,
  orderType: 'market'
});
```

## Webhooks

### Order Updates
```http
POST /webhooks/orders
```

**Headers:**
```
X-PaiiD-Signature: sha256=...
```

**Payload:**
```json
{
  "event": "order.filled",
  "order_id": "uuid",
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 100,
  "filled_price": 185.50,
  "timestamp": "2024-01-15T10:30:15Z"
}
```

### Market Data Updates
```http
POST /webhooks/market-data
```

**Payload:**
```json
{
  "event": "price.update",
  "symbol": "AAPL",
  "price": 185.50,
  "change": 2.15,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Testing

### Postman Collection
Download the complete Postman collection: [PaiiD API Collection](https://api.paiid.com/docs/postman)

### API Testing Tool
```bash
# Install the testing tool
pip install paiid-api-test

# Run tests
paiid-api-test --api-key your_key --environment production
```

## Support

- **Documentation**: https://docs.paiid.com
- **API Status**: https://status.paiid.com
- **Support Email**: api-support@paiid.com
- **GitHub Issues**: https://github.com/paiid/api-issues

---

*Last Updated: January 15, 2024*
*Version: 1.0.0*
