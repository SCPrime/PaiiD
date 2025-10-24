# 🚀 ML Features - Quick Start Guide

**Get started with PaiiD's AI-powered trading intelligence in 5 minutes!**

---

## 📦 **Installation**

### **1. Install Backend Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

**New ML Dependencies:**
- `scikit-learn>=1.3.0` - Machine learning algorithms
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing
- `joblib>=1.3.0` - Model persistence
- `ta>=0.11.0` - Technical indicators

### **2. Start Backend**

```bash
python -m uvicorn app.main:app --reload --port 8001
```

### **3. Verify ML Module**

```bash
curl http://localhost:8001/api/ml/health
```

Expected response:
```json
{
  "status": "healthy",
  "regime_detector_ready": false,
  "regime_labels": {},
  "n_clusters": 4
}
```

---

## ⚡ **Quick Examples**

### **1. Detect Market Regime** (Fastest - No Training Required!)

```bash
# What's the current market state?
curl "http://localhost:8001/api/ml/market-regime?symbol=SPY"
```

**Response:**
```json
{
  "symbol": "SPY",
  "regime": "trending_bullish",
  "confidence": 0.87,
  "features": {
    "trend_direction": 0.12,
    "trend_strength": 35.6,
    "volatility": 0.18,
    "rsi": 62.4
  },
  "recommended_strategies": [
    "trend-following-ma-crossover",
    "momentum-breakout"
  ]
}
```

**What This Tells You:**
- Market is in a strong uptrend (87% confidence)
- RSI at 62.4 (bullish but not overbought)
- Volatility at 18% (moderate)
- Best strategies: Trend-following and momentum

---

### **2. Detect Chart Patterns** (Instant - Rule-Based!)

```bash
# Find patterns in AAPL
curl "http://localhost:8001/api/ml/detect-patterns?symbol=AAPL&min_confidence=0.7"
```

**Response:**
```json
{
  "symbol": "AAPL",
  "patterns": [
    {
      "pattern_type": "double_bottom",
      "signal": "bullish",
      "confidence": 0.78,
      "description": "Double bottom at $168.50, neckline at $175.80",
      "target_price": 182.50,
      "stop_loss": 168.85
    }
  ],
  "total_patterns": 1
}
```

**How to Use:**
- Pattern detected: Double bottom (bullish reversal)
- Entry: Above $175.80 (neckline break)
- Target: $182.50 (projected gain)
- Stop-loss: $168.85 (risk management)

---

### **3. Get Strategy Recommendations** (Requires Training - See Below)

```bash
# Which strategy should I use for TSLA?
curl "http://localhost:8001/api/ml/recommend-strategy?symbol=TSLA&top_n=3"
```

**Response:**
```json
{
  "symbol": "TSLA",
  "market_regime": "high_volatility",
  "recommendations": [
    {
      "strategy_id": "volatility-breakout",
      "probability": 0.68,
      "confidence": 0.68
    },
    {
      "strategy_id": "mean-reversion-bb-rsi",
      "probability": 0.22,
      "confidence": 0.22
    },
    {
      "strategy_id": "momentum-breakout",
      "probability": 0.10,
      "confidence": 0.10
    }
  ]
}
```

**How to Use:**
- ML recommends: Volatility-breakout strategy (68% confidence)
- Market is choppy (high_volatility regime)
- Alternative: Mean-reversion (22% confidence)

---

## 🎓 **First-Time Setup** (One-Time Training)

### **Train Market Regime Detector** (~10 seconds)

```bash
# Train on SPY (S&P 500) - 2 years of data
curl -X POST "http://localhost:8001/api/ml/train-regime-detector?symbol=SPY&lookback_days=730"
```

**Response:**
```json
{
  "success": true,
  "message": "Regime detector trained successfully on SPY",
  "regime_labels": {
    "0": "high_volatility",
    "1": "trending_bullish",
    "2": "trending_bearish",
    "3": "ranging"
  }
}
```

**When to Retrain:**
- Weekly (recommended)
- After major market events (crashes, rallies)
- When switching primary indices

---

### **Train Strategy Selector** (~5 minutes - OPTIONAL)

```bash
# Train on 4 major indices
curl -X POST "http://localhost:8001/api/ml/train-strategy-selector?symbols=SPY&symbols=QQQ&symbols=IWM&symbols=DIA&lookback_days=365"
```

**Response:**
```json
{
  "success": true,
  "train_accuracy": 0.73,
  "test_accuracy": 0.68,
  "n_samples": 245,
  "strategies": [
    "trend-following-ma-crossover",
    "mean-reversion-bb-rsi",
    "momentum-breakout",
    "volatility-breakout"
  ],
  "top_features": {
    "avg_rsi": 0.18,
    "avg_volatility": 0.15,
    "regime_trending_bullish": 0.12
  }
}
```

**Why Train?**
- Learns which strategies work best in different market conditions
- 68% test accuracy means ML is better than random guessing
- Top features show RSI and volatility are most predictive

**When to Retrain:**
- Monthly (recommended)
- After major strategy updates
- When adding new strategies

---

## 🎯 **Real-World Trading Workflow**

### **Morning Routine Example**

```bash
SYMBOL="SPY"

# 1. Check market regime
curl "http://localhost:8001/api/ml/market-regime?symbol=$SYMBOL"
# Output: "trending_bullish" - Market is trending up

# 2. Get strategy recommendations
curl "http://localhost:8001/api/ml/recommend-strategy?symbol=$SYMBOL&top_n=3"
# Output: "trend-following-ma-crossover" (72% confidence)

# 3. Check for patterns
curl "http://localhost:8001/api/ml/detect-patterns?symbol=$SYMBOL&min_confidence=0.7"
# Output: "ascending_triangle" found - Bullish breakout setup

# DECISION: Use trend-following strategy, watch for triangle breakout
```

### **Before Entering a Trade**

```bash
SYMBOL="AAPL"

# Get complete ML analysis
curl "http://localhost:8001/api/ml/market-regime?symbol=$SYMBOL"
curl "http://localhost:8001/api/ml/detect-patterns?symbol=$SYMBOL"
curl "http://localhost:8001/api/ml/recommend-strategy?symbol=$SYMBOL"

# Check confidence scores:
# - Regime confidence: 0.85 ✅ (high)
# - Pattern confidence: 0.78 ✅ (good)
# - Strategy probability: 0.68 ✅ (reliable)

# ALL GREEN? Enter trade with calculated target & stop-loss from pattern
```

---

## 📊 **Understanding Confidence Scores**

### **Confidence Levels**

| Score Range | Meaning | Action |
|-------------|---------|--------|
| 0.90 - 1.00 | Very High | High conviction trades |
| 0.75 - 0.89 | High | Good trade setups |
| 0.60 - 0.74 | Moderate | Proceed with caution |
| 0.50 - 0.59 | Low | Wait for better signals |
| < 0.50 | Very Low | Avoid trading |

### **Combining Signals**

**Strong Trade Setup (All Align):**
```
Market Regime: trending_bullish (0.87)
Pattern: double_bottom (0.78)
Strategy: trend-following (0.72)
→ HIGH CONFIDENCE BUY SIGNAL
```

**Mixed Signals (Proceed with Caution):**
```
Market Regime: ranging (0.65)
Pattern: symmetric_triangle (0.62)
Strategy: mean-reversion (0.58)
→ WAIT FOR BREAKOUT DIRECTION
```

---

## 🔧 **Advanced Usage**

### **Custom Confidence Thresholds**

```bash
# Only show HIGH confidence patterns (>80%)
curl "http://localhost:8001/api/ml/detect-patterns?symbol=SPY&min_confidence=0.8"

# Show all patterns (even low confidence)
curl "http://localhost:8001/api/ml/detect-patterns?symbol=SPY&min_confidence=0.5"
```

### **Different Lookback Periods**

```bash
# Short-term (30 days) - More responsive
curl "http://localhost:8001/api/ml/market-regime?symbol=SPY&lookback_days=30"

# Long-term (180 days) - More stable
curl "http://localhost:8001/api/ml/market-regime?symbol=SPY&lookback_days=180"
```

### **More Recommendations**

```bash
# Get top 5 strategies (instead of default 3)
curl "http://localhost:8001/api/ml/recommend-strategy?symbol=AAPL&top_n=5"
```

---

## 🚨 **Common Issues & Solutions**

### **Issue: "No data available" error**
**Cause:** Symbol not found or insufficient history
**Solution:**
- Check symbol spelling (use uppercase: "AAPL" not "aapl")
- Try a more liquid stock (SPY, QQQ, AAPL, TSLA)
- Reduce lookback_days if stock is newly listed

### **Issue: "Model not trained yet" warning**
**Cause:** Strategy selector needs initial training
**Solution:**
```bash
# Quick training (2 symbols, ~2 minutes)
curl -X POST "http://localhost:8001/api/ml/train-strategy-selector?symbols=SPY&symbols=QQQ&lookback_days=180"
```

### **Issue: No patterns detected**
**Cause:** No strong patterns in recent history
**Solution:**
- Lower min_confidence to 0.6 or 0.5
- Increase lookback_days to 120 or 180
- Try different symbols (some are more pattern-rich)

### **Issue: Fallback recommendations returned**
**Cause:** ML model not trained, using regime-based rules instead
**Solution:**
- Train the strategy selector (see above)
- Or use fallback recommendations anyway (still useful!)

---

## 📱 **Frontend Integration**

### **React/TypeScript Example**

```typescript
// Fetch ML insights for a symbol
async function getMLInsights(symbol: string) {
  const [regime, patterns, strategies] = await Promise.all([
    fetch(`/api/proxy/api/ml/market-regime?symbol=${symbol}`).then(r => r.json()),
    fetch(`/api/proxy/api/ml/detect-patterns?symbol=${symbol}`).then(r => r.json()),
    fetch(`/api/proxy/api/ml/recommend-strategy?symbol=${symbol}`).then(r => r.json())
  ]);

  return {
    regime: regime.regime,
    regimeConfidence: regime.confidence,
    patterns: patterns.patterns,
    topStrategy: strategies.recommendations[0]?.strategy_id,
    strategyConfidence: strategies.recommendations[0]?.probability
  };
}

// Usage in component
const insights = await getMLInsights('AAPL');

console.log(`Market: ${insights.regime} (${insights.regimeConfidence})`);
console.log(`Strategy: ${insights.topStrategy} (${insights.strategyConfidence})`);
console.log(`Patterns found: ${insights.patterns.length}`);
```

---

## ⏱️ **Performance Tips**

### **Cache Results**
- Market regime: Cache for 1 hour (changes slowly)
- Patterns: Cache for 30 minutes (update on new bars)
- Strategy recommendations: Cache for 1 hour

### **Parallel Requests**
```bash
# Fetch all ML data at once (fastest!)
curl "http://localhost:8001/api/ml/market-regime?symbol=AAPL" &
curl "http://localhost:8001/api/ml/detect-patterns?symbol=AAPL" &
curl "http://localhost:8001/api/ml/recommend-strategy?symbol=AAPL" &
wait
```

### **Batch Training** (Production)
```bash
# Schedule weekly retraining (cron job)
0 2 * * 0 curl -X POST "http://localhost:8001/api/ml/train-regime-detector?symbol=SPY"
0 3 1 * * curl -X POST "http://localhost:8001/api/ml/train-strategy-selector"
```

---

## 🎉 **You're Ready!**

**Start using ML insights in your trading:**
1. ✅ Check market regime before each trading session
2. ✅ Scan for patterns in your watchlist
3. ✅ Get AI strategy recommendations
4. ✅ Use confidence scores to filter signals
5. ✅ Combine ML insights with your own analysis

**Next Steps:**
- Read `PHASE_2_ML_COMPLETE.md` for deep technical dive
- Integrate ML endpoints into frontend
- Set up automated retraining schedule
- Monitor accuracy metrics over time

---

**Happy Trading! 📈🚀**

**Questions?** Check the full documentation in `PHASE_2_ML_COMPLETE.md`
