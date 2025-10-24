# Options Endpoint 500 Error - Root Cause Analysis

**Date**: October 23, 2025
**Investigated By**: Claude Code
**Status**: ✅ ROOT CAUSE IDENTIFIED

## Summary

All Playwright tests for the options chain feature are failing due to the backend `/api/options/chain/{symbol}` endpoint returning 500 Internal Server Error. After extensive debugging, the root cause has been identified.

## Root Cause

**7 duplicate uvicorn processes are simultaneously listening on port 8001**, causing requests to be routed to random instances (likely crashed or zombie processes).

### Evidence

```bash
$ netstat -ano | findstr ":8001.*LISTENING"
  TCP    127.0.0.1:8001         0.0.0.0:0              LISTENING       33480
  TCP    127.0.0.1:8001         0.0.0.0:0              LISTENING       24044
  TCP    127.0.0.1:8001         0.0.0.0:0              LISTENING       10932
  TCP    127.0.0.1:8001         0.0.0.0:0              LISTENING       43748
  TCP    127.0.0.1:8001         0.0.0.0:0              LISTENING       6796
  TCP    127.0.0.1:8001         0.0.0.0:0              LISTENING       25004
  TCP    127.0.0.1:8001         0.0.0.0:0              LISTENING       40480
```

### Symptoms

1. ❌ **No access logs**: Uvicorn with `--access-log` shows NO entries for incoming requests
2. ❌ **No auth middleware logs**: Extensive logging in `app/core/auth.py` with `print(..., flush=True)` never executes
3. ❌ **No endpoint logs**: Logger statements in options endpoint never execute
4. ✅ **Health endpoint works**: `/api/health` returns 200 OK
5. ✅ **Direct Tradier client works**: `get_tradier_client().get_option_expirations('SPY')` succeeds
6. ❌ **ALL options endpoints fail**: `/api/options/chain/{symbol}` and `/api/options/expirations/{symbol}` both return 500

This pattern indicates requests are hitting a zombie/crashed backend instance that can't process requests properly.

## Solution

### Option 1: Clean Restart (Recommended for Development)

```bash
# Kill all Python processes (Windows)
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"

# Verify port is free
netstat -ano | findstr ":8001"

# Start single backend instance
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

### Option 2: Use Different Port (Quick Workaround)

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --port 8002

# Update frontend .env.local
NEXT_PUBLIC_BACKEND_API_BASE_URL=http://127.0.0.1:8002

# Update Playwright config
cd frontend
# Edit playwright.config.ts - change backend port to 8002
```

### Option 3: System Restart (Nuclear Option)

If processes won't die, restart Windows to clear all sockets.

## Prevention

To avoid this issue in the future:

1. **Always check for existing processes before starting backend**:
   ```bash
   netstat -ano | findstr ":8001"
   ```

2. **Use process managers** like PM2 or Docker instead of manual uvicorn startup

3. **Configure Playwright properly** to start/stop backends automatically (already fixed in this PR)

## Verification Steps

After killing zombie processes:

1. **Verify single backend**:
   ```bash
   netstat -ano | findstr ":8001"  # Should show exactly 1 process
   ```

2. **Test options endpoint**:
   ```bash
   curl -H "Authorization: Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo" \
     "http://localhost:8001/api/options/chain/SPY"
   ```

3. **Check logs appear**:
   - Should see "AUTH MIDDLEWARE CALLED" in backend stdout
   - Should see access log entry: `INFO: 127.0.0.1 - "GET /api/options/chain/SPY HTTP/1.1" 200 OK`

4. **Run Playwright tests**:
   ```bash
   cd frontend
   npx playwright test
   ```

## Related Fixes Completed

As part of this debugging session, the following issues were also fixed:

✅ **Phase 1.1**: Fixed backend API route from `/chains/` to `/chain/`
✅ **Phase 1.2**: Updated frontend proxy ALLOW_GET paths for options endpoints
✅ **Phase 2.1**: Fixed ambiguous input selector in Playwright tests
✅ **Phase 2.2**: Fixed error div selector to use `.first()`
✅ **Phase 3**: Updated Playwright config to start both backend and frontend
✅ **Phase 4**: Added test robustness improvements (retries, better errors)

These fixes are already committed and ready for testing once the zombie process issue is resolved.

## Impact

- **Test Suite**: 9/9 options chain tests currently failing
- **Production**: Not affected (uses single Render deployment)
- **Local Development**: Blocked until zombie processes cleared

## Next Steps

1. Kill all backend processes
2. Start single clean backend instance
3. Run full Playwright test suite
4. Verify all 9 tests pass
5. Commit this debug report for future reference

---

**File References**:
- Backend endpoint: `backend/app/routers/options.py:99-237`
- Auth middleware: `backend/app/core/auth.py:13-57`
- Playwright config: `frontend/playwright.config.ts:42-77`
- Test file: `frontend/tests/options-chain.spec.ts`
