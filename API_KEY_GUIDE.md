# PaiiD API Key Configuration Guide

This document explains every API key in your `.env` files, what they're used for, and where to get them.

## ✅ ALREADY CONFIGURED (From Your List)

### 1. Custom Backend API Token
**Current Value:** `tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo`
**Purpose:** Secures communication between your frontend and backend
**Source:** You generated this yourself (it's in your credentials list)
**Action Required:** None - already working
**Files Using It:**
- `backend/.env` → `API_TOKEN`
- `frontend/.env.local` → `NEXT_PUBLIC_API_TOKEN`

---

### 2. Alpaca Paper Trading API
**Current Values:**
- API Key: `PKZOA0NRY3QYX6N04X7E`
- Secret Key: `SlqOecEmLf9uihsEmBIT38bt0sdxFQXWdUME5isX`

**Purpose:** Execute paper trades (simulated trading, no real money)
**Where to Get:** https://app.alpaca.markets/paper/dashboard/overview
**Action Required:** ⚠️ ROTATE AFTER TESTING (these keys were exposed publicly)
**Files Using It:**
- `backend/.env` → `ALPACA_PAPER_API_KEY`, `ALPACA_PAPER_SECRET_KEY`

**How to Rotate:**
1. Go to https://app.alpaca.markets/paper/dashboard/overview
2. Click "Regenerate API Keys"
3. Copy new keys to `backend/.env`
4. Restart backend server

---

### 3. Tradier API (Market Data)
**Current Values:**
- API Key: `1tIR8iQL9epAwNcc7HSXPuCypjkf`
- Account ID: `6YB64299`

**Purpose:** Real-time market quotes, historical data, options chains
**Where to Get:** https://developer.tradier.com/
**Action Required:** ⚠️ ROTATE AFTER TESTING (exposed publicly)
**Files Using It:**
- `backend/.env` → `TRADIER_API_KEY`, `TRADIER_ACCOUNT_ID`

**How to Rotate:**
1. Go to https://developer.tradier.com/
2. Login as user "Super_Cool"
3. Navigate to "API Access"
4. Generate new API key
5. Update `backend/.env`

---

### 4. Anthropic Claude API
**Current Value:** `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`

**Purpose:** AI-powered trading recommendations, chat features, strategy analysis
**Where to Get:** https://console.anthropic.com/settings/keys
**Action Required:** ⚠️ ROTATE AFTER TESTING (3 keys exposed publicly)
**Files Using It:**
- `backend/.env` → `ANTHROPIC_API_KEY`
- `frontend/.env.local` → `NEXT_PUBLIC_ANTHROPIC_API_KEY`

**How to Rotate:**
1. Go to https://console.anthropic.com/settings/keys
2. Delete ALL exposed keys:
   - `sk-ant-api03-3du5KZQNDEQH4LqAOagRla...` (PaiiD key)
   - `sk-ant-api03-xAC9YcAfBvuRrBbqOT7ayEC...` (PaiiD v2.0)
   - `sk-ant-api03-gPJ-JjR5y0Sq55RpUTSZRKQ...` (PaiiD v2.002 - currently active)
3. Create ONE new key
4. Update both `.env` files
5. Restart backend server

---

### 5. PostgreSQL Database (Render)
**Current Connection String:**
```
postgresql://paiid_user:uxjNib9k8jrF1g1OyBlk2pIptxHM9vUG@dpg-d3m9etumcj7s73age4gg-a.oregon-postgres.render.com/paiid_db
```

**Purpose:** Stores user data, trades, strategies, historical performance
**Where to Manage:** https://dashboard.render.com/
**Action Required:** ⚠️ ROTATE PASSWORD AFTER TESTING
**Files Using It:**
- `backend/.env` → `DATABASE_URL`

**How to Rotate:**
1. Go to https://dashboard.render.com/
2. Find your PostgreSQL service `paiid_db`
3. Click "Reset Database Password"
4. Copy new connection string
5. Update `backend/.env`

---

### 6. Redis Cache (Render)
**Current Value:** `redis://red-d3n6o4adbo4c73dr06dg:6379`

**Purpose:** Caches market data for faster performance
**Where to Manage:** https://dashboard.render.com/
**Status:** ⚠️ Currently failing to connect (hostname not resolving)
**Action Required:** Fix Redis URL format (missing credentials or wrong hostname)

**Correct Format Should Be:**
```
redis://default:PASSWORD@red-d3n6o4adbo4c73dr06dg.oregon-redis.render.com:6379
```

**To Fix:**
1. Go to https://dashboard.render.com/
2. Find your Redis instance
3. Copy the **External Connection String** (not Internal)
4. Update `backend/.env` → `REDIS_URL`

---

### 7. Sentry Error Tracking
**Current Value:** `https://6271697e50c97cf94696e5239a1c7ea9@o4510184169144320.ingest.us.sentry.io/4510191168323584`

**Purpose:** Monitors errors and performance in production
**Where to Manage:** https://sentry.io/
**Action Required:** ✅ Working, but rotate after testing (DSN exposed)
**Files Using It:**
- `backend/.env` → `SENTRY_DSN`

**How to Rotate:**
1. Go to https://sentry.io/settings/projects/paiid/keys/
2. Regenerate the DSN
3. Update `backend/.env`

---

### 8. News API Keys (Optional - Already Working!)

#### Finnhub
**Current Value:** `d3jv3d9r01qtciv0n8jgd3jv3d9r01qtciv0n8k0`
**Purpose:** Financial news aggregation
**Where to Get:** https://finnhub.io/register
**Status:** ✅ Working

#### Alpha Vantage
**Current Value:** `V9EG1Z3TPETGAJO9`
**Purpose:** Market news and data
**Where to Get:** https://www.alphavantage.co/support/#api-key
**Status:** ✅ Working

#### Polygon
**Current Value:** `bOg6WM_KKgATQvpN_DLrdm8RHqxImrvE`
**Purpose:** Market data and news
**Where to Get:** https://polygon.io/dashboard/api-keys
**Status:** ✅ Working

---

## 🚨 KEYS THAT MUST BE ROTATED AFTER TESTING

Because you posted these keys publicly in this conversation, they are compromised. Here's the priority order:

### CRITICAL (Rotate Immediately After Testing):
1. **Alpaca Paper API Keys** - Can execute trades on your account
2. **Tradier API Key** - Live market data access
3. **Anthropic API Keys** - Can rack up AI usage charges
4. **Custom API Token** - Secures your frontend/backend connection

### HIGH PRIORITY:
5. **PostgreSQL Password** - Full database access
6. **Sentry DSN** - Error tracking access

### MEDIUM PRIORITY:
7. **Redis URL** - Caching only
8. **News API Keys** - Limited free tier abuse

---

## 📋 POST-TESTING ROTATION CHECKLIST

Once you've tested the app and confirmed everything works, follow these steps:

### Step 1: Rotate Alpaca Keys
- [ ] Go to https://app.alpaca.markets/paper/dashboard/overview
- [ ] Click "Regenerate API Keys"
- [ ] Copy new `ALPACA_PAPER_API_KEY` and `ALPACA_PAPER_SECRET_KEY`
- [ ] Update `backend/.env`

### Step 2: Rotate Tradier Key
- [ ] Go to https://developer.tradier.com/
- [ ] Delete old API key
- [ ] Generate new API key
- [ ] Update `backend/.env` → `TRADIER_API_KEY`

### Step 3: Rotate Anthropic Keys
- [ ] Go to https://console.anthropic.com/settings/keys
- [ ] Delete all 3 exposed keys
- [ ] Create 1 new key
- [ ] Update `backend/.env` → `ANTHROPIC_API_KEY`
- [ ] Update `frontend/.env.local` → `NEXT_PUBLIC_ANTHROPIC_API_KEY`

### Step 4: Generate New Custom API Token
Run this command to generate a new secure token:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
- [ ] Copy the generated token
- [ ] Update `backend/.env` → `API_TOKEN`
- [ ] Update `frontend/.env.local` → `NEXT_PUBLIC_API_TOKEN`

### Step 5: Rotate Database Password
- [ ] Go to https://dashboard.render.com/
- [ ] Find PostgreSQL service `paiid_db`
- [ ] Reset password
- [ ] Copy new connection string
- [ ] Update `backend/.env` → `DATABASE_URL`

### Step 6: Fix Redis URL
- [ ] Go to https://dashboard.render.com/
- [ ] Find Redis instance
- [ ] Copy **External Connection String**
- [ ] Update `backend/.env` → `REDIS_URL`

### Step 7: Rotate Sentry DSN
- [ ] Go to https://sentry.io/settings/projects/paiid/keys/
- [ ] Regenerate DSN
- [ ] Update `backend/.env` → `SENTRY_DSN`

### Step 8: Restart Services
- [ ] Stop backend server (Ctrl+C)
- [ ] Restart: `cd backend && python -m uvicorn app.main:app --reload --port 8001`
- [ ] Restart frontend: `cd frontend && npm run dev`
- [ ] Test all endpoints to confirm new keys work

---

## ❓ QUESTIONS?

**Q: Do I need to get NEW API keys from external services?**
A: NO! You already have all the keys you need. You just need to ROTATE (regenerate) them after testing because they were exposed publicly.

**Q: What's the Custom API Token and where do I get it?**
A: It's YOUR internal token for securing frontend-backend communication. You already generated it (`tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo`). After testing, generate a new one using the Python command above.

**Q: Why is Redis failing to connect?**
A: The hostname format looks incomplete. You need the full External Connection String from Render, which includes credentials and the full hostname (e.g., `red-xxx.oregon-redis.render.com`).

**Q: Can I skip rotating the keys?**
A: NO! These keys were posted publicly in this conversation and could be used by anyone to access your accounts, rack up API charges, or compromise your database. You MUST rotate them.

---

## 🎯 CURRENT STATUS

✅ All services configured and starting successfully
✅ Backend server running on http://127.0.0.1:8001
✅ PostgreSQL database connected
✅ Sentry error tracking active
✅ News aggregators working
⚠️ Redis connection failing (needs correct URL format)
⚠️ Tradier streaming timeouts (non-critical, will retry)
🔴 `/api/account` and `/api/positions` returning 500 errors (needs investigation)

**Next Step:** Fix the 500 errors on account/positions endpoints so you can test the full app!
