# PaiiD Deployment Verification Checklist

**Last Updated**: October 15, 2025
**Latest Commit**: 0611579 (deployment fix + VS Code tooling)
**Expected Status**: All features deployed and visible

---

## Phase 1: Verify Deployed Commit on Render

### Frontend (paiid-frontend)
1. Go to: https://dashboard.render.com/web/srv-d3nqjbe3jptc73c5h0v0
2. Check **"Latest deploy"** section
3. **Expected commit**: `0611579` or newer
4. **If showing older commit** (3cba38b, c6ab6b5, 14cabba):
   - Auto-deploy is OFF or deployment failed
   - Proceed to Phase 2 (Manual Deploy)

### Backend (paiid-backend)
1. Go to: https://dashboard.render.com (find paiid-backend service)
2. Check **"Latest deploy"** section
3. **Expected commit**: `0611579` or newer
4. **Check deploy logs** for any errors

---

## Phase 2: Test Live Frontend Features

### Test 1: Basic Site Load
**URL**: https://paiid-frontend.onrender.com

**Expected**:
- ✅ Site loads without errors (no blank page)
- ✅ Dark gradient background (#0f1828 → #1a2a3f)
- ✅ **PaiiD logo** visible with:
  - "P" in teal
  - "aii" in teal with **GLOWING green animation** (key feature!)
  - "D" in teal
  - Subtitle: "10 Stage Workflow"

**If NOT seeing**:
- ❌ 404 error → Service not deployed
- ❌ Blank white page → Build failed
- ❌ Old layout → Wrong commit deployed

### Test 2: User Onboarding (First Visit)
**Action**: Clear site data and refresh (Ctrl+Shift+Delete → Clear cookies/storage)

**Expected**:
- ✅ **UserSetupAI modal** appears automatically
- ✅ AI chat interface with conversational questions
- ✅ "Skip to Dashboard" button visible
- ✅ Glassmorphic card with blur effect

**If NOT seeing**:
- ❌ No modal → Check localStorage: `user-setup-complete` should be missing
- ❌ Old form layout → Wrong component deployed

### Test 3: Radial Menu (10 Stages)
**Action**: Complete onboarding or use bypass (Ctrl+Shift+A)

**Expected - 10 Workflow Segments**:
1. 🌅 **Morning Routine** (Orange, #f97316)
2. 📊 **Active Positions** (Blue, #3b82f6)
3. ⚡ **Execute Trade** (Green, #10b981)
4. 🔍 **Research** (Purple, #8b5cf6)
5. 💡 **AI Recommendations** (Yellow, #facc15)
6. 📈 **P&L Dashboard** (Cyan, #06b6d4)
7. 📰 **News Review** (Pink, #ec4899)
8. 🛠️ **Strategy Builder** (Indigo, #6366f1)
9. 🎯 **Backtesting** (Teal, #14b8a6)
10. ⚙️ **Settings** (Gray, #6b7280)

**Center Logo**:
- ✅ "PaiiD" in center of radial menu (42px size)
- ✅ Market data (SPY/QQQ prices) below logo

**Interactions**:
- ✅ Hover segment → Border highlights, tooltip appears
- ✅ Click segment → Split-screen layout activates
- ✅ Keyboard: Tab to focus, Arrow keys to rotate, Enter to select

**If NOT seeing**:
- ❌ Only text/no visual → RadialMenu.tsx not deployed
- ❌ Wrong colors → Old version deployed
- ❌ <10 segments → Incomplete build

### Test 4: Split-Screen Layout
**Action**: Click any workflow segment

**Expected**:
- ✅ **Left panel** (40%): Scaled radial menu (0.5x) + logo header
- ✅ **Right panel** (60%): Workflow content
- ✅ **Draggable gutter** between panels (green indicator)
- ✅ Gutter shows vertical dots on hover

**Workflows to Test**:
- **Morning Routine** → AI-powered market briefing
- **Active Positions** → Table of current holdings
- **Execute Trade** → Order entry form with AI assist
- **Research** → Market scanner with filters
- **AI Recommendations** → Smart trade suggestions

**If NOT seeing**:
- ❌ Full-screen only → Split library not loaded
- ❌ No content → Component failed to load

### Test 5: Keyboard Shortcuts
**Action**: Press keys while on main menu

**Test**:
- `Tab` → Focus radial menu
- `← →` → Rotate segments
- `Enter` → Select focused segment
- `Esc` → Close split-screen
- `Ctrl+Shift+A` → **Admin bypass** (should show alert)

**Expected**:
- ✅ All shortcuts work without page reload
- ✅ Bottom bar shows keyboard hints

### Test 6: Mobile Responsiveness
**Action**: Open site on mobile device or resize browser <768px

**Expected**:
- ✅ Stacked layout (no split-screen)
- ✅ "← Menu" button appears when workflow selected
- ✅ Touch interactions work (tap segments)
- ✅ No keyboard shortcuts hint (hidden on mobile)

---

## Phase 3: Test Backend Connectivity

### Test 1: Health Check
**Action**: Visit https://paiid-backend.onrender.com/api/health

**Expected Response**:
```json
{
  "status": "ok",
  "time": "2025-10-15T17:48:46.843347+00:00",
  "redis": {
    "connected": true,
    "latency_ms": 1
  }
}
```

**If NOT seeing**:
- ❌ 404 error → Backend not deployed
- ❌ 500 error → Backend crashed (check logs)
- ❌ Timeout → Service sleeping (cold start ~30s)

### Test 2: CORS Configuration
**Action**: Open browser console (F12) on frontend, refresh page

**Expected**:
- ✅ **NO** CORS errors in console
- ✅ Successful API calls to paiid-backend.onrender.com

**If seeing**:
- ❌ `CORS policy: No 'Access-Control-Allow-Origin'` → Backend CORS misconfigured
- ❌ Check `backend/app/main.py` line 32: should have `paiid-frontend.onrender.com`

### Test 3: API Endpoints
**Action**: Test key endpoints via curl or browser:

```bash
# Market data
curl https://paiid-backend.onrender.com/api/market/indices

# User preferences (requires auth token)
curl -H "Authorization: Bearer rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl" \
  https://paiid-backend.onrender.com/api/users/preferences

# Strategy templates
curl https://paiid-backend.onrender.com/api/strategies/templates
```

**Expected**:
- ✅ All endpoints return JSON data (not errors)
- ✅ Response times <2 seconds

### Test 4: Frontend → Backend Integration
**Action**: Click "Morning Routine" workflow on frontend

**Expected**:
- ✅ Component loads market data from backend
- ✅ Browser console shows successful API calls
- ✅ Live prices displayed (not "Loading..." forever)

**If NOT seeing**:
- ❌ Check environment variables on Render:
  - Frontend: `NEXT_PUBLIC_BACKEND_API_BASE_URL=https://paiid-backend.onrender.com`
  - Backend: `ALLOW_ORIGIN=https://paiid-frontend.onrender.com`

---

## Phase 4: Verify Environment Variables

### Frontend Environment Variables (Render Dashboard)
**Required**:
1. ✅ `NEXT_PUBLIC_API_TOKEN` → Set via dashboard (not public)
2. ✅ `NEXT_PUBLIC_BACKEND_API_BASE_URL` → `https://paiid-backend.onrender.com`
3. ✅ `NEXT_PUBLIC_ANTHROPIC_API_KEY` → Set via dashboard
4. ✅ `NODE_ENV` → `production`
5. ✅ `PORT` → `3000`

### Backend Environment Variables (Render Dashboard)
**Required**:
1. ✅ `API_TOKEN` → Match frontend token
2. ✅ `ALPACA_PAPER_API_KEY` → Set for paper trading
3. ✅ `ALPACA_PAPER_SECRET_KEY` → Set for paper trading
4. ✅ `TRADIER_API_KEY` → Set for market data
5. ✅ `TRADIER_ACCOUNT_ID` → Set for market data
6. ✅ `ANTHROPIC_API_KEY` → Set for AI features
7. ✅ `ALLOW_ORIGIN` → `https://paiid-frontend.onrender.com`

---

## Phase 5: Performance Checks

### Frontend Performance
**Action**: Open Chrome DevTools → Lighthouse → Run audit

**Expected**:
- ✅ Performance: >80
- ✅ Accessibility: >90
- ✅ Best Practices: >85
- ✅ First Contentful Paint: <2s

### Backend Performance
**Action**: Test response times

```bash
time curl https://paiid-backend.onrender.com/api/health
```

**Expected**:
- ✅ Cold start (first request): <30s
- ✅ Warm requests: <1s
- ✅ Redis connected: true

---

## Phase 6: Feature-Specific Tests

### AI Features
**Test**: Click "AI Recommendations" workflow

**Expected**:
- ✅ AI analysis loads
- ✅ Trade suggestions appear
- ✅ "Ask AI" chat button works

### Trading Features
**Test**: Click "Execute Trade" workflow

**Expected**:
- ✅ Order form loads
- ✅ Stock lookup works
- ✅ Order preview shows calculated values

### Data Visualization
**Test**: Click "P&L Dashboard" workflow

**Expected**:
- ✅ Charts render (D3.js)
- ✅ Performance metrics display
- ✅ Historical data loads

---

## Common Issues & Solutions

### Issue: "sh: next: not found" in Render logs
**Solution**:
- ✅ **FIXED** in commit 0611579
- Check `package.json` line 7: should be `"start": "node server.js"`
- NOT `"start": "next start"`

### Issue: 502 Bad Gateway
**Causes**:
1. Service sleeping (cold start) → Wait 30 seconds
2. Build failed → Check Render logs for errors
3. Health check failing → Check `/` endpoint

**Solution**:
- Manual re-deploy on Render
- Check Docker build logs

### Issue: Features not visible
**Causes**:
1. Old commit deployed → Check "Latest deploy" on Render
2. Auto-deploy OFF → Enable in settings
3. Browser cache → Hard refresh (Ctrl+Shift+R)

**Solution**:
- Force manual deploy of latest commit
- Clear browser cache

### Issue: CORS errors in console
**Cause**: Backend not allowing frontend origin

**Solution**:
- Update `backend/app/main.py` CORS origins
- Verify `ALLOW_ORIGIN` env var on Render

---

## Success Criteria Checklist

All items must be ✅ for successful deployment:

### Visual Features
- [ ] PaiiD logo with glowing "aii" animation
- [ ] 10-stage radial menu with correct colors
- [ ] Split-screen layout works
- [ ] Glassmorphic dark theme throughout
- [ ] Mobile responsive layout

### Functional Features
- [ ] UserSetupAI onboarding on first visit
- [ ] All 10 workflows load correctly
- [ ] Keyboard shortcuts work
- [ ] AI chat modal opens
- [ ] Settings panel accessible

### Backend Connectivity
- [ ] Health check returns 200 OK
- [ ] No CORS errors in console
- [ ] Market data loads in workflows
- [ ] Redis connected: true
- [ ] API response times <2s

### Deployment Configuration
- [ ] Latest commit (0611579+) deployed
- [ ] Auto-deploy enabled
- [ ] All environment variables set
- [ ] No errors in Render logs
- [ ] Docker build succeeds

---

## If ALL Tests Pass

**Congratulations!** 🎉 PaiiD is fully deployed with all features visible.

**Next Steps**:
1. Test with real user account
2. Monitor Render logs for errors
3. Check SonarCloud for code quality
4. Plan next feature additions

---

## If Tests Fail

### Immediate Actions:
1. **Check Render Dashboard** for deployed commit
2. **Review Render logs** for errors
3. **Force manual re-deploy** of latest commit
4. **Clear browser cache** and test again
5. **Verify environment variables** are set

### Need Help?
- Render logs: Check for specific error messages
- GitHub Actions: Check CI/CD pipeline status
- Local test: Run `npm run build` to verify build works
- Rollback: Deploy last known working commit

---

**Generated**: October 15, 2025
**Commit**: 0611579
**Status**: Ready for verification
