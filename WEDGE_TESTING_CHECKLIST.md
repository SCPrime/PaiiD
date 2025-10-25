# 🔍 PaiiD Radial Menu Wedge Testing Checklist

**Purpose**: Manual testing guide to verify all 10 wedges receive live data without errors

**Tester**: _____________________
**Date**: _____________________
**Environment**: □ Local  □ Render Production
**Browser**: □ Chrome  □ Firefox  □ Edge  □ Safari

---

## 🚀 Pre-Test Setup

- [ ] Backend is running: https://paiid-backend.onrender.com/api/health returns `{"status":"ok"}`
- [ ] Frontend is accessible: https://paiid-frontend.onrender.com loads
- [ ] Browser DevTools console is open (F12)
- [ ] Network tab is open to monitor API calls
- [ ] Skip onboarding (Press `Ctrl+Shift+A` or complete setup)
- [ ] Radial menu is visible with 10+ wedges

---

## 1️⃣ **MORNING ROUTINE** Wedge

**Wedge Location**: Top (12 o'clock position)
**Icon**: 🌅
**Component**: `MorningRoutineAI.tsx`

### Test Steps:
1. [ ] Click the "MORNING ROUTINE" wedge
2. [ ] Component loads within 3 seconds
3. [ ] Check Network tab for successful API calls:
   - [ ] `/api/proxy/api/account` → Status 200
   - [ ] `/api/market/indices` → Status 200
4. [ ] UI Elements Display:
   - [ ] Portfolio balance shows ($X,XXX.XX format)
   - [ ] Account summary section visible
   - [ ] Market indices (SPY, QQQ) show current prices
   - [ ] AI insights/recommendations section present
5. [ ] **No Error Messages**:
   - [ ] No "Failed to load" text
   - [ ] No "Error fetching data" alerts
   - [ ] No red error boxes
6. [ ] **Console Check**:
   - [ ] No JavaScript errors (red text)
   - [ ] No 401/403 auth errors
   - [ ] No CORS errors

**Status**: □ PASS  □ FAIL  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 2️⃣ **NEWS REVIEW** Wedge

**Wedge Location**: Clockwise from Morning Routine
**Icon**: 📰
**Component**: `NewsReview.tsx`

### Test Steps:
1. [ ] Click the "NEWS REVIEW" wedge
2. [ ] Component loads within 3 seconds
3. [ ] Check Network tab:
   - [ ] `/api/proxy/news/providers` → Status 200
   - [ ] `/api/proxy/news/market` or `/api/proxy/news/company/*` → Status 200
   - [ ] `/api/proxy/news/sentiment/market` → Status 200
4. [ ] UI Elements:
   - [ ] News articles list displays (at least 1 article)
   - [ ] Each article shows: headline, source, date
   - [ ] Sentiment indicators visible (🟢 positive / 🔴 negative / 🟡 neutral)
   - [ ] Filter buttons work (All / Technology / Finance, etc.)
5. [ ] **Interactive Elements**:
   - [ ] Click "Analyze with AI" button (if present)
   - [ ] AI summary loads successfully
6. [ ] **No Errors**:
   - [ ] No "No news available" with errors
   - [ ] News feed populates with real articles

**Status**: □ PASS  □ FAIL  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 3️⃣ **AI RECS** (Proposals) Wedge

**Wedge Location**: Continue clockwise
**Icon**: 🤖
**Component**: `AIRecommendations.tsx`

### Test Steps:
1. [ ] Click the "AI RECS" wedge
2. [ ] Component loads
3. [ ] Check Network tab:
   - [ ] `/api/ai/recommendations` → Status 200
4. [ ] UI Elements:
   - [ ] AI recommendations list displays
   - [ ] Each recommendation shows:
     - [ ] Symbol (e.g., AAPL)
     - [ ] Action (Buy/Sell)
     - [ ] Rationale text
     - [ ] Confidence score/percentage
   - [ ] "Approve" and "Reject" buttons present
5. [ ] **Interactive Test**:
   - [ ] Click "Approve" on one recommendation
   - [ ] Confirmation appears or status updates
6. [ ] **No Timeouts**:
   - [ ] AI API responds within 10 seconds
   - [ ] No "Claude AI unavailable" errors

**Status**: □ PASS  □ FAIL  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 4️⃣ **ACTIVE POSITIONS** Wedge

**Wedge Location**: Continue clockwise
**Icon**: 📊
**Component**: `PositionManager.tsx`

### Test Steps:
1. [ ] Click the "ACTIVE POSITIONS" wedge
2. [ ] Component loads
3. [ ] Check Network tab:
   - [ ] `/api/proxy/positions` → Status 200 (Alpaca API)
   - [ ] `/api/proxy/positions/greeks` → Status 200 (if options)
4. [ ] UI Elements:
   - [ ] Positions table displays (or "No open positions" if empty)
   - [ ] If positions exist, each shows:
     - [ ] Symbol
     - [ ] Quantity
     - [ ] Entry price
     - [ ] Current price
     - [ ] P&L ($XXX.XX and +/-X.XX%)
     - [ ] Market value
   - [ ] Portfolio summary at top (total value, total P&L)
   - [ ] **Options Greeks** (if applicable):
     - [ ] Delta, Gamma, Theta, Vega display
5. [ ] **Interactive Elements**:
   - [ ] "Close Position" button visible
   - [ ] Click "Close" → Confirmation dialog appears
   - [ ] Auto-refresh indicator (data updates every 10s)
6. [ ] **No Errors**:
   - [ ] Alpaca Paper Trading account accessible
   - [ ] No "Failed to fetch positions" message

**Status**: □ PASS  □ FAIL  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 5️⃣ **P&L DASHBOARD** (My Account) Wedge

**Wedge Location**: Continue clockwise
**Icon**: 💰
**Component**: Iframe → `/my-account` page

### Test Steps:
1. [ ] Click the "P&L DASHBOARD" wedge
2. [ ] Iframe loads successfully
3. [ ] Check Network tab:
   - [ ] `/my-account` page → Status 200 (not 404)
   - [ ] Chart data API calls succeed
4. [ ] UI Elements:
   - [ ] Financial chart displays (line/area chart)
   - [ ] Chart.js library loads (no "chart.js not found" errors)
   - [ ] X-axis shows dates/time
   - [ ] Y-axis shows dollar values
   - [ ] Account value line is visible (not flat at $0)
5. [ ] **Chart Interactions**:
   - [ ] Hover over chart shows tooltips
   - [ ] Time range selector works (if present)
6. [ ] **No Errors**:
   - [ ] Chart renders without blank canvas
   - [ ] Data points are realistic (not all zeros)

**Status**: □ PASS  □ FAIL  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 6️⃣ **STRATEGY BUILDER** Wedge

**Wedge Location**: Continue clockwise
**Icon**: 🎯
**Component**: `StrategyBuilderAI.tsx`

### Test Steps:
1. [ ] Click the "STRATEGY BUILDER" wedge
2. [ ] Component loads
3. [ ] Check Network tab:
   - [ ] `/api/strategies` → Status 200 (list saved strategies)
4. [ ] UI Elements:
   - [ ] Strategy builder interface visible
   - [ ] Drag-and-drop rule builder or form inputs
   - [ ] "Create New Strategy" button present
   - [ ] Saved strategies list (if any exist)
5. [ ] **Interactive Test**:
   - [ ] Click "Create Strategy"
   - [ ] Enter strategy name
   - [ ] Add at least one rule/condition
   - [ ] "Save" button works (API call succeeds)
6. [ ] **No Errors**:
   - [ ] Strategy form validates input
   - [ ] No "Strategy service unavailable" errors

**Status**: □ PASS  □ FAIL  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 7️⃣ **BACKTESTING** Wedge

**Wedge Location**: Continue clockwise
**Icon**: 📈
**Component**: `Backtesting.tsx`

### Test Steps:
1. [ ] Click the "BACKTESTING" wedge
2. [ ] Component loads
3. [ ] Check Network tab:
   - [ ] `/api/backtesting/strategies` → Status 200
   - [ ] `/api/market/historical` → Status 200 (when test runs)
4. [ ] UI Elements:
   - [ ] Strategy dropdown populated
   - [ ] Date range picker visible (start/end dates)
   - [ ] "Run Backtest" button present
5. [ ] **Interactive Test**:
   - [ ] Select a strategy from dropdown
   - [ ] Choose date range (e.g., last 30 days)
   - [ ] Click "Run Backtest"
   - [ ] Progress indicator appears
   - [ ] **Results Display**:
     - [ ] P&L chart renders
     - [ ] Performance metrics (total return, Sharpe ratio, max drawdown)
     - [ ] Trade log/history table
6. [ ] **No Timeouts**:
   - [ ] Backtest completes within 30 seconds
   - [ ] Historical data loads from Tradier API

**Status**: □ PASS  □ FAIL  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 8️⃣ **EXECUTE TRADE** Wedge

**Wedge Location**: Continue clockwise
**Icon**: ⚡
**Component**: `ExecuteTradeForm.tsx`

### Test Steps:
1. [ ] Click the "EXECUTE" wedge
2. [ ] Trade form loads
3. [ ] Check Network tab (as you interact):
   - [ ] `/api/market/quote/{symbol}` → Status 200 (real-time price)
4. [ ] UI Elements:
   - [ ] Symbol input field
   - [ ] Quantity input
   - [ ] Order type dropdown (Market, Limit, Stop)
   - [ ] Buy/Sell buttons
   - [ ] "Preview Order" button
5. [ ] **Interactive Test**:
   - [ ] Enter symbol "AAPL"
   - [ ] Symbol autocomplete works (suggestions appear)
   - [ ] Real-time price displays (e.g., $175.23)
   - [ ] Enter quantity "10"
   - [ ] Select order type "Market"
   - [ ] Click "Preview Order"
   - [ ] **Preview Shows**:
     - [ ] Estimated cost
     - [ ] Current price
     - [ ] Commission (if any)
   - [ ] Click "Submit Order" (⚠️ PAPER TRADING ONLY)
   - [ ] Order confirmation appears
   - [ ] Check `/api/orders` → Status 200 (Alpaca)
6. [ ] **No Errors**:
   - [ ] Quote data updates in real-time
   - [ ] No "Invalid API key" errors (Tradier/Alpaca)
   - [ ] Order submits successfully to Alpaca Paper Trading

**Status**: □ PASS  □ FAIL  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 9️⃣ **OPTIONS TRADING** Wedge

**Wedge Location**: Continue clockwise
**Icon**: 📈
**Component**: (TBD - may not be implemented)

### Test Steps:
1. [ ] Click the "OPTIONS TRADING" wedge
2. [ ] Component loads (or shows "Coming Soon" message)
3. [ ] If implemented:
   - [ ] Check Network tab:
     - [ ] `/api/options/chain/{symbol}` → Status 200
     - [ ] `/api/options/greeks/{symbol}` → Status 200
   - [ ] UI Elements:
     - [ ] Symbol search input
     - [ ] Options chain table (Calls and Puts)
     - [ ] Strike prices display
     - [ ] Expiration date selector
     - [ ] Greeks columns (Delta, Gamma, Theta, Vega, IV)
   - [ ] **Interactive Test**:
     - [ ] Search for "SPY"
     - [ ] Options chain populates
     - [ ] Select an expiration date
     - [ ] Chain updates with new strikes
     - [ ] Click a strike to view details
     - [ ] Greeks display for selected option
4. [ ] **No Errors**:
   - [ ] Tradier options API accessible
   - [ ] Chain data loads within 5 seconds

**Status**: □ PASS  □ FAIL  □ NOT IMPLEMENTED  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 🔟 **REPO MONITOR** (Dev Progress) Wedge

**Wedge Location**: Continue clockwise
**Icon**: 🔍
**Component**: Iframe → `/progress` page

### Test Steps:
1. [ ] Click the "REPO MONITOR" wedge
2. [ ] Iframe loads successfully
3. [ ] Check Network tab:
   - [ ] `/progress` page → Status 200 (not 404)
   - [ ] GitHub API calls succeed (if used)
   - [ ] `progress-data.json` loads
4. [ ] UI Elements:
   - [ ] Progress dashboard displays
   - [ ] Progress percentage shows (should be 100%)
   - [ ] GitHub metrics visible:
     - [ ] Total commits
     - [ ] Open/closed issues
     - [ ] PR count
     - [ ] Workflow runs
   - [ ] Visual charts/graphs render (if present)
5. [ ] **Data Accuracy**:
   - [ ] Metrics match actual GitHub repository
   - [ ] Progress percentage is realistic
6. [ ] **No Errors**:
   - [ ] No "GitHub API rate limit exceeded"
   - [ ] Dashboard loads completely

**Status**: □ PASS  □ FAIL  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 1️⃣1️⃣ **ML INTELLIGENCE** Wedge

**Wedge Location**: Last wedge clockwise
**Icon**: 🧠
**Component**: `MLIntelligenceWorkflow.tsx`

### Test Steps:
1. [ ] Click the "ML INTELLIGENCE" wedge
2. [ ] Component loads
3. [ ] Check Network tab:
   - [ ] `/api/ml/sentiment/{symbol}` → Status 200
   - [ ] `/api/ml/patterns/{symbol}` → Status 200
   - [ ] `/api/ml/predictions` → Status 200
4. [ ] UI Elements:
   - [ ] Symbol input or selector
   - [ ] Sentiment analysis section
   - [ ] Pattern recognition display
   - [ ] ML predictions/insights
   - [ ] Confidence scores
5. [ ] **Interactive Test**:
   - [ ] Enter symbol "AAPL"
   - [ ] Sentiment analysis loads
   - [ ] Pattern charts display
   - [ ] ML model predictions shown
6. [ ] **No Errors**:
   - [ ] ML models accessible
   - [ ] No "Model not found" errors
   - [ ] Predictions display with confidence scores

**Status**: □ PASS  □ FAIL  □ PARTIAL

**Notes**: _______________________________________________________________

---

## 🏁 **Overall Test Summary**

### Pass/Fail Count:
- **PASS**: _____ / 11 wedges
- **FAIL**: _____ / 11 wedges
- **PARTIAL**: _____ / 11 wedges
- **NOT IMPLEMENTED**: _____ / 11 wedges

### Critical Issues Found:
1. _______________________________________________________________
2. _______________________________________________________________
3. _______________________________________________________________

### Non-Critical Issues:
1. _______________________________________________________________
2. _______________________________________________________________

### Network Health:
- **Total API Calls Made**: _____
- **Successful (200-299)**: _____
- **Failed (400-599)**: _____
- **Most Common Errors**: _______________________________________________

### Browser Console Errors:
- **JavaScript Errors**: _____
- **Network Errors**: _____
- **CORS Errors**: _____

---

## 🎯 **Recommendations**

**High Priority Fixes**:
- [ ] _______________________________________________________________
- [ ] _______________________________________________________________

**Medium Priority**:
- [ ] _______________________________________________________________

**Low Priority / Enhancements**:
- [ ] _______________________________________________________________

---

## ✅ **Sign-Off**

**Tested By**: _____________________
**Date**: _____________________
**Overall Assessment**: □ Production Ready  □ Minor Fixes Needed  □ Major Issues

**Notes**:
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

---

**Next Steps**:
1. Fix critical issues identified
2. Re-test failed wedges
3. Update components with error boundaries
4. Add loading states where missing
5. Document any API endpoint changes needed
