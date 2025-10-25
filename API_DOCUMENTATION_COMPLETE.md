# PaiiD API Documentation

## 🚀 **Live API Endpoints**

### **Base URL**
- **Production:** `https://paiid-backend.onrender.com`
- **WebSocket:** `wss://paiid-backend.onrender.com/ws`

---

## 📊 **Core Trading Endpoints**

### **Market Data**
```http
GET /api/market-data/{symbol}
GET /api/options/{symbol}
GET /api/options/{symbol}/chains
```

### **Account Management**
```http
GET /api/account/balance
GET /api/account/positions
GET /api/account/orders
POST /api/account/orders
```

### **Trading Operations**
```http
POST /api/trading/execute
POST /api/trading/options/execute
GET /api/trading/history
```

---

## 🧠 **ML Intelligence Endpoints**

### **Pattern Recognition**
```http
POST /api/ml/detect-patterns
GET /api/ml/patterns/{symbol}
POST /api/ml/backtest-patterns
```

### **Market Regime Detection**
```http
GET /api/ml/market-regime/{symbol}
POST /api/ml/train-regime-detector
GET /api/ml/recommend-strategy/{symbol}
```

### **Personal Analytics**
```http
GET /api/ml/analytics/performance
GET /api/ml/analytics/risk
POST /api/ml/optimize-portfolio
```

---

## 🔧 **System Endpoints**

### **Health & Status**
```http
GET /api/health
GET /api/status
GET /api/version
```

### **Monitoring**
```http
GET /api/monitor/metrics
GET /api/monitor/logs
GET /api/monitor/performance
```

---

## 🔐 **Authentication**

### **API Key Required**
All endpoints require authentication via API key:

```http
Authorization: Bearer YOUR_API_KEY
```

### **Rate Limits**
- **Standard:** 100 requests/minute
- **ML Endpoints:** 20 requests/minute
- **Trading:** 10 requests/minute

---

## 📈 **Response Format**

### **Success Response**
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-10-25T02:00:00Z"
}
```

### **Error Response**
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-10-25T02:00:00Z"
}
```

---

## 🚀 **WebSocket Events**

### **Real-time Data**
```javascript
// Connect to WebSocket
const ws = new WebSocket('wss://paiid-backend.onrender.com/ws');

// Listen for events
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### **Available Events**
- `market_data_update`
- `order_status_change`
- `ml_prediction_ready`
- `system_alert`

---

## 📚 **SDK Examples**

### **JavaScript/TypeScript**
```typescript
import { PaiiDClient } from '@paiid/sdk';

const client = new PaiiDClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://paiid-backend.onrender.com'
});

// Get market data
const data = await client.getMarketData('AAPL');

// Execute trade
const order = await client.executeTrade({
  symbol: 'AAPL',
  side: 'buy',
  quantity: 100,
  type: 'market'
});
```

### **Python**
```python
from paiid import PaiiDClient

client = PaiiDClient(
    api_key='your-api-key',
    base_url='https://paiid-backend.onrender.com'
)

# Get market data
data = client.get_market_data('AAPL')

# Execute trade
order = client.execute_trade(
    symbol='AAPL',
    side='buy',
    quantity=100,
    type='market'
)
```

---

## 🔧 **Development & Testing**

### **Local Development**
```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# Start frontend
cd frontend
npm run dev
```

### **Testing**
```bash
# Run API tests
pytest backend/tests/

# Run frontend tests
npm test
```

---

## 📞 **Support**

- **Documentation:** [GitHub Wiki](https://github.com/SCPrime/PaiiD/wiki)
- **Issues:** [GitHub Issues](https://github.com/SCPrime/PaiiD/issues)
- **Discussions:** [GitHub Discussions](https://github.com/SCPrime/PaiiD/discussions)

---

## 🏆 **Status: Production Ready**

✅ **All endpoints tested and documented**  
✅ **Rate limiting implemented**  
✅ **Error handling complete**  
✅ **WebSocket support active**  
✅ **SDK examples provided**  

**Last Updated:** October 25, 2025
