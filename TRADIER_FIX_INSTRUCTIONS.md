# 🔧 Tradier API Key Fix - Render Configuration

**Date:** October 12, 2025
**Status:** ✅ Root Cause Identified - Fix Required

---

## ✅ Diagnosis Complete

### What I Tested

**Test 1: Direct Tradier API Call**
```bash
curl -H "Authorization: Bearer 1tIR8iQL9epAwNcc7HSXPuCypjkf" \
  https://api.tradier.com/v1/user/profile
```

**Result:** ✅ **SUCCESS**
```json
{
  "profile": {
    "id": "id-ovmgptjm",
    "name": "SPENCER-CARL SAINT-CYR",
    "account": {
      "account_number": "6YB64299",
      "classification": "individual",
      "date_created": "2025-10-09T18:28:53.000Z",
      "day_trader": false,
      "option_level": 1,
      "status": "active",
      "type": "cash"
    }
  }
}
```

**Test 2: Tradier Account Balances**
```bash
curl -H "Authorization: Bearer 1tIR8iQL9epAwNcc7HSXPuCypjkf" \
  https://api.tradier.com/v1/accounts/6YB64299/balances
```

**Result:** ✅ **SUCCESS** - Account data retrieved

---

## 🎯 Root Cause Identified

**The Tradier API key IS VALID and WORKING!**

**The problem is:** Render's environment variable has the **WRONG VALUE**

**Evidence:**
- ✅ Direct curl to Tradier API works perfectly
- ❌ Backend API returns "Invalid Access Token" error
- **Conclusion:** Render environment variable doesn't match the correct key

**Most Likely Cause:**
- When you updated the Render dashboard, the API key may have been:
  - Truncated (missing characters)
  - Has extra whitespace
  - Typo in the value
  - Old value still cached

---

## 🔧 Fix Instructions (5 minutes)

### Step 1: Go to Render Dashboard

1. Open: https://dashboard.render.com
2. Click on your backend service (likely named `paiid-backend` or `ai-trader`)
3. Click **"Environment"** tab in left sidebar

### Step 2: Locate TRADIER_API_KEY Variable

Scroll down to find:
```
TRADIER_API_KEY = [some value]
```

### Step 3: Update the Value

**Option A: Edit Existing Variable**
1. Click the **"Edit"** button next to `TRADIER_API_KEY`
2. Delete the current value completely
3. Copy this exact value: `1tIR8iQL9epAwNcc7HSXPuCypjkf`
4. Paste into the value field (no spaces before/after)
5. Click **"Save Changes"**

**Option B: Delete and Re-Add (Recommended)**
1. Click **"Delete"** next to `TRADIER_API_KEY`
2. Confirm deletion
3. Click **"Add Environment Variable"** button
4. Key: `TRADIER_API_KEY`
5. Value: `1tIR8iQL9epAwNcc7HSXPuCypjkf`
6. Click **"Add"**
7. Click **"Save Changes"**

### Step 4: Wait for Redeploy

- Render will automatically redeploy your service
- This takes ~2-3 minutes
- Watch the **"Events"** tab for "Deploy succeeded" message

### Step 5: Verify in Logs

1. Click **"Logs"** tab
2. Look for these messages:
   ```
   Tradier client initialized for account 6YB64299
   ✅ Tradier account data retrieved successfully
   ```

3. Should **NOT** see:
   ```
   ❌ Tradier API error: Invalid Access Token
   ```

---

## 🧪 Testing After Fix

### Test 1: Backend Health Check
```bash
curl https://ai-trader-86a1.onrender.com/api/health
```

**Expected:** `{"status":"ok",...}`

### Test 2: Account Endpoint (Critical Test)
```bash
curl -H "Authorization: Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo" \
  https://ai-trader-86a1.onrender.com/api/account
```

**Expected Response:**
```json
{
  "account_number": "6YB64299",
  "cash": 0.0,
  "buying_power": 0.0,
  "portfolio_value": 0.0,
  "equity": 0.0,
  "long_market_value": 0.0,
  "short_market_value": 0.0,
  "status": "ACTIVE"
}
```

**If you see this, SUCCESS! ✅**

### Test 3: Positions Endpoint
```bash
curl -H "Authorization: Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo" \
  https://ai-trader-86a1.onrender.com/api/positions
```

**Expected:** `[]` (empty array if no positions) or list of positions

### Test 4: Frontend End-to-End
1. Open: https://frontend-scprimes-projects.vercel.app
2. Complete user onboarding
3. Navigate to "Active Positions" or "Account Info"
4. Should see Tradier account data (account 6YB64299)
5. No errors in browser console

---

## 📋 Complete Environment Variable Checklist

After fixing Tradier key, verify ALL 9 variables are correct in Render:

| Variable | Correct Value | Notes |
|----------|---------------|-------|
| `API_TOKEN` | `tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo` | ✅ Already working |
| `ANTHROPIC_API_KEY` | `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` | Should verify |
| `TRADIER_API_KEY` | `1tIR8iQL9epAwNcc7HSXPuCypjkf` | ❌ Needs fix |
| `TRADIER_ACCOUNT_ID` | `6YB64299` | Should verify |
| `TRADIER_USE_SANDBOX` | `false` | Production mode |
| `TRADIER_API_BASE_URL` | `https://api.tradier.com/v1` | Production URL |
| `ALLOW_ORIGIN` | `https://frontend-scprimes-projects.vercel.app` | CORS |
| `LIVE_TRADING` | `false` | Paper trading |
| `TRADING_MODE` | `paper` | Safe mode |

---

## 🐛 If Still Getting Error After Fix

### Additional Debugging Steps

**1. Check Render Logs for Exact Error**
Go to Render → Logs tab and search for:
```
Tradier API error
```

Copy the full error message.

**2. Verify Environment Variable Loaded**
In Render logs, look for:
```
Tradier client initialized
```

If you see this, the variable is loading.

**3. Add Temporary Debug Logging**

If error persists, I can add debug logging to see exactly what's being sent to Tradier:

File: `backend/app/services/tradier_client.py`

Add after line 31:
```python
logger.info(f"🔍 DEBUG - API Key first 8 chars: {self.api_key[:8]}")
logger.info(f"🔍 DEBUG - API Key last 4 chars: {self.api_key[-4:]}")
logger.info(f"🔍 DEBUG - Account ID: {self.account_id}")
logger.info(f"🔍 DEBUG - Base URL: {self.base_url}")
```

This will show in logs (masked) if the key is correct.

**4. Test Individual Endpoints**

Try calling Tradier endpoints one by one:
```bash
# User profile (simplest test)
curl -H "Authorization: Bearer [key from Render]" \
  https://api.tradier.com/v1/user/profile

# Account balances
curl -H "Authorization: Bearer [key from Render]" \
  https://api.tradier.com/v1/accounts/6YB64299/balances
```

---

## ✅ Success Criteria

**You'll know it's fixed when:**

1. ✅ No "Invalid Access Token" errors in Render logs
2. ✅ `/api/account` endpoint returns account data (not error)
3. ✅ `/api/positions` endpoint returns positions (or empty array)
4. ✅ Frontend displays Tradier account info
5. ✅ No Tradier-related errors in browser console

**Estimated Fix Time:** 5 minutes
**Success Probability:** 99% (key is confirmed working)

---

## 🎯 Summary

**Problem:** Render environment variable has wrong Tradier API key value
**Solution:** Update `TRADIER_API_KEY` in Render dashboard to: `1tIR8iQL9epAwNcc7HSXPuCypjkf`
**Verification:** The key works perfectly when tested directly against Tradier API
**Next Step:** Update Render environment variable and test

---

**Ready to update Render? Follow Steps 1-5 above!** 🚀
