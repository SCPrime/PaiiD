# PaiiD API Quick Reference
**Version:** 1.0.0
**Base URL (Production):** `https://paiid-backend.onrender.com`
**Base URL (Development):** `http://127.0.0.1:8001`

---

## Authentication

PaiiD supports **two authentication methods**:

### 1. API Token Authentication (Recommended for development)
```bash
curl -H "Authorization: Bearer rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl" \
  https://paiid-backend.onrender.com/api/health
```

### 2. JWT Token Authentication (Production)
```bash
# Step 1: Login to get JWT token
curl -X POST https://paiid-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "yourpassword"}'

# Response:
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}

# Step 2: Use JWT token for authenticated requests
curl -H "Authorization: Bearer eyJhbGci..." \
  https://paiid-backend.onrender.com/api/account
```

---

## Essential Endpoints

### Health & Status

#### GET `/api/health`
Basic health check (no auth required).

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-27T21:00:00Z"
}
```

#### GET `/api/health/detailed`
Detailed health check with dependency status (auth required).

**Response:**
```json
{
  "status": "healthy",
  "uptime_seconds": 123456,
  "dependencies": {
    "database": {"status": "healthy", "latency_ms": 12},
    "redis": {"status": "healthy", "latency_ms": 5},
    "tradier_api": {"status": "healthy", "latency_ms": 145},
    "alpaca_api": {"status": "healthy", "latency_ms": 89}
  }
}
```

---

### Trading & Portfolio

#### GET `/api/account`
Get Alpaca paper trading account details.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "account_number": "PA...",
  "status": "ACTIVE",
  "cash": "100000.00",
  "portfolio_value": "105432.50",
  "buying_power": "200000.00",
  "pattern_day_trader": false
}
```

#### GET `/api/positions`
Get current paper trading positions.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "positions": [
    {
      "symbol": "AAPL",
      "qty": "10",
      "avg_entry_price": "180.50",
      "current_price": "185.20",
      "market_value": "1852.00",
      "unrealized_pl": "47.00",
      "unrealized_plpc": "0.026"
    }
  ]
}
```

#### POST `/api/orders`
Place a new paper trade order.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "symbol": "AAPL",
  "qty": 10,
  "side": "buy",
  "type": "market",
  "time_in_force": "day"
}
```

**Response:**
```json
{
  "id": "order_123",
  "symbol": "AAPL",
  "qty": "10",
  "side": "buy",
  "type": "market",
  "status": "accepted",
  "submitted_at": "2025-10-27T21:00:00Z"
}
```

---

### Market Data

#### GET `/api/market/quote`
Get real-time quote for a symbol (Tradier API).

**Query Parameters:**
- `symbol` (required): Stock symbol (e.g., AAPL)

**Example:**
```bash
curl "https://paiid-backend.onrender.com/api/market/quote?symbol=AAPL" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "symbol": "AAPL",
  "last": "185.20",
  "bid": "185.18",
  "ask": "185.22",
  "volume": "45123456",
  "open": "183.50",
  "high": "186.00",
  "low": "182.80",
  "close": "184.90",
  "change": "0.30",
  "change_percentage": "0.16"
}
```

#### GET `/api/market/bars`
Get historical OHLCV bars (Tradier API).

**Query Parameters:**
- `symbol` (required): Stock symbol
- `interval` (optional): 1min, 5min, 15min, 1day (default: 1day)
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD

**Example:**
```bash
curl "https://paiid-backend.onrender.com/api/market/bars?symbol=AAPL&interval=1day&start_date=2025-01-01" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "symbol": "AAPL",
  "interval": "1day",
  "bars": [
    {
      "time": "2025-01-02T00:00:00Z",
      "open": "180.00",
      "high": "182.50",
      "low": "179.50",
      "close": "181.80",
      "volume": "50000000"
    }
  ]
}
```

#### GET `/api/market/options/chain`
Get options chain for a symbol (Tradier API).

**Query Parameters:**
- `symbol` (required): Stock symbol
- `expiration` (optional): YYYY-MM-DD

**Response:**
```json
{
  "symbol": "AAPL",
  "options": [
    {
      "symbol": "AAPL250131C00180000",
      "type": "call",
      "strike": "180.00",
      "expiration_date": "2025-01-31",
      "bid": "5.20",
      "ask": "5.30",
      "last": "5.25",
      "volume": "1523",
      "open_interest": "8942",
      "greeks": {
        "delta": "0.55",
        "gamma": "0.02",
        "theta": "-0.05",
        "vega": "0.15"
      }
    }
  ]
}
```

---

### AI & Machine Learning

#### POST `/api/ai/recommendations`
Get AI-powered trade recommendations based on market data.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "symbols": ["AAPL", "GOOGL", "MSFT"],
  "risk_tolerance": "moderate",
  "time_horizon": "medium"
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "symbol": "AAPL",
      "action": "buy",
      "confidence": 0.78,
      "rationale": "Strong technical indicators and positive earnings outlook",
      "suggested_entry": "184.50",
      "target_price": "195.00",
      "stop_loss": "180.00"
    }
  ],
  "generated_at": "2025-10-27T21:00:00Z"
}
```

#### GET `/api/ml/market-regime`
Detect current market regime (trending, volatile, ranging).

**Response:**
```json
{
  "regime": "trending_bullish",
  "confidence": 0.85,
  "indicators": {
    "volatility": "low",
    "trend_strength": "strong",
    "market_breadth": "positive"
  }
}
```

---

### Strategies

#### GET `/api/strategies`
List all custom trading strategies.

**Response:**
```json
{
  "strategies": [
    {
      "id": "strategy_123",
      "name": "SMA Crossover",
      "description": "50/200 simple moving average crossover",
      "created_at": "2025-10-01T12:00:00Z",
      "status": "active"
    }
  ]
}
```

#### POST `/api/strategies`
Create a new trading strategy.

**Request Body:**
```json
{
  "name": "RSI Oversold",
  "description": "Buy when RSI < 30, sell when RSI > 70",
  "config": {
    "entry_rules": [
      {"indicator": "RSI", "value": 30, "operator": "<"}
    ],
    "exit_rules": [
      {"indicator": "RSI", "value": 70, "operator": ">"}
    ],
    "position_sizing": {
      "method": "fixed_percentage",
      "percentage": 5
    }
  }
}
```

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 422 | Unprocessable Entity | Validation error |
| 423 | Locked | Kill switch active, mutations disabled |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily down |

---

## Rate Limiting

**Default Limits:**
- 100 requests per minute per IP
- 1000 requests per hour per IP

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1698441600
```

**When Rate Limited:**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

---

## Swagger/OpenAPI Documentation

**Full API documentation available at:**
- **Production:** https://paiid-backend.onrender.com/docs
- **Development:** http://127.0.0.1:8001/docs

Interactive Swagger UI allows:
- Browsing all endpoints
- Testing requests directly
- Viewing request/response schemas
- Downloading OpenAPI JSON spec

---

## Common Patterns

### Error Handling
```python
import requests

response = requests.get(
    "https://paiid-backend.onrender.com/api/account",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 200:
    data = response.json()
    print(f"Account balance: ${data['cash']}")
elif response.status_code == 401:
    print("Authentication failed - check your token")
elif response.status_code == 429:
    retry_after = response.headers.get('Retry-After', 60)
    print(f"Rate limited - retry after {retry_after}s")
else:
    print(f"Error {response.status_code}: {response.text}")
```

### Pagination
```bash
# Not all endpoints support pagination yet
# Use limit/offset or cursor-based pagination where available

curl "https://paiid-backend.onrender.com/api/news?limit=10&offset=0"
```

### WebSocket Connections
```javascript
// Real-time market data via WebSocket
const ws = new WebSocket("wss://paiid-backend.onrender.com/ws/market");

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: "subscribe",
    symbols: ["AAPL", "GOOGL"]
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Quote update:", data);
};
```

---

## Support & Resources

- **Full Documentation:** See `/docs` directory in repository
- **OpenAPI Spec:** https://paiid-backend.onrender.com/docs
- **Issues:** https://github.com/SCPrime/PaiiD/issues
- **Developer Guide:** See `docs/DEVELOPER_ONBOARDING.md`

**Last Updated:** 2025-10-27
