# ML Sentiment Router Guide

## Overview

The ML Sentiment Router (`/api/sentiment`) provides AI-powered sentiment analysis and trade signal generation for financial markets. This system combines news sentiment analysis with technical indicators to generate actionable trading signals.

## Features

- **Real-time Sentiment Analysis**: Analyzes news sentiment for any stock symbol
- **Trade Signal Generation**: Generates buy/sell/hold signals based on sentiment and technical analysis
- **Redis Caching**: Optimizes performance with intelligent caching
- **Unified Authentication**: Supports both API token and JWT-based authentication
- **Configurable Parameters**: Customizable lookback periods and analysis depth

## API Endpoints

### 1. Get Sentiment Analysis

```http
GET /api/sentiment/{symbol}?include_news=true&lookback_days=7
```

**Parameters:**
- `symbol` (path): Stock symbol (e.g., AAPL, MSFT, TSLA)
- `include_news` (query): Include news analysis (default: true)
- `lookback_days` (query): Days of news to analyze (1-30, default: 7)

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

### 2. Get Trade Signals

```http
GET /api/sentiment/{symbol}/signals?signal_type=buy&confidence_threshold=0.7
```

**Parameters:**
- `symbol` (path): Stock symbol
- `signal_type` (query): Signal type filter (buy/sell/hold, optional)
- `confidence_threshold` (query): Minimum confidence level (0.0-1.0, default: 0.7)

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

## Authentication

The ML Sentiment Router supports unified authentication:

### API Token Authentication
```http
Authorization: Bearer your_api_token_here
```

### JWT Authentication
```http
Authorization: Bearer your_jwt_token_here
```

### Single User MVP Mode
No authentication required for development/testing.

## Caching Strategy

The system uses Redis for intelligent caching:

- **Sentiment Cache**: 15-minute TTL for sentiment analysis
- **Signal Cache**: 5-minute TTL for trade signals
- **News Cache**: 30-minute TTL for news data
- **Cache Keys**: `sentiment:{symbol}`, `signals:{symbol}`, `news:{symbol}`

## Performance Optimization

- **Parallel Processing**: News analysis and technical indicators processed concurrently
- **Batch Operations**: Multiple symbols processed in batches
- **Connection Pooling**: Efficient database and Redis connections
- **Rate Limiting**: Built-in rate limiting to prevent abuse

## Error Handling

The system provides comprehensive error handling:

```json
{
  "error": "SYMBOL_NOT_FOUND",
  "message": "Stock symbol 'INVALID' not found",
  "details": "Please check the symbol format and try again",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Common Error Codes:**
- `SYMBOL_NOT_FOUND`: Invalid stock symbol
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `AUTHENTICATION_FAILED`: Invalid credentials
- `SERVICE_UNAVAILABLE`: External service down
- `INVALID_PARAMETERS`: Invalid request parameters

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# ML Model Configuration
SENTIMENT_MODEL_PATH=/models/sentiment_model.pkl
SIGNAL_MODEL_PATH=/models/signal_model.pkl

# API Configuration
SENTIMENT_CACHE_TTL=900  # 15 minutes
SIGNAL_CACHE_TTL=300     # 5 minutes
NEWS_CACHE_TTL=1800      # 30 minutes

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600   # 1 hour
```

### Model Configuration

The system supports multiple ML models:

1. **Sentiment Analysis Models**:
   - VADER Sentiment Analyzer
   - Custom BERT-based model
   - FinBERT (Financial BERT)

2. **Signal Generation Models**:
   - Technical Analysis Engine
   - ML-based Pattern Recognition
   - Ensemble Methods

## Usage Examples

### Python Client

```python
import requests
import json

# Get sentiment analysis
response = requests.get(
    "http://localhost:8000/api/sentiment/AAPL",
    headers={"Authorization": "Bearer your_token"},
    params={"include_news": True, "lookback_days": 7}
)

sentiment_data = response.json()
print(f"Sentiment: {sentiment_data['sentiment_label']}")
print(f"Confidence: {sentiment_data['confidence']}")

# Get trade signals
response = requests.get(
    "http://localhost:8000/api/sentiment/AAPL/signals",
    headers={"Authorization": "Bearer your_token"},
    params={"confidence_threshold": 0.8}
)

signals = response.json()
for signal in signals['signals']:
    print(f"Signal: {signal['signal_type']} - {signal['reasoning']}")
```

### JavaScript Client

```javascript
// Get sentiment analysis
const response = await fetch('/api/sentiment/AAPL?include_news=true&lookback_days=7', {
  headers: {
    'Authorization': 'Bearer your_token'
  }
});

const sentimentData = await response.json();
console.log(`Sentiment: ${sentimentData.sentiment_label}`);
console.log(`Confidence: ${sentimentData.confidence}`);

// Get trade signals
const signalsResponse = await fetch('/api/sentiment/AAPL/signals?confidence_threshold=0.8', {
  headers: {
    'Authorization': 'Bearer your_token'
  }
});

const signals = await signalsResponse.json();
signals.signals.forEach(signal => {
  console.log(`Signal: ${signal.signal_type} - ${signal.reasoning}`);
});
```

## Monitoring and Logging

### Health Check

```http
GET /api/sentiment/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "redis": "connected",
    "ml_models": "loaded",
    "news_api": "operational"
  },
  "metrics": {
    "requests_per_minute": 45,
    "cache_hit_rate": 0.78,
    "average_response_time": 0.15
  }
}
```

### Logging

The system logs all operations with structured logging:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "ml_sentiment",
  "operation": "sentiment_analysis",
  "symbol": "AAPL",
  "duration_ms": 150,
  "cache_hit": false,
  "user_id": "user_123"
}
```

## Troubleshooting

### Common Issues

1. **High Response Times**
   - Check Redis connection
   - Verify ML model loading
   - Monitor external API rate limits

2. **Cache Misses**
   - Verify Redis configuration
   - Check cache TTL settings
   - Monitor memory usage

3. **Authentication Errors**
   - Verify token format
   - Check token expiration
   - Validate user permissions

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG_ML_SENTIMENT=true
export LOG_LEVEL=DEBUG
```

## Security Considerations

- **Input Validation**: All parameters validated and sanitized
- **Rate Limiting**: Prevents abuse and DoS attacks
- **Authentication**: Secure token-based authentication
- **Data Privacy**: No sensitive data logged or cached
- **CORS**: Properly configured for web clients

## Performance Benchmarks

- **Average Response Time**: 150ms
- **Cache Hit Rate**: 78%
- **Concurrent Users**: 100+
- **Throughput**: 1000 requests/hour

## Future Enhancements

- **Real-time Streaming**: WebSocket support for live updates
- **Multi-language Support**: Support for international markets
- **Advanced ML Models**: Deep learning integration
- **Custom Indicators**: User-defined technical indicators
- **Portfolio Integration**: Direct portfolio management integration

## Support

For technical support or feature requests:
- **Documentation**: See `/docs` directory
- **Issues**: Create GitHub issue
- **Contact**: team@paiid.com

---

*Last Updated: January 15, 2024*
*Version: 1.0.0*
