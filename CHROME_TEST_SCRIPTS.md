# Chrome Testing Scripts for PaiiD
## Complete Guide for Testing with Chrome DevTools

**Date:** October 22, 2025
**Status:** ✅ Ready for Use
**Frontend:** http://localhost:3000
**Backend:** http://127.0.0.1:8001

---

## 🌐 Quick Links (Click to Open in Chrome)

### Frontend
- **Main Dashboard:** [http://localhost:3000](http://localhost:3000)
- **API Proxy Health:** [http://localhost:3000/api/health](http://localhost:3000/api/health)

### Backend
- **Health Check:** [http://127.0.0.1:8001/api/health](http://127.0.0.1:8001/api/health)
- **API Documentation (Swagger):** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- **Alternative Docs (ReDoc):** [http://127.0.0.1:8001/redoc](http://127.0.0.1:8001/redoc)

---

## 🧪 Chrome DevTools Console Scripts

### **Script 1: Test Options Expirations Endpoint**

**Open Chrome DevTools (F12) → Console Tab → Paste:**

```javascript
// Test Options Expirations for AAPL
fetch('http://127.0.0.1:8001/api/options/expirations/AAPL', {
  headers: {
    'Authorization': 'Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo'
  }
})
.then(response => {
  console.log('Status:', response.status);
  return response.json();
})
.then(data => {
  console.log('✅ Options Expirations:', data);
  console.table(data);
})
.catch(error => console.error('❌ Error:', error));
```

**Expected Output:**
```json
[
  {"date": "2025-10-24", "days_to_expiry": 2},
  {"date": "2025-10-31", "days_to_expiry": 9},
  ...
]
```

---

### **Script 2: Test Options Chain Endpoint**

```javascript
// Test Options Chain for AAPL (Oct 24 expiration)
fetch('http://127.0.0.1:8001/api/options/chain/AAPL?expiration=2025-10-24', {
  headers: {
    'Authorization': 'Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo'
  }
})
.then(response => {
  console.log('Status:', response.status);
  return response.json();
})
.then(data => {
  console.log('✅ Options Chain:', data);
  console.log('Symbol:', data.symbol);
  console.log('Total Contracts:', data.total_contracts);
  console.log('Calls:', data.calls.length);
  console.log('Puts:', data.puts.length);

  // Show first call option with Greeks
  if (data.calls.length > 0) {
    console.log('\n📊 Sample Call Option:');
    console.table([data.calls[0]]);
  }
})
.catch(error => console.error('❌ Error:', error));
```

**Expected Output:**
```
Symbol: AAPL
Total Contracts: 200+
Calls: 100+
Puts: 100+
📊 Sample Call Option:
{
  symbol: "AAPL251024C00150000",
  strike_price: 150,
  delta: 0.65,
  gamma: 0.023,
  theta: -0.45,
  vega: 0.18,
  bid: 5.20,
  ask: 5.40
}
```

---

### **Script 3: Test Multiple Symbols in Parallel**

```javascript
// Test options for multiple symbols
const symbols = ['AAPL', 'SPY', 'TSLA'];

Promise.all(
  symbols.map(symbol =>
    fetch(`http://127.0.0.1:8001/api/options/expirations/${symbol}`, {
      headers: {
        'Authorization': 'Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo'
      }
    }).then(r => r.json()).then(data => ({ symbol, data }))
  )
)
.then(results => {
  console.log('✅ Multi-Symbol Results:');
  results.forEach(({ symbol, data }) => {
    console.log(`\n${symbol}: ${data.length} expirations`);
    console.table(data.slice(0, 3)); // First 3 expirations
  });
})
.catch(error => console.error('❌ Error:', error));
```

---

### **Script 4: Monitor Frontend API Calls**

```javascript
// Intercept and log all fetch requests from frontend
const originalFetch = window.fetch;
window.fetch = function(...args) {
  console.log('🌐 Fetch Request:', args[0]);
  return originalFetch.apply(this, arguments)
    .then(response => {
      console.log('✅ Response:', response.status, args[0]);
      return response;
    })
    .catch(error => {
      console.error('❌ Fetch Error:', args[0], error);
      throw error;
    });
};
console.log('✅ Fetch monitoring enabled. All network requests will be logged.');
```

**Usage:** Run this before clicking UI elements to see all API calls.

---

### **Script 5: Test Options Chain with Error Handling**

```javascript
// Robust options chain test with detailed error reporting
async function testOptionsChain(symbol, expiration = '2025-10-24') {
  console.log(`🔍 Testing Options Chain: ${symbol} @ ${expiration}`);

  try {
    const response = await fetch(
      `http://127.0.0.1:8001/api/options/chain/${symbol}?expiration=${expiration}`,
      {
        headers: {
          'Authorization': 'Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo'
        }
      }
    );

    console.log('📡 Response Status:', response.status);
    console.log('📝 Response Headers:', [...response.headers.entries()]);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ HTTP Error ${response.status}:`, errorText);
      return;
    }

    const data = await response.json();

    console.log(`✅ Success! Got ${data.total_contracts} total contracts`);
    console.log(`   - ${data.calls.length} calls`);
    console.log(`   - ${data.puts.length} puts`);

    // Analyze Greeks availability
    const callsWithGreeks = data.calls.filter(c => c.delta !== null);
    const putsWithGreeks = data.puts.filter(p => p.delta !== null);

    console.log(`\n📊 Greeks Coverage:`);
    console.log(`   - Calls with Greeks: ${callsWithGreeks.length}/${data.calls.length}`);
    console.log(`   - Puts with Greeks: ${putsWithGreeks.length}/${data.puts.length}`);

    // Show ATM options (closest to current price)
    const atmCalls = data.calls.filter(c => Math.abs(c.delta - 0.5) < 0.1);
    const atmPuts = data.puts.filter(p => Math.abs(p.delta + 0.5) < 0.1);

    if (atmCalls.length > 0) {
      console.log('\n💰 At-The-Money Call:');
      console.table([atmCalls[0]]);
    }

    if (atmPuts.length > 0) {
      console.log('\n💰 At-The-Money Put:');
      console.table([atmPuts[0]]);
    }

    return data;

  } catch (error) {
    console.error('❌ Network Error:', error);
  }
}

// Run test
testOptionsChain('AAPL');
```

---

### **Script 6: Performance Timing**

```javascript
// Measure API response times
async function benchmarkOptionsAPI(symbol = 'SPY', runs = 5) {
  console.log(`⏱️  Benchmarking Options API (${runs} runs)`);

  const times = [];

  for (let i = 0; i < runs; i++) {
    const start = performance.now();

    await fetch(`http://127.0.0.1:8001/api/options/expirations/${symbol}`, {
      headers: {
        'Authorization': 'Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo'
      }
    });

    const end = performance.now();
    const time = end - start;
    times.push(time);

    console.log(`Run ${i + 1}: ${time.toFixed(2)}ms`);
  }

  const avg = times.reduce((a, b) => a + b, 0) / times.length;
  const min = Math.min(...times);
  const max = Math.max(...times);

  console.log('\n📊 Results:');
  console.log(`   Average: ${avg.toFixed(2)}ms`);
  console.log(`   Min: ${min.toFixed(2)}ms`);
  console.log(`   Max: ${max.toFixed(2)}ms`);
  console.log(`   Cache Effect: ${((max - min) / max * 100).toFixed(1)}% faster`);
}

benchmarkOptionsAPI();
```

---

## 🎯 Testing the Options Trading UI

### **Step-by-Step Manual Test:**

1. **Open Frontend:**
   ```
   chrome://newtab
   → Navigate to: http://localhost:3000
   ```

2. **Open DevTools:**
   ```
   Press F12 or Ctrl+Shift+I
   ```

3. **Load Dashboard:**
   - You should see the radial menu with 10 wedges
   - Center should show SPY/QQQ live prices

4. **Click "Options Trading" Wedge:**
   - Look for the wedge labeled "OPTIONS TRADING"
   - Click to open split-screen view

5. **Monitor Network Tab:**
   - Switch to Network tab in DevTools
   - Filter by "Fetch/XHR"
   - Watch for calls to `/api/proxy/api/options/...`

6. **Check Console:**
   - Switch to Console tab
   - Run Script 4 (Fetch monitoring) above
   - Click Options Trading again
   - See all API calls logged

7. **Verify Options Data:**
   - Options chain should load
   - Greeks (Delta, Gamma, Theta, Vega) should display
   - Strike prices should be visible
   - Bid/Ask prices should update

---

## 🔧 Thunder Client Setup (Chrome Extension Alternative)

Thunder Client is available for VS Code, not Chrome. For Chrome-based API testing, use:

### **Option 1: Built-in Swagger UI**

1. Open: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
2. Click "Authorize" button
3. Enter: `tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo`
4. Click "Authorize"
5. Test any endpoint directly from browser

### **Option 2: Postman (Chrome App)**

1. Download: [https://www.postman.com/downloads/](https://www.postman.com/downloads/)
2. Install Postman Chrome extension
3. Import PaiiD collection (create below)

### **Option 3: DevTools Snippets (Recommended)**

1. Open DevTools (F12)
2. Go to Sources → Snippets
3. Right-click → New snippet
4. Paste any script from above
5. Save (Ctrl+S)
6. Run (Ctrl+Enter or right-click → Run)

---

## 📝 Save Test Scripts as DevTools Snippets

### **How to Save:**

1. **Open DevTools:** Press F12
2. **Go to Sources tab**
3. **Click Snippets** (left sidebar)
4. **Create new snippet:** Right-click → New
5. **Name it:** e.g., "Test Options Chain"
6. **Paste script** from above
7. **Save:** Ctrl+S
8. **Run:** Right-click snippet → Run (or Ctrl+Enter)

### **Recommended Snippets to Create:**

1. **test-options-expirations** → Script 1
2. **test-options-chain** → Script 2
3. **monitor-fetch** → Script 4
4. **robust-test** → Script 5
5. **benchmark-api** → Script 6

---

## 🚀 Quick Test Commands

### **One-Liner Tests (Paste in Console):**

**Test Health:**
```javascript
fetch('http://127.0.0.1:8001/api/health').then(r => r.json()).then(console.log)
```

**Test Expirations:**
```javascript
fetch('http://127.0.0.1:8001/api/options/expirations/SPY', {headers: {'Authorization': 'Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo'}}).then(r => r.json()).then(console.table)
```

**Test Chain:**
```javascript
fetch('http://127.0.0.1:8001/api/options/chain/SPY', {headers: {'Authorization': 'Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo'}}).then(r => r.json()).then(d => console.log(d.symbol, d.total_contracts, 'contracts'))
```

---

## 🎨 Chrome DevTools Tips

### **Enable Dark Theme:**
1. DevTools → Settings (⚙️)
2. Preferences → Appearance → Theme → Dark

### **Preserve Console Log:**
1. Console → Settings (⚙️)
2. Check "Preserve log"
3. Logs won't clear on page refresh

### **Network Throttling:**
1. Network tab → Throttling dropdown
2. Select "Slow 3G" or "Fast 3G"
3. Test performance under poor conditions

### **Device Emulation:**
1. Toggle device toolbar (Ctrl+Shift+M)
2. Select device (iPhone, iPad, etc.)
3. Test responsive design

---

## 📊 Expected Test Results

### **Options Expirations (AAPL):**
- **Response Time:** < 100ms (cached) or < 500ms (fresh)
- **Data:** Array of 10-20 expiration dates
- **Fields:** `date`, `days_to_expiry`

### **Options Chain (AAPL):**
- **Response Time:** < 500ms (cached) or < 2s (fresh)
- **Total Contracts:** 200-500 (varies by symbol)
- **Greeks:** All present (delta, gamma, theta, vega, rho)
- **Pricing:** Bid, ask, last_price all populated

---

## 🐛 Troubleshooting

### **401 Unauthorized:**
- **Issue:** Wrong or missing API token
- **Fix:** Check Authorization header matches backend `.env`

### **404 Not Found:**
- **Issue:** Wrong endpoint path
- **Fix:** Verify path is `/api/options/chain/SYMBOL` (not `/chain`)

### **CORS Error:**
- **Issue:** Frontend proxy not working
- **Fix:** Use backend URL directly (`127.0.0.1:8001`) not `localhost:3000/api/proxy`

### **Network Error:**
- **Issue:** Backend not running
- **Fix:** Start backend: `cd backend && python -m uvicorn app.main:app --reload --port 8001`

### **Empty Data:**
- **Issue:** Market closed or symbol invalid
- **Fix:** Try SPY or AAPL (always have data)

---

## ✅ Checklist

After running tests, verify:

- [ ] Chrome can access `http://localhost:3000` (frontend loads)
- [ ] Backend health check returns `{"status": "ok"}`
- [ ] Options expirations endpoint returns data
- [ ] Options chain endpoint returns calls and puts
- [ ] Greeks are present in options data
- [ ] Frontend Options Trading wedge opens
- [ ] Network tab shows successful API calls
- [ ] No console errors in DevTools
- [ ] Response times < 2 seconds
- [ ] Data updates when switching symbols

---

**Created By:** Claude Code
**For:** Dr. SC Prime
**Date:** October 22, 2025
**Status:** ✅ Complete and Tested

**Quick Start:** Open Chrome → Navigate to http://localhost:3000 → Press F12 → Paste any script above!
