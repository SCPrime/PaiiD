# Sentry Error Tracking - Quick Setup Guide

**Time to Complete:** 5 minutes
**Status:** Code is ready, just needs DSN configuration

---

## 🎯 WHAT YOU GET

- **Real-time Error Alerts** - Get notified immediately when errors occur
- **Stack Traces** - See exactly where errors happened in your code
- **User Context** - Know which users are affected
- **Performance Monitoring** - Track slow endpoints and queries
- **Session Replay** - Watch what users did before an error occurred

---

## 📝 STEP-BY-STEP SETUP

### Step 1: Create Sentry Account (2 minutes)

1. Go to https://sentry.io/signup/
2. Sign up with GitHub (fastest) or email
3. Choose "Free" plan (50,000 errors/month - plenty for MVP)
4. Click "Create Project"

### Step 2: Configure Project (1 minute)

1. Select Platform: **Next.js** (for frontend)
2. Set Alert Frequency: **On every new issue** (recommended)
3. Project Name: `paiid-frontend`
4. Click "Create Project"
5. **Copy the DSN** - looks like: `https://abc123@o123456.ingest.sentry.io/789`

### Step 3: Add DSN to Vercel (1 minute)

1. Go to https://vercel.com/dashboard
2. Select your project
3. Click "Settings" → "Environment Variables"
4. Add new variable:
   - **Name:** `NEXT_PUBLIC_SENTRY_DSN`
   - **Value:** (paste your DSN from Step 2)
   - **Environments:** Production, Preview, Development
5. Click "Save"
6. Redeploy your app (Settings → Deployments → Redeploy)

### Step 4: Configure Backend (1 minute)

1. In Sentry dashboard, click "Create Project" again
2. Select Platform: **FastAPI** or **Python**
3. Project Name: `paiid-backend`
4. **Copy the DSN**
5. Go to https://dashboard.render.com
6. Select your backend service
7. Click "Environment" tab
8. Add new variable:
   - **Key:** `SENTRY_DSN`
   - **Value:** (paste your backend DSN)
9. Click "Save Changes" (auto-redeploys)

---

## ✅ VERIFICATION

### Test Frontend Sentry (30 seconds)

1. Visit your deployed app
2. Open browser console (F12)
3. You should see: `[Sentry] ✅ Error tracking initialized`
4. Go to Sentry dashboard → Issues
5. Within 1-2 minutes, you'll see test events appear

### Test Backend Sentry (30 seconds)

1. Check backend logs at https://dashboard.render.com
2. You should see: `[OK] Sentry error tracking initialized`
3. Visit: https://paiid-backend.onrender.com/api/health
4. Go to Sentry backend project → Performance
5. You'll see the health check request appear

---

## 🔔 CONFIGURE ALERTS (Optional but Recommended)

1. In Sentry dashboard, go to **Alerts**
2. Click "Create Alert Rule"
3. Choose "Issues"
4. Set conditions:
   - When: **A new issue is created**
   - Then: **Send a notification to:**
   - Select: **Email** (or Slack if you have it)
5. Click "Save Rule"

Now you'll get emails when new errors occur!

---

## 📊 WHAT'S CONFIGURED

### Frontend (`frontend/lib/sentry.ts`)
- ✅ Browser error tracking
- ✅ Performance monitoring (10% sample)
- ✅ Session replay (10% sessions, 100% on errors)
- ✅ User context tracking
- ✅ Breadcrumbs for debugging
- ✅ Privacy-first (masks text, blocks media)
- ✅ Filters out API tokens and auth headers

### Backend (`backend/app/main.py`)
- ✅ FastAPI error tracking
- ✅ Performance monitoring (10% sample)
- ✅ Request context
- ✅ Environment detection (production vs development)
- ✅ Release tracking
- ✅ Auth header redaction

### ErrorBoundary Integration
- ✅ React errors automatically sent to Sentry
- ✅ Component stack traces included
- ✅ User-friendly fallback UI
- ✅ Graceful degradation if Sentry unavailable

---

## 🎯 WHAT TO MONITOR

### Critical Errors (Fix Immediately)
- `TypeError` - Usually indicates null/undefined bugs
- `Network Error` - API unavailable
- `Authorization Failed` - Token issues
- `Division by Zero` - Math errors in calculations

### Performance Issues (Optimize Later)
- Requests >1000ms - Slow API calls
- Transactions >3000ms - Slow page loads
- Memory leaks - Growing memory usage

### User Impact
- Error frequency by user - Who's affected most?
- Error frequency by endpoint - Which APIs are failing?
- Error frequency by browser - Browser-specific issues?

---

## 💡 PRO TIPS

### 1. Use Source Maps (Already Configured)
Your code is minified in production, but Sentry will show the original source code thanks to source maps automatically uploaded by Next.js.

### 2. Add Custom Context
```typescript
import { addBreadcrumb } from '../lib/sentry';

// Before making an API call
addBreadcrumb('Fetching user positions', { userId: user.id });

// Before a critical operation
addBreadcrumb('Executing trade', { symbol: 'AAPL', quantity: 100 });
```

### 3. Capture Custom Errors
```typescript
import { captureException, captureMessage } from '../lib/sentry';

try {
  // risky operation
} catch (error) {
  captureException(error as Error, {
    operation: 'trade_execution',
    symbol: 'AAPL'
  });
}

// Log important events
captureMessage('User exceeded daily trade limit', 'warning');
```

### 4. Set Up Slack Notifications
1. Sentry dashboard → **Settings** → **Integrations**
2. Find **Slack** → Click "Add to Slack"
3. Choose your Slack workspace and channel
4. Now errors appear in Slack instantly!

---

## 🚨 TROUBLESHOOTING

### Issue: "Sentry DSN not configured" in console

**Cause:** Environment variable not set or not deployed
**Fix:**
1. Verify `NEXT_PUBLIC_SENTRY_DSN` exists in Vercel
2. Redeploy your app
3. Hard refresh browser (Ctrl+Shift+R)

### Issue: No errors appearing in Sentry

**Cause:** Sampling rate too low or no errors occurring
**Fix:**
1. Trigger a test error (throw new Error in code)
2. Wait 1-2 minutes for Sentry to process
3. Check Sentry dashboard → Issues

### Issue: Too many errors flooding Sentry

**Cause:** High-frequency errors hitting rate limits
**Fix:**
1. Sentry dashboard → Project Settings → Inbound Filters
2. Add "Ignore errors from" rules
3. Filter out known non-critical errors

---

## 📈 SUCCESS METRICS

**After 24 hours with Sentry:**
- ✅ 0-5 new issues discovered (good - stable platform)
- ✅ 6-20 new issues discovered (normal - fixing bugs)
- ⚠️ 20+ new issues discovered (needs attention - stability issues)

**After 1 week:**
- ✅ Error rate < 1% (excellent)
- ✅ Average response time < 500ms (fast)
- ✅ All P0/P1 errors resolved (production-ready)

---

## 🎉 YOU'RE DONE!

Your platform now has **enterprise-grade error tracking**:
- Real-time visibility into production errors
- Stack traces for instant debugging
- Performance monitoring
- User impact analysis

**Sentry Setup Time:** 5 minutes
**Value Delivered:** Priceless 🚀

---

**Next Steps:**
1. Configure DSN (5 minutes)
2. Deploy and test
3. Set up Slack alerts
4. Monitor for 24 hours
5. Fix any issues that appear

**Questions?** Check https://docs.sentry.io/platforms/javascript/guides/nextjs/

---

_PaiiD - Now with enterprise-grade error tracking_ 🔍✨
