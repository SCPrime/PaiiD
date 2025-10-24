# 🤖 PaiiD ML API Documentation

**Phase 2: Sentiment Analysis & Trade Signals**  
**Version**: 1.0.0  
**Last Updated**: October 24, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Request/Response Models](#requestresponse-models)
5. [Examples](#examples)
6. [Rate Limits](#rate-limits)
7. [Error Handling](#error-handling)

---

## 🎯 Overview

The PaiiD ML API provides AI-powered trading insights through:

- **Sentiment Analysis**: Analyze market news using Anthropic Claude
- **Trade Signals**: Generate BUY/SELL/HOLD signals combining technical + sentiment
- **Batch Processing**: Analyze multiple symbols simultaneously

### Key Features

✅ **Real-time Sentiment**: Analyze recent news and market sentiment  
✅ **Technical Analysis**: RSI, MACD, Bollinger Bands, Moving Averages  
✅ **AI Integration**: Powered by Anthropic Claude 3.5 Sonnet  
✅ **Risk Management**: Automatic target prices and stop losses  
✅ **Confidence Scoring**: Know how reliable each signal is

---

## 🔐 Authentication

All ML endpoints require JWT authentication.

### Headers

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

### Getting a Token

```bash
# Login to get JWT token
curl -X POST https://paiid-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "your_password"}'
```

---

## 🔗 Endpoints

### Base URL

```
https://paiid-backend.onrender.com/api/ml
```

---

### 1. Get Sentiment Analysis

**Endpoint**: `GET /ml/sentiment/{symbol}`

Analyzes recent news sentiment for a stock using AI.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | path | ✅ Yes | - | Stock symbol (e.g., AAPL, TSLA) |
| `include_news` | query | No | true | Include news analysis |
| `lookback_days` | query | No | 7 | Days of news to analyze (1-30) |

#### Response

```json
{
  "symbol": "AAPL",
  "sentiment": "bullish",
  "score": 0.65,
  "confidence": 0.82,
  "reasoning": "Strong positive earnings report exceeded expectations. Multiple analyst upgrades. Product launch momentum building.",
  "timestamp": "2025-10-24T20:15:30.123456Z",
  "source": "news"
}
```

#### Sentiment Values

- **bullish**: Positive market sentiment (score > 0.2)
- **bearish**: Negative market sentiment (score < -0.2)
- **neutral**: Mixed or no clear sentiment (-0.2 to 0.2)

#### Score Range

- `1.0`: Very bullish
- `0.0`: Neutral
- `-1.0`: Very bearish

---

### 2. Get Trade Signal

**Endpoint**: `GET /ml/signals/{symbol}`

Generates an AI-powered trade signal combining technical analysis and sentiment.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | path | ✅ Yes | - | Stock symbol (e.g., AAPL, TSLA) |
| `include_sentiment` | query | No | true | Include sentiment analysis |
| `lookback_days` | query | No | 30 | Days of price history (7-90) |

#### Response

```json
{
  "symbol": "AAPL",
  "signal": "BUY",
  "strength": "STRONG",
  "confidence": 0.78,
  "price": 175.50,
  "target_price": 184.28,
  "stop_loss": 171.99,
  "reasoning": "BUY signal with technical score 0.72 and sentiment score 0.65. Technical: MACD bullish crossover, RSI oversold. Sentiment: Strong positive earnings report exceeded expectations. Multiple analyst upgrades. Product launch momentum building.",
  "technical_score": 0.72,
  "sentiment_score": 0.65,
  "combined_score": 0.70,
  "timestamp": "2025-10-24T20:15:30.123456Z"
}
```

#### Signal Types

- **BUY**: Combined score > 0.3
- **SELL**: Combined score < -0.3
- **HOLD**: Combined score between -0.3 and 0.3

#### Strength Levels

- **STRONG**: |score| > 0.7
- **MODERATE**: |score| > 0.4
- **WEAK**: |score| ≤ 0.4

---

### 3. Get Batch Signals

**Endpoint**: `POST /ml/signals/batch`

Generate trade signals for multiple symbols (max 10).

#### Request Body

```json
{
  "symbols": ["AAPL", "TSLA", "MSFT"],
  "include_sentiment": true,
  "lookback_days": 30
}
```

#### Response

```json
[
  {
    "symbol": "AAPL",
    "signal": "BUY",
    "strength": "STRONG",
    "confidence": 0.78,
    "price": 175.50,
    "target_price": 184.28,
    "stop_loss": 171.99,
    "reasoning": "...",
    "technical_score": 0.72,
    "sentiment_score": 0.65,
    "combined_score": 0.70,
    "timestamp": "2025-10-24T20:15:30.123456Z"
  },
  {
    "symbol": "TSLA",
    "signal": "HOLD",
    "strength": "WEAK",
    "confidence": 0.45,
    "price": 242.80,
    "target_price": null,
    "stop_loss": null,
    "reasoning": "...",
    "technical_score": 0.15,
    "sentiment_score": 0.10,
    "combined_score": 0.13,
    "timestamp": "2025-10-24T20:15:31.456789Z"
  }
]
```

---

### 4. ML Health Check

**Endpoint**: `GET /ml/health`

Check ML service status (no authentication required).

#### Response

```json
{
  "status": "healthy",
  "services": {
    "sentiment_analyzer": "ready",
    "signal_generator": "ready",
    "anthropic_configured": true
  },
  "timestamp": "2025-10-24T20:15:30.123456Z"
}
```

---

## 📊 Request/Response Models

### SentimentResponse

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Stock symbol |
| `sentiment` | string | "bullish", "bearish", or "neutral" |
| `score` | float | Sentiment score (-1.0 to 1.0) |
| `confidence` | float | Confidence level (0.0 to 1.0) |
| `reasoning` | string | AI-generated explanation |
| `timestamp` | datetime | Analysis timestamp |
| `source` | string | Data source ("news", "social", "combined") |

### SignalResponse

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Stock symbol |
| `signal` | string | "BUY", "SELL", or "HOLD" |
| `strength` | string | "STRONG", "MODERATE", or "WEAK" |
| `confidence` | float | Signal confidence (0.0 to 1.0) |
| `price` | float | Current price |
| `target_price` | float \| null | Recommended target price |
| `stop_loss` | float \| null | Recommended stop loss |
| `reasoning` | string | Detailed explanation |
| `technical_score` | float | Technical analysis score (-1.0 to 1.0) |
| `sentiment_score` | float | Sentiment score (-1.0 to 1.0) |
| `combined_score` | float | Weighted combination (-1.0 to 1.0) |
| `timestamp` | datetime | Signal generation timestamp |

---

## 💡 Examples

### Example 1: Get Sentiment for AAPL

```bash
curl -X GET "https://paiid-backend.onrender.com/api/ml/sentiment/AAPL?include_news=true&lookback_days=7" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example 2: Get Trade Signal for TSLA

```bash
curl -X GET "https://paiid-backend.onrender.com/api/ml/signals/TSLA?include_sentiment=true&lookback_days=30" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example 3: Batch Analysis

```bash
curl -X POST "https://paiid-backend.onrender.com/api/ml/signals/batch" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "TSLA", "MSFT", "GOOGL"],
    "include_sentiment": true,
    "lookback_days": 30
  }'
```

### Example 4: Python Integration

```python
import requests

BASE_URL = "https://paiid-backend.onrender.com/api/ml"
TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# Get sentiment
response = requests.get(
    f"{BASE_URL}/sentiment/AAPL",
    headers=headers,
    params={"include_news": True, "lookback_days": 7}
)
sentiment = response.json()
print(f"AAPL Sentiment: {sentiment['sentiment']} ({sentiment['score']:.2f})")

# Get trade signal
response = requests.get(
    f"{BASE_URL}/signals/AAPL",
    headers=headers,
    params={"include_sentiment": True, "lookback_days": 30}
)
signal = response.json()
print(f"AAPL Signal: {signal['signal']} ({signal['strength']})")
print(f"Confidence: {signal['confidence']:.2%}")
print(f"Target: ${signal['target_price']}, Stop Loss: ${signal['stop_loss']}")
```

---

## 🚦 Rate Limits

- **Sentiment Analysis**: 60 requests/minute per user
- **Trade Signals**: 60 requests/minute per user
- **Batch Signals**: 10 requests/minute, max 10 symbols per request

---

## ❌ Error Handling

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

### Common Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 401 | Unauthorized | Missing or invalid JWT token |
| 404 | Not Found | No data available for symbol |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | ML service error |

### Error Examples

**401 Unauthorized**
```json
{
  "detail": "Could not validate credentials"
}
```

**404 Not Found**
```json
{
  "detail": "No price data available for INVALID"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Sentiment analysis failed: API connection error"
}
```

---

## 🎯 Best Practices

### 1. Caching
- Sentiment scores are valid for ~15-30 minutes
- Cache results to avoid redundant API calls
- Use batch endpoints for multiple symbols

### 2. Signal Interpretation
- **Strong signals** with high confidence (>0.7) are most reliable
- Always use stop losses provided by the API
- Consider both technical and sentiment scores
- Don't trade on WEAK signals unless confirmed elsewhere

### 3. Risk Management
- Never risk more than 1-2% of portfolio on a single signal
- Use provided stop losses
- Wait for pullbacks on STRONG BUY signals
- Consider market conditions and overall portfolio balance

### 4. Performance
- Batch requests are more efficient than individual calls
- Sentiment analysis takes 2-5 seconds per symbol
- Signal generation takes 1-3 seconds per symbol
- Use health endpoint to verify service availability

---

## 🔧 Technical Details

### Score Weights

**Default Configuration**:
- Technical Analysis: 70%
- Sentiment Analysis: 30%

### Technical Indicators Used

- **RSI (14)**: Relative Strength Index
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Volatility bands
- **SMA (20, 50)**: Simple Moving Averages
- **Volume Ratio**: Current vs average volume

### AI Model

- **Provider**: Anthropic
- **Model**: Claude 3.5 Sonnet (2024-10-22)
- **Max Tokens**: 1024 (sentiment), 2048 (batch)

---

## 📞 Support

**Issues**: https://github.com/SCPrime/PaiiD/issues  
**API Docs**: https://paiid-backend.onrender.com/docs  
**Health Check**: https://paiid-backend.onrender.com/api/health

---

## 🎓 Changelog

### v1.0.0 (2025-10-24)
- ✅ Initial release
- ✅ Sentiment analysis with Anthropic Claude
- ✅ Trade signal generation
- ✅ Batch processing support
- ✅ JWT authentication
- ✅ Comprehensive documentation

---

**Built with ❤️ by Dr. SC Prime & Team**  
**Powered by Anthropic Claude & FastAPI**

