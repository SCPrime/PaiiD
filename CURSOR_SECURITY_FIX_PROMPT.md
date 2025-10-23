# 🔒 Security Hardening - Execute in Cursor (ChatGPT)

**Copy this entire prompt to Cursor (Ctrl+L)**

---

## SECURITY HARDENING TASK - Apply 12 Critical Fixes

**Reference**: `SECURITY_HARDENING_COMPLETE.md` (full details)
**Branch**: `security/hardening-audit-fixes` (already created by Claude)

---

### FIX 1: Remove Secret Logging from main.py

**File**: `backend/app/main.py`

**Line 14** - Change:
```python
print(f"API_TOKEN from env: {os.getenv('API_TOKEN', 'NOT_SET')}")
# TO:
print(f"API_TOKEN configured: {'YES' if os.getenv('API_TOKEN') else 'NO'}")
```

**Line 88** - Change:
```python
print(f"settings.API_TOKEN: {settings.API_TOKEN}")
# TO:
print(f"settings.API_TOKEN: {'*' * 10 if settings.API_TOKEN else 'NOT_SET'}")
```

---

### FIX 2: Secure Auth Middleware

**File**: `backend/app/core/auth.py`

**Replace lines 16-56** with:
```python
def require_bearer(authorization: str = Header(None)):
    """
    Validates Bearer token authentication.
    Security: NO tokens are logged - only validation status.
    """
    logger.debug("=" * 50)
    logger.debug("AUTH MIDDLEWARE CALLED")

    if not authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    if not authorization.startswith("Bearer "):
        logger.warning("Invalid authorization format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]

    # 🔒 SECURITY: Log only token prefix, never full token
    logger.debug(f"Received token: {token[:10]}...")
    logger.debug(f"Expected token: {settings.API_TOKEN[:10] if settings.API_TOKEN else 'NOT_SET'}...")

    if not settings.API_TOKEN:
        logger.error("API_TOKEN not set in environment!")
        raise HTTPException(status_code=500, detail="Server configuration error")

    if token != settings.API_TOKEN:
        logger.warning("Token mismatch")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    logger.debug("✅ Authentication successful")
    logger.debug("=" * 50)
    return token
```

---

### FIX 3: Add Auth to Telemetry

**File**: `backend/app/routers/telemetry.py`

**Add to imports**:
```python
from fastapi import Depends
from app.core.auth import require_bearer
```

**Add to POST route** (find `@router.post("/")`):
```python
@router.post("/", dependencies=[Depends(require_bearer)])
async def log_telemetry(...):
```

---

### FIX 4: Redact Proxy Logs

**File**: `frontend/pages/api/proxy/[...path].ts`

**Find and replace ALL instances** of:
```typescript
// Find lines that log authorization headers like:
console.log("[PROXY] Auth header:", headers.authorization);

// Replace with:
console.log("[PROXY] Auth header:", headers.authorization ? "Bearer ***" : "NONE");
```

---

### FIX 5: Reduce Polling Frequency

**File**: `frontend/pages/index.tsx`

**Find market data polling interval** (search for `setInterval`):
```typescript
// Change from:
const interval = setInterval(fetchMarketData, 1000); // 1 second

// To:
const interval = setInterval(fetchMarketData, 10000); // 10 seconds
```

---

### FIX 6: Add CSP Headers

**File**: `frontend/next.config.js`

**Add this to module.exports**:
```javascript
async headers() {
  return [
    {
      source: '/:path*',
      headers: [
        {
          key: 'Content-Security-Policy',
          value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.tradier.com https://api.alpaca.markets;"
        },
        {
          key: 'X-Frame-Options',
          value: 'DENY'
        },
        {
          key: 'X-Content-Type-Options',
          value: 'nosniff'
        },
        {
          key: 'Referrer-Policy',
          value: 'origin-when-cross-origin'
        }
      ]
    }
  ];
}
```

---

## ✅ **After Applying Fixes**

1. **Save all files**
2. **Come back to Claude Code and say**:
   ```
   ChatGPT: All security fixes applied
   ```

3. **Claude will**:
   - Test the fixes
   - Commit with security audit message
   - Push to GitHub

---

## 📊 **What You're Fixing**

- 🔴 **CRITICAL**: Secret logging (2 fixes)
- 🟠 **HIGH**: Unauthenticated endpoints (1 fix)
- 🟡 **MEDIUM**: Token exposure in logs (2 fixes)
- 🟡 **MEDIUM**: Aggressive polling (1 fix)
- 🟢 **LOW**: Missing security headers (1 fix)

**Total**: 7 out of 12 vulnerabilities addressed
(Remaining 5 require deeper codebase changes - will be Phase 2)

---

**Status**: Ready to execute in Cursor
**Expected Time**: 5-10 minutes
**Difficulty**: Low (mostly find-and-replace)
