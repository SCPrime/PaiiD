# PaiiD Backend Documentation

## Phase 1 Options Trading Implementation

This directory contains reference documentation for implementing the options trading features in PaiiD.

### 🔄 2025-10-24 Regression Recovery Snapshot

Recent regressions around authentication and the options expirations endpoint have been addressed. Key updates:

- **JWT-first authentication:** every router now relies on `app.core.jwt.get_current_user` (via `CurrentUser` / `require_current_user`). Legacy API tokens are no longer accepted for protected endpoints.
- **Options expirations reliability:** the `/api/options/expirations/{symbol}` handler guards against Tradier client misconfiguration and returns structured cache-friendly data, eliminating the 500 error reported in `BUG_REPORT_OPTIONS_500.md`.
- **Telemetry metadata:** high-value market responses (`/api/market/quote*`, options chains, portfolio data) now include a `source` flag (e.g. `tradier`, `cache`) so downstream consumers can track provenance.
- **Tests & tooling:** backend pytest coverage exercises login + token refresh, options chains/expirations, and cached responses. Playwright/API suites were extended to mirror these flows.

See `docs/RELEASE_NOTES.md` for the detailed changelog and verification checklist.

### 📚 Documents

1. **TRADIER_IMPLEMENTATION.md** ⭐ **PRIMARY REFERENCE**
   - Complete Tradier API integration guide
   - Production-ready FastAPI code (copy-paste ready)
   - Next.js SSE streaming implementation
   - Fixes for 405/500 errors and stale data
   - **Use this for Phase 1 (6-8 hours)**

2. **STREAMING_ARCHITECTURE.md** 📖 **ADVANCED REFERENCE**
   - Full 4-tier failover architecture
   - Tradier → Polygon.io → REST → Cache
   - Circuit breakers, health monitoring, reconnection logic
   - **Use for Phase 2+ (when building production reliability)**

### 🎯 Quick Start for Phase 1

```bash
# Step 1: Read TRADIER_IMPLEMENTATION.md
# Step 2: Extract backend code (lines 76-527)
# Step 3: Extract frontend code (lines 435-750)
# Step 4: Deploy and test
```

### 📋 Phase 1 Scope (from TODO.md)

- [ ] Options chain API integration (Alpaca)
- [ ] Greeks calculation (delta, gamma, theta, vega)
- [ ] Options-specific trade execution
- [ ] Add to RadialMenu workflow
- [ ] Test with paper trading account

**Estimated Time:** 6-8 hours

### 🔗 Key Sections

**TRADIER_IMPLEMENTATION.md:**
- Lines 76-240: Complete FastAPI backend with TradierClient
- Lines 242-527: Next.js RadialHub component with SSE
- Lines 528-750: Options Greeks streaming endpoint
- Lines 752-850: Deployment configurations (Render + Vercel)

**STREAMING_ARCHITECTURE.md:**
- Tier 1: Primary WebSocket (use this pattern)
- Tier 2-4: Backup tiers (implement in Phase 2)
- Testing procedures and monitoring setup

### 💡 Usage Tips

**For Dr. Cursor Claude:**
```
"Read backend/docs/TRADIER_IMPLEMENTATION.md and implement:
1. TradierClient class (lines 76-141)
2. /api/market/indices endpoint (lines 149-240)
3. Frontend RadialHub component (lines 435-527)

Adapt for 6-8 hour Phase 1 scope."
```

**For Quick Reference:**
- Tradier session creation: TRADIER_IMPLEMENTATION.md lines 107-120
- SSE streaming pattern: TRADIER_IMPLEMENTATION.md lines 149-240
- Options Greeks: TRADIER_IMPLEMENTATION.md lines 528-606
- Testing procedures: TRADIER_IMPLEMENTATION.md lines 852-900

### ⚠️ Important Notes

1. **Use Tradier for market data ONLY** (not execution)
2. **Use Alpaca for execution ONLY** (not quotes)
3. **X-Accel-Buffering: no** header is critical for Render
4. **Cache-busting** required for EventSource (`?t=${Date.now()}`)
5. **Greeks update hourly** via ORATS (Tradier integration)

### 🚀 Next Steps

After reading both documents:
1. Implement backend FastAPI code from TRADIER_IMPLEMENTATION.md
2. Test with `curl` before touching frontend
3. Implement frontend SSE connection
4. Test on localhost:3000
5. Deploy to Render + Vercel
6. Monitor with Render logs

---

**Last Updated:** October 22, 2025
**Phase:** 0 → 1 Transition
**Status:** Ready for Implementation
