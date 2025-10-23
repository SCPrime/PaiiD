# ⚡ QUICK FIXES - P0 Critical Issues

**Total P0 Issues:** 12
**Estimated Fix Time:** 18 hours over 3 days
**Blocking Production:** YES

---

## DAY 1 FIXES (6 hours)

### Fix 1: API Contract Path Parameters (2 hours)

**Issue:** Frontend proxy doesn't handle dynamic path parameters

**File:** `frontend/pages/api/proxy/[...path].ts`

**Change lines 206-232:**

```typescript
// BEFORE (static match only)
if (req.method === "GET" && !ALLOW_GET.has(path)) {
  const isAllowedPattern = Array.from(ALLOW_GET).some(
    (allowed) => path.startsWith(allowed + "/") || path === allowed
  );
  if (!isAllowedPattern) {
    return res.status(405).json({ error: "Not allowed" });
  }
}

// AFTER (pattern matching with path params)
function isPathAllowed(path: string, allowedSet: Set<string>, method: string): boolean {
  // Exact match
  if (allowedSet.has(path)) return true;

  // Pattern match for paths with params
  for (const allowed of allowedSet) {
    // Handle trailing wildcards: "market/quote" allows "market/quote/AAPL"
    if (path.startsWith(allowed + "/")) return true;

    // Handle param placeholders: "market/quote/{symbol}" matches "market/quote/AAPL"
    const pattern = allowed.replace(/\{[^}]+\}/g, "[^/]+");
    const regex = new RegExp(`^${pattern}$`);
    if (regex.test(path)) return true;
  }

  return false;
}

// Then replace all method checks:
if (req.method === "GET" && !isPathAllowed(path, ALLOW_GET, "GET")) {
  return res.status(405).json({ error: "Not allowed" });
}
if (req.method === "POST" && !isPathAllowed(path, ALLOW_POST, "POST")) {
  return res.status(405).json({ error: "Not allowed" });
}
if (req.method === "DELETE" && !isPathAllowed(path, ALLOW_DELETE, "DELETE")) {
  return res.status(405).json({ error: "Not allowed" });
}
```

---

### Fix 2: Add Missing Backend Endpoints (3 hours)

**File 1:** `backend/app/routers/alpaca_passthrough.py` (NEW FILE)

```python
"""Alpaca API passthrough endpoints for direct client access"""
from fastapi import APIRouter, Depends, HTTPException
from ..core.jwt import get_current_user
from ..services.alpaca_client import get_alpaca_client

router = APIRouter(prefix="/api", tags=["alpaca"])

@router.get("/assets")
async def get_assets(current_user = Depends(get_current_user)):
    """Get list of tradeable assets from Alpaca"""
    try:
        client = get_alpaca_client()
        # Alpaca Python SDK: trading_client.get_all_assets()
        assets = client.get_all_assets()
        return [a.dict() for a in assets]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clock")
async def get_clock(current_user = Depends(get_current_user)):
    """Get market clock from Alpaca"""
    try:
        client = get_alpaca_client()
        clock = client.get_clock()
        return clock.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar")
async def get_calendar(current_user = Depends(get_current_user)):
    """Get market calendar from Alpaca"""
    try:
        client = get_alpaca_client()
        calendar = client.get_calendar()
        return [c.dict() for c in calendar]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/watchlists")
async def get_watchlists(current_user = Depends(get_current_user)):
    """Get user watchlists from Alpaca"""
    try:
        client = get_alpaca_client()
        watchlists = client.get_watchlists()
        return [w.dict() for w in watchlists]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/watchlists")
async def create_watchlist(name: str, symbols: list[str], current_user = Depends(get_current_user)):
    """Create new watchlist in Alpaca"""
    try:
        client = get_alpaca_client()
        watchlist = client.create_watchlist(name, symbols)
        return watchlist.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/watchlists/{watchlist_id}")
async def delete_watchlist(watchlist_id: str, current_user = Depends(get_current_user)):
    """Delete watchlist from Alpaca"""
    try:
        client = get_alpaca_client()
        client.delete_watchlist(watchlist_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**File 2:** `backend/app/main.py` - Add router registration

```python
# Add import (line 28)
from .routers import alpaca_passthrough

# Add router (line 256, after telemetry)
app.include_router(alpaca_passthrough.router)
```

---

### Fix 3: Environment Variable Naming (15 minutes)

**File:** `backend/app/routers/orders.py`

**Change lines 38-40:**

```python
# BEFORE
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# AFTER
from ..core.config import settings

# Then replace all uses of ALPACA_API_KEY with settings.ALPACA_API_KEY
# And all uses of ALPACA_SECRET_KEY with settings.ALPACA_SECRET_KEY

# Update line 51:
# BEFORE
api_key=ALPACA_API_KEY,
secret_key=ALPACA_SECRET_KEY,

# AFTER
api_key=settings.ALPACA_API_KEY,
secret_key=settings.ALPACA_SECRET_KEY,
```

---

### Fix 4: Delete Duplicate Greeks Implementation (30 minutes)

**Step 1:** Delete file
```bash
rm backend/app/services/greeks.py
```

**Step 2:** Update imports in 3 files

**File 1:** `backend/app/services/position_tracker.py` (line 11)
```python
# BEFORE
from app.services.greeks import GreeksCalculator

# AFTER
from app.services.options_greeks import GreeksCalculator
```

**File 2:** `backend/app/routers/positions.py` (if imported)
```python
# Check for any imports of greeks.py and update to options_greeks.py
```

**File 3:** `backend/app/routers/options.py` (if imported)
```python
# Check for any imports of greeks.py and update to options_greeks.py
```

---

### Fix 5: JWT Secret Validation (10 minutes)

**File:** `backend/app/core/config.py`

**Change lines 43-49:**

```python
# BEFORE
JWT_SECRET_KEY: str = os.getenv(
    "JWT_SECRET_KEY", "dev-secret-key-change-in-production-NEVER-COMMIT-THIS"
)

# AFTER
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")

# ADD after Settings class definition:
def __post_init__(self):
    """Validate settings after initialization"""
    # Validate JWT secret in production
    if not self.TESTING:
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY environment variable must be set!")
        if self.JWT_SECRET_KEY == "dev-secret-key-change-in-production-NEVER-COMMIT-THIS":
            raise ValueError("JWT_SECRET_KEY must not use default value in production!")
        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters!")
```

**Also update `backend/app/main.py`:**

```python
# Add after line 93 (settings loaded)
print(f"\n===== JWT VALIDATION =====")
print(f"JWT_SECRET_KEY length: {len(settings.JWT_SECRET_KEY)} chars")
print(f"JWT_SECRET_KEY valid: {'YES' if len(settings.JWT_SECRET_KEY) >= 32 else 'NO'}")
print("==========================\n", flush=True)
```

---

## DAY 2 FIXES (8 hours)

### Fix 6: Consolidate Authentication to JWT (4 hours)

**Step 1:** Identify all endpoints using `require_bearer` (22 router files)

**File:** `backend/app/routers/portfolio.py`

**Change all endpoints:**

```python
# BEFORE
from ..core.auth import require_bearer

@router.get("/account", dependencies=[Depends(require_bearer)])
def get_account():
    ...

# AFTER
from ..core.jwt import get_current_user
from ..models.database import User

@router.get("/account")
async def get_account(current_user: User = Depends(get_current_user)):
    # Now you have access to current_user.id, current_user.email, etc.
    ...
```

**Files to update (22 total):**
1. portfolio.py (3 endpoints)
2. market.py (4 endpoints)
3. options.py (2 endpoints)
4. positions.py (3 endpoints)
5. orders.py (1 endpoint - /trading/execute)
6. ai.py (3 endpoints)
7. analytics.py (2 endpoints)
8. backtesting.py (2 endpoints)
9. claude.py (1 endpoint)
10. market_data.py (3 endpoints)
11. news.py (2 endpoints)
12. proposals.py (2 endpoints)
13. screening.py (2 endpoints)
14. settings.py (2 endpoints)
15. stock.py (1 endpoint)
16. strategies.py (5 endpoints)
17. stream.py (2 endpoints)
18. scheduler.py (2 endpoints)
19. telemetry.py (1 endpoint)
20. users.py (already uses JWT - verify)
21. auth.py (already uses JWT - verify)
22. health.py (public - no auth needed)

**Note:** This is repetitive work. Consider creating a helper script to automate the replacement.

---

### Fix 7: Add Error Handling to 8 Routers (4 hours)

**Template for all endpoints:**

```python
# BEFORE (unsafe)
@router.get("")
async def get_positions():
    service = PositionTrackerService()
    return await service.get_open_positions()

# AFTER (safe)
import logging
logger = logging.getLogger(__name__)

@router.get("")
async def get_positions(current_user: User = Depends(get_current_user)):
    try:
        service = PositionTrackerService()
        positions = await service.get_open_positions()
        logger.info(f"User {current_user.id} retrieved {len(positions)} positions")
        return positions
    except HTTPException:
        raise  # Re-raise HTTP exceptions (401, 404, etc.)
    except Exception as e:
        logger.error(f"Failed to get positions for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve positions. Please try again later."
        )
```

**Files to update:**

1. **positions.py** - All 3 endpoints
2. **proposals.py** - All endpoints
3. **telemetry.py** - POST /telemetry
4. **users.py** - 4 endpoints
5. **scheduler.py** - 2 endpoints
6. **stream.py** - 2 endpoints
7. **stock.py** - 1 endpoint
8. **screening.py** - 2 endpoints

---

## DAY 3 FIXES (4 hours)

### Fix 8: Replace Mock Data (2 hours)

**File 1:** `frontend/components/MarketScanner.tsx`

**Change lines 58-160:**

```typescript
// BEFORE (mock data)
const handleScan = () => {
  setLoading(true);
  setTimeout(() => {
    const mockResults: ScanResult[] = [
      { symbol: "AAPL", price: 182.3, ... },
    ];
    setResults(mockResults);
    setLoading(false);
  }, 1500);
};

// AFTER (real API)
const handleScan = async () => {
  setLoading(true);
  setError("");

  try {
    const response = await fetch('/api/proxy/api/market/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scanType: selectedScan,
        filter: selectedFilter
      })
    });

    if (!response.ok) {
      throw new Error(`Scan failed: ${response.statusText}`);
    }

    const data = await response.json();
    setResults(data.results || []);
  } catch (err: any) {
    setError(err.message || "Failed to run market scan");
    setResults([]);
  } finally {
    setLoading(false);
  }
};
```

**File 2:** `frontend/components/Backtesting.tsx`

**Change lines 60-85:**

```typescript
// BEFORE (mock data)
const runBacktest = async () => {
  setLoading(true);
  setTimeout(() => {
    const mockEquity = [
      { date: "2024-01-01", value: 100000 },
      // ... more mock data
    ];
    setEquityCurve(mockEquity);
    setLoading(false);
  }, 2000);
};

// AFTER (real API)
const runBacktest = async () => {
  setLoading(true);
  setError("");

  try {
    const response = await fetch('/api/proxy/api/backtesting/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        strategy,
        startDate,
        endDate,
        initialCapital
      })
    });

    if (!response.ok) {
      throw new Error(`Backtest failed: ${response.statusText}`);
    }

    const data = await response.json();
    setEquityCurve(data.equity_curve || []);
    setMetrics(data.metrics || {});
  } catch (err: any) {
    setError(err.message || "Failed to run backtest");
  } finally {
    setLoading(false);
  }
};
```

**Note:** Backend `/api/backtesting/run` endpoint must be implemented to return equity curve data.

---

### Fix 9: Add Error Boundary (1 hour)

**File 1:** `frontend/components/ErrorBoundary.tsx` (CREATE)

```typescript
import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Component error caught:", error, errorInfo);

    // Send to Sentry if configured
    if (typeof window !== "undefined" && window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack,
          },
        },
      });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          backgroundColor: "#0f172a",
          color: "#cbd5e1",
          padding: "2rem",
          textAlign: "center"
        }}>
          <h1 style={{ fontSize: "2rem", marginBottom: "1rem" }}>
            Oops! Something went wrong
          </h1>
          <p style={{ marginBottom: "2rem", maxWidth: "600px" }}>
            We apologize for the inconvenience. The error has been logged and our team will investigate.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: "0.75rem 2rem",
              fontSize: "1rem",
              backgroundColor: "#3b82f6",
              color: "white",
              border: "none",
              borderRadius: "0.5rem",
              cursor: "pointer"
            }}
          >
            Reload Page
          </button>
          {process.env.NODE_ENV === "development" && this.state.error && (
            <details style={{ marginTop: "2rem", maxWidth: "800px", textAlign: "left" }}>
              <summary style={{ cursor: "pointer", marginBottom: "1rem" }}>
                Error Details (dev only)
              </summary>
              <pre style={{
                backgroundColor: "#1e293b",
                padding: "1rem",
                borderRadius: "0.5rem",
                overflow: "auto",
                fontSize: "0.875rem"
              }}>
                {this.state.error.stack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

**File 2:** `frontend/pages/_app.tsx`

**Change lines to wrap Component:**

```typescript
import ErrorBoundary from "../components/ErrorBoundary";

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ErrorBoundary>
      <Component {...pageProps} />
    </ErrorBoundary>
  );
}
```

---

### Fix 10: Delete Dead Code (5 minutes)

**Step 1:** Delete deprecated components

```bash
rm frontend/components/MorningRoutine.deprecated.tsx
rm frontend/components/StrategyBuilder.deprecated.tsx
```

**Step 2:** Delete test pages

```bash
rm frontend/pages/test-alpaca.tsx
rm frontend/pages/test-news.tsx
rm frontend/pages/test-options.tsx
rm frontend/pages/test-sentry.tsx
rm frontend/pages/test-tradier.tsx
```

**Step 3:** Verify no imports reference deleted files

```bash
# Search for imports
grep -r "MorningRoutine.deprecated" frontend/
grep -r "StrategyBuilder.deprecated" frontend/
grep -r "test-alpaca" frontend/
# Should return no results
```

---

### Fix 11: Database Connection Verification (30 minutes)

**File:** `backend/app/main.py`

**Add to startup_event (after line 119):**

```python
@app.on_event("startup")
async def startup_event():
    # ... existing code ...

    # Verify database connection (if using PostgreSQL)
    if settings.DATABASE_URL:
        try:
            async with monitor.phase("database_init", timeout=10.0):
                from .db.session import SessionLocal
                from .models.database import Base

                # Test connection
                db = SessionLocal()
                try:
                    result = db.execute("SELECT 1")
                    db.close()
                    print("[OK] Database connection verified", flush=True)
                except Exception as db_err:
                    db.close()
                    raise db_err
        except Exception as e:
            print(f"[CRITICAL] Database connection failed: {e}", flush=True)
            print("[INFO] Multi-user features will be disabled", flush=True)
            # Don't crash - allow app to start without database
    else:
        print("[WARNING] DATABASE_URL not set - multi-user features disabled", flush=True)
```

---

### Fix 12: LIVE_TRADING Confirmation (15 minutes)

**File:** `backend/app/main.py`

**Add after settings loaded (line 94):**

```python
print("\n===== TRADING MODE VALIDATION =====")
if settings.LIVE_TRADING:
    print("=" * 80, flush=True)
    print("⚠️  WARNING: LIVE TRADING ENABLED - REAL MONEY AT RISK ⚠️", flush=True)
    print("=" * 80, flush=True)

    # Require explicit confirmation
    if os.getenv("LIVE_TRADING_CONFIRMED") != "yes":
        print("\n[CRITICAL] LIVE_TRADING requires LIVE_TRADING_CONFIRMED=yes", flush=True)
        print("[CRITICAL] Set environment variable: LIVE_TRADING_CONFIRMED=yes", flush=True)
        print("[CRITICAL] This prevents accidental live trading activation", flush=True)
        raise ValueError("LIVE_TRADING requires LIVE_TRADING_CONFIRMED=yes to proceed")

    print("\n[OK] Live trading confirmed by LIVE_TRADING_CONFIRMED flag", flush=True)
else:
    print("✅ Paper trading mode active (safe)", flush=True)
print("====================================\n", flush=True)
```

---

## TESTING CHECKLIST AFTER FIXES

### Backend Tests
- [ ] Run `pytest backend/tests/` - all tests pass
- [ ] Start backend: `python -m uvicorn app.main:app --reload --port 8001`
- [ ] Verify no errors in startup logs
- [ ] Test health endpoint: `curl http://localhost:8001/api/health`
- [ ] Test JWT authentication with sample token
- [ ] Verify database connection established
- [ ] Confirm LIVE_TRADING flag requires confirmation

### Frontend Tests
- [ ] Run `npm run test:ci` - all tests pass
- [ ] Start frontend: `npm run dev`
- [ ] Verify no console errors
- [ ] Test error boundary (deliberately throw error)
- [ ] Verify deprecated components removed
- [ ] Test market scanner with real API
- [ ] Test backtesting with real API
- [ ] Confirm all 10 workflows load

### Integration Tests
- [ ] Test authentication flow end-to-end
- [ ] Verify API contract endpoints work
- [ ] Test position tracking with real data
- [ ] Confirm Greeks calculation returns non-zero values
- [ ] Test Alpaca endpoints (assets, clock, calendar, watchlists)
- [ ] Verify environment variables loaded correctly

---

## DEPLOYMENT VERIFICATION

After all fixes complete:

```bash
# 1. Commit all changes
git add .
git commit -m "fix: resolve all P0 critical issues (12 fixes)"

# 2. Run deployment automation
./deploy-production.ps1 -SkipTests  # Tests already run locally

# 3. Monitor deployment
./test-production.ps1 -ApiToken "your-token"

# 4. Verify in production
curl https://paiid-backend.onrender.com/api/health
# Should return 200 OK
```

---

## SUCCESS CRITERIA

All P0 issues are considered fixed when:
- ✅ All API contract endpoints return expected status codes
- ✅ Authentication uses JWT only (no legacy bearer token)
- ✅ All routers have try-catch error handling
- ✅ No mock data in production components
- ✅ Error boundary prevents app crashes
- ✅ No deprecated or test files in production build
- ✅ JWT secret validation enforced
- ✅ Greeks calculation returns correct values
- ✅ Database connection verified at startup
- ✅ LIVE_TRADING requires explicit confirmation
- ✅ Environment variables aligned across codebase
- ✅ Data source architecture rules enforced

**Total Estimated Time:** 18 hours over 3 days
**Blocking Production:** YES - must complete before launch

---

**Created:** October 23, 2025
**Last Updated:** October 23, 2025
**Status:** Ready for execution
