# Production Deployment Checklist - PaiiD Platform

**Last Updated:** 2025-10-27
**Platform:** Render (Frontend + Backend)
**Environment:** Production
**Region:** Oregon (us-west)

---

## Table of Contents
1. [Pre-Deployment Checks](#pre-deployment-checks)
2. [Environment Configuration](#environment-configuration)
3. [Code Quality Checks](#code-quality-checks)
4. [Security Verification](#security-verification)
5. [Deployment Process](#deployment-process)
6. [Post-Deployment Validation](#post-deployment-validation)
7. [Rollback Procedures](#rollback-procedures)
8. [Monitoring & Alerts](#monitoring--alerts)

---

## Pre-Deployment Checks

### 1. Local Testing
- [ ] Frontend builds successfully: `cd frontend && npm run build`
- [ ] Frontend runs in production mode: `npm start`
- [ ] Backend starts without errors: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001`
- [ ] All tests pass (if applicable)
- [ ] No TypeScript errors: `cd frontend && npx tsc --noEmit`
- [ ] No linting errors: `cd backend && ruff check .`

### 2. Git Repository Status
- [ ] All changes committed to feature branch
- [ ] Feature branch merged to `main` (or ready to merge)
- [ ] No uncommitted secrets in `.env` or `.env.local`
- [ ] `.gitignore` excludes sensitive files
- [ ] Recent commits have meaningful messages
- [ ] No large binary files accidentally committed

### 3. Dependencies
- [ ] `frontend/package-lock.json` is up to date
- [ ] `backend/requirements.txt` is up to date
- [ ] No critical security vulnerabilities: `cd frontend && npm audit`
- [ ] All production dependencies are pinned to specific versions

### 4. Documentation
- [ ] `README.md` is up to date
- [ ] `CLAUDE.md` reflects current architecture
- [ ] API changes documented in relevant files
- [ ] Environment variable changes documented

---

## Environment Configuration

### Frontend Environment Variables (Render Dashboard)

**Service:** paiid-frontend
**Dashboard:** https://dashboard.render.com/web/srv-<service-id>

#### Required Variables
- [ ] `NEXT_PUBLIC_API_TOKEN` - Set to match backend `API_TOKEN`
- [ ] `API_TOKEN` - Set to same value as `NEXT_PUBLIC_API_TOKEN`
- [ ] `NEXT_PUBLIC_BACKEND_API_BASE_URL` - Set to `https://paiid-backend.onrender.com`
- [ ] `NEXT_PUBLIC_ANTHROPIC_API_KEY` - Set to valid Claude API key (starts with `sk-ant-api03-`)
- [ ] `NODE_ENV` - Set to `production` (auto-set by render.yaml)
- [ ] `PORT` - Set to `3000` (auto-set by render.yaml)

**Verification Command:**
```bash
# Check if environment variables are accessible (after deployment)
curl https://paiid-frontend.onrender.com/api/proxy/api/health
```

### Backend Environment Variables (Render Dashboard)

**Service:** paiid-backend
**Dashboard:** https://dashboard.render.com/web/srv-<service-id>

#### Required Variables
- [ ] `API_TOKEN` - Set to match frontend `NEXT_PUBLIC_API_TOKEN`
- [ ] `ALPACA_PAPER_API_KEY` - Set to Alpaca paper trading key
- [ ] `ALPACA_PAPER_SECRET_KEY` - Set to Alpaca paper trading secret
- [ ] `APCA_API_BASE_URL` - Set to `https://paper-api.alpaca.markets`
- [ ] `TRADIER_API_KEY` - Set to Tradier live account API key
- [ ] `TRADIER_ACCOUNT_ID` - Set to Tradier account ID
- [ ] `TRADIER_API_BASE_URL` - Set to `https://api.tradier.com/v1`
- [ ] `ANTHROPIC_API_KEY` - Set to valid Claude API key (starts with `sk-ant-api03-`)
- [ ] `ALLOW_ORIGIN` - Set to `https://paiid-frontend.onrender.com`
- [ ] `DATABASE_URL` - Set to Render PostgreSQL connection string
- [ ] `REDIS_URL` - Set to Render Redis connection string (or auto-generated)
- [ ] `SENTRY_DSN` - Set to Sentry error tracking DSN
- [ ] `SENTRY_ENVIRONMENT` - Set to `production`
- [ ] `LOG_LEVEL` - Set to `INFO`
- [ ] `LIVE_TRADING` - Set to `false` (paper trading only)
- [ ] `TRADING_MODE` - Set to `paper`
- [ ] `USE_TEST_FIXTURES` - Set to `false`

**Verification Command:**
```bash
# Check backend health
curl https://paiid-backend.onrender.com/api/health

# Expected response:
# {"status":"ok","time":"2025-10-27T..."}
```

---

## Code Quality Checks

### Frontend (Next.js/TypeScript)
- [ ] TypeScript compilation succeeds: `npx tsc --noEmit`
- [ ] Production build succeeds: `npm run build`
- [ ] No console errors in build output
- [ ] Bundle size is reasonable (check `.next/analyze` if needed)
- [ ] No unused dependencies in `package.json`

### Backend (FastAPI/Python)
- [ ] Python syntax is valid: `python -m py_compile app/main.py`
- [ ] Imports resolve correctly: `python -c "from app.main import app; print('OK')"`
- [ ] Pre-launch checks pass: `python -m app.core.prelaunch --check-only`
- [ ] No critical linting errors: `ruff check .`
- [ ] Requirements can be installed: `pip install -r requirements.txt --dry-run`

---

## Security Verification

### Secrets Management
- [ ] No API keys in source code (use environment variables)
- [ ] No hardcoded credentials in any files
- [ ] `.env` and `.env.local` are in `.gitignore`
- [ ] API tokens are at least 32 characters (prefer 48+)
- [ ] Anthropic API keys start with `sk-ant-api03-`
- [ ] Alpaca keys are for PAPER TRADING ONLY

### CORS Configuration
- [ ] Frontend origin in backend CORS whitelist (backend/app/main.py line 658-662)
  ```python
  allow_origins=[
      "http://localhost:3000",
      "http://localhost:3003",
      "https://paiid-frontend.onrender.com",  # ✅ Must be present
  ]
  ```
- [ ] Backend origin in frontend proxy whitelist (frontend/pages/api/proxy/[...path].ts line 107-118)
  ```typescript
  const ALLOWED_ORIGINS = new Set<string>([
      "http://localhost:3000",
      "https://paiid-frontend.onrender.com",  // ✅ Must be present
  ]);
  ```

### API Authentication
- [ ] API proxy requires Bearer token (frontend/pages/api/proxy/[...path].ts line 262)
- [ ] Backend validates API token on all routes (except /api/health)
- [ ] No anonymous access to sensitive endpoints
- [ ] Rate limiting configured (if applicable)

### Data Protection
- [ ] User data is NOT stored (privacy-first design)
- [ ] Only trading preferences stored in localStorage
- [ ] No personal information collected (name, email, etc.)
- [ ] Paper trading only (no real money at risk)

---

## Deployment Process

### Step 1: Prepare for Deployment
```bash
# 1. Ensure you're on main branch
git checkout main
git pull origin main

# 2. Verify no uncommitted changes
git status

# 3. Check recent commits
git log --oneline -5
```

### Step 2: Trigger Deployment (Auto-Deploy from Git)

**Render Auto-Deploy Behavior:**
- Frontend and backend auto-deploy on push to `main` branch
- Render watches the GitHub repository for changes
- Builds and deploys automatically (usually takes 5-10 minutes)

**Manual Deploy (if needed):**
1. Go to Render Dashboard
2. Select service (paiid-frontend or paiid-backend)
3. Click "Manual Deploy" → "Deploy latest commit"

### Step 3: Monitor Build Logs

**Frontend Build Logs:**
1. Go to https://dashboard.render.com/web/srv-<frontend-service-id>
2. Click "Logs" tab
3. Watch for:
   - `Building Docker image...`
   - `npm ci` (dependency installation)
   - `npm run build` (Next.js build)
   - `Copying standalone server...`
   - `Deploy succeeded`

**Backend Build Logs:**
1. Go to https://dashboard.render.com/web/srv-<backend-service-id>
2. Click "Logs" tab
3. Watch for:
   - `pip install -r requirements.txt`
   - `python -m app.core.prelaunch --check-only`
   - `bash start.sh`
   - `Uvicorn running on http://0.0.0.0:$PORT`
   - `Deploy succeeded`

### Step 4: Wait for Health Checks

**Frontend Health Check:**
- Path: `/` (root)
- Interval: 30s
- Timeout: 10s
- Expected: HTTP 200

**Backend Health Check:**
- Path: `/api/health`
- Interval: 30s
- Timeout: 10s
- Expected: `{"status":"ok","time":"..."}`

**Deployment Status:**
- ✅ Green: Service is healthy and serving traffic
- 🟡 Yellow: Build in progress or starting up
- 🔴 Red: Build failed or service crashed

---

## Post-Deployment Validation

### 1. Frontend Validation

#### Basic Functionality
- [ ] Frontend loads: https://paiid-frontend.onrender.com
- [ ] No errors in browser console (F12 → Console tab)
- [ ] RadialMenu renders with 10 wedges
- [ ] Logo displays correctly in center
- [ ] Live market data loads (SPY/QQQ in center logo)

#### API Connectivity
- [ ] Backend API proxy works (check Network tab for `/api/proxy/*` calls)
- [ ] No 401/403 authentication errors
- [ ] No CORS errors in console
- [ ] Health check responds:
  ```bash
  curl https://paiid-frontend.onrender.com/api/proxy/api/health
  ```

#### AI Features
- [ ] UserSetupAI component loads on first visit
- [ ] Claude AI chat interface works
- [ ] No "API key not configured" errors
- [ ] Strategy builder AI responds to queries

#### Workflow Components
- [ ] Morning Routine loads
- [ ] Active Positions displays data from Alpaca
- [ ] Execute Trade form submits successfully
- [ ] Market Scanner shows results
- [ ] AI Recommendations generate and display
- [ ] P&L Dashboard renders charts
- [ ] News Review fetches and displays news
- [ ] Backtesting runs without errors
- [ ] Settings save correctly

### 2. Backend Validation

#### Health & Connectivity
- [ ] Health check responds:
  ```bash
  curl https://paiid-backend.onrender.com/api/health
  # Expected: {"status":"ok","time":"2025-10-27T..."}
  ```

#### API Endpoints (with authentication)
- [ ] Account endpoint:
  ```bash
  curl -H "Authorization: Bearer <token>" \
    https://paiid-backend.onrender.com/api/account
  # Expected: Alpaca account data
  ```
- [ ] Positions endpoint:
  ```bash
  curl -H "Authorization: Bearer <token>" \
    https://paiid-backend.onrender.com/api/positions
  # Expected: Array of positions (may be empty)
  ```
- [ ] Market data endpoint:
  ```bash
  curl -H "Authorization: Bearer <token>" \
    "https://paiid-backend.onrender.com/api/market/quote?symbol=SPY"
  # Expected: Real-time quote data from Tradier
  ```

#### External API Connectivity
- [ ] Tradier API is reachable (market data loads)
- [ ] Alpaca API is reachable (positions load)
- [ ] Anthropic API is reachable (AI recommendations work)
- [ ] PostgreSQL database is accessible (check logs)
- [ ] Redis cache is accessible (if configured)

### 3. End-to-End Testing

#### User Journey: New User Onboarding
1. [ ] Open https://paiid-frontend.onrender.com
2. [ ] UserSetupAI modal appears
3. [ ] Complete AI-guided setup conversation
4. [ ] Trading preferences saved to localStorage
5. [ ] Dashboard loads with radial menu

#### User Journey: Execute a Paper Trade
1. [ ] Select "Execute Trade" from radial menu
2. [ ] Enter symbol (e.g., SPY)
3. [ ] Select order type (market/limit)
4. [ ] Set quantity
5. [ ] Submit order
6. [ ] Order confirmation appears
7. [ ] Position appears in "Active Positions"

#### User Journey: View AI Recommendations
1. [ ] Select "AI Recommendations" from radial menu
2. [ ] AI generates recommendations based on market conditions
3. [ ] Recommendations display with confidence scores
4. [ ] Click to expand details

### 4. Performance Checks

- [ ] Frontend loads in < 3 seconds
- [ ] API responses are < 1 second
- [ ] No memory leaks (check browser Task Manager)
- [ ] No infinite re-renders (check console for warnings)
- [ ] WebSocket connections stable (if applicable)

### 5. Error Handling

- [ ] 404 page displays for invalid routes
- [ ] API errors show user-friendly messages
- [ ] Network failures handled gracefully
- [ ] No unhandled promise rejections in console

---

## Rollback Procedures

### When to Rollback
- Critical bugs preventing core functionality
- Security vulnerabilities exposed
- Data corruption or loss
- Service crashes repeatedly
- Unrecoverable API errors

### Rollback Process (Render)

#### Option 1: Redeploy Previous Commit
1. Go to Render Dashboard → Service → "Deploys" tab
2. Find the last known good deployment
3. Click "Redeploy" on that commit
4. Wait for build to complete

#### Option 2: Git Revert (if Option 1 fails)
```bash
# 1. Identify problematic commit
git log --oneline -10

# 2. Revert the commit (creates new commit)
git revert <commit-hash>

# 3. Push to main (triggers auto-deploy)
git push origin main

# 4. Monitor deployment in Render Dashboard
```

#### Option 3: Emergency Rollback (Manual)
```bash
# 1. Create emergency rollback branch
git checkout -b emergency-rollback

# 2. Reset to last known good commit
git reset --hard <good-commit-hash>

# 3. Force push to main (BE CAREFUL!)
git push origin emergency-rollback:main --force

# 4. Monitor deployment in Render Dashboard
```

**WARNING:** Option 3 rewrites history. Only use in emergencies!

### Post-Rollback Validation
- [ ] Service is running (check Render Dashboard)
- [ ] Health checks pass
- [ ] Basic functionality works
- [ ] No new errors in logs
- [ ] Notify team of rollback

---

## Monitoring & Alerts

### Health Monitoring

**Automated Health Checks:**
- Frontend: https://paiid-frontend.onrender.com/ (every 30s)
- Backend: https://paiid-backend.onrender.com/api/health (every 30s)

**Manual Health Checks:**
```bash
# Frontend health
curl -I https://paiid-frontend.onrender.com/

# Backend health
curl https://paiid-backend.onrender.com/api/health

# Full API test
curl -H "Authorization: Bearer <token>" \
  https://paiid-frontend.onrender.com/api/proxy/api/account
```

### Error Tracking (Sentry)

**Backend Sentry Integration:**
- Configured in `backend/app/main.py`
- DSN set via `SENTRY_DSN` environment variable
- Environment: `production`

**Monitor Errors:**
1. Go to https://sentry.io
2. Select "paiid-backend" project
3. Check for new errors/exceptions
4. Set up alerts for critical errors

### Log Monitoring

**Render Logs:**
1. Go to Render Dashboard → Service → "Logs" tab
2. Filter by:
   - Errors: `level:error`
   - Warnings: `level:warning`
   - API calls: `[PROXY]` or `[API]`
3. Download logs if needed (Logs → "Download")

**Key Log Patterns to Watch:**
- `[PROXY] ⛔ REJECTING REQUEST` - CORS/auth failures
- `[PROXY] ⚠️ Origin blocked` - Origin not in whitelist
- `ERROR` - Application errors
- `500` or `502` - Server errors
- `401` or `403` - Authentication failures

### Performance Monitoring

**Metrics to Track:**
- Response times (should be < 1s for API calls)
- Error rates (should be < 1%)
- Uptime (should be > 99.9%)
- Memory usage (watch for leaks)
- CPU usage (watch for spikes)

**Render Metrics:**
1. Go to Render Dashboard → Service → "Metrics" tab
2. Monitor:
   - HTTP requests/min
   - Response time (p50, p95, p99)
   - Memory usage
   - CPU usage

---

## Troubleshooting Common Issues

### Issue: Frontend won't build
**Symptoms:** Build fails during `npm run build`
**Causes:**
- TypeScript errors
- Missing dependencies
- Syntax errors

**Solution:**
1. Run locally: `cd frontend && npm run build`
2. Fix TypeScript errors: `npx tsc --noEmit`
3. Check dependencies: `npm install`
4. Push fixes and redeploy

### Issue: Backend won't start
**Symptoms:** Backend crashes on startup
**Causes:**
- Missing environment variables
- Import errors
- Database connection failures

**Solution:**
1. Check logs in Render Dashboard
2. Verify all required env vars are set
3. Test locally: `python -m app.core.prelaunch --check-only`
4. Check database connectivity
5. Fix issues and redeploy

### Issue: CORS errors in browser console
**Symptoms:** `Access-Control-Allow-Origin` errors
**Causes:**
- Frontend origin not in backend whitelist
- Backend origin not in frontend proxy whitelist

**Solution:**
1. Verify backend CORS config (backend/app/main.py line 658-662)
2. Verify frontend proxy config (frontend/pages/api/proxy/[...path].ts line 107-118)
3. Add `https://paiid-frontend.onrender.com` to both
4. Redeploy both services

### Issue: API requests return 401 Unauthorized
**Symptoms:** All API calls fail with 401
**Causes:**
- API token mismatch
- API token not set

**Solution:**
1. Check frontend `NEXT_PUBLIC_API_TOKEN` in Render Dashboard
2. Check backend `API_TOKEN` in Render Dashboard
3. Ensure both are EXACTLY the same
4. Redeploy both services

### Issue: AI features not working
**Symptoms:** "API key not configured" errors
**Causes:**
- `NEXT_PUBLIC_ANTHROPIC_API_KEY` not set or invalid

**Solution:**
1. Check frontend Render Dashboard → Environment Variables
2. Verify key starts with `sk-ant-api03-`
3. Test key validity with Anthropic API
4. Set correct key and redeploy

---

## Deployment Checklist Summary

### Before Deployment
- [ ] Local tests pass
- [ ] Code committed and pushed to `main`
- [ ] Environment variables configured in Render
- [ ] Documentation updated
- [ ] Security review complete

### During Deployment
- [ ] Monitor build logs
- [ ] Watch for errors
- [ ] Wait for health checks to pass

### After Deployment
- [ ] Frontend loads and renders correctly
- [ ] Backend API responds to health checks
- [ ] API connectivity works (no CORS/auth errors)
- [ ] AI features work
- [ ] Critical workflows tested
- [ ] Logs monitored for errors
- [ ] Performance metrics acceptable

### If Issues Arise
- [ ] Assess severity (critical vs. minor)
- [ ] Check logs for root cause
- [ ] Attempt quick fix if possible
- [ ] Rollback if necessary
- [ ] Post-mortem analysis
- [ ] Document lessons learned

---

## Contact & Resources

**Documentation:**
- Project README: `README.md`
- Architecture: `CLAUDE.md`
- Deployment: `docs/DEPLOYMENT.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- API Reference: `docs/API_REFERENCE.md`

**External Links:**
- Render Dashboard: https://dashboard.render.com
- Sentry Monitoring: https://sentry.io
- Anthropic Console: https://console.anthropic.com
- Alpaca Dashboard: https://app.alpaca.markets/paper/dashboard
- Tradier Dashboard: https://dash.tradier.com

**Health Check URLs:**
- Frontend: https://paiid-frontend.onrender.com
- Backend: https://paiid-backend.onrender.com/api/health

**Emergency Contacts:**
- Platform Owner: [Add contact info]
- DevOps Lead: [Add contact info]
- On-Call Engineer: [Add contact info]

---

**Document Version:** 1.0
**Last Reviewed:** 2025-10-27
**Next Review:** Monthly or after major deployments
