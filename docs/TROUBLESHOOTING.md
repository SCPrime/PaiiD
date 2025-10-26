# PaiiD Troubleshooting Guide

## Overview

This guide provides solutions to common issues encountered during development, deployment, and operation of the PaiiD trading platform. Issues are organized by category for quick reference.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Frontend Issues](#frontend-issues)
3. [Backend Issues](#backend-issues)
4. [API Integration Issues](#api-integration-issues)
5. [Database Issues](#database-issues)
6. [Authentication Issues](#authentication-issues)
7. [Deployment Issues](#deployment-issues)
8. [Performance Issues](#performance-issues)
9. [Development Environment Issues](#development-environment-issues)
10. [Getting Help](#getting-help)

---

## Quick Diagnostics

### Health Check Command

Run this command to check system health:

```bash
# Backend health
curl http://localhost:8001/api/health

# Frontend health
curl -I http://localhost:3000

# Production health
curl https://paiid-backend.onrender.com/api/health
```

### Log Analysis

```bash
# Frontend logs
cd frontend && npm run dev

# Backend logs
cd backend && python -m uvicorn app.main:app --reload --port 8001

# Check for errors in output
```

### Common Error Patterns

| Error Message | Category | Quick Fix |
|---------------|----------|-----------|
| `401 Unauthorized` | Authentication | Check API_TOKEN matches |
| `Connection refused` | Network | Ensure service is running |
| `Module not found` | Dependencies | Run `npm install` or `pip install` |
| `CORS policy` | Configuration | Check ALLOW_ORIGIN setting |
| `Database connection failed` | Database | Verify DATABASE_URL |

---

## Frontend Issues

### Issue: Frontend Not Starting

**Symptoms:**
```bash
npm run dev
# Error: Cannot find module 'next'
```

**Solution:**
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next

# Try again
npm run dev
```

### Issue: TypeScript Compilation Errors

**Symptoms:**
```bash
npm run build
# Error: Type 'X' is not assignable to type 'Y'
```

**Solution:**
```bash
# Check TypeScript version
npx tsc --version

# Reinstall type definitions
npm install --save-dev @types/react @types/node @types/d3

# Run type check
npm run type-check

# Fix errors in reported files
```

### Issue: API Calls Failing (404)

**Symptoms:**
```
Console: GET /api/proxy/api/positions 404 Not Found
```

**Solution:**
```typescript
// Check proxy configuration
// frontend/pages/api/proxy/[...path].ts

// Verify backend URL
console.log('Backend URL:', process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL);

// Should be: http://127.0.0.1:8001

// Test backend directly
curl http://127.0.0.1:8001/api/positions
```

**Common Causes:**
1. Backend not running on port 8001
2. Wrong backend URL in `.env.local`
3. CORS issues (check backend logs)

### Issue: D3.js Radial Menu Not Rendering

**Symptoms:**
```
Console: Cannot read property 'arc' of undefined
```

**Solution:**
```bash
# Verify D3 installation
npm list d3

# Should show: d3@7.9.0

# Reinstall D3
npm install d3@7.9.0 @types/d3@7.4.3

# Clear cache and rebuild
rm -rf .next
npm run dev
```

### Issue: Environment Variables Not Loading

**Symptoms:**
```typescript
console.log(process.env.NEXT_PUBLIC_API_TOKEN);
// Output: undefined
```

**Solution:**
```bash
# 1. Check .env.local exists
ls -la frontend/.env.local

# 2. Verify variable names have NEXT_PUBLIC_ prefix
cat frontend/.env.local
# Must be: NEXT_PUBLIC_API_TOKEN=...

# 3. Restart dev server (env vars loaded at startup)
# Stop server (Ctrl+C)
npm run dev

# 4. Check variable in browser console
console.log(process.env.NEXT_PUBLIC_API_TOKEN);
```

### Issue: Hot Reload Not Working

**Symptoms:**
- Save file, but changes not reflected
- Browser doesn't auto-refresh

**Solution:**
```bash
# 1. Check for syntax errors in code
npm run lint

# 2. Clear .next cache
rm -rf .next

# 3. Restart dev server
npm run dev

# 4. Hard refresh browser (Ctrl+Shift+R)

# 5. If still not working, check file watchers
# Windows: May need to increase file watcher limit
```

---

## Backend Issues

### Issue: Backend Not Starting

**Symptoms:**
```bash
python -m uvicorn app.main:app --reload --port 8001
# Error: ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Verify virtual environment is activated
which python  # Should show venv path

# If not activated:
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Try again
python -m uvicorn app.main:app --reload --port 8001
```

### Issue: ImportError - Circular Imports

**Symptoms:**
```
ImportError: cannot import name 'X' from partially initialized module 'Y'
```

**Solution:**
```python
# Identify circular dependency
# Example: auth.py imports user.py, user.py imports auth.py

# Fix: Use TYPE_CHECKING for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User

# Or: Move import to function scope
def get_user():
    from .models import User
    return User.query.first()
```

### Issue: Database Connection Failed

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# 1. Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:pass@host:port/dbname

# 2. Test connection directly
psql $DATABASE_URL
# If connection fails, check:
# - PostgreSQL is running
# - Credentials are correct
# - Host is reachable

# 3. For local development, use SQLite
# In .env:
DATABASE_URL=sqlite:///./dev.db

# 4. Run migrations
alembic upgrade head
```

### Issue: Alembic Migration Errors

**Symptoms:**
```bash
alembic upgrade head
# Error: Target database is not up to date.
```

**Solution:**
```bash
# Check current revision
alembic current

# Check pending revisions
alembic heads

# Reset to head (CAUTION: drops data)
alembic downgrade base
alembic upgrade head

# Or: Auto-resolve conflicts
alembic stamp head
alembic upgrade head
```

### Issue: Port Already in Use

**Symptoms:**
```
Error: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8001
lsof -i :8001  # Linux/Mac
netstat -ano | findstr :8001  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Or: Use different port
python -m uvicorn app.main:app --reload --port 8002
```

### Issue: Pydantic Validation Errors

**Symptoms:**
```
pydantic.error_wrappers.ValidationError: 2 validation errors
```

**Solution:**
```python
# Check Pydantic model definition
class OrderRequest(BaseModel):
    symbol: str  # Required field
    quantity: int

# Ensure all required fields provided
order = OrderRequest(
    symbol="AAPL",
    quantity=10
)

# Use Field for validation
from pydantic import Field

class OrderRequest(BaseModel):
    symbol: str = Field(..., regex=r"^[A-Z]{1,5}$")
    quantity: int = Field(..., gt=0, le=10000)
```

---

## API Integration Issues

### Issue: Tradier API 401 Unauthorized

**Symptoms:**
```
Response: {"fault": {"detail": {"errorcode": "oauth.v2.InvalidApiKey"}}}
```

**Solution:**
```bash
# 1. Verify API key in .env
cat backend/.env | grep TRADIER_API_KEY

# 2. Test API key manually
curl -H "Authorization: Bearer YOUR_TRADIER_KEY" \
     https://api.tradier.com/v1/markets/quotes?symbols=AAPL

# 3. Check API key is active in Tradier dashboard
# https://dash.tradier.com

# 4. Regenerate API key if expired
# Copy new key to .env
# Restart backend
```

### Issue: Alpaca API Connection Timeout

**Symptoms:**
```
TimeoutError: Connection to Alpaca API timed out
```

**Solution:**
```bash
# 1. Check network connectivity
ping paper-api.alpaca.markets

# 2. Verify API keys
echo $ALPACA_PAPER_API_KEY

# 3. Test API directly
curl -H "APCA-API-KEY-ID: YOUR_KEY" \
     -H "APCA-API-SECRET-KEY: YOUR_SECRET" \
     https://paper-api.alpaca.markets/v2/account

# 4. Check Alpaca service status
# https://status.alpaca.markets

# 5. Increase timeout in code
import httpx

client = httpx.AsyncClient(timeout=30.0)
```

### Issue: Anthropic API Rate Limit

**Symptoms:**
```
AnthropicError: Rate limit exceeded
```

**Solution:**
```python
# 1. Implement exponential backoff
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3)
)
def call_anthropic_api():
    # API call

# 2. Cache AI responses
from app.services.cache import cache_service

cache_key = f"ai_rec_{symbol}"
cached = cache_service.get(cache_key)
if cached:
    return cached

response = call_anthropic_api()
cache_service.set(cache_key, response, ttl=300)

# 3. Upgrade Anthropic plan for higher limits
```

### Issue: CORS Errors in Browser

**Symptoms:**
```
Access to fetch at 'http://localhost:8001/api/positions' blocked by CORS policy
```

**Solution:**
```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://paiid-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Verify middleware is registered
# Check startup logs for "CORS middleware enabled"

# Restart backend after changes
```

---

## Database Issues

### Issue: Migration Conflicts

**Symptoms:**
```
alembic.util.CommandError: Multiple head revisions are present
```

**Solution:**
```bash
# 1. Check current heads
alembic heads

# 2. Merge heads
alembic merge -m "merge heads" <rev1> <rev2>

# 3. Apply merged migration
alembic upgrade head
```

### Issue: SQLAlchemy Session Errors

**Symptoms:**
```
sqlalchemy.exc.InvalidRequestError: Object is already attached to session
```

**Solution:**
```python
# Use session properly with dependency injection
from app.db.session import get_db
from sqlalchemy.orm import Session

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
    # Session automatically closed after request

# Don't reuse objects across sessions
# If needed, use merge()
user = db.merge(existing_user)
```

### Issue: Database Lock (SQLite)

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# SQLite not suitable for production with multiple workers
# Switch to PostgreSQL

# For development:
# 1. Use single worker
uvicorn app.main:app --workers 1

# 2. Or migrate to PostgreSQL
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:pass@localhost/paiid

# Run migrations
alembic upgrade head
```

### Issue: Connection Pool Exhausted

**Symptoms:**
```
sqlalchemy.exc.TimeoutError: QueuePool limit exceeded
```

**Solution:**
```python
# backend/app/db/session.py
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Increase pool size
    max_overflow=40,     # Increase overflow
    pool_timeout=30,     # Increase timeout
    pool_recycle=3600    # Recycle connections every hour
)

# Also check for unclosed sessions
# Always use dependency injection with get_db()
```

---

## Authentication Issues

### Issue: JWT Token Expired

**Symptoms:**
```
401 Unauthorized: Token has expired
```

**Solution:**
```typescript
// Frontend: Implement token refresh
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');

  const response = await fetch('/api/proxy/api/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });

  const { access_token } = await response.json();
  localStorage.setItem('access_token', access_token);
  return access_token;
}

// Use in API calls
async function fetchWithAuth(url: string) {
  let token = localStorage.getItem('access_token');

  let response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });

  // If 401, refresh and retry
  if (response.status === 401) {
    token = await refreshAccessToken();
    response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }

  return response.json();
}
```

### Issue: API Token Mismatch

**Symptoms:**
```
403 Forbidden: Invalid API token
```

**Solution:**
```bash
# 1. Generate new token
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Update backend/.env
API_TOKEN=new-token-here

# 3. Update frontend/.env.local
NEXT_PUBLIC_API_TOKEN=new-token-here

# 4. Restart both services
# Backend:
python -m uvicorn app.main:app --reload --port 8001

# Frontend:
npm run dev

# 5. Verify token in requests
curl -H "Authorization: Bearer new-token-here" \
     http://localhost:8001/api/health
```

### Issue: Password Hash Validation Failing

**Symptoms:**
```
Login fails with correct password
```

**Solution:**
```python
# Check password hashing
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Hash password (during registration)
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Test manually
plain = "testpassword"
hashed = hash_password(plain)
print(verify_password(plain, hashed))  # Should be True
```

---

## Deployment Issues

### Issue: Render Build Failing

**Symptoms:**
```
Render: Build failed with exit code 1
```

**Solution:**
```bash
# 1. Check build logs on Render dashboard
# Common issues:
# - Missing environment variables
# - Dependency installation failure
# - Build command incorrect

# 2. Test build locally
cd frontend
npm run build

cd backend
pip install -r requirements.txt

# 3. Fix any errors found
# 4. Commit and push
git add .
git commit -m "fix: resolve build errors"
git push origin main
```

### Issue: Environment Variables Not Set

**Symptoms:**
```
Backend logs: API_TOKEN not set
```

**Solution:**
```bash
# 1. Go to Render dashboard
# 2. Select service (frontend or backend)
# 3. Go to "Environment" tab
# 4. Add missing variables:
#    - API_TOKEN
#    - DATABASE_URL
#    - TRADIER_API_KEY
#    etc.
# 5. Click "Save Changes"
# 6. Render will auto-redeploy
```

### Issue: Database Migration Not Applied

**Symptoms:**
```
sqlalchemy.exc.ProgrammingError: relation "users" does not exist
```

**Solution:**
```bash
# Connect to Render shell
render shell -s paiid-backend

# Run migrations
alembic upgrade head

# Verify tables exist
psql $DATABASE_URL -c "\dt"
```

### Issue: Health Check Timing Out

**Symptoms:**
```
Render: Health check failed, service marked as unhealthy
```

**Solution:**
```python
# backend/app/routers/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/health")
async def health_check():
    # Keep health check fast (< 1 second)
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }

# Don't include slow checks in health endpoint
# Create separate endpoint for detailed checks
@router.get("/api/health/detailed")
async def detailed_health():
    return {
        "database": check_database(),
        "redis": check_redis(),
        # ... other checks
    }
```

---

## Performance Issues

### Issue: Slow API Response Times

**Symptoms:**
```
API calls taking > 2 seconds
```

**Solution:**
```python
# 1. Add caching
from app.services.cache import cache_service

@router.get("/market/quote/{symbol}")
async def get_quote(symbol: str):
    cache_key = f"quote_{symbol}"
    cached = cache_service.get(cache_key)

    if cached:
        return cached

    data = tradier_client.get_quote(symbol)
    cache_service.set(cache_key, data, ttl=5)
    return data

# 2. Add database indexing
# In migration:
op.create_index('idx_trades_user', 'trades', ['user_id'])

# 3. Use connection pooling
# See database section above

# 4. Profile slow queries
import time

start = time.time()
result = db.query(User).all()
print(f"Query took {time.time() - start:.2f}s")
```

### Issue: High Memory Usage

**Symptoms:**
```
Backend using > 500MB memory
```

**Solution:**
```python
# 1. Paginate large queries
from fastapi import Query

@router.get("/trades")
async def get_trades(
    skip: int = Query(0),
    limit: int = Query(100, le=1000)
):
    trades = db.query(Trade).offset(skip).limit(limit).all()
    return trades

# 2. Use streaming for large responses
from fastapi.responses import StreamingResponse

@router.get("/export/trades")
async def export_trades():
    def generate():
        for trade in db.query(Trade).yield_per(100):
            yield trade.to_json() + "\n"

    return StreamingResponse(generate(), media_type="application/json")

# 3. Clear caches periodically
cache_service.clear_expired()
```

### Issue: Frontend Bundle Too Large

**Symptoms:**
```
npm run build
# Warning: Large bundle size (> 1MB)
```

**Solution:**
```typescript
// Use dynamic imports for large components
import dynamic from 'next/dynamic';

const MLIntelligence = dynamic(
  () => import('../components/MLIntelligenceDashboard'),
  { loading: () => <Spinner /> }
);

// Analyze bundle
npm run analyze

// Check for:
// - Duplicate dependencies
// - Large libraries
// - Unused code
```

---

## Development Environment Issues

### Issue: Git Merge Conflicts

**Symptoms:**
```bash
git pull
# CONFLICT (content): Merge conflict in frontend/package.json
```

**Solution:**
```bash
# 1. View conflicted files
git status

# 2. Open file and resolve conflicts
# Look for markers: <<<<<<<, =======, >>>>>>>

# 3. Keep desired changes, remove markers

# 4. Mark as resolved
git add frontend/package.json

# 5. Complete merge
git commit -m "resolve: merge conflict in package.json"
```

### Issue: VS Code TypeScript Server Crash

**Symptoms:**
```
VS Code: The TypeScript language service crashed
```

**Solution:**
```bash
# 1. Restart TS server
# VS Code: Ctrl+Shift+P → "TypeScript: Restart TS Server"

# 2. If persists, delete cache
rm -rf frontend/.next
rm -rf frontend/node_modules/.cache

# 3. Reinstall TypeScript
cd frontend
npm install --save-dev typescript@5.9.2

# 4. Restart VS Code
```

### Issue: ESLint Not Working

**Symptoms:**
```
VS Code: No ESLint errors showing
```

**Solution:**
```bash
# 1. Check ESLint extension installed
# VS Code: Extensions → Search "ESLint"

# 2. Verify .eslintrc.json exists
cat frontend/.eslintrc.json

# 3. Check ESLint output panel
# VS Code: View → Output → Select "ESLint"

# 4. Run ESLint manually
cd frontend
npm run lint

# 5. Reinstall ESLint
npm install --save-dev eslint eslint-config-next
```

---

## Getting Help

### Self-Service Resources

**Documentation:**
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) - Development setup
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment instructions
- [API_DOCUMENTATION_COMPREHENSIVE.md](./API_DOCUMENTATION_COMPREHENSIVE.md) - API reference

**External Resources:**
- Next.js Docs: https://nextjs.org/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Render Docs: https://render.com/docs
- Tradier API Docs: https://documentation.tradier.com
- Alpaca API Docs: https://alpaca.markets/docs

### Community Support

**GitHub:**
- Search existing issues: https://github.com/YOUR-REPO/issues
- Create new issue with:
  - Clear description
  - Steps to reproduce
  - Expected vs actual behavior
  - Environment details
  - Error logs

**Issue Template:**
```markdown
**Describe the issue**
[Clear description]

**Steps to reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
[What should happen]

**Actual behavior**
[What actually happens]

**Environment**
- OS: [e.g., macOS 14.0]
- Node: [e.g., 20.17.0]
- Python: [e.g., 3.10.5]
- Browser: [e.g., Chrome 120]

**Error logs**
```
[Paste error logs here]
```
```

### Debugging Checklist

Before asking for help, try these steps:

- [ ] Check this troubleshooting guide
- [ ] Search existing GitHub issues
- [ ] Review error logs carefully
- [ ] Test in isolation (minimal reproduction)
- [ ] Verify environment variables set
- [ ] Check service status (Tradier, Alpaca, etc.)
- [ ] Restart development servers
- [ ] Clear caches (.next, node_modules/.cache)
- [ ] Update dependencies to latest versions
- [ ] Test in different environment (local vs production)

### Contact Information

**Project Maintainers:**
- GitHub: Open an issue
- Email: [Project email if available]

**Service Providers:**
- Render Support: https://render.com/support
- Tradier Support: https://support.tradier.com
- Alpaca Support: https://alpaca.markets/support

---

## Appendix: Error Code Reference

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Endpoint doesn't exist |
| 422 | Unprocessable | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Backend crash |
| 502 | Bad Gateway | Backend unreachable |
| 503 | Service Unavailable | Service down |

### Backend Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `AUTH_001` | Invalid API token | Check API_TOKEN in .env |
| `AUTH_002` | JWT expired | Refresh token |
| `DB_001` | Database connection failed | Check DATABASE_URL |
| `API_001` | Tradier API error | Verify TRADIER_API_KEY |
| `API_002` | Alpaca API error | Verify ALPACA credentials |

---

**Document Version:** 1.0.0
**Last Updated:** October 26, 2025
**Maintainer:** PaiiD Development Team

**Remember:** Most issues have simple solutions. Stay calm, read error messages carefully, and work through the troubleshooting steps systematically. You've got this! 💪
