# ActivePositions AI Analysis Backend Endpoint

## Overview

This document describes the new AI-powered analysis endpoint for active trading positions in the PaiiD backend.

## Endpoint: `POST /api/ai/analyze-positions`

### Description
Provides comprehensive AI analysis of all active trading positions with:
- Technical analysis for each position
- Entry/exit recommendations (HOLD, ADD, REDUCE, CLOSE)
- Risk assessment and adjustment suggestions
- Support/resistance levels
- Portfolio-level metrics and recommendations

### Authentication
Requires Bearer token authentication:
```
Authorization: Bearer {API_TOKEN}
```

### Request Body

```json
{
  "include_technicals": true,
  "include_sentiment": false,
  "timeframe": "1-2 weeks"
}
```

**Parameters:**
- `include_technicals` (boolean, default: true) - Include technical indicator analysis
- `include_sentiment` (boolean, default: false) - Include sentiment analysis (future feature)
- `timeframe` (string, default: "1-2 weeks") - Analysis timeframe

### Response Schema

```json
{
  "positions": [
    {
      "symbol": "AAPL",
      "current_price": 175.50,
      "quantity": 100.0,
      "avg_entry_price": 170.00,
      "unrealized_pl": 550.00,
      "unrealized_pl_percent": 3.24,
      "market_value": 17550.00,

      "current_analysis": {
        "rsi": 58.5,
        "macd_histogram": 0.25,
        "sma_20": 173.50,
        "sma_50": 171.00,
        "sma_200": 165.00
      },

      "momentum": "Bullish",
      "trend": "Strong Uptrend",
      "support_level": 172.00,
      "resistance_level": 178.50,
      "risk_assessment": "Low - Strong signal",

      "recommendation": "HOLD",
      "recommendation_confidence": 80.0,
      "improvement_opportunities": "Strong technical setup. Let position continue to work.",
      "short_term_outlook": "Uptrend intact. Next target: $178.50",
      "risk_adjustment_suggestion": "Raise stop to $173.40 (breakeven + 2%)",
      "stop_loss_suggestion": 166.75,
      "take_profit_suggestion": 187.00,

      "summary": "Strong Uptrend with bullish momentum. Support: $172.00, Resistance: $178.50"
    }
  ],

  "portfolio_summary": {
    "total_positions": 5,
    "total_value": 125000.00,
    "total_unrealized_pl": 5600.00,
    "total_unrealized_pl_percent": 4.69
  },

  "overall_risk_score": 4.5,
  "diversification_score": 8.0,

  "portfolio_recommendations": [
    "Portfolio performance: +4.7%",
    "1 positions up >20% - consider taking profits",
    "Good diversification with 5 positions"
  ],

  "generated_at": "2025-10-19T04:20:00.000Z"
}
```

### Response Fields

#### Position-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Stock ticker symbol |
| `current_price` | float | Current market price |
| `quantity` | float | Number of shares held |
| `avg_entry_price` | float | Average entry price per share |
| `unrealized_pl` | float | Unrealized profit/loss in dollars |
| `unrealized_pl_percent` | float | Unrealized P/L as percentage |
| `market_value` | float | Current market value of position |
| `current_analysis` | object | Technical indicator values (RSI, MACD, SMAs) |
| `momentum` | string | Momentum classification (e.g., "Bullish", "Bearish") |
| `trend` | string | Trend classification (e.g., "Strong Uptrend", "Downtrend") |
| `support_level` | float | Key support price level |
| `resistance_level` | float | Key resistance price level |
| `risk_assessment` | string | Risk description |
| `recommendation` | string | Action recommendation: HOLD, ADD, REDUCE, or CLOSE |
| `recommendation_confidence` | float | Confidence level (0-100) |
| `improvement_opportunities` | string | Detailed reasoning for recommendation |
| `short_term_outlook` | string | Near-term price outlook |
| `risk_adjustment_suggestion` | string | Suggested stop loss adjustments |
| `stop_loss_suggestion` | float | Recommended stop loss price |
| `take_profit_suggestion` | float | Recommended take profit price |
| `summary` | string | Brief summary of technical situation |

#### Portfolio-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `portfolio_summary.total_positions` | integer | Number of open positions |
| `portfolio_summary.total_value` | float | Total portfolio value |
| `portfolio_summary.total_unrealized_pl` | float | Total unrealized P/L |
| `portfolio_summary.total_unrealized_pl_percent` | float | Total P/L percentage |
| `overall_risk_score` | float | Portfolio risk score (1-10, higher = more risk) |
| `diversification_score` | float | Diversification score (1-10, higher = better) |
| `portfolio_recommendations` | array[string] | Top 5 portfolio-level recommendations |
| `generated_at` | string | Timestamp of analysis generation (ISO 8601) |

### Recommendation Logic

The endpoint generates recommendations based on:

1. **Big Winners (P/L > 20%)**:
   - HOLD if uptrend continues with momentum
   - REDUCE if momentum weakening

2. **Losing Positions (P/L < -10%)**:
   - CLOSE if downtrend with no reversal signals
   - HOLD if showing support with reversal potential

3. **Healthy Positions (Uptrend + Bullish Momentum)**:
   - HOLD if already profitable
   - ADD if early in trend with good entry points

4. **Weak Positions (Downtrend)**:
   - REDUCE exposure
   - Set stop loss at support level

5. **Neutral/Sideways**:
   - HOLD and wait for directional break

### Portfolio Risk Scoring

**Risk Score (1-10):**
- Base: 5.0
- +2.0 if < 3 positions (under-diversified)
- +1.0 if > 15 positions (over-diversified)
- +0.5 per position down >10% (max +3.0)

**Diversification Score (1-10):**
- 10.0 for empty portfolio
- 3.0 for < 3 positions
- 6.0 for > 15 positions
- 4.0 if any position > 30% of portfolio
- 6.0 if any position > 20% of portfolio
- 9.0 for well-balanced portfolios (5-15 positions, no concentration)

### Error Responses

**404 Not Found:**
```json
{
  "detail": "Not Found"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to analyze positions: <error message>"
}
```

### Empty Portfolio Response

When no positions exist:
```json
{
  "positions": [],
  "portfolio_summary": {
    "total_positions": 0,
    "total_value": 0.0,
    "total_unrealized_pl": 0.0
  },
  "overall_risk_score": 5.0,
  "diversification_score": 10.0,
  "portfolio_recommendations": [
    "No active positions. Consider starting with AI recommendations."
  ],
  "generated_at": "2025-10-19T04:20:00.000Z"
}
```

---

## Endpoint: `POST /api/ai/analyze-positions/claude-insights`

### Description
Generates natural language insights about active positions using Claude AI. Provides conversational analysis and actionable recommendations in plain English.

### Authentication
Requires Bearer token authentication.

### Request Body

```json
{
  "positions_summary": {
    "total_positions": 5,
    "total_value": 125000.00,
    "total_unrealized_pl": 5600.00,
    "total_unrealized_pl_percent": 4.69,
    "overall_risk_score": 4.5,
    "diversification_score": 8.0,
    "positions": [
      {
        "symbol": "AAPL",
        "quantity": 100,
        "current_price": 175.50,
        "avg_entry_price": 170.00,
        "unrealized_pl_percent": 3.24,
        "recommendation": "HOLD",
        "recommendation_confidence": 80,
        "trend": "Strong Uptrend",
        "momentum": "Bullish",
        "short_term_outlook": "Continued strength likely"
      }
    ],
    "portfolio_recommendations": [
      "Portfolio up +4.7%",
      "Good diversification"
    ]
  },
  "specific_question": "Should I take profits on my winners?" // optional
}
```

### Response Schema

```json
{
  "insights": "Your portfolio is showing solid performance with a +4.7% gain...",
  "key_recommendations": [
    "Consider taking partial profits on AAPL given the strong 20% gain",
    "Maintain current positions in trending stocks",
    "Review stop losses on underperforming positions"
  ],
  "generated_at": "2025-10-19T04:20:00.000Z"
}
```

### Implementation Details

**Data Sources:**
- Position data: Tradier API (real-time quotes, positions)
- Technical analysis: TechnicalIndicators service (RSI, MACD, SMA, Bollinger Bands, ATR)
- AI insights: Anthropic Claude API (claude-sonnet-4-5-20250929)

**Technical Indicators Used:**
- RSI (Relative Strength Index) - momentum oscillator
- MACD (Moving Average Convergence Divergence) - trend following
- SMA-20, SMA-50, SMA-200 - moving averages for trend identification
- Bollinger Bands - volatility and support/resistance
- ATR (Average True Range) - volatility measurement

**Caching:**
- Position data cached for 30 seconds (via portfolio.py)
- No caching for analysis results (always fresh analysis)

**Rate Limiting:**
- Applied via backend rate limiting middleware
- Depends on backend configuration

---

## Testing the Endpoint

### Using curl:

```bash
curl -X POST "http://localhost:8001/api/ai/analyze-positions" \
  -H "Authorization: Bearer rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl" \
  -H "Content-Type: application/json" \
  -d '{"include_technicals": true, "timeframe": "1-2 weeks"}'
```

### Using Python:

```python
import requests

url = "http://localhost:8001/api/ai/analyze-positions"
headers = {
    "Authorization": "Bearer rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl",
    "Content-Type": "application/json"
}
data = {
    "include_technicals": True,
    "timeframe": "1-2 weeks"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

### Frontend Integration:

```typescript
// In ActivePositions.tsx or similar component
const analyzePositions = async () => {
  const response = await fetch('/api/proxy/api/ai/analyze-positions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      include_technicals: true,
      timeframe: '1-2 weeks'
    })
  });

  const analysis = await response.json();
  console.log(analysis);
};
```

---

## File Locations

- **Endpoint Implementation**: `backend/app/routers/ai.py` (lines 459-1082)
- **Position Data Source**: `backend/app/routers/portfolio.py`
- **Technical Indicators**: `backend/app/services/technical_indicators.py`
- **Tradier Client**: `backend/app/services/tradier_client.py`
- **Test Script**: `backend/test_positions_endpoint.py`

---

## Future Enhancements

1. **Sentiment Analysis Integration** (include_sentiment parameter)
   - News sentiment for each position
   - Social media sentiment signals
   - Analyst rating changes

2. **Historical Performance Tracking**
   - Track recommendation accuracy over time
   - Learn from past recommendations
   - Improve confidence scoring

3. **Sector Correlation Analysis**
   - Identify sector concentration risk
   - Suggest hedging strategies
   - Market regime detection

4. **Real-time Updates via SSE**
   - Stream position analysis updates
   - Alert on significant changes
   - Live recommendation updates

5. **Custom User Preferences**
   - Risk tolerance adjustments
   - Preferred holding periods
   - Custom technical indicator weights

---

## Notes

- The endpoint requires Tradier API credentials to fetch position data
- Claude AI integration requires `ANTHROPIC_API_KEY` environment variable
- Empty portfolios return sensible defaults (no errors)
- All monetary values in USD
- Percentages as floats (e.g., 4.5 = 4.5%)
- Timestamps in ISO 8601 format with 'Z' suffix

---

## Status

✅ **IMPLEMENTED** - Ready for testing and frontend integration

**Created**: October 19, 2025
**Author**: Claude Code (Sonnet 4.5)
**Version**: 1.0.0
