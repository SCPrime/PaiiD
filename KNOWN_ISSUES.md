# Known Issues

## Options Endpoint 500 Error

**Route:** `/api/expirations/{symbol}`
**Status:** Returns 500 Internal Server Error, request never reaches handler
**Impact:** Frontend OptionsChain component can't load expiration dates dropdown
**Discovered:** 2025-10-22

### Root Cause
FastAPI routing/middleware issue prevents requests from reaching the endpoint handler.

**Evidence:**
- No logs showing request arrival at handler
- No exception caught by endpoint error handling
- Other endpoints work normally (`/api/health`, `/api/positions`, etc.)
- Route is properly defined and registered in `backend/app/routers/options.py:242`
- Router is properly included in `backend/app/main.py:224` with `/api` prefix
- TradierClient service imports successfully
- Server starts without errors

### Code Status
✅ Handler code is clean and production-ready
✅ TradierClient service properly structured
✅ Auth middleware functional
✅ Tradier API verified working externally

### Attempted Fixes
- Removed async/await (changed to sync function)
- Removed global exception handlers
- Simplified endpoint implementation
- Removed inline TradierClient class, used service import
- Removed auth dependency, then re-added it
- Tested with/without bearer token

### Workaround Options
1. **Frontend Direct Call:** Frontend can call Tradier API directly for expirations
2. **Mock Data:** Use static expiration dates for development
3. **Alternative Endpoint:** Create a different route pattern (e.g., `/api/options/expirations`)

### Next Steps
Requires Python debugger session to trace FastAPI routing internals:
- Attach `pdb` to uvicorn process
- Set breakpoint in FastAPI routing code
- Trace request path to identify where it's being blocked
- Check middleware stack execution order

### Related Files
- `backend/app/routers/options.py` - Endpoint definition (line 242)
- `backend/app/main.py` - Router registration (line 224)
- `backend/app/services/tradier_client.py` - TradierClient service
- `frontend/components/trading/OptionsChain.tsx` - Frontend component

---

## Working Systems

### Backend APIs
✅ `/api/health` - Health check
✅ `/api/account` - Account balance
✅ `/api/positions` - Portfolio positions
✅ `/api/market/indices` - Market indices data
✅ `/api/market/quote/{symbol}` - Stock quotes

### Frontend Components
✅ RadialMenu - 10-stage workflow navigation
✅ Split-screen UI - Menu + content panels
✅ Market data streaming - Real-time SPY/QQQ prices
✅ Authentication - Bearer token auth

### Integrations
✅ Tradier API - Market data (verified externally)
✅ Alpaca API - Paper trading account
✅ Anthropic API - AI chat features
