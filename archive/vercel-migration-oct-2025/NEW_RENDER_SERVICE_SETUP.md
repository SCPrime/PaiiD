# Create New Render Service - Step-by-Step Guide

**Date:** October 12, 2025
**Reason:** Old `ai-Trader` service stuck on commit 41ea1be, refuses to deploy latest code
**Solution:** Create fresh service to deploy commit b8990b0 with Tradier integration

---

## Overview

We're creating a **NEW** Render service because the old one has a corrupted cache that keeps deploying an old commit (41ea1be from October 11) despite:
- Auto-deploy being ON
- 6+ newer commits in GitHub
- Multiple webhook triggers

This fresh service will:
- Pull latest code (commit b8990b0 or newer)
- Have Tradier integration working
- Have finnhub-python installed
- NO Alpaca market data calls

---

## Phase 1: Create New Render Service (5 minutes)

### Step 1: Go to Render Dashboard

1. Navigate to: **https://dashboard.render.com**
2. Click the blue **"New +"** button (top right)
3. Select: **"Web Service"**

### Step 2: Connect Repository

1. Find and select: **"SCPrime/ai-Trader"** repository
2. If not listed, click "Configure account" to grant access
3. Click **"Connect"** next to the repository

### Step 3: Configure Service Settings

Fill in these EXACT values:

**Name:**
```
paiid-backend
```

**Region:**
```
Oregon (US West)
```
*(Same as old service for consistency)*

**Branch:**
```
main
```

**Root Directory:**
```
backend
```
*(CRITICAL - must be set or deployment will fail!)*

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Instance Type:**
```
Free
```
*(You can upgrade later if needed)*

**Auto-Deploy:**
```
Yes - enabled
```

### Step 4: Create Service

1. Click **"Create Web Service"** (bottom of page)
2. Render will start building immediately
3. **DON'T WAIT** - Go to Phase 2 while it builds!

---

## Phase 2: Set Environment Variables (3 minutes)

### Critical Environment Variables

The new service needs these environment variables to work. **Set them NOW** while first build is running:

1. **In the NEW service**, go to: **Environment** tab (left sidebar)
2. Click **"Add Environment Variable"** for each one below:

### Required Variables:

**API_TOKEN:**
```
tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo
```

**TRADIER_API_KEY:**
```
(Copy from OLD ai-Trader service Environment tab)
```

**TRADIER_ACCOUNT_ID:**
```
(Copy from OLD ai-Trader service Environment tab)
```

**TRADIER_API_BASE_URL:**
```
https://api.tradier.com/v1
```

**ANTHROPIC_API_KEY:**
```
(Copy from OLD ai-Trader service Environment tab)
```

**ALLOW_ORIGIN:**
```
https://frontend-scprimes-projects.vercel.app
```

**LIVE_TRADING:**
```
false
```

**TRADING_MODE:**
```
paper
```

### Optional Variables (if you want Alpaca paper trading):

**ALPACA_PAPER_API_KEY:**
```
(Copy from OLD service if present)
```

**ALPACA_PAPER_SECRET_KEY:**
```
(Copy from OLD service if present)
```

**APCA_API_BASE_URL:**
```
https://paper-api.alpaca.markets
```

### Step 5: Save and Redeploy

1. After adding environment variables, Render will ask: **"Redeploy service?"**
2. Click **"Yes, redeploy"** or **"Save Changes"**
3. This triggers a fresh deploy with all environment variables

---

## Phase 3: Verify Deployment (5-10 minutes)

### Watch the Deploy

1. Go to **"Events"** tab
2. You should see: `Deploy started for b8990b0` (or a7a4ef2)
3. Click on the deploy to see live logs

### Check Logs for SUCCESS Indicators

Go to **"Logs"** tab and look for these lines:

#### ✅ SUCCESS Indicators:

**1. Correct Commit:**
```
==> Checking out commit b8990b0
```
OR
```
==> Checking out commit a7a4ef2
```
*(NOT 41ea1be!)*

**2. Finnhub Package Installing:**
```
Collecting finnhub-python>=1.4.0
```

**3. Tradier Integration Loaded:**
```
🚨 TRADIER INTEGRATION CODE LOADED - market.py
🚨 TRADIER INTEGRATION CODE LOADED - market_data.py
TRADIER_API_KEY configured: YES
```

**4. Finnhub Working:**
```
[OK] Finnhub provider initialized
```

**5. Service Live:**
```
==> Your service is live 🎉
Available at your primary URL https://paiid-backend.onrender.com
```

#### ❌ BAD Indicators (If you see these, something went wrong):

```
❌ Checking out commit 41ea1be
❌ [WARNING] News aggregator failed to initialize: No module named 'finnhub'
❌ paper-api.alpaca.markets:443 "GET /v2/stocks/
```

### Get Your New Backend URL

Once deployed, your new backend URL will be shown in:
- Events tab: "Available at https://paiid-backend.onrender.com"
- Settings → Domains section

**Copy this URL** - you'll need it for Phase 4!

Example URLs (yours will vary):
- `https://paiid-backend.onrender.com`
- `https://paiid-backend-xyz.onrender.com`

---

## Phase 4: Update Frontend to Use New Backend

### Option A: Update Vercel Environment Variable (Recommended)

1. Go to: **https://vercel.com/scprimes-projects/frontend**
2. Click: **Settings** → **Environment Variables**
3. Find: `NEXT_PUBLIC_BACKEND_API_BASE_URL`
4. Click: **Edit**
5. Change value to: `https://paiid-backend.onrender.com` (your actual new URL)
6. Click: **Save**
7. **Redeploy frontend**:
   - Go to **Deployments** tab
   - Click **"..."** on latest deployment
   - Select **"Redeploy"**

### Option B: Update Code (If env var doesn't exist)

If the environment variable doesn't exist in Vercel, let me know and I'll update the frontend code.

---

## Phase 5: Test New Backend

### Test Health Endpoint

```bash
curl https://paiid-backend.onrender.com/api/health
```

**Expected:**
```json
{"status":"ok","time":"2025-10-12T...","redis":{"connected":false}}
```

### Test Market Indices (Tradier Integration)

```bash
curl -H "Authorization: Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo" \
  https://paiid-backend.onrender.com/api/market/indices
```

**Expected (SUCCESS):**
```json
{
  "dow": {"last": 42850.23, "change": 156.78, "changePercent": 0.37},
  "nasdaq": {"last": 18645.91, "change": 112.45, "changePercent": 0.61},
  "source": "tradier"  ← CONFIRMS NEW CODE!
}
```

OR if Tradier fails but Claude AI works:
```json
{
  "dow": {...},
  "nasdaq": {...},
  "source": "claude_ai"  ← FALLBACK WORKING!
}
```

### Test Single Quote

```bash
curl -H "Authorization: Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo" \
  https://paiid-backend.onrender.com/api/market/quote/AAPL
```

**Expected:**
```json
{
  "symbol": "AAPL",
  "bid": 175.25,
  "ask": 175.30,
  "last": 175.28,
  "volume": 45678900,
  "timestamp": "2025-10-12T..."
}
```

### Test Multiple Quotes

```bash
curl -H "Authorization: Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo" \
  "https://paiid-backend.onrender.com/api/market/quotes?symbols=AAPL,MSFT,GOOGL"
```

**Expected:**
```json
{
  "AAPL": {"bid": 175.25, "ask": 175.30, "last": 175.28, ...},
  "MSFT": {"bid": 415.50, "ask": 415.60, "last": 415.55, ...},
  "GOOGL": {"bid": 142.80, "ask": 142.90, "last": 142.85, ...}
}
```

### Test Stock Scanner

```bash
curl -H "Authorization: Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo" \
  https://paiid-backend.onrender.com/api/market/scanner/under4
```

**Expected:**
```json
{
  "candidates": [
    {"symbol": "F", "price": 2.85, ...},
    {"symbol": "SOFI", "price": 3.45, ...}
  ],
  "count": 8
}
```

---

## Phase 6: Cleanup (After Confirming Working)

### Once ALL Tests Pass:

1. **Go to OLD service** (`ai-Trader`) in Render dashboard
2. **Settings** → Scroll to bottom
3. Click: **"Delete Service"**
4. Type service name to confirm: `ai-Trader`
5. Click: **"Delete"**

### Optional: Rename New Service

If you want the URL to stay as `ai-trader`:

1. **In NEW service**, go to: **Settings** → **Name**
2. Click: **"Edit"**
3. Change from `paiid-backend` to `ai-trader`
4. Save (this changes the URL to `ai-trader.onrender.com`)
5. **Update Vercel env var again** with new URL

---

## Troubleshooting

### If First Deploy Fails:

**Check Logs for:**
- Missing environment variables
- Python errors
- Build command errors

**Common Fixes:**
- Add missing environment variables in Environment tab
- Trigger manual redeploy: Events → "Manual Deploy"

### If Tests Return 401 Unauthorized:

**Check:**
- API_TOKEN environment variable is set correctly
- Using correct token in curl commands

**Fix:**
- Add/update API_TOKEN in Environment tab
- Redeploy service

### If Tradier Integration Not Working:

**Check Logs for:**
```
TRADIER_API_KEY configured: NO  ← BAD!
```

**Fix:**
- Add TRADIER_API_KEY and TRADIER_ACCOUNT_ID in Environment tab
- Redeploy service

### If Frontend Can't Connect:

**Check:**
- Vercel environment variable updated with correct URL
- Frontend redeployed after env var change
- ALLOW_ORIGIN in backend includes frontend URL

**Fix:**
- Update NEXT_PUBLIC_BACKEND_API_BASE_URL in Vercel
- Redeploy frontend
- Add frontend URL to ALLOW_ORIGIN in backend

---

## Summary Checklist

### ✅ Phase 1: Create Service
- [ ] New Render service created
- [ ] Name: `paiid-backend`
- [ ] Branch: `main`
- [ ] Root Directory: `backend`
- [ ] Build/Start commands correct

### ✅ Phase 2: Environment Variables
- [ ] API_TOKEN set
- [ ] TRADIER_API_KEY set
- [ ] TRADIER_ACCOUNT_ID set
- [ ] ANTHROPIC_API_KEY set
- [ ] ALLOW_ORIGIN set
- [ ] Service redeployed with env vars

### ✅ Phase 3: Verify Deployment
- [ ] Commit b8990b0 (or newer) deployed
- [ ] finnhub-python installed
- [ ] Tradier integration logs appear
- [ ] Service is live

### ✅ Phase 4: Update Frontend
- [ ] Vercel env var updated
- [ ] Frontend redeployed

### ✅ Phase 5: Test Endpoints
- [ ] /api/health works
- [ ] /api/market/indices returns "source": "tradier" or "claude_ai"
- [ ] /api/market/quote/AAPL works
- [ ] /api/market/quotes works
- [ ] /api/market/scanner/under4 works

### ✅ Phase 6: Cleanup
- [ ] All tests passing
- [ ] Old ai-Trader service deleted

---

**Status:** Ready to begin Phase 1
**Action Required:** User must create new Render service (I cannot do this programmatically)
**Next Step:** Follow Phase 1 instructions above
