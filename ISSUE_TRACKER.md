# 🐛 ISSUE TRACKER - GitHub-Ready Issues

**Total Issues:** 65
**Critical (P0):** 12
**High Priority (P1):** 27
**Medium Priority (P2):** 26

---

## 🔴 CRITICAL (P0) - Must Fix Before Production

### Issue #1: API Contract Path Parameter Mismatches
**Labels:** `P0`, `bug`, `backend`, `frontend`, `api`
**Assignee:** Backend + Frontend developers
**Estimated:** 2 hours

**Description:**
Frontend proxy doesn't handle dynamic path parameters correctly, causing 405 errors for:
- `/market/quote/{symbol}`
- `/options/chain/{symbol}`
- `/market/bars/{symbol}`
- `/news/company/{symbol}`
- `/ai/analyze-symbol/{symbol}`

**Files:**
- `frontend/pages/api/proxy/[...path].ts`

**Solution:**
Implement pattern matching function to handle `{param}` placeholders in allowed paths.

**Acceptance Criteria:**
- [ ] All path parameter endpoints return 200 OK
- [ ] Frontend can call `/market/quote/AAPL` successfully
- [ ] Options chain fetching works with symbol parameter

---

### Issue #2: Three Authentication Systems Active
**Labels:** `P0`, `security`, `backend`, `authentication`
**Assignee:** Backend developer
**Estimated:** 4 hours

**Description:**
System has 3 concurrent auth mechanisms:
1. Legacy bearer token (`require_bearer`)
2. JWT authentication (`get_current_user`)
3. Mixed usage across endpoints

Security vulnerability - attackers can exploit weaker legacy system.

**Files:**
- 22 router files using `require_bearer`

**Solution:**
Standardize all endpoints to use JWT only.

**Acceptance Criteria:**
- [ ] All endpoints use `get_current_user` dependency
- [ ] No endpoints use `require_bearer`
- [ ] JWT tokens work for all protected routes
- [ ] Legacy token authentication removed

---

### Issue #3: Missing Error Handling in 8 Routers
**Labels:** `P0`, `bug`, `backend`, `error-handling`
**Assignee:** Backend developer
**Estimated:** 4 hours

**Description:**
Multiple routers have bare `async def` functions with NO try-catch blocks:
- `positions.py` - all 3 endpoints
- `proposals.py` - all endpoints
- `telemetry.py` - 1 endpoint
- `users.py` - 4 endpoints
- `scheduler.py` - 2 endpoints

Unhandled exceptions expose stack traces to clients.

**Solution:**
Add try-catch blocks to all endpoints following standard template.

**Acceptance Criteria:**
- [ ] All endpoints have try-catch error handling
- [ ] HTTP exceptions properly re-raised
- [ ] Generic exceptions return 500 with safe error message
- [ ] All errors logged with logger.error()

---

### Issue #4: Data Source Architecture Violation
**Labels:** `P0`, `bug`, `backend`, `critical`
**Assignee:** Backend developer
**Estimated:** 1 hour

**Description:**
`position_tracker.py` line 69 calls non-existent method:
```python
quote = self.tradier.get_option_quote(pos.symbol)
```

Method doesn't exist in TradierClient, causing production failure.

**Files:**
- `backend/app/services/position_tracker.py`
- `backend/app/services/tradier_client.py`
- `backend/app/routers/options.py`

**Solution:**
1. Use existing `get_quote()` method
2. Delete stub function `fetch_options_chain_from_alpaca()`

**Acceptance Criteria:**
- [ ] Position tracker fetches quotes successfully
- [ ] No references to Alpaca for options data
- [ ] All positions show correct quote data

---

### Issue #5: Duplicate Greeks Implementations
**Labels:** `P0`, `bug`, `backend`, `logic`
**Assignee:** Backend developer
**Estimated:** 30 minutes

**Description:**
Two Greek calculation implementations:
- `greeks.py` - stub returning zeros ❌
- `options_greeks.py` - full scipy implementation ✅

`position_tracker.py` imports from stub → all Greeks = 0.0

**Solution:**
1. Delete `greeks.py`
2. Update imports to `options_greeks.py`

**Acceptance Criteria:**
- [ ] Only one Greeks implementation exists
- [ ] Position tracker shows non-zero Greeks
- [ ] Delta, Gamma, Theta, Vega calculated correctly

---

### Issue #6: Environment Variable Naming Inconsistency
**Labels:** `P0`, `bug`, `backend`, `configuration`
**Assignee:** Backend developer
**Estimated:** 15 minutes

**Description:**
`orders.py` uses wrong environment variable names:
- Uses: `ALPACA_API_KEY`
- Should use: `ALPACA_PAPER_API_KEY`

Order execution fails in production if only correct env vars are set.

**Solution:**
Import from `settings` object instead of direct `os.getenv()`.

**Acceptance Criteria:**
- [ ] Orders use settings.ALPACA_API_KEY
- [ ] Environment variable names match config.py
- [ ] Order execution works in production

---

### Issue #7: JWT Secret Has Insecure Default
**Labels:** `P0`, `security`, `backend`, `critical`
**Assignee:** Backend developer
**Estimated:** 10 minutes

**Description:**
```python
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production-NEVER-COMMIT-THIS")
```

If env var not set → uses hardcoded default → all tokens compromised.

**Solution:**
Require JWT_SECRET_KEY in production, validate length ≥ 32 chars.

**Acceptance Criteria:**
- [ ] Startup fails if JWT_SECRET_KEY not set
- [ ] Startup fails if default value used
- [ ] Minimum 32 character length enforced

---

### Issue #8: Mock Data in Production Components
**Labels:** `P0`, `bug`, `frontend`, `data`
**Assignee:** Frontend developer
**Estimated:** 2 hours

**Description:**
Two components use hardcoded mock data instead of backend API:
1. `MarketScanner.tsx` - fake scan results
2. `Backtesting.tsx` - fake equity curve

Users see misleading fake data.

**Solution:**
Replace setTimeout mock data with real API calls.

**Acceptance Criteria:**
- [ ] MarketScanner fetches from `/api/market/scan`
- [ ] Backtesting fetches from `/api/backtesting/run`
- [ ] No hardcoded market data in components
- [ ] Real-time data displayed to users

---

### Issue #9: No Error Boundaries (Frontend)
**Labels:** `P0`, `bug`, `frontend`, `ux`
**Assignee:** Frontend developer
**Estimated:** 1 hour

**Description:**
No ErrorBoundary component exists. If any workflow component crashes, entire app goes down.

**Solution:**
Create ErrorBoundary component and wrap app in `_app.tsx`.

**Acceptance Criteria:**
- [ ] ErrorBoundary component created
- [ ] Wraps entire app in _app.tsx
- [ ] Shows user-friendly error message
- [ ] Logs errors to Sentry (if configured)
- [ ] Provides reload button

---

### Issue #10: Dead Code in Production Build
**Labels:** `P0`, `cleanup`, `frontend`, `performance`
**Assignee:** Frontend developer
**Estimated:** 5 minutes

**Description:**
Deprecated and test files increase bundle size:
- `MorningRoutine.deprecated.tsx`
- `StrategyBuilder.deprecated.tsx`
- 5 test pages (`test-*.tsx`)

**Solution:**
Delete all deprecated and test files.

**Acceptance Criteria:**
- [ ] No .deprecated.tsx files in codebase
- [ ] No test-*.tsx files in pages/
- [ ] Bundle size reduced
- [ ] No broken imports

---

### Issue #11: Missing Database Connection Verification
**Labels:** `P0`, `bug`, `backend`, `infrastructure`
**Assignee:** Backend developer
**Estimated:** 30 minutes

**Description:**
10 routers use database but no startup verification exists.
Multi-user features fail silently if database not connected.

**Solution:**
Add database connection test in startup_event.

**Acceptance Criteria:**
- [ ] Startup verifies database connection
- [ ] Logs success/failure clearly
- [ ] Gracefully handles missing DATABASE_URL
- [ ] Multi-user features work correctly

---

### Issue #12: LIVE_TRADING Flag Unsafe
**Labels:** `P0`, `safety`, `backend`, `trading`
**Assignee:** Backend developer
**Estimated:** 15 minutes

**Description:**
`LIVE_TRADING=true` can be set without explicit confirmation.
Risk of accidental live trading activation.

**Solution:**
Require `LIVE_TRADING_CONFIRMED=yes` environment variable.

**Acceptance Criteria:**
- [ ] LIVE_TRADING requires LIVE_TRADING_CONFIRMED=yes
- [ ] Startup fails if confirmation not set
- [ ] Clear warning displayed when live trading active
- [ ] Paper trading default remains safe

---

## 🟡 HIGH PRIORITY (P1) - Fix Soon

### Backend Issues (17 total)

#### Issue #13: Missing Rate Limiting on Critical Endpoints
**Labels:** `P1`, `security`, `backend`
**Estimated:** 1 hour

Order execution endpoint has no rate limiting. Attacker could spam orders.

**Solution:** Add `@limiter.limit("5/minute")` decorator.

---

#### Issue #14: API Tokens Logged in Plaintext
**Labels:** `P1`, `security`, `backend`
**Estimated:** 30 minutes

Authentication middleware logs full tokens to stdout.

**Solution:** Mask tokens in logs (show first 8 + last 4 chars only).

---

#### Issue #15: Missing HTTP Timeouts
**Labels:** `P1`, `reliability`, `backend`
**Estimated:** 1 hour

8 HTTP requests missing timeout parameter → can hang indefinitely.

**Files:** `market.py`, `options.py`, `news.py`, `screening.py`

**Solution:** Add `timeout=5` to all requests.get/post calls.

---

#### Issue #16: No Circuit Breaker for Tradier API
**Labels:** `P1`, `reliability`, `backend`
**Estimated:** 2 hours

Tradier market data requests have no circuit breaker. If API goes down, every request retries 3x causing latency spike.

**Solution:** Implement TradierCircuitBreaker similar to AlpacaCircuitBreaker.

---

#### Issue #17: No Idempotency on Non-Trading Endpoints
**Labels:** `P1`, `reliability`, `backend`
**Estimated:** 3 hours

Only `/trading/execute` has idempotency check. Other POST endpoints can create duplicates on retry.

**Solution:** Add idempotency key header to all POST/PUT/DELETE endpoints.

---

#### Issue #18: No Request ID Tracking
**Labels:** `P1`, `observability`, `backend`
**Estimated:** 2 hours

No correlation ID for tracing requests through system. Impossible to debug distributed requests.

**Solution:** Create RequestIDMiddleware to track request IDs.

---

#### Issue #19: Inconsistent Caching Strategy
**Labels:** `P1`, `performance`, `backend`
**Estimated:** 2 hours

`options.py` uses TTLCache, others use CacheService (Redis). Options cache doesn't scale across workers.

**Solution:** Standardize all caching to use CacheService.

---

#### Issue #20: Kill Switch Not Enforced Globally
**Labels:** `P1`, `trading`, `backend`
**Estimated:** 1 hour

Kill switch only checked in `/trading/execute`. User could trigger trades via templates during kill switch.

**Solution:** Create KillSwitchMiddleware to block all mutations.

---

#### Issue #21: No HTTP Connection Pooling
**Labels:** `P1`, `performance`, `backend`
**Estimated:** 1 hour

Every Tradier request creates new HTTP connection.

**Solution:** Use `requests.Session()` for connection pooling.

---

#### Issue #22: Cache Service Missing Metrics
**Labels:** `P1`, `observability`, `backend`
**Estimated:** 1 hour

No metrics on cache hit/miss rates.

**Solution:** Add metrics.increment("cache.hit/miss") calls.

---

#### Issue #23: Rate Limiter Uses In-Memory Storage
**Labels:** `P1`, `bug`, `backend`
**Estimated:** 1 hour

Rate limiter uses `memory://` storage. With multiple workers, each has separate counters → rate limit bypass.

**Solution:** Use Redis for rate limiting: `storage_uri=settings.REDIS_URL`.

---

#### Issue #24: Missing Env Var Validation at Startup
**Labels:** `P1`, `configuration`, `backend`
**Estimated:** 1 hour

App starts even if critical env vars missing. Errors only appear when endpoints called.

**Solution:** Validate required vars in startup_event.

---

#### Issue #25: No Environment-Specific Configuration
**Labels:** `P1`, `configuration`, `backend`
**Estimated:** 1 hour

No way to differentiate dev/staging/production. Same settings for all.

**Solution:** Add ENVIRONMENT variable and environment detection.

---

#### Issue #26: Delete Alpaca Options Stub Function
**Labels:** `P1`, `cleanup`, `backend`
**Estimated:** 5 minutes

`options.py` line 305 has `fetch_options_chain_from_alpaca()` stub that violates architecture.

**Solution:** Delete function entirely.

---

#### Issue #27: Verbose Debug Logging in Production
**Labels:** `P1`, `observability`, `backend`
**Estimated:** 30 minutes

Auth middleware prints verbose logs on every request.

**Solution:** Remove print statements, keep logger.debug only.

---

#### Issue #28: Inconsistent Response Models
**Labels:** `P1`, `api`, `backend`
**Estimated:** 3 hours

Some endpoints return dicts, others Pydantic models. No standardization.

**Solution:** Use Pydantic models for all responses.

---

#### Issue #29: Redundant Validation Middleware
**Labels:** `P1`, `cleanup`, `backend`
**Estimated:** 2 hours

Validation logic duplicated in middleware and Pydantic validators.

**Solution:** Refactor to use centralized validation or remove middleware.

---

### Frontend Issues (10 total)

#### Issue #30: Inconsistent API Error Handling
**Labels:** `P1`, `bug`, `frontend`
**Estimated:** 3 hours

Components don't check HTTP status codes. All errors show generic message.

**Solution:** Standardize error handling with status code checks (401, 429, 500).

---

#### Issue #31: No Loading State Skeletons
**Labels:** `P1`, `ux`, `frontend`
**Estimated:** 4 hours

Components show "Loading..." text instead of skeleton screens.

**Solution:** Replace text with skeleton placeholders.

---

#### Issue #32: Unsafe `any` Types Throughout
**Labels:** `P1`, `typescript`, `frontend`
**Estimated:** 6 hours

Multiple components use `any` type, defeating TypeScript safety.

**Solution:** Define proper interfaces for all `any` types.

---

#### Issue #33: No Data Caching Strategy
**Labels:** `P1`, `performance`, `frontend`
**Estimated:** 4 hours

Components refetch data on every mount. No caching.

**Solution:** Implement SWR or React Query for automatic caching.

---

#### Issue #34: Hardcoded API URLs
**Labels:** `P1`, `configuration`, `frontend`
**Estimated:** 1 hour

Components fall back to production URL in development.

**Solution:** Require env vars, don't fall back to production.

---

#### Issue #35: Large Component Files
**Labels:** `P1`, `maintainability`, `frontend`
**Estimated:** 8 hours

Settings.tsx = 1475 lines, AIRecommendations.tsx = 1242 lines.

**Solution:** Split into smaller components.

---

#### Issue #36: Prop Drilling in Settings
**Labels:** `P1`, `architecture`, `frontend`
**Estimated:** 3 hours

Settings component passes props through multiple levels.

**Solution:** Use Context API for shared state.

---

#### Issue #37: Inconsistent Mobile Responsiveness
**Labels:** `P1`, `ux`, `frontend`
**Estimated:** 6 hours

Some components use `useIsMobile()`, others don't handle mobile.

**Solution:** Audit all components for mobile UX, standardize on useIsMobile().

---

#### Issue #38: Excessive Re-renders
**Labels:** `P1`, `performance`, `frontend`
**Estimated:** 2 hours

Functions recreated on every render, missing useCallback.

**Solution:** Wrap functions in useCallback with proper dependencies.

---

#### Issue #39: No Code Splitting
**Labels:** `P1`, `performance`, `frontend`
**Estimated:** 3 hours

All 10 workflows loaded upfront. Large initial bundle.

**Solution:** Use dynamic imports for workflow components.

---

## 🟢 MEDIUM PRIORITY (P2) - Technical Debt

### Backend Issues (5 total)

#### Issue #40: Missing OpenAPI Tags
**Labels:** `P2`, `documentation`, `backend`
**Estimated:** 1 hour

Some routers missing tags for API documentation grouping.

---

#### Issue #41: Hardcoded Risk-Free Rate
**Labels:** `P2`, `finance`, `backend`
**Estimated:** 2 hours

Greeks calculation uses hardcoded 5% risk-free rate.

**Solution:** Fetch from Fed API or make configurable.

---

#### Issue #42: No Metrics on Critical Paths
**Labels:** `P2`, `observability`, `backend`
**Estimated:** 4 hours

No metrics tracking on order execution, API response times, etc.

---

#### Issue #43: Incomplete Health Checks
**Labels:** `P2`, `infrastructure`, `backend`
**Estimated:** 2 hours

Health endpoint doesn't verify DB/Redis/API dependencies.

---

#### Issue #44: TODO Comments Should Be Issues
**Labels:** `P2`, `cleanup`, `backend`
**Estimated:** 2 hours

68 TODO comments found. Should be GitHub issues.

---

### Frontend Issues (8 total)

#### Issue #45: API Tokens in LocalStorage
**Labels:** `P2`, `security`, `frontend`
**Estimated:** 3 hours

Tokens stored in localStorage. Should use HTTP-only cookies.

---

#### Issue #46: No Input Sanitization
**Labels:** `P2`, `security`, `frontend`
**Estimated:** 2 hours

User inputs not validated (e.g., symbol format).

---

#### Issue #47: No Unit Tests
**Labels:** `P2`, `testing`, `frontend`
**Estimated:** 20 hours

Component test coverage ~8%. Target: 70%.

---

#### Issue #48: Missing JSDoc Comments
**Labels:** `P2`, `documentation`, `frontend`
**Estimated:** 8 hours

Complex functions lack documentation.

---

#### Issue #49: No Accessibility Audit
**Labels:** `P2`, `a11y`, `frontend`
**Estimated:** 6 hours

Components not tested for keyboard navigation, screen readers.

---

#### Issue #50: Bundle Size Not Optimized
**Labels:** `P2`, `performance`, `frontend`
**Estimated:** 4 hours

No analysis of bundle composition, potential tree-shaking improvements.

---

#### Issue #51: Test Pages in Production
**Labels:** `P2`, `cleanup`, `frontend`
**Estimated:** 5 minutes

Test pages should be in __tests__/ or deleted.

---

#### Issue #52: Inconsistent Error Messages
**Labels:** `P2`, `ux`, `frontend`
**Estimated:** 2 hours

Error messages not user-friendly or consistent.

---

### Code Smells (13 total - condensed)

#### Issue #53-65: Code Quality Improvements
**Labels:** `P2`, `code-quality`, `refactoring`

Includes:
- Inconsistent async/sync patterns
- Print statements instead of logger (47 instances)
- Missing type hints
- Magic numbers not named constants
- Duplicate code
- Deep nesting
- Complex conditionals
- Mixed indentation
- Unused imports
- Commented-out code
- Inconsistent naming
- Long parameter lists
- Deep nesting

**Total estimated:** 30 hours for all code smell fixes

---

## 📊 SUMMARY BY LABEL

| Label | Count |
|-------|-------|
| `P0` | 12 |
| `P1` | 27 |
| `P2` | 26 |
| `backend` | 35 |
| `frontend` | 25 |
| `security` | 7 |
| `performance` | 10 |
| `bug` | 18 |
| `configuration` | 6 |
| `cleanup` | 5 |

---

## 🎯 RECOMMENDED SPRINT PLANNING

### Sprint 1: Critical Fixes (Week 1)
- Issues #1-12 (all P0 issues)
- **Goal:** Make platform production-safe
- **Team:** 2 backend + 2 frontend developers
- **Effort:** 18 hours total

### Sprint 2: Reliability (Week 2)
- Issues #13-29 (backend P1 issues)
- **Goal:** Production-grade reliability
- **Team:** 2 backend developers
- **Effort:** 25 hours total

### Sprint 3: Performance (Week 3)
- Issues #30-39 (frontend P1 issues)
- **Goal:** Optimal user experience
- **Team:** 2 frontend developers
- **Effort:** 40 hours total

### Sprint 4: Polish (Week 4)
- Issues #40-52 (P2 issues)
- **Goal:** Code quality and maintainability
- **Team:** Full team
- **Effort:** 50 hours total

---

**Created:** October 23, 2025
**Last Updated:** October 23, 2025
**Status:** Ready for GitHub import
