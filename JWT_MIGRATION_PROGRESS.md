# JWT Authentication Migration Progress

**Issue #2 (P0): Standardize Authentication to JWT Only**

**Date Started:** October 24, 2025  
**Status:** 🟡 In Progress  
**Completion:** 19 / 106 endpoints (17.9%)

---

## 📊 MIGRATION OVERVIEW

### What's Changing

**FROM (Legacy `require_bearer`):**
```python
from ..core.auth import require_bearer

@router.get("/endpoint")
def endpoint(_=Depends(require_bearer)):
    # Returns token string (usually ignored)
    pass
```

**TO (JWT `get_current_user`):**
```python
from ..core.jwt import get_current_user
from ..models.database import User

@router.get("/endpoint")
def endpoint(current_user: User = Depends(get_current_user)):
    # Returns User object with: id, email, role, preferences
    # Now we have proper user context!
    pass
```

### Benefits of JWT Migration
1. ✅ **Proper user identification** - Know who is making each request
2. ✅ **Role-based access control** - Can check `current_user.role`
3. ✅ **User preferences** - Access to user-specific settings
4. ✅ **Audit trail** - Track actions by user ID
5. ✅ **Session management** - Token refresh, logout functionality
6. ✅ **Security** - Industry-standard JWT tokens

---

## ✅ COMPLETED FILES

### 1. settings.py (2 endpoints) ✅
- `/settings` POST
- `/config` GET

### 2. health.py (1 endpoint) ✅
- `/health/detailed` GET

### 3. portfolio.py (3 endpoints) ✅
- `/account` GET
- `/positions` GET
- `/positions/{symbol}` GET

### 4. positions.py (3 endpoints) ✅
- `/api/positions` GET
- `/api/positions/greeks` GET
- `/api/positions/{id}/close` POST

### 5. proposals.py (3 endpoints) ✅
- `/api/proposals/create` POST
- `/api/proposals/execute` POST
- `/api/proposals/history` GET

### 6. users.py (3 endpoints) ✅ **BONUS: Removed hardcoded user_id=1!**
- `/users/preferences` GET - Now uses `current_user.id`
- `/users/preferences` PATCH - Now uses `current_user.id`
- `/users/risk-limits` GET - Now uses `current_user.id`

### 7. market_data.py (4 endpoints) ✅
- `/market/quote/{symbol}` GET
- `/market/quotes` GET
- `/market/bars/{symbol}` GET
- `/market/scanner/under4` GET

**Total: 7 files, 19 endpoints completed**

---

## 📋 REMAINING FILES (20 files, 100 endpoints)

### High Priority Files (Used by Frontend)

#### positions.py (3 endpoints)
- GET `` (list positions)
- GET `/greeks` (portfolio Greeks)
- POST `/{position_id}/close` (close position)

#### proposals.py (3 endpoints)
- POST `/create`
- POST `/execute`
- GET `/history`

#### market_data.py (3 endpoints)
- GET `/market/quote/{symbol}`
- GET `/market/quotes`
- GET `/market/bars/{symbol}`
- GET `/scanner/under4`

#### orders.py (8 endpoints)
- POST `/trading/execute`
- POST `/admin/kill`
- GET `/order-templates`
- POST `/order-templates`
- GET `/order-templates/{id}`
- PUT `/order-templates/{id}`
- DELETE `/order-templates/{id}`

### Medium Priority Files

#### users.py (4 endpoints)
- GET `/users/preferences`
- PUT `/users/preferences`
- GET `/users/risk-limits`

#### scheduler.py (12 endpoints)
- GET `/schedules`
- POST `/schedules`
- PUT `/schedules/{id}`
- DELETE `/schedules/{id}`
- POST `/schedules/pause-all`
- POST `/schedules/resume-all`
- GET `/executions`
- GET `/approvals/pending`
- POST `/approvals/{id}/approve`
- POST `/approvals/{id}/decision`
- GET `/status`

#### stream.py (4 endpoints)
- GET `/stream/market-data`
- GET `/stream/market-indices`
- GET `/stream/positions`
- GET `/stream/alpaca-market-data`
- GET `/stream/status`

#### analytics.py (3 endpoints)
- GET `/portfolio/summary`
- GET `/portfolio/history`
- GET `/analytics/performance`

#### options.py (5 endpoints)
- GET `/options/chain/{symbol}`
- GET `/options/expirations/{symbol}`
- POST `/options/greeks`
- GET `/options/strategies`

#### strategies.py (8 endpoints)
- POST `/strategies`
- GET `/strategies/{type}`
- GET `/strategies`
- POST `/strategies/run`
- DELETE `/strategies/{type}`
- GET `/opportunity-scanner`
- GET `/strategy-builder`
- POST `/validate-strategy`

### Lower Priority Files

#### claude.py (1 endpoint)
- POST `/claude/chat`

#### ai.py (16 endpoints)
- GET `/recommendations`
- GET `/signals`
- GET `/analyze-symbol/{symbol}`
- GET `/recommended-templates`
- POST `/recommendations/save`
- GET `/recommendation-history`
- GET `/analyze-portfolio`
- POST `/analyze-news`
- POST `/analyze-news-batch`

#### news.py (7 endpoints)
- GET `/news/company/{symbol}`
- GET `/news/market`
- GET `/news/providers`
- GET `/news/health`
- GET `/news/sentiment/market`
- GET `/news/cache/stats`
- POST `/news/cache/clear`

#### stock.py (3 endpoints)
- GET `/stock/{symbol}/info`
- GET `/stock/{symbol}/news`
- GET `/stock/{symbol}/complete`

#### screening.py (2 endpoints)
- GET `/screening/opportunities`
- GET `/screening/strategies`

#### backtesting.py (2 endpoints)
- POST `/backtesting/run`
- GET `/backtesting/quick-test`

#### market.py (4 endpoints)
- GET `/market/conditions`
- GET `/market/indices`
- GET `/market/sectors`
- GET `/market/status`

---

## 🔄 MIGRATION PROCESS

### Step 1: Update Imports
```python
# OLD
from ..core.auth import require_bearer

# NEW
from ..core.jwt import get_current_user
from ..models.database import User
```

### Step 2: Update Function Signatures
```python
# OLD
def endpoint(_=Depends(require_bearer)):

# NEW  
def endpoint(current_user: User = Depends(get_current_user)):
```

### Step 3: Update dependencies= Style (if used)
```python
# OLD
@router.get("/endpoint", dependencies=[Depends(require_bearer)])

# NEW
@router.get("/endpoint")
async def endpoint(current_user: User = Depends(get_current_user)):
```

---

## 🧪 TESTING CHECKLIST

After migration, test:
- [ ] User can authenticate with JWT token
- [ ] All endpoints require authentication
- [ ] Tokens expire correctly (15 min for access, 7 days for refresh)
- [ ] Token refresh works
- [ ] Logout invalidates sessions
- [ ] Different user roles work (owner, beta_tester, personal_only)
- [ ] Legacy bearer tokens are rejected

---

## 📈 ESTIMATED COMPLETION

- **Completed:** 6 / 106 endpoints (5.7%)
- **Remaining:** 100 endpoints
- **Estimated time:** ~3-4 hours
- **Current pace:** ~6 endpoints per 30 minutes
- **ETA:** ~5 hours from start

---

## 🚨 POTENTIAL ISSUES

### Issue 1: Dependencies on Token String
Some code may expect a token string from `require_bearer`. Need to check:
- Logging that uses the token
- Passing token to external services
- Token validation logic

**Solution:** Extract token from JWT if needed using `decode_token()`

### Issue 2: Database Dependency
JWT auth requires database for user lookup and session validation.

**Solution:** All endpoints already have DB access via `Depends(get_db)`

### Issue 3: User ID for Personal Data
Some endpoints (e.g., `/users/preferences`) need the current user's ID.

**Solution:** Use `current_user.id` instead of hardcoded user IDs

---

## 💡 NEXT STEPS

1. **Complete High Priority Files First**
   - positions.py
   - proposals.py
   - market_data.py
   - orders.py

2. **Update TODO.md**
   - Mark migration progress
   - Update completion percentage

3. **Test in Development**
   - Verify JWT tokens work
   - Test all migrated endpoints

4. **Deploy to Production**
   - Update environment variables
   - Run migration script
   - Monitor for errors

---

**Last Updated:** October 24, 2025  
**Updated By:** Dr. Cursor Claude  
**Next Update:** After completing high-priority files

