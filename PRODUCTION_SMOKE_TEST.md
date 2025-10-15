# PaiiD - Production Smoke Test Checklist

**Test Date:** October 15, 2025
**Test URL:** https://frontend-scprimes-projects.vercel.app
**Backend:** https://paiid-backend.onrender.com
**Tester:** [Your Name]

---

## ✅ Backend Status (Automated)

- ✅ **Backend Health:** OK (Redis connected, 1ms latency)
- ✅ **API Docs:** Accessible at https://paiid-backend.onrender.com/docs
- ✅ **Database:** PostgreSQL ready (via migrations)
- ✅ **SSE Endpoints:** Configured and ready

---

## 🧪 Frontend Smoke Tests (10 Workflows)

**Time Estimate:** 30-45 minutes
**Goal:** Verify each workflow loads and core functionality works

### Critical Tests (Must Pass)

#### 1. User Onboarding
- [ ] **Test:** First load shows UserSetupAI
- [ ] **Test:** Can skip setup or complete AI chat
- [ ] **Expected:** localStorage gets 'user-setup-complete'
- [ ] **Status:** _________

#### 2. Active Positions ⚡ CRITICAL
- [ ] **Test:** Navigate to Active Positions
- [ ] **Test:** Connection indicator shows "Live" (green WiFi icon)
- [ ] **Test:** Positions load from Alpaca
- [ ] **Test:** Metrics cards show portfolio value, buying power, P&L
- [ ] **Expected:** Real-time SSE connection established
- [ ] **Dev Tools Check:** Network tab shows `/api/proxy/api/stream/positions` EventStream
- [ ] **Status:** _________

#### 3. Execute Trade ⚡ CRITICAL
- [ ] **Test:** Navigate to Execute Trade
- [ ] **Test:** Fill in: Symbol (AAPL), Quantity (1), Side (Buy)
- [ ] **Test:** Click "Preview Order" or "Execute Trade"
- [ ] **Expected:** Dry-run order executes successfully
- [ ] **Console Check:** No 500 errors
- [ ] **Status:** _________

#### 4. AI Recommendations
- [ ] **Test:** Navigate to AI Recommendations
- [ ] **Test:** Click "Get Recommendations"
- [ ] **Expected:** 5 recommendations load with confidence scores
- [ ] **Test:** Portfolio analysis section shows risk/diversification
- [ ] **Test:** Click on a recommendation to expand details
- [ ] **Status:** _________

#### 5. Market Scanner
- [ ] **Test:** Navigate to Market Scanner
- [ ] **Test:** Enter filters (price range, volume, etc.)
- [ ] **Test:** Click "Scan Now"
- [ ] **Expected:** Scanner results appear
- [ ] **Status:** _________

---

### Standard Tests (Should Pass)

#### 6. P&L Dashboard (Analytics)
- [ ] **Test:** Navigate to Analytics
- [ ] **Test:** Equity curve chart renders
- [ ] **Test:** Daily P&L chart renders
- [ ] **Test:** TradingView widget loads (may take 5-10s)
- [ ] **Test:** Click "Export Chart" button
- [ ] **Expected:** PNG downloads
- [ ] **Status:** _________

#### 7. News Review
- [ ] **Test:** Navigate to News Review
- [ ] **Test:** Market sentiment section loads
- [ ] **Test:** News articles appear with timestamps
- [ ] **Test:** Click on a news article
- [ ] **Expected:** Opens in new tab
- [ ] **Status:** _________

#### 8. Strategy Builder AI
- [ ] **Test:** Navigate to Strategy Builder
- [ ] **Test:** Template gallery loads
- [ ] **Test:** Click on a strategy template
- [ ] **Test:** Click "Quick Clone" or "Customize"
- [ ] **Expected:** Modal opens with template details
- [ ] **Status:** _________

#### 9. Backtesting
- [ ] **Test:** Navigate to Backtesting
- [ ] **Test:** Select strategy, date range, initial capital
- [ ] **Test:** Click "Run Backtest"
- [ ] **Expected:** Results appear with equity curve
- [ ] **Status:** _________

#### 10. Settings
- [ ] **Test:** Navigate to Settings
- [ ] **Test:** Tabs switch (Account, Trading, Theme, etc.)
- [ ] **Test:** Adjust risk tolerance slider
- [ ] **Test:** Click "Save Settings"
- [ ] **Expected:** Toast notification appears
- [ ] **Status:** _________

---

## 🔥 Critical Path Test (5 min)

**This must work for launch:**

1. [ ] **Load site** → UserSetupAI appears
2. [ ] **Skip setup** → Radial menu appears
3. [ ] **Click "Active Positions"** → Positions load, "Live" indicator shows
4. [ ] **Click "Execute Trade"** → Form appears
5. [ ] **Submit dry-run order** → Success toast appears
6. [ ] **Click "AI Recommendations"** → 5 recommendations load

**If ALL 6 steps pass:** ✅ **READY FOR LAUNCH**

---

## 🐛 Known Issues Log

### Critical (P0) - Launch Blockers
*None currently identified*

### High Priority (P1)
*None currently identified*

### Medium Priority (P2)
*None currently identified*

### Low Priority (P3)
*None currently identified*

---

## 📊 Test Results Summary

**Date Tested:** __________
**Tester:** __________
**Browser:** Chrome / Safari / Edge (circle one)
**Device:** Desktop / Mobile (circle one)

**Results:**
- Critical Tests Passed: ___ / 5
- Standard Tests Passed: ___ / 5
- Critical Path Passed: Yes / No

**Overall Status:** PASS / FAIL / NEEDS FIXES

**Notes:**
_______________________________________________
_______________________________________________
_______________________________________________

---

## ✅ Sign-Off

**Tested By:** _______________
**Date:** _______________
**Status:** Ready for Launch / Needs Fixes

**Next Steps:**
- [ ] Mobile device testing (if not done)
- [ ] Configure Sentry DSN
- [ ] Run Alembic migration in production (if database used)
- [ ] Announce launch!

---

**Generated:** October 15, 2025
**Document Version:** 1.0
**For:** PaiiD MVP Launch (94% → 100%)
